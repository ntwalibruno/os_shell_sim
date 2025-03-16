"""
Directory-related commands implementation
"""
import os
import sys
from pathlib import Path
from utils.error_handler import handle_error

def change_directory(current_dir, args):
    """
    Change the current working directory
    
    Args:
        current_dir: Current working directory
        args: Command arguments, should contain the target directory
        
    Returns:
        str: New current working directory
    """
    try:
        # If no path provided, go to home directory
        if not args:
            new_dir = str(Path.home())
        else:
            path = args[0]
            
            # Handle home directory shortcut
            if path.startswith('~'):
                path = str(Path.home()) + path[1:]
                
            # Handle absolute paths
            if os.path.isabs(path):
                new_dir = path
            else:
                # Handle relative paths
                new_dir = os.path.join(current_dir, path)
                
        # Normalize the path to handle '..' and '.'
        new_dir = os.path.normpath(new_dir)
        
        # Check if directory exists and is accessible
        if not os.path.exists(new_dir):
            print(f"Error: Directory '{new_dir}' does not exist")
            return current_dir
            
        if not os.path.isdir(new_dir):
            print(f"Error: '{new_dir}' is not a directory")
            return current_dir
            
        # Actually change the process's working directory
        os.chdir(new_dir)
        return new_dir
        
    except PermissionError:
        print(f"Error: Permission denied for directory '{new_dir}'")
        return current_dir
    except Exception as e:
        handle_error(e)
        return current_dir

def print_working_directory(current_dir):
    """
    Print the current working directory
    
    Args:
        current_dir: Current working directory
    """
    print(current_dir)

def list_directory(current_dir, args):
    """
    List contents of a directory
    
    Args:
        current_dir: Current working directory
        args: Command arguments
    """
    try:
        # Determine which directory to list
        target_dir = current_dir
        if args:
            path = args[0]
            if os.path.isabs(path):
                target_dir = path
            else:
                target_dir = os.path.join(current_dir, path)
        
        # Get directory contents
        entries = os.listdir(target_dir)
        
        # Format and display contents
        for entry in sorted(entries):
            full_path = os.path.join(target_dir, entry)
            if os.path.isdir(full_path):
                # Display directories with a trailing slash
                print(f"\033[1;34m{entry}/\033[0m" if os.name != 'nt' else f"{entry}/")
            else:
                # Display files normally
                print(entry)
    except FileNotFoundError:
        print(f"Error: Directory not found: {target_dir}")
    except PermissionError:
        print(f"Error: Permission denied for directory: {target_dir}")
    except Exception as e:
        handle_error(e)

def make_directory(current_dir, args):
    """
    Create a new directory
    
    Args:
        current_dir: Current working directory
        args: Command arguments
    """
    if not args:
        print("Error: mkdir requires a directory name")
        return
    
    try:
        path = args[0]
        
        # Handle absolute vs relative paths
        if os.path.isabs(path):
            new_dir = path
        else:
            new_dir = os.path.join(current_dir, path)
            
        os.makedirs(new_dir, exist_ok=False)
        print(f"Directory created: {new_dir}")
    except FileExistsError:
        print(f"Error: Directory already exists: {path}")
    except PermissionError:
        print(f"Error: Permission denied")
    except Exception as e:
        handle_error(e)

def remove_directory(current_dir, args):
    """
    Remove an empty directory
    
    Args:
        current_dir: Current working directory
        args: Command arguments
    """
    if not args:
        print("Error: rmdir requires a directory name")
        return
    
    try:
        path = args[0]
        
        # Handle absolute vs relative paths
        if os.path.isabs(path):
            target_dir = path
        else:
            target_dir = os.path.join(current_dir, path)
            
        os.rmdir(target_dir)
        print(f"Directory removed: {target_dir}")
    except FileNotFoundError:
        print(f"Error: Directory not found: {path}")
    except OSError as e:
        if "directory is not empty" in str(e).lower():
            print(f"Error: Directory is not empty: {path}")
        else:
            handle_error(e)
    except Exception as e:
        handle_error(e)