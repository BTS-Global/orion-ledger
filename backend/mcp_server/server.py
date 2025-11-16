"""
Orion Ledger MCP Server
FastAPI-based Model Context Protocol server
"""
import logging
import sys
import os
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import redis.asyncio as redis
import uvicorn

from .config import settings, SUPPORTED_MODELS
from .middleware import (
    MCPAuthMiddleware,
    RateLimitMiddleware,
    AuditLogMiddleware,
    setup_cors_middleware
)
from .resources import get_resource, RESOURCE_REGISTRY
from .tools import execute_tool, TOOL_REGISTRY
from .prompts import get_prompt, list_prompts

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Redis client
redis_client: Optional[redis.Redis] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global redis_client
    
    # Startup
    logger.info("Starting Orion MCP Server...")
    
    # Connect to Redis
    try:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            decode_responses=True
        )
        await redis_client.ping()
        logger.info("✓ Connected to Redis")
    except Exception as e:
        logger.error(f"✗ Failed to connect to Redis: {e}")
        redis_client = None
    
    logger.info(f"✓ MCP Server started on {settings.HOST}:{settings.PORT}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Orion MCP Server...")
    
    if redis_client:
        await redis_client.close()
        logger.info("✓ Redis connection closed")


# Create FastAPI app
app = FastAPI(
    title="Orion Ledger MCP Server",
    description="Model Context Protocol server for AI-powered accounting",
    version="0.1.0",
    lifespan=lifespan
)


# Setup middleware
setup_cors_middleware(app)

# Add custom middleware (order matters!)
if redis_client:
    app.add_middleware(AuditLogMiddleware)
    app.add_middleware(RateLimitMiddleware, redis_client=redis_client)
    app.add_middleware(MCPAuthMiddleware, redis_client=redis_client)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "service": "mcp-server",
        "version": "0.1.0",
        "redis": "connected" if redis_client else "disconnected",
    }
    
    return JSONResponse(content=health_status)


# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Metrics endpoint for monitoring"""
    # TODO: Implement comprehensive metrics
    return {
        "requests_total": 0,
        "requests_per_minute": 0,
        "avg_latency_ms": 0,
        "error_rate": 0,
    }


# MCP Resources Endpoints

@app.get("/resources")
async def list_resources():
    """List available MCP resources"""
    return {
        "resources": [
            {
                "type": name,
                "description": f"Access {name} data",
                "uri_pattern": f"mcp://orion/{name}/{{company_id}}"
            }
            for name in RESOURCE_REGISTRY.keys()
        ]
    }


@app.get("/resources/{resource_type}/{company_id}")
async def get_resource_endpoint(
    resource_type: str,
    company_id: str,
    request: Request
):
    """Get a specific resource"""
    try:
        # Verify company_id matches authenticated company
        if company_id != request.state.company_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company's data"
            )
        
        # Get query parameters
        params = dict(request.query_params)
        
        # Get resource
        resource = get_resource(resource_type, company_id, **params)
        data = resource.to_dict()
        
        return JSONResponse(content=data)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting resource: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# MCP Tools Endpoints

@app.get("/tools")
async def list_tools():
    """List available MCP tools"""
    return {
        "tools": [
            {
                "name": name,
                "description": config["description"],
                "parameters": config["params"].schema()
            }
            for name, config in TOOL_REGISTRY.items()
        ]
    }


@app.post("/tools/{tool_name}")
async def execute_tool_endpoint(
    tool_name: str,
    params: Dict[str, Any],
    request: Request
):
    """Execute a tool"""
    try:
        # Verify company_id in params matches authenticated company
        if params.get("company_id") != request.state.company_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company's data"
            )
        
        # Execute tool
        result = await execute_tool(tool_name, params)
        
        if not result.get("success"):
            return JSONResponse(
                status_code=400,
                content=result
            )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error executing tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# MCP Prompts Endpoints

@app.get("/prompts")
async def list_prompts_endpoint():
    """List available prompt templates"""
    prompts = list_prompts()
    
    return {
        "prompts": [
            {
                "name": name,
                "template": template[:200] + "..."  # Preview only
            }
            for name, template in prompts.items()
        ]
    }


@app.post("/prompts/{prompt_name}")
async def render_prompt_endpoint(
    prompt_name: str,
    variables: Dict[str, Any]
):
    """Render a prompt template with variables"""
    try:
        rendered = get_prompt(prompt_name, **variables)
        
        return {
            "prompt_name": prompt_name,
            "rendered": rendered
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error rendering prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# MCP Models Endpoint

@app.get("/models")
async def list_models():
    """List supported LLM models"""
    return {
        "models": SUPPORTED_MODELS
    }


# Main entry point
def main():
    """Run the MCP server"""
    uvicorn.run(
        "mcp_server.server:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()
