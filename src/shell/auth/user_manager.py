"""
User authentication and management system
"""
import os
import json
import hashlib
import getpass
from enum import Enum
from typing import Dict, List, Optional

class PermissionLevel(Enum):
    """User permission levels"""
    USER = 1
    STANDARD = 2
    ADMIN = 3
    
    def __str__(self):
        return self.name

class User:
    """User account information"""
    def __init__(self, username: str, password_hash: str, permission_level: PermissionLevel):
        self.username = username
        self.password_hash = password_hash
        self.permission_level = permission_level
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Create a secure hash of the password"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary for serialization"""
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "permission_level": self.permission_level.name
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create user from dictionary"""
        return cls(
            username=data["username"],
            password_hash=data["password_hash"],
            permission_level=PermissionLevel[data["permission_level"]]
        )


class UserManager:
    """Manages users and authentication"""
    def __init__(self, users_file: str = None):
        self.users: Dict[str, User] = {}
        self.current_user: Optional[User] = None
        
        if users_file is None:
            # Default location for users file
            self.users_file = os.path.join(os.path.dirname(__file__), "users.json")
        else:
            self.users_file = users_file
        
        self.load_users()
        
        # If no users exist, create default admin
        if not self.users:
            self.create_default_admin()
    
    def create_default_admin(self):
        """Create default admin account"""
        admin_user = User(
            username="admin",
            password_hash=User.hash_password("admin"),
            permission_level=PermissionLevel.ADMIN
        )
        self.users["admin"] = admin_user
        self.save_users()
        print("Created default admin account (username: admin, password: admin)")
    
    def load_users(self):
        """Load users from file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    users_data = json.load(f)
                    for user_data in users_data:
                        user = User.from_dict(user_data)
                        self.users[user.username] = user
            except Exception as e:
                print(f"Error loading users: {e}")
                print("Creating new users file...")
        
    def save_users(self):
        """Save users to file"""
        try:
            users_data = [user.to_dict() for user in self.users.values()]
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
            
            with open(self.users_file, 'w') as f:
                json.dump(users_data, f, indent=4)
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate a user with username and password"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        password_hash = User.hash_password(password)
        
        if user.password_hash == password_hash:
            self.current_user = user
            return True
        
        return False
    
    def login(self) -> bool:
        """Interactive login prompt"""
        attempts = 0
        max_attempts = 3
        
        while attempts < max_attempts:
            print("\n=== Shell Simulator Login ===")
            username = input("Username: ")
            password = getpass.getpass("Password: ")
            
            if self.authenticate(username, password):
                print(f"\nWelcome, {username}!")
                return True
            
            print("Invalid username or password.")
            attempts += 1
            remaining = max_attempts - attempts
            if remaining > 0:
                print(f"{remaining} attempt(s) remaining.")
        
        print("Too many failed attempts. Exiting.")
        return False
    
    def logout(self):
        """Log out the current user"""
        self.current_user = None
    
    def add_user(self, username: str, password: str, permission_level: PermissionLevel) -> bool:
        """Add a new user (requires admin)"""
        if username in self.users:
            print(f"User {username} already exists")
            return False
        
        user = User(
            username=username,
            password_hash=User.hash_password(password),
            permission_level=permission_level
        )
        
        self.users[username] = user
        self.save_users()
        return True
    
    def remove_user(self, username: str) -> bool:
        """Remove a user (requires admin)"""
        if username not in self.users:
            return False
        
        del self.users[username]
        self.save_users()
        return True
    
    def change_password(self, username: str, new_password: str) -> bool:
        """Change a user's password"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        user.password_hash = User.hash_password(new_password)
        self.save_users()
        return True
    
    def get_users_list(self) -> List[Dict]:
        """Get list of users (without password hashes)"""
        return [
            {"username": u.username, "permission_level": str(u.permission_level)}
            for u in self.users.values()
        ]