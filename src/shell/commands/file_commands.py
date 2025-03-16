"""
File-related commands implementation
"""
import os
import sys
from utils.error_handler import handle_error

def touch(current_dir, args):
    """
    Create an empty file or update the timestamp of an existing file
    
    Args:
        current_dir: Current working directory
        args: Command arguments
    """
    if not args:
        print("Error: touch requires a filename")
        return
    
    try:
        filename = args[0]
        
        # Handle absolute vs relative paths
        if os.path.isabs(filename):
            filepath = filename
        else:
            filepath = os.path.join(current_dir, filename)
            
        with open(filepath, 'a'):
            os.utime(filepath, None)  # Update the access/modification time
        
        if not os.path.exists(filepath):
            print(f"File created: {filepath}")
    except PermissionError:
        print(f"Error: Permission denied")
    except Exception as e:
        handle_error(e)

def cat(current_dir, args):
    """
    Display contents of a file
    
    Args:
        current_dir: Current working directory
        args: Command arguments
    """
    if not args:
        print("Error: cat requires a filename")
        return
    
    try:
        filename = args[0]
        
        # Handle absolute vs relative paths
        if os.path.isabs(filename):
            filepath = filename
        else:
            filepath = os.path.join(current_dir, filename)
            
        if not os.path.exists(filepath):
            print(f"Error: File not found: {filename}")
            return
            
        if os.path.isdir(filepath):
            print(f"Error: {filename} is a directory")
            return
            
        with open(filepath, 'r') as f:
            print(f.read())
    except PermissionError:
        print(f"Error: Permission denied")
    except UnicodeDecodeError:
        print(f"Error: Cannot display binary file: {filename}")
    except Exception as e:
        handle_error(e)

def remove_file(current_dir, args):
    """
    Remove a file
    
    Args:
        current_dir: Current working directory
        args: Command arguments
    """
    if not args:
        print("Error: rm requires a filename")
        return
    
    try:
        filename = args[0]
        
        # Handle absolute vs relative paths
        if os.path.isabs(filename):
            filepath = filename
        else:
            filepath = os.path.join(current_dir, filename)
            
        if not os.path.exists(filepath):
            print(f"Error: File not found: {filename}")
            return
            
        if os.path.isdir(filepath):
            print(f"Error: {filename} is a directory, use rmdir instead")
            return
            
        os.remove(filepath)
        print(f"File removed: {filepath}")
    except PermissionError:
        print(f"Error: Permission denied")
    except Exception as e:
        handle_error(e)