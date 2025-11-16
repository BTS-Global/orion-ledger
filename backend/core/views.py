from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, login
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.http import JsonResponse
from companies.models import UserProfile
from companies.serializers import UserProfileSerializer
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get the current authenticated user's information."""
    
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'full_name': request.user.get_full_name() or request.user.email}
    )
    
    # Get or create auth token
    token, _ = Token.objects.get_or_create(user=request.user)
    
    return Response({
        'user': {
            'id': request.user.id,
            'email': request.user.email,
            'username': request.user.username,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        },
        'profile': UserProfileSerializer(profile).data,
        'token': token.key
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout the current user and delete their token."""
    
    try:
        # Delete the user's token
        request.user.auth_token.delete()
    except:
        pass
    
    return Response({
        'message': 'Successfully logged out'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def auth_status(request):
    """Check if the user is authenticated."""
    
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'email': request.user.email,
            }
        })
    
    return Response({
        'authenticated': False
    })


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def get_csrf_token(request):
    """Get CSRF token for frontend."""
    return Response({
        'csrfToken': get_token(request)
    })


# DEBUG ENDPOINTS - Remove in production
@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def debug_session(request):
    """Debug endpoint to check session and authentication status."""
    
    session_data = {
        'session_key': request.session.session_key,
        'session_items': dict(request.session.items()),
        'is_authenticated': request.user.is_authenticated,
        'user_id': request.user.id if request.user.is_authenticated else None,
        'user_email': request.user.email if request.user.is_authenticated else None,
        'cookies': {k: v for k, v in request.COOKIES.items()},
        'headers': {k: v for k, v in request.META.items() if k.startswith('HTTP_')},
    }
    
    logger.info(f"Debug session: {session_data}")
    return JsonResponse(session_data)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def test_login(request):
    """Test endpoint to manually create a session."""
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
        }
    )
    
    # Login the user
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    
    # Save session
    request.session.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Test user logged in',
        'user_id': user.id,
        'session_key': request.session.session_key,
    })

