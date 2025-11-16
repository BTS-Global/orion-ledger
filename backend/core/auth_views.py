from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from rest_framework.authtoken.models import Token


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user with email and password"""
    email = request.data.get('email')
    password = request.data.get('password')
    name = request.data.get('name', '')
    
    if not email or not password:
        return Response(
            {'error': 'Email and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user already exists
    if User.objects.filter(username=email).exists():
        return Response(
            {'error': 'User with this email already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create user
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=name.split()[0] if name else '',
        last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
    )
    
    # Create token
    token, _ = Token.objects.get_or_create(user=user)
    
    return Response({
        'message': 'User created successfully',
        'user': {
            'id': user.id,
            'email': user.email,
            'name': user.get_full_name() or user.username,
        },
        'token': token.key
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def login_user(request):
    """Login user with email and password"""
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response(
            {'error': 'Email and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Authenticate user
    user = authenticate(request, username=email, password=password)
    
    if user is None:
        return Response(
            {'error': 'Invalid email or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Login user
    login(request, user)
    
    # Get or create token
    token, _ = Token.objects.get_or_create(user=user)
    
    return Response({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'email': user.email,
            'name': user.get_full_name() or user.username,
        },
        'token': token.key
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def logout_user(request):
    """Logout current user"""
    logout(request)
    
    # Delete token if exists
    try:
        request.user.auth_token.delete()
    except:
        pass
    
    return Response({
        'message': 'Logout successful'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def current_user(request):
    """Get current authenticated user"""
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Not authenticated'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    return Response({
        'user': {
            'id': request.user.id,
            'email': request.user.email,
            'name': request.user.get_full_name() or request.user.username,
        }
    }, status=status.HTTP_200_OK)

