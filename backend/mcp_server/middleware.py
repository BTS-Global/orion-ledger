"""
MCP Server Middleware
Authentication, rate limiting, and audit logging
"""
import time
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as redis
from .config import settings

logger = logging.getLogger(__name__)


class MCPAuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware for MCP server.
    Validates API keys and enforces company-level isolation.
    """
    
    def __init__(self, app, redis_client: redis.Redis):
        super().__init__(app)
        self.redis = redis_client
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for health checks
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
        
        # Extract API key
        api_key = request.headers.get(settings.API_KEY_HEADER)
        if not api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Missing API key"}
            )
        
        # Validate API key and get company_id
        company_id = await self._validate_api_key(api_key)
        if not company_id:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid API key"}
            )
        
        # Add company_id to request state
        request.state.company_id = company_id
        request.state.api_key = api_key
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Add timing header
        response.headers["X-Process-Time"] = str(duration)
        
        return response
    
    async def _validate_api_key(self, api_key: str) -> Optional[str]:
        """Validate API key and return company_id"""
        try:
            # Check cache first
            cache_key = f"mcp:apikey:{api_key}"
            cached = await self.redis.get(cache_key)
            
            if cached:
                return cached.decode()
            
            # Query database (import here to avoid circular dependency)
            from core.models import APIKey
            
            try:
                api_key_obj = APIKey.objects.select_related('company').get(
                    key=api_key,
                    is_active=True
                )
                company_id = str(api_key_obj.company.id)
                
                # Cache for 5 minutes
                await self.redis.setex(cache_key, 300, company_id)
                
                return company_id
            except APIKey.DoesNotExist:
                return None
                
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return None


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis.
    Implements per-company rate limits.
    """
    
    def __init__(self, app, redis_client: redis.Redis):
        super().__init__(app)
        self.redis = redis_client
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
        
        company_id = getattr(request.state, "company_id", None)
        if not company_id:
            return await call_next(request)
        
        # Check rate limits
        rate_limit_ok, retry_after = await self._check_rate_limit(company_id)
        
        if not rate_limit_ok:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": retry_after
                },
                headers={"Retry-After": str(retry_after)}
            )
        
        return await call_next(request)
    
    async def _check_rate_limit(self, company_id: str) -> tuple[bool, int]:
        """Check if request is within rate limits"""
        try:
            current_time = int(time.time())
            
            # Per-minute limit
            minute_key = f"mcp:ratelimit:{company_id}:minute:{current_time // 60}"
            minute_count = await self.redis.incr(minute_key)
            
            if minute_count == 1:
                await self.redis.expire(minute_key, 60)
            
            if minute_count > settings.RATE_LIMIT_PER_MINUTE:
                retry_after = 60 - (current_time % 60)
                return False, retry_after
            
            # Per-hour limit
            hour_key = f"mcp:ratelimit:{company_id}:hour:{current_time // 3600}"
            hour_count = await self.redis.incr(hour_key)
            
            if hour_count == 1:
                await self.redis.expire(hour_key, 3600)
            
            if hour_count > settings.RATE_LIMIT_PER_HOUR:
                retry_after = 3600 - (current_time % 3600)
                return False, retry_after
            
            return True, 0
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # Fail open - allow request if Redis is down
            return True, 0


class AuditLogMiddleware(BaseHTTPMiddleware):
    """
    Audit logging middleware.
    Logs all MCP operations for compliance and debugging.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Skip audit for health checks
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
        
        # Capture request info
        request_id = request.headers.get("X-Request-ID", f"req_{int(time.time() * 1000)}")
        company_id = getattr(request.state, "company_id", None)
        
        # Add request_id to state
        request.state.request_id = request_id
        
        start_time = time.time()
        
        # Process request
        try:
            response = await call_next(request)
            success = True
            status_code = response.status_code
        except Exception as e:
            success = False
            status_code = 500
            logger.error(f"Request failed: {e}")
            raise
        finally:
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log audit entry
            await self._log_audit_entry(
                request_id=request_id,
                company_id=company_id,
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration_ms=duration_ms,
                success=success
            )
        
        # Add request_id to response
        response.headers["X-Request-ID"] = request_id
        
        return response
    
    async def _log_audit_entry(
        self,
        request_id: str,
        company_id: Optional[str],
        method: str,
        path: str,
        status_code: int,
        duration_ms: int,
        success: bool
    ):
        """Log audit entry"""
        try:
            audit_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id,
                "company_id": company_id,
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "success": success,
                "service": "mcp-server"
            }
            
            logger.info(f"MCP Audit: {json.dumps(audit_entry)}")
            
            # Also store in database for long-term retention
            from core.models import AuditLog
            
            AuditLog.objects.create(
                company_id=company_id,
                request_id=request_id,
                service="mcp-server",
                method=method,
                path=path,
                status_code=status_code,
                duration_ms=duration_ms,
                success=success
            )
            
        except Exception as e:
            logger.error(f"Error logging audit entry: {e}")


def setup_cors_middleware(app):
    """Setup CORS middleware"""
    from fastapi.middleware.cors import CORSMiddleware
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure properly in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
