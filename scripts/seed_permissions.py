"""
Seed Permissions Script - Initialize default roles and permissions.

Run this script after database setup to create:
- Default permissions for all resources
- Default roles (super_admin, agency_admin, manager, agent, viewer)
- Role-permission mappings

Usage:
    python scripts/seed_permissions.py
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_async_session_context
from app.services.permission_service import PermissionService
from app.database.models import Permission, Role
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================
# Permission Definitions
# ============================================================

PERMISSIONS = [
    # ========== Contacts/Leads ==========
    {"name": "contacts.view", "resource": "contacts", "action": "view", "description": "View contacts and leads"},
    {"name": "contacts.create", "resource": "contacts", "action": "create", "description": "Create new contacts"},
    {"name": "contacts.edit", "resource": "contacts", "action": "edit", "description": "Edit existing contacts"},
    {"name": "contacts.delete", "resource": "contacts", "action": "delete", "description": "Delete contacts"},
    {"name": "contacts.export", "resource": "contacts", "action": "export", "description": "Export contact data"},
    {"name": "contacts.import", "resource": "contacts", "action": "import", "description": "Import contacts"},
    {"name": "contacts.merge", "resource": "contacts", "action": "merge", "description": "Merge duplicate contacts"},
    
    # ========== Properties ==========
    {"name": "properties.view", "resource": "properties", "action": "view", "description": "View properties"},
    {"name": "properties.create", "resource": "properties", "action": "create", "description": "Create new properties"},
    {"name": "properties.edit", "resource": "properties", "action": "edit", "description": "Edit properties"},
    {"name": "properties.delete", "resource": "properties", "action": "delete", "description": "Delete properties"},
    {"name": "properties.publish", "resource": "properties", "action": "publish", "description": "Publish/unpublish properties"},
    {"name": "properties.import", "resource": "properties", "action": "import", "description": "Import properties from portals"},
    
    # ========== Viewings/Bookings ==========
    {"name": "viewings.view", "resource": "viewings", "action": "view", "description": "View viewing appointments"},
    {"name": "viewings.create", "resource": "viewings", "action": "create", "description": "Create viewing appointments"},
    {"name": "viewings.edit", "resource": "viewings", "action": "edit", "description": "Edit viewings"},
    {"name": "viewings.cancel", "resource": "viewings", "action": "cancel", "description": "Cancel viewings"},
    {"name": "viewings.reschedule", "resource": "viewings", "action": "reschedule", "description": "Reschedule viewings"},
    {"name": "viewings.complete", "resource": "viewings", "action": "complete", "description": "Mark viewings as complete"},
    
    # ========== Deals/Pipeline ==========
    {"name": "deals.view", "resource": "deals", "action": "view", "description": "View deals and pipeline"},
    {"name": "deals.create", "resource": "deals", "action": "create", "description": "Create new deals"},
    {"name": "deals.edit", "resource": "deals", "action": "edit", "description": "Edit deals"},
    {"name": "deals.delete", "resource": "deals", "action": "delete", "description": "Delete deals"},
    {"name": "deals.close", "resource": "deals", "action": "close", "description": "Mark deals as won/lost"},
    {"name": "deals.reassign", "resource": "deals", "action": "reassign", "description": "Reassign deals to other agents"},
    
    # ========== Conversations/Messages ==========
    {"name": "conversations.view", "resource": "conversations", "action": "view", "description": "View conversations"},
    {"name": "conversations.handle", "resource": "conversations", "action": "handle", "description": "Handle and respond to conversations"},
    {"name": "conversations.escalate", "resource": "conversations", "action": "escalate", "description": "Escalate conversations"},
    {"name": "conversations.reassign", "resource": "conversations", "action": "reassign", "description": "Reassign conversations"},
    {"name": "conversations.close", "resource": "conversations", "action": "close", "description": "Close conversations"},
    
    # ========== Analytics/Reporting ==========
    {"name": "analytics.view", "resource": "analytics", "action": "view", "description": "View analytics and reports"},
    {"name": "analytics.export", "resource": "analytics", "action": "export", "description": "Export reports"},
    {"name": "analytics.view_all_agents", "resource": "analytics", "action": "view_all_agents", "description": "View analytics for all agents"},
    
    # ========== Team Management ==========
    {"name": "team.view", "resource": "team", "action": "view", "description": "View team members"},
    {"name": "team.invite", "resource": "team", "action": "invite", "description": "Invite new team members"},
    {"name": "team.remove", "resource": "team", "action": "remove", "description": "Remove team members"},
    {"name": "team.edit_roles", "resource": "team", "action": "edit_roles", "description": "Edit team member roles"},
    
    # ========== Settings ==========
    {"name": "settings.view", "resource": "settings", "action": "view", "description": "View agency settings"},
    {"name": "settings.edit", "resource": "settings", "action": "edit", "description": "Edit agency settings"},
    {"name": "settings.billing", "resource": "settings", "action": "billing", "description": "Manage billing and subscription"},
    {"name": "settings.integrations", "resource": "settings", "action": "integrations", "description": "Manage integrations (WhatsApp, Calendar, etc.)"},
    {"name": "settings.ai_config", "resource": "settings", "action": "ai_config", "description": "Configure AI agent settings"},
    
    # ========== AI Agents ==========
    {"name": "ai_agents.view", "resource": "ai_agents", "action": "view", "description": "View AI agent activity"},
    {"name": "ai_agents.configure", "resource": "ai_agents", "action": "configure", "description": "Configure AI agents"},
    {"name": "ai_agents.enable_disable", "resource": "ai_agents", "action": "enable_disable", "description": "Enable/disable AI agents"},
    
    # ========== API Keys ==========
    {"name": "api_keys.view", "resource": "api_keys", "action": "view", "description": "View API keys"},
    {"name": "api_keys.create", "resource": "api_keys", "action": "create", "description": "Create API keys"},
    {"name": "api_keys.revoke", "resource": "api_keys", "action": "revoke", "description": "Revoke API keys"},
    
    # ========== Activity Logs ==========
    {"name": "activity_logs.view", "resource": "activity_logs", "action": "view", "description": "View activity logs"},
    {"name": "activity_logs.export", "resource": "activity_logs", "action": "export", "description": "Export activity logs"},
]


# ============================================================
# Role Definitions with Permissions
# ============================================================

ROLES = {
    "super_admin": {
        "description": "Platform super administrator with full access to all agencies",
        "is_system_role": True,
        "permissions": [
            # Super admin has ALL permissions
            "*"
        ]
    },
    "agency_admin": {
        "description": "Agency administrator with full access to agency resources",
        "is_system_role": True,
        "permissions": [
            # Contacts
            "contacts.view", "contacts.create", "contacts.edit", "contacts.delete",
            "contacts.export", "contacts.import", "contacts.merge",
            
            # Properties
            "properties.view", "properties.create", "properties.edit", "properties.delete",
            "properties.publish", "properties.import",
            
            # Viewings
            "viewings.view", "viewings.create", "viewings.edit", "viewings.cancel",
            "viewings.reschedule", "viewings.complete",
            
            # Deals
            "deals.view", "deals.create", "deals.edit", "deals.delete",
            "deals.close", "deals.reassign",
            
            # Conversations
            "conversations.view", "conversations.handle", "conversations.escalate",
            "conversations.reassign", "conversations.close",
            
            # Analytics
            "analytics.view", "analytics.export", "analytics.view_all_agents",
            
            # Team
            "team.view", "team.invite", "team.remove", "team.edit_roles",
            
            # Settings
            "settings.view", "settings.edit", "settings.billing",
            "settings.integrations", "settings.ai_config",
            
            # AI Agents
            "ai_agents.view", "ai_agents.configure", "ai_agents.enable_disable",
            
            # API Keys
            "api_keys.view", "api_keys.create", "api_keys.revoke",
            
            # Activity Logs
            "activity_logs.view", "activity_logs.export",
        ]
    },
    "manager": {
        "description": "Team manager with access to team operations and analytics",
        "is_system_role": True,
        "permissions": [
            # Contacts
            "contacts.view", "contacts.create", "contacts.edit", "contacts.export",
            "contacts.merge",
            
            # Properties
            "properties.view", "properties.create", "properties.edit", "properties.publish",
            
            # Viewings
            "viewings.view", "viewings.create", "viewings.edit", "viewings.cancel",
            "viewings.reschedule", "viewings.complete",
            
            # Deals
            "deals.view", "deals.create", "deals.edit", "deals.close", "deals.reassign",
            
            # Conversations
            "conversations.view", "conversations.handle", "conversations.escalate",
            "conversations.reassign", "conversations.close",
            
            # Analytics
            "analytics.view", "analytics.export", "analytics.view_all_agents",
            
            # Team
            "team.view",
            
            # Settings
            "settings.view",
            
            # AI Agents
            "ai_agents.view",
            
            # Activity Logs
            "activity_logs.view",
        ]
    },
    "agent": {
        "description": "Sales agent with access to core operations",
        "is_system_role": True,
        "permissions": [
            # Contacts
            "contacts.view", "contacts.create", "contacts.edit",
            
            # Properties
            "properties.view",
            
            # Viewings
            "viewings.view", "viewings.create", "viewings.edit", "viewings.cancel",
            "viewings.reschedule", "viewings.complete",
            
            # Deals
            "deals.view", "deals.create", "deals.edit", "deals.close",
            
            # Conversations
            "conversations.view", "conversations.handle", "conversations.escalate",
            
            # Analytics (own data only)
            "analytics.view",
            
            # Settings
            "settings.view",
            
            # AI Agents
            "ai_agents.view",
        ]
    },
    "viewer": {
        "description": "Read-only access to agency data",
        "is_system_role": True,
        "permissions": [
            # View-only permissions
            "contacts.view",
            "properties.view",
            "viewings.view",
            "deals.view",
            "conversations.view",
            "analytics.view",
            "team.view",
            "settings.view",
        ]
    },
}


# ============================================================
# Seed Functions
# ============================================================

async def seed_permissions(permission_service: PermissionService) -> dict[str, Permission]:
    """
    Seed all permissions.
    
    Returns:
        Dictionary mapping permission name to Permission object
    """
    logger.info(f"Seeding {len(PERMISSIONS)} permissions...")
    
    permission_map = {}
    
    for perm_data in PERMISSIONS:
        try:
            # Check if exists
            existing = await permission_service.get_permission_by_name(perm_data["name"])
            
            if existing:
                logger.debug(f"Permission '{perm_data['name']}' already exists")
                permission_map[perm_data["name"]] = existing
            else:
                # Create new permission
                permission = await permission_service.create_permission(
                    name=perm_data["name"],
                    resource=perm_data["resource"],
                    action=perm_data["action"],
                    description=perm_data.get("description")
                )
                permission_map[perm_data["name"]] = permission
                logger.info(f"Created permission: {perm_data['name']}")
        
        except Exception as e:
            logger.error(f"Error creating permission '{perm_data['name']}': {e}")
    
    logger.info(f"Seeded {len(permission_map)} permissions")
    return permission_map


async def seed_roles(
    permission_service: PermissionService,
    permission_map: dict[str, Permission]
) -> dict[str, Role]:
    """
    Seed all roles with their permissions.
    
    Args:
        permission_service: PermissionService instance
        permission_map: Dictionary of permission name to Permission object
        
    Returns:
        Dictionary mapping role name to Role object
    """
    logger.info(f"Seeding {len(ROLES)} roles...")
    
    role_map = {}
    
    for role_name, role_data in ROLES.items():
        try:
            # Check if exists
            existing = await permission_service.get_role_by_name(role_name)
            
            if existing:
                logger.debug(f"Role '{role_name}' already exists")
                role = existing
            else:
                # Create new role (without permissions for now)
                role = await permission_service.create_role(
                    name=role_name,
                    description=role_data["description"],
                    is_system_role=role_data["is_system_role"],
                    permission_ids=[]  # Add permissions separately
                )
                logger.info(f"Created role: {role_name}")
            
            role_map[role_name] = role
            
            # Assign permissions
            permissions_to_assign = role_data["permissions"]
            
            # Handle super_admin special case (all permissions)
            if "*" in permissions_to_assign:
                permissions_to_assign = list(permission_map.keys())
            
            # Assign each permission
            assigned_count = 0
            for perm_name in permissions_to_assign:
                permission = permission_map.get(perm_name)
                
                if permission:
                    try:
                        await permission_service.assign_permission_to_role(
                            role.id,
                            permission.id
                        )
                        assigned_count += 1
                    except Exception as e:
                        logger.debug(f"Permission '{perm_name}' already assigned to '{role_name}'")
                else:
                    logger.warning(f"Permission '{perm_name}' not found for role '{role_name}'")
            
            logger.info(f"Assigned {assigned_count} permissions to role '{role_name}'")
        
        except Exception as e:
            logger.error(f"Error creating role '{role_name}': {e}")
    
    logger.info(f"Seeded {len(role_map)} roles")
    return role_map


async def verify_seeding(permission_service: PermissionService):
    """Verify that seeding was successful."""
    logger.info("Verifying seeding...")
    
    # Check permissions
    all_permissions = await permission_service.get_all_permissions()
    logger.info(f"✓ Total permissions in database: {len(all_permissions)}")
    
    # Check roles
    all_roles = await permission_service.get_all_roles()
    logger.info(f"✓ Total roles in database: {len(all_roles)}")
    
    # Check role-permission mappings
    for role in all_roles:
        role_permissions = await permission_service.get_role_permissions(role.id)
        logger.info(f"✓ Role '{role.name}': {len(role_permissions)} permissions")


async def main():
    """Main seeding function."""
    logger.info("=" * 60)
    logger.info("RBAC Seeding Script")
    logger.info("=" * 60)
    
    async with get_async_session_context() as db:
        permission_service = PermissionService(db)
        
        try:
            # Seed permissions
            permission_map = await seed_permissions(permission_service)
            
            # Seed roles
            role_map = await seed_roles(permission_service, permission_map)
            
            # Verify
            await verify_seeding(permission_service)
            
            logger.info("=" * 60)
            logger.info("✓ Seeding completed successfully!")
            logger.info("=" * 60)
            
            # Print summary
            logger.info("\nDefault Roles Created:")
            for role_name in ROLES.keys():
                logger.info(f"  - {role_name}")
            
            logger.info("\nNext Steps:")
            logger.info("  1. Assign roles to users using the API or admin panel")
            logger.info("  2. Test permission checks in your endpoints")
            logger.info("  3. Create custom roles if needed")
        
        except Exception as e:
            logger.error(f"❌ Seeding failed: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    asyncio.run(main())

