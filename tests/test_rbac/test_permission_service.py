"""
Unit tests for PermissionService.

Tests core RBAC functionality:
- Permission checking
- Role assignment
- Permission caching
- Role management
"""
import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from app.services.permission_service import PermissionService
from app.database.models import Permission, Role, RolePermission, UserRole, AuthUser, Agency
from app.auth.exceptions import PermissionDeniedError, InvalidInputError


@pytest.fixture
async def sample_agency(db_session):
    """Create sample agency for testing."""
    agency = Agency(
        name="Test Agency",
        owner_id=uuid4(),
        business_type="letting_agency"
    )
    db_session.add(agency)
    await db_session.commit()
    await db_session.refresh(agency)
    return agency


@pytest.fixture
async def sample_user(db_session):
    """Create sample user for testing."""
    user = AuthUser(
        email=f"test_{uuid4()}@example.com",
        password_hash="fake_hash",
        full_name="Test User"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def sample_permissions(db_session):
    """Create sample permissions."""
    permissions = [
        Permission(name="contacts.view", resource="contacts", action="view"),
        Permission(name="contacts.edit", resource="contacts", action="edit"),
        Permission(name="properties.view", resource="properties", action="view"),
    ]
    
    for perm in permissions:
        db_session.add(perm)
    
    await db_session.commit()
    
    for perm in permissions:
        await db_session.refresh(perm)
    
    return {p.name: p for p in permissions}


@pytest.fixture
async def sample_role(db_session, sample_permissions):
    """Create sample role with permissions."""
    role = Role(
        name="test_agent",
        description="Test agent role",
        is_system_role=False
    )
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    
    # Assign permissions
    for perm in sample_permissions.values():
        role_perm = RolePermission(role_id=role.id, permission_id=perm.id)
        db_session.add(role_perm)
    
    await db_session.commit()
    
    return role


class TestPermissionService:
    """Test PermissionService."""
    
    @pytest.mark.asyncio
    async def test_create_permission(self, db_session):
        """Test creating a new permission."""
        service = PermissionService(db_session)
        
        permission = await service.create_permission(
            name="test.permission",
            resource="test",
            action="permission",
            description="Test permission"
        )
        
        assert permission.id is not None
        assert permission.name == "test.permission"
        assert permission.resource == "test"
        assert permission.action == "permission"
    
    @pytest.mark.asyncio
    async def test_create_duplicate_permission_fails(self, db_session, sample_permissions):
        """Test that creating duplicate permission fails."""
        service = PermissionService(db_session)
        
        with pytest.raises(InvalidInputError):
            await service.create_permission(
                name="contacts.view",  # Already exists
                resource="contacts",
                action="view"
            )
    
    @pytest.mark.asyncio
    async def test_create_role(self, db_session, sample_permissions):
        """Test creating a new role."""
        service = PermissionService(db_session)
        
        perm_ids = [p.id for p in sample_permissions.values()]
        
        role = await service.create_role(
            name="test_role",
            description="Test role",
            is_system_role=False,
            permission_ids=perm_ids
        )
        
        assert role.id is not None
        assert role.name == "test_role"
        
        # Verify permissions assigned
        role_perms = await service.get_role_permissions(role.id)
        assert len(role_perms) == len(sample_permissions)
    
    @pytest.mark.asyncio
    async def test_assign_role_to_user(
        self,
        db_session,
        sample_user,
        sample_role,
        sample_agency
    ):
        """Test assigning role to user."""
        service = PermissionService(db_session)
        
        assignment = await service.assign_role(
            user_id=sample_user.id,
            role_id=sample_role.id,
            agency_id=sample_agency.id,
            granted_by=sample_user.id
        )
        
        assert assignment.id is not None
        assert assignment.user_id == sample_user.id
        assert assignment.role_id == sample_role.id
        assert assignment.agency_id == sample_agency.id
    
    @pytest.mark.asyncio
    async def test_get_user_permissions(
        self,
        db_session,
        sample_user,
        sample_role,
        sample_agency,
        sample_permissions
    ):
        """Test getting user permissions."""
        service = PermissionService(db_session)
        
        # Assign role
        await service.assign_role(
            user_id=sample_user.id,
            role_id=sample_role.id,
            agency_id=sample_agency.id,
            granted_by=sample_user.id
        )
        
        # Get permissions
        permissions = await service.get_user_permissions(
            sample_user.id,
            sample_agency.id
        )
        
        assert len(permissions) == len(sample_permissions)
        assert "contacts.view" in permissions
        assert "contacts.edit" in permissions
        assert "properties.view" in permissions
    
    @pytest.mark.asyncio
    async def test_check_permission(
        self,
        db_session,
        sample_user,
        sample_role,
        sample_agency
    ):
        """Test checking if user has permission."""
        service = PermissionService(db_session)
        
        # Assign role
        await service.assign_role(
            user_id=sample_user.id,
            role_id=sample_role.id,
            agency_id=sample_agency.id,
            granted_by=sample_user.id
        )
        
        # Check permission user has
        has_perm = await service.check_permission(
            sample_user.id,
            sample_agency.id,
            "contacts.view"
        )
        assert has_perm is True
        
        # Check permission user doesn't have
        has_perm = await service.check_permission(
            sample_user.id,
            sample_agency.id,
            "contacts.delete"
        )
        assert has_perm is False
    
    @pytest.mark.asyncio
    async def test_has_role(
        self,
        db_session,
        sample_user,
        sample_role,
        sample_agency
    ):
        """Test checking if user has role."""
        service = PermissionService(db_session)
        
        # Initially doesn't have role
        has_role = await service.has_role(
            sample_user.id,
            sample_agency.id,
            "test_agent"
        )
        assert has_role is False
        
        # Assign role
        await service.assign_role(
            user_id=sample_user.id,
            role_id=sample_role.id,
            agency_id=sample_agency.id,
            granted_by=sample_user.id
        )
        
        # Now has role
        has_role = await service.has_role(
            sample_user.id,
            sample_agency.id,
            "test_agent"
        )
        assert has_role is True
    
    @pytest.mark.asyncio
    async def test_revoke_role(
        self,
        db_session,
        sample_user,
        sample_role,
        sample_agency
    ):
        """Test revoking role from user."""
        service = PermissionService(db_session)
        
        # Assign role
        await service.assign_role(
            user_id=sample_user.id,
            role_id=sample_role.id,
            agency_id=sample_agency.id,
            granted_by=sample_user.id
        )
        
        # Verify has role
        has_role = await service.has_role(
            sample_user.id,
            sample_agency.id,
            "test_agent"
        )
        assert has_role is True
        
        # Revoke role
        revoked = await service.revoke_role(
            sample_user.id,
            sample_role.id,
            sample_agency.id
        )
        assert revoked is True
        
        # Verify no longer has role
        has_role = await service.has_role(
            sample_user.id,
            sample_agency.id,
            "test_agent"
        )
        assert has_role is False
    
    @pytest.mark.asyncio
    async def test_expired_role_not_active(
        self,
        db_session,
        sample_user,
        sample_role,
        sample_agency
    ):
        """Test that expired roles are not considered active."""
        service = PermissionService(db_session)
        
        # Assign role with expiration in the past
        expired_time = datetime.now(timezone.utc) - timedelta(days=1)
        await service.assign_role(
            user_id=sample_user.id,
            role_id=sample_role.id,
            agency_id=sample_agency.id,
            granted_by=sample_user.id,
            expires_at=expired_time
        )
        
        # Should not have role (expired)
        has_role = await service.has_role(
            sample_user.id,
            sample_agency.id,
            "test_agent"
        )
        assert has_role is False
        
        # Should not have permissions
        permissions = await service.get_user_permissions(
            sample_user.id,
            sample_agency.id
        )
        assert len(permissions) == 0
    
    @pytest.mark.asyncio
    async def test_set_role_permissions(
        self,
        db_session,
        sample_role,
        sample_permissions
    ):
        """Test setting role permissions (replaces existing)."""
        service = PermissionService(db_session)
        
        # Initially has 3 permissions
        perms = await service.get_role_permissions(sample_role.id)
        assert len(perms) == 3
        
        # Set to just one permission
        contacts_view_id = sample_permissions["contacts.view"].id
        await service.set_role_permissions(
            sample_role.id,
            [contacts_view_id]
        )
        
        # Now has only 1 permission
        perms = await service.get_role_permissions(sample_role.id)
        assert len(perms) == 1
        assert perms[0].name == "contacts.view"
    
    @pytest.mark.asyncio
    async def test_get_user_roles(
        self,
        db_session,
        sample_user,
        sample_role,
        sample_agency
    ):
        """Test getting user's roles."""
        service = PermissionService(db_session)
        
        # Initially no roles
        roles = await service.get_user_roles(
            sample_user.id,
            sample_agency.id
        )
        assert len(roles) == 0
        
        # Assign role
        await service.assign_role(
            user_id=sample_user.id,
            role_id=sample_role.id,
            agency_id=sample_agency.id,
            granted_by=sample_user.id
        )
        
        # Now has 1 role
        roles = await service.get_user_roles(
            sample_user.id,
            sample_agency.id
        )
        assert len(roles) == 1
        assert roles[0].name == "test_agent"
    
    @pytest.mark.asyncio
    async def test_cannot_modify_system_role(self, db_session):
        """Test that system roles cannot be modified."""
        service = PermissionService(db_session)
        
        # Create system role
        role = await service.create_role(
            name="system_role",
            is_system_role=True
        )
        
        # Attempt to update should fail
        with pytest.raises(InvalidInputError):
            await service.update_role(
                role.id,
                name="modified_name"
            )
        
        # Attempt to delete should fail
        with pytest.raises(InvalidInputError):
            await service.delete_role(role.id)
    
    @pytest.mark.asyncio
    async def test_get_users_with_permission(
        self,
        db_session,
        sample_user,
        sample_role,
        sample_agency
    ):
        """Test getting all users with a specific permission."""
        service = PermissionService(db_session)
        
        # Assign role
        await service.assign_role(
            user_id=sample_user.id,
            role_id=sample_role.id,
            agency_id=sample_agency.id,
            granted_by=sample_user.id
        )
        
        # Get users with permission
        users = await service.get_users_with_permission(
            "contacts.view",
            sample_agency.id
        )
        
        assert len(users) >= 1
        assert any(u.id == sample_user.id for u in users)
    
    @pytest.mark.asyncio
    async def test_get_user_agencies(
        self,
        db_session,
        sample_user,
        sample_role,
        sample_agency
    ):
        """Test getting all agencies where user has roles."""
        service = PermissionService(db_session)
        
        # Assign role
        await service.assign_role(
            user_id=sample_user.id,
            role_id=sample_role.id,
            agency_id=sample_agency.id,
            granted_by=sample_user.id
        )
        
        # Get agencies
        agencies = await service.get_user_agencies(sample_user.id)
        
        assert len(agencies) >= 1
        assert any(a.id == sample_agency.id for a in agencies)

