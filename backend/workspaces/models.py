from django.db import models
from django.conf import settings


class Workspace(models.Model):
    """
    Workspace model representing a team or organization space.
    Memory-efficient design with strategic indexing.
    """

    # Core fields
    name = models.CharField(
        max_length=100,
        help_text='Workspace name'
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text='URL-friendly workspace identifier'
    )
    description = models.TextField(
        max_length=500,
        blank=True,
        default='',
        help_text='Workspace description'
    )

    # Owner relationship
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_workspaces',
        help_text='Workspace owner'
    )

    # Settings
    logo_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text='URL to workspace logo'
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text='Workspace is active'
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='Workspace creation timestamp'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last update timestamp'
    )

    class Meta:
        db_table = 'workspaces'
        verbose_name = 'Workspace'
        verbose_name_plural = 'Workspaces'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['owner', 'is_active']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name


class WorkspaceMember(models.Model):
    """
    Workspace membership with bitmap RBAC/ABAC permissions.
    Uses 8 bytes (64 bits) for all workspace-level permissions.

    Bitmap Permission Positions (0-63):
    0-15: Basic workspace permissions
    16-31: Project management permissions
    32-47: Issue management permissions
    48-63: Advanced/admin permissions
    """

    # Role choices (for display purposes)
    OWNER = 'owner'
    ADMIN = 'admin'
    MEMBER = 'member'
    GUEST = 'guest'

    ROLE_CHOICES = [
        (OWNER, 'Owner'),
        (ADMIN, 'Admin'),
        (MEMBER, 'Member'),
        (GUEST, 'Guest'),
    ]

    # Relationships
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='members',
        help_text='Associated workspace'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workspace_memberships',
        help_text='Member user'
    )

    # Role and permissions
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=MEMBER,
        help_text='Member role (display only)'
    )

    # Bitmap permissions (64 bits = 8 bytes)
    # This single field replaces hundreds of permission rows!
    permissions = models.BigIntegerField(
        default=0,
        help_text='Bitmap for workspace permissions (64 bits)'
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text='Membership is active'
    )

    # Timestamps
    joined_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='Member joined timestamp'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last update timestamp'
    )

    class Meta:
        db_table = 'workspace_members'
        verbose_name = 'Workspace Member'
        verbose_name_plural = 'Workspace Members'
        ordering = ['-joined_at']
        unique_together = [['workspace', 'user']]
        indexes = [
            models.Index(fields=['workspace', 'user']),
            models.Index(fields=['workspace', 'is_active']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['joined_at']),
        ]

    def __str__(self):
        return f"{self.user.email} in {self.workspace.name}"

    def has_permission(self, permission_bit):
        """
        Check if member has a specific permission using bitwise AND.

        Args:
            permission_bit (int): Bit position (0-63) to check

        Returns:
            bool: True if member has the permission

        Example:
            >>> member.has_permission(WorkspacePermissions.CREATE_PROJECT)
            True
        """
        return bool(self.permissions & (1 << permission_bit))

    def grant_permission(self, permission_bit):
        """
        Grant a permission to the member using bitwise OR.

        Args:
            permission_bit (int): Bit position (0-63) to grant
        """
        self.permissions |= (1 << permission_bit)
        self.save(update_fields=['permissions'])

    def revoke_permission(self, permission_bit):
        """
        Revoke a permission from the member using bitwise AND NOT.

        Args:
            permission_bit (int): Bit position (0-63) to revoke
        """
        self.permissions &= ~(1 << permission_bit)
        self.save(update_fields=['permissions'])

    def set_role_permissions(self):
        """
        Set default permissions based on role.
        This demonstrates the power of bitmap permissions!
        """
        if self.role == self.OWNER:
            # Owner has all permissions (all 64 bits set to 1)
            self.permissions = (1 << 64) - 1  # 0xFFFFFFFFFFFFFFFF
        elif self.role == self.ADMIN:
            # Admin has most permissions (bits 0-55)
            self.permissions = (1 << 56) - 1
        elif self.role == self.MEMBER:
            # Member has basic permissions (bits 0-31)
            self.permissions = (1 << 32) - 1
        elif self.role == self.GUEST:
            # Guest has minimal permissions (bits 0-7)
            self.permissions = (1 << 8) - 1
        self.save(update_fields=['permissions'])


class WorkspacePermissions:
    """
    Workspace permission bit definitions.
    Using constants for better code readability and maintenance.

    Memory efficiency: 64 permissions in 8 bytes vs ~6.4KB traditional approach!
    """

    # Basic workspace permissions (0-15)
    VIEW_WORKSPACE = 0
    EDIT_WORKSPACE = 1
    DELETE_WORKSPACE = 2
    MANAGE_MEMBERS = 3
    INVITE_MEMBERS = 4
    REMOVE_MEMBERS = 5
    VIEW_MEMBERS = 6
    MANAGE_SETTINGS = 7

    # Project management (16-31)
    CREATE_PROJECT = 16
    EDIT_PROJECT = 17
    DELETE_PROJECT = 18
    ARCHIVE_PROJECT = 19
    VIEW_PROJECT = 20
    MANAGE_PROJECT_MEMBERS = 21

    # Issue management (32-47)
    CREATE_ISSUE = 32
    EDIT_ISSUE = 33
    DELETE_ISSUE = 34
    ASSIGN_ISSUE = 35
    CHANGE_ISSUE_STATUS = 36
    VIEW_ISSUE = 37
    COMMENT_ISSUE = 38
    EDIT_ISSUE_COMMENTS = 39

    # Messaging (48-55)
    CREATE_CHANNEL = 48
    EDIT_CHANNEL = 49
    DELETE_CHANNEL = 50
    SEND_MESSAGE = 51
    DELETE_MESSAGE = 52
    VIEW_CHANNEL = 53

    # Advanced/Admin permissions (56-63)
    MANAGE_INTEGRATIONS = 56
    VIEW_ANALYTICS = 57
    EXPORT_DATA = 58
    MANAGE_BILLING = 59
    MANAGE_SECURITY = 60
