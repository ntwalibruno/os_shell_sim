"""
File permissions system
"""
import os
import json
import stat
from typing import Dict, Set, Optional, Tuple
from enum import Flag, auto
from ..auth.user_manager import User, PermissionLevel

class FilePermission(Flag):
    """File permission flags"""
    NONE = 0
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()
    ALL = READ | WRITE | EXECUTE


class FilePermissionManager:
    """Manages file permissions for users"""
    def __init__(self, permissions_file: str = None):
        if permissions_file is None:
            self.permissions_file = os.path.expanduser("~/.shell_simulator_permissions.json")
        else:
            self.permissions_file = permissions_file
        
        # Structure: {filepath: {username: permissions_int}}
        self.file_permissions: Dict[str, Dict[str, int]] = {}
        
        # Default permissions by user level
        self.default_permissions = {
            PermissionLevel.ADMIN: FilePermission.ALL,
            PermissionLevel.STANDARD: FilePermission.READ | FilePermission.EXECUTE,
            PermissionLevel.USER: FilePermission.READ
        }
        
        self.load_permissions()
    
    def load_permissions(self):
        """Load permissions from file"""
        if os.path.exists(self.permissions_file):
            try:
                with open(self.permissions_file, 'r') as f:
                    self.file_permissions = json.load(f)
            except Exception as e:
                print(f"Error loading file permissions: {e}")
                print("Creating new permissions file...")
    
    def save_permissions(self):
        """Save permissions to file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.permissions_file), exist_ok=True)
            
            with open(self.permissions_file, 'w') as f:
                json.dump(self.file_permissions, f, indent=4)
        except Exception as e:
            print(f"Error saving file permissions: {e}")
    
    def get_permissions(self, filepath: str, user: User) -> FilePermission:
        """Get a user's permissions for a file"""
        # Admins always have full permissions
        if user.permission_level == PermissionLevel.ADMIN:
            return FilePermission.ALL
        
        # Look up specific permissions for this file
        if filepath in self.file_permissions and user.username in self.file_permissions[filepath]:
            return FilePermission(self.file_permissions[filepath][user.username])
        
        # Use default permissions based on user level
        return self.default_permissions[user.permission_level]
    
    def check_permission(self, filepath: str, user: User, required_permission: FilePermission) -> bool:
        """Check if user has required permission for a file"""
        permissions = self.get_permissions(filepath, user)
        return required_permission in permissions
    
    def set_permissions(self, filepath: str, username: str, permissions: FilePermission) -> bool:
        """Set permissions for a specific file and user"""
        if filepath not in self.file_permissions:
            self.file_permissions[filepath] = {}
        
        self.file_permissions[filepath][username] = permissions.value
        self.save_permissions()
        return True
    
    def remove_permissions(self, filepath: str) -> bool:
        """Remove permissions for a file"""
        if filepath in self.file_permissions:
            del self.file_permissions[filepath]
            self.save_permissions()
            return True
        return False


def check_file_permission(filepath: str, user: User, permission_manager: FilePermissionManager, 
                         required_permission: FilePermission) -> Tuple[bool, str]:
    """
    Check if a user has the required permission for a file operation
    
    Args:
        filepath: Path to the file
        user: Current user
        permission_manager: File permission manager instance
        required_permission: Permission needed for the operation
        
    Returns:
        Tuple of (has_permission, error_message)
    """
    if not permission_manager.check_permission(filepath, user, required_permission):
        op_name = "read" if required_permission == FilePermission.READ else \
                 "write" if required_permission == FilePermission.WRITE else \
                 "execute" if required_permission == FilePermission.EXECUTE else "access"
        return False, f"Permission denied: You don't have {op_name} permission for {filepath}"
    
    return True, ""