"""
Core Shell implementation
"""
import os
import io
import sys
import getpass
from .command_parser import CommandParser
from .auth.user_manager import UserManager, PermissionLevel
from .permissions.file_permissions import FilePermissionManager, FilePermission, check_file_permission
from utils.error_handler import handle_error

class Shell:
    def __init__(self):
        self.running = True
        self.cwd = os.getcwd()
        self.parser = CommandParser()
        self.cmd_history = []
        self.user_manager = UserManager()
        self.permission_manager = FilePermissionManager()
        
    def start(self):
        """Start the shell with login"""
        print("Welcome to Python Shell Simulator")
        
        # Require login before proceeding
        if not self.user_manager.login():
            print("Login required. Exiting...")
            return
        
        print("\nType 'help' to see available commands")
        self.run()
    
    def run(self):
        """Main shell loop"""
        while self.running:
            try:
                # Display prompt with current directory and username
                username = self.user_manager.current_user.username
                user_prefix = f"\033[1;36m{username}\033[0m@" if os.name != 'nt' else f"{username}@"
                dir_suffix = f"\033[1;32m{os.path.basename(self.cwd)}\033[0m$ " if os.name != 'nt' else f"{os.path.basename(self.cwd)}$ "
                prompt = f"{user_prefix}{dir_suffix}"
                
                user_input = input(prompt)
                
                if not user_input.strip():
                    continue
                
                self.cmd_history.append(user_input)
                
                # Check if the command includes pipes
                if "|" in user_input:
                    # Parse as pipeline
                    pipeline = self.parser.parse_pipeline(user_input)
                    
                    # Validate each command in the pipeline
                    valid_pipeline = True
                    for cmd, _ in pipeline:
                        if not self.parser.validate_command(cmd) and cmd:
                            print(f"Command not found: {cmd}")
                            valid_pipeline = False
                            break
                    
                    if valid_pipeline:
                        self.execute_pipeline(pipeline)
                else:
                    # Regular command execution
                    command, args = self.parser.parse(user_input)
                    
                    # Validate the command
                    if not self.parser.validate_command(command) and command:
                        print(f"Command not found: {command}")
                        continue
                        
                    self.execute_command(command, args)
                
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit the shell")
            except Exception as e:
                handle_error(e)
    
    def execute_pipeline(self, pipeline):
        """Execute a pipeline of commands"""
        if not pipeline:
            return
        
        # Start with no input
        input_data = None
        
        # Process each command in the pipeline
        for i, (command, args) in enumerate(pipeline):
            # If not the last command, capture output
            if i < len(pipeline) - 1:
                # Redirect stdout to capture output
                original_stdout = sys.stdout
                captured_output = io.StringIO()
                sys.stdout = captured_output
                
                # Execute the command
                self.execute_command(command, args, input_data)
                
                # Get the output and restore stdout
                sys.stdout = original_stdout
                input_data = captured_output.getvalue()
                captured_output.close()
            else:
                # Last command, output to terminal
                self.execute_command(command, args, input_data)
    
    def execute_command(self, command, args, input_data=None):
        """Execute the given command with arguments"""
        # User management commands
        if command == "useradd":
            self.cmd_useradd(args)
            return
        elif command == "userdel":
            self.cmd_userdel(args)
            return
        elif command == "passwd":
            self.cmd_passwd(args)
            return
        elif command == "whoami":
            self.cmd_whoami()
            return
        elif command == "logout":
            self.cmd_logout()
            return
        elif command == "users":
            self.cmd_users()
            return
        elif command == "chmod":
            self.cmd_chmod(args)
            return
            
        # Text processing commands for pipelines
        elif command == "grep":
            self.cmd_grep(args, input_data)
            return
        elif command == "sort":
            self.cmd_sort(args, input_data)
            return
            
        # Directory commands
        if command == "cd":
            from .commands.directory_commands import change_directory
            self.cwd = change_directory(self.cwd, args)
        elif command == "pwd":
            from .commands.directory_commands import print_working_directory
            print_working_directory(self.cwd)
        elif command == "ls":
            # Check directory permissions before listing
            target_dir = self.cwd
            if args:
                path = args[0]
                if os.path.isabs(path):
                    target_dir = path
                else:
                    target_dir = os.path.join(self.cwd, path)
            
            has_perm, error = check_file_permission(
                target_dir, 
                self.user_manager.current_user,
                self.permission_manager,
                FilePermission.READ
            )
            
            if not has_perm:
                print(error)
                return
            
            from .commands.directory_commands import list_directory
            list_directory(self.cwd, args)
        elif command == "mkdir":
            # Check parent directory permissions
            if not args:
                print("Error: mkdir requires a directory name")
                return
                
            path = args[0]
            parent_dir = os.path.dirname(os.path.join(self.cwd, path)) or self.cwd
            
            has_perm, error = check_file_permission(
                parent_dir, 
                self.user_manager.current_user,
                self.permission_manager,
                FilePermission.WRITE
            )
            
            if not has_perm:
                print(error)
                return
                
            from .commands.directory_commands import make_directory
            make_directory(self.cwd, args)
        elif command == "rmdir":
            if not args:
                print("Error: rmdir requires a directory name")
                return
                
            path = args[0]
            dir_path = os.path.join(self.cwd, path)
                
            has_perm, error = check_file_permission(
                dir_path, 
                self.user_manager.current_user,
                self.permission_manager,
                FilePermission.WRITE
            )
            
            if not has_perm:
                print(error)
                return
                
            from .commands.directory_commands import remove_directory
            remove_directory(self.cwd, args)
        
        # File commands with permission checks
        elif command == "cat":
            if input_data:
                # If we have input data from a pipe, print it
                print(input_data, end='')
                return
            
            if not args:
                print("Error: cat requires a filename")
                return
                
            filename = args[0]
            filepath = os.path.join(self.cwd, filename)
                
            has_perm, error = check_file_permission(
                filepath,
                self.user_manager.current_user,
                self.permission_manager,
                FilePermission.READ
            )
            
            if not has_perm:
                print(error)
                return
                
            from .commands.file_commands import cat
            cat(self.cwd, args)
        elif command == "touch":
            if not args:
                print("Error: touch requires a filename")
                return
                
            filename = args[0]
            filepath = os.path.join(self.cwd, filename)
            parent_dir = os.path.dirname(filepath) or self.cwd
                
            has_perm, error = check_file_permission(
                parent_dir,
                self.user_manager.current_user,
                self.permission_manager,
                FilePermission.WRITE
            )
            
            if not has_perm:
                print(error)
                return
                
            from .commands.file_commands import touch
            touch(self.cwd, args)
        elif command == "rm":
            if not args:
                print("Error: rm requires a filename")
                return
                
            filename = args[0]
            filepath = os.path.join(self.cwd, filename)
                
            has_perm, error = check_file_permission(
                filepath,
                self.user_manager.current_user,
                self.permission_manager,
                FilePermission.WRITE
            )
            
            if not has_perm:
                print(error)
                return
                
            from .commands.file_commands import remove_file
            remove_file(self.cwd, args)
        
        # System commands
        elif command == "echo":
            if input_data:
                print(input_data, end='')
            else:
                from .commands.system_commands import echo
                echo(args)
        elif command == "clear":
            from .commands.system_commands import clear_screen
            clear_screen()
        elif command == "sleep":
            from .commands.system_commands import sleep_command
            sleep_command(args)
        elif command == "jobs":
            from .commands.system_commands import jobs_command
            jobs = jobs_command()
            print(jobs)
        elif command == "bg":
            from .commands.system_commands import bg_command
            bg_command(args)
        elif command == "fg":
            from .commands.system_commands import fg_command
            fg_command(args)
        elif command == "kill":
            from .commands.system_commands import kill_process
            kill_process(args)
        elif command == "history":
            for i, cmd in enumerate(self.cmd_history):
                print(f"{i+1}: {cmd}")
            
        # Scheduling simulation commands
        elif command == "roundrobin":
            from .commands.scheduler_commands import simulate_round_robin
            result = simulate_round_robin(args)
            print(result)
        elif command == "priority":
            from .commands.scheduler_commands import simulate_priority
            result = simulate_priority(args)
            print(result)
            
        # Memory management simulation command
        elif command == "paging":
            from .commands.memory_commands import simulate_memory_paging
            simulate_memory_paging(args)
            
        # Process synchronization commands
        elif command == "philosophers":
            from .commands.synchronization_commands import simulate_dining_philosophers
            result = simulate_dining_philosophers(args)
            print(result)
            
        elif command == "exit":
            self.running = False
            print("Exiting shell...")
        elif command == "help":
            self.show_help()
        elif command:
            print(f"Command not implemented: {command}")
    
    # User management command implementations
    def cmd_useradd(self, args):
        """Add a new user"""
        current_user = self.user_manager.current_user
        
        if current_user.permission_level != PermissionLevel.ADMIN:
            print("Error: Only administrators can add users")
            return
            
        if len(args) < 2:
            print("Usage: useradd <username> <permission_level>")
            print("Permission levels: USER, STANDARD, ADMIN")
            return
            
        username = args[0]
        try:
            permission_level = PermissionLevel[args[1].upper()]
        except KeyError:
            print(f"Invalid permission level: {args[1]}")
            print("Valid levels are: USER, STANDARD, ADMIN")
            return
            
        password = getpass.getpass(f"Enter password for new user '{username}': ")
        
        if self.user_manager.add_user(username, password, permission_level):
            print(f"User '{username}' added with {permission_level.name} permissions")
        else:
            print(f"Failed to add user '{username}'")
    
    def cmd_userdel(self, args):
        """Delete a user"""
        current_user = self.user_manager.current_user
        
        if current_user.permission_level != PermissionLevel.ADMIN:
            print("Error: Only administrators can delete users")
            return
            
        if not args:
            print("Usage: userdel <username>")
            return
            
        username = args[0]
        
        if username == current_user.username:
            print("Error: Cannot delete your own account")
            return
            
        if self.user_manager.remove_user(username):
            print(f"User '{username}' deleted")
        else:
            print(f"Failed to delete user '{username}'")
    
    def cmd_passwd(self, args):
        """Change password"""
        current_user = self.user_manager.current_user
        
        if args:
            # Changing another user's password requires admin
            if current_user.permission_level != PermissionLevel.ADMIN:
                print("Error: Only administrators can change other users' passwords")
                return
                
            username = args[0]
        else:
            # Changing own password
            username = current_user.username
            
        new_password = getpass.getpass("Enter new password: ")
        confirm = getpass.getpass("Confirm new password: ")
        
        if new_password != confirm:
            print("Passwords do not match")
            return
            
        if self.user_manager.change_password(username, new_password):
            print(f"Password changed for user '{username}'")
        else:
            print(f"Failed to change password for '{username}'")
    
    def cmd_whoami(self):
        """Show current user information"""
        current_user = self.user_manager.current_user
        print(f"Username: {current_user.username}")
        print(f"Permission level: {current_user.permission_level.name}")
    
    def cmd_logout(self):
        """Log out the current user"""
        self.user_manager.logout()
        print("Logged out")
        
        # Prompt for new login
        if not self.user_manager.login():
            self.running = False
            print("Exiting shell...")
    
    def cmd_users(self):
        """List all users"""
        current_user = self.user_manager.current_user
        
        if current_user.permission_level != PermissionLevel.ADMIN:
            print("Error: Only administrators can list all users")
            return
            
        users = self.user_manager.get_users_list()
        print("Users:")
        for user in users:
            print(f"  {user['username']} ({user['permission_level']})")
    
    def cmd_chmod(self, args):
        """Change file permissions"""
        current_user = self.user_manager.current_user
        
        if current_user.permission_level != PermissionLevel.ADMIN:
            print("Error: Only administrators can change file permissions")
            return
            
        if len(args) < 3:
            print("Usage: chmod <username> <r|w|x|rwx> <filepath>")
            return
            
        username = args[0]
        perm_str = args[1].lower()
        filepath = args[2]
        
        # Convert relative path to absolute
        if not os.path.isabs(filepath):
            filepath = os.path.join(self.cwd, filepath)
            
        if not os.path.exists(filepath):
            print(f"Error: File not found: {filepath}")
            return
            
        # Parse permission string
        permissions = FilePermission.NONE
        if 'r' in perm_str:
            permissions |= FilePermission.READ
        if 'w' in perm_str:
            permissions |= FilePermission.WRITE
        if 'x' in perm_str:
            permissions |= FilePermission.EXECUTE
            
        if permissions == FilePermission.NONE:
            print("Error: Invalid permissions. Use r, w, x or combinations")
            return
            
        if self.permission_manager.set_permissions(filepath, username, permissions):
            print(f"Changed permissions for '{username}' on '{filepath}'")
        else:
            print(f"Failed to change permissions")
    
    def show_help(self):
        """Display help information"""
        print("\nAvailable commands:")
        print("\nFile Operations:")
        print("  ls [dir]           - List directory contents")
        print("  cat <file>         - Display file contents")
        print("  touch <file>       - Create an empty file")
        print("  rm <file>          - Remove file")
        
        print("\nDirectory Operations:")
        print("  pwd                - Print working directory")
        print("  cd <dir>           - Change directory")
        print("  mkdir <dir>        - Create directory")
        print("  rmdir <dir>        - Remove directory")
        
        print("\nUser Management:")
        print("  whoami             - Display current user")
        print("  logout             - Log out current user")
        print("  passwd [user]      - Change password")
        print("  useradd <user> <level> - Add new user (admin)")
        print("  userdel <user>     - Remove user (admin)")
        print("  users              - List all users (admin)")
        print("  chmod <user> <perms> <file> - Set file permissions (admin)")
        
        print("\nText Processing:")
        print("  grep <pattern> [file] - Search for pattern")
        print("  sort [file]        - Sort lines of text")
        
        print("\nSystem Commands:")
        print("  echo <text>        - Display text")
        print("  clear              - Clear screen")
        print("  history            - Show command history")
        print("  exit               - Exit shell")
        
        print("\nSimulation Commands:")
        print("  philosophers       - Run Dining Philosophers simulation")
        print("  paging             - Run Memory Paging simulation")
        print("  roundrobin         - Run Round Robin scheduling simulation")
        print("  priority           - Run Priority scheduling simulation")
        
        print("\nPipe Support:")
        print("  command1 | command2 | command3  - Chain commands with pipes")
    
    def cmd_grep(self, args, input_data=None):
        """
        Filter input lines containing pattern
        
        Args:
            args: Command arguments [pattern, filename?]
            input_data: Input from previous command in pipeline
        """
        if not args:
            print("Error: grep requires a pattern")
            return
        
        pattern = args[0]
        
        # If we have input from a pipe
        if input_data:
            lines = input_data.splitlines()
            for line in lines:
                if pattern in line:
                    print(line)
            return
        
        # Otherwise read from a file
        if len(args) < 2:
            print("Error: grep requires a filename when not in a pipeline")
            return
        
        filename = args[1]
        
        # Handle relative paths
        if not os.path.isabs(filename):
            filename = os.path.join(self.cwd, filename)
        
        try:
            with open(filename, 'r') as file:
                for line in file:
                    if pattern in line:
                        print(line.rstrip())
        except FileNotFoundError:
            print(f"Error: File not found: {filename}")
        except PermissionError:
            print(f"Error: Permission denied: {filename}")
        except Exception as e:
            handle_error(e)
    
    def cmd_sort(self, args, input_data=None):
        """
        Sort lines of text
        
        Args:
            args: Command arguments [filename?]
            input_data: Input from previous command in pipeline
        """
        # If we have input from a pipe
        if input_data:
            lines = input_data.splitlines()
            for line in sorted(lines):
                print(line)
            return
        
        # Otherwise read from a file
        if not args:
            print("Error: sort requires a filename when not in a pipeline")
            return
        
        filename = args[0]
        
        # Handle relative paths
        if not os.path.isabs(filename):
            filename = os.path.join(self.cwd, filename)
        
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()
                for line in sorted(lines):
                    print(line.rstrip())
        except FileNotFoundError:
            print(f"Error: File not found: {filename}")
        except PermissionError:
            print(f"Error: Permission denied: {filename}")
        except Exception as e:
            handle_error(e)

