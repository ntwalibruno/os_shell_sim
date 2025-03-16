# settings.py

DEFAULT_PATH = "/home/user"  # Default path for Linux
WINDOWS_DEFAULT_PATH = "C:\\Users\\User"  # Default path for Windows

COMMAND_OPTIONS = {
    "echo": {
        "enabled": True,
        "description": "Displays a line of text."
    },
    "cd": {
        "enabled": True,
        "description": "Changes the current directory."
    },
    "pwd": {
        "enabled": True,
        "description": "Prints the current working directory."
    },
    "exit": {
        "enabled": True,
        "description": "Exits the shell."
    },
    "clear": {
        "enabled": True,
        "description": "Clears the terminal screen."
    },
    "ls": {
        "enabled": True,
        "description": "Lists directory contents."
    },
    "cat": {
        "enabled": True,
        "description": "Concatenates and displays file content."
    },
    "mkdir": {
        "enabled": True,
        "description": "Creates a new directory."
    },
    "rmdir": {
        "enabled": True,
        "description": "Removes an empty directory."
    },
    "rm": {
        "enabled": True,
        "description": "Removes files or directories."
    },
    "touch": {
        "enabled": True,
        "description": "Creates an empty file or updates the timestamp."
    },
    "kill": {
        "enabled": True,
        "description": "Terminates a process."
    }
}