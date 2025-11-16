from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Company, UserProfile, ChartOfAccounts
from .serializers import (
    CompanySerializer, 
    CompanyDetailSerializer,
    UserProfileSerializer, 
    ChartOfAccountsSerializer
)


class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet for Company CRUD operations."""
    
    permission_classes = []  # Temporarily allow any for testing
    
    def get_queryset(self):
        """Return companies owned by or accessible to the current user."""
        # TODO: Re-enable authentication filtering after implementing proper login
        # if self.request.user.is_authenticated:
        #     user = self.request.user
        #     return Company.objects.filter(owner=user) | Company.objects.filter(users=user)
        return Company.objects.all()
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action."""
        if self.action == 'retrieve':
            return CompanyDetailSerializer
        return CompanySerializer
    
    def perform_create(self, serializer):
        """Set the owner to the current user when creating a company."""
        company = serializer.save(owner=self.request.user)
        # Add owner to users as well
        company.users.add(self.request.user)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Set this company as the active company for the current user."""
        company = self.get_object()
        
        # TODO: Re-enable authentication after implementing proper login
        # For now, just return success without saving to profile
        if not request.user.is_authenticated:
            return Response({
                'status': 'success',
                'message': f'{company.name} is now your active company (auth disabled)'
            })
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'full_name': request.user.get_full_name() or request.user.username}
        )
        
        profile.active_company = company
        profile.save()
        
        return Response({
            'status': 'success',
            'message': f'{company.name} is now your active company'
        })


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for UserProfile operations."""
    
    permission_classes = []  # Temporarily allow any for testing
    serializer_class = UserProfileSerializer
    
    def get_queryset(self):
        """Return only the current user's profile."""
        if self.request.user.is_authenticated:
            return UserProfile.objects.filter(user=self.request.user)
        return UserProfile.objects.none()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get the current user's profile."""
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'full_name': request.user.get_full_name() or request.user.username}
        )
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class ChartOfAccountsViewSet(viewsets.ModelViewSet):
    """ViewSet for Chart of Accounts CRUD operations."""
    
    permission_classes = []  # Temporarily allow any for testing
    serializer_class = ChartOfAccountsSerializer
    
    def get_queryset(self):
        """Return accounts for companies accessible to the current user."""
        if self.request.user.is_authenticated:
            user = self.request.user
            accessible_companies = Company.objects.filter(owner=user) | Company.objects.filter(users=user)
            queryset = ChartOfAccounts.objects.filter(company__in=accessible_companies)
        else:
            queryset = ChartOfAccounts.objects.all()
        
        # Filter by company if provided
        company_id = self.request.query_params.get('company', None)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # Filter by account type if provided
        account_type = self.request.query_params.get('type', None)
        if account_type:
            queryset = queryset.filter(account_type=account_type)
        
        # Filter by active status
        is_active = self.request.query_params.get('active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset

