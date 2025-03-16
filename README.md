# Python Shell Simulator

## Overview
The Python Shell Simulator is a comprehensive terminal shell simulator that emulates core functionality found in Unix/Linux and Windows environments. It supports a wide range of commands including file operations, directory management, process management, and advanced OS concept simulations. The simulator is designed to be cross-platform, functioning seamlessly on both Windows and Linux systems.

## Features

### Basic Shell Functionality
- Execute basic shell commands (`cd`, `pwd`, `ls`, `cat`, `mkdir`, etc.)
- Command history tracking with the `history` command
- Cross-platform compatibility (Windows and Linux)
- Error handling for command execution

### Advanced Shell Features
- **Command Piping**: Chain commands using the pipe operator (`|`), e.g., `ls | grep txt` or `cat file | grep error | sort`
- **User Authentication**: Multi-user system with login/logout functionality
- **Permission Levels**: Support for different user types (admin, standard, user)
- **File Permissions**: Implement `chmod` to control read, write, and execute permissions
- **File Access Control**: File access restricted based on user permissions

### Operating System Concept Simulations
- **Process Scheduling**: 
  - Round Robin scheduling simulation (`roundrobin [num_processes] [time_quantum]`)
  - Priority-based scheduling simulation (`priority [num_processes]`)
- **Memory Management**: 
  - Paging system simulation with FIFO and LRU page replacement algorithms (`paging [algo] [processes] [frames]`)
- **Process Synchronization**: 
  - Dining Philosophers problem simulation (`philosophers [num_philosophers] [time]`)
  - Demonstrates deadlock prevention and mutual exclusion

## Installation
To set up the Python Shell Simulator, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   ```

2. Navigate to the project directory:
   ```
   cd python-shell-simulator
   ```


## Usage
To run the shell simulator, execute the following command in your terminal:
```
python src/main.py
```

### Basic Commands
- `pwd`: Print the current working directory
- `ls`: List files in the current directory
- `cd <directory>`: Change the current directory
- `mkdir <directory>`: Create a new directory
- `touch <file>`: Create a new file
- `cat <file>`: Display the contents of a file
- `rm <file>`: Remove a file
- `rmdir <directory>`: Remove an empty directory
- `clear`: Clear the terminal screen
- `history`: Show command history
- `exit`: Exit the shell simulator

### User Management Commands
- `useradd <username> [level]`: Add a new user (levels: admin, standard, user)
- `userdel <username>`: Delete a user
- `passwd [username]`: Change a user's password
- `whoami`: Display current user information
- `users`: List all users (admin only)
- `logout`: Log out current user
- `chmod <permissions> <file>`: Change file permissions (e.g., `chmod rw file.txt`)

### Pipe Commands
Combine commands using the pipe operator:
```
ls | grep .txt      # List only .txt files
cat file.log | grep <text>   # Show sorted error lines from a log file
```

### Simulation Commands
- `roundrobin [processes] [quantum]`: Simulate Round Robin CPU scheduling
- `priority [processes]`: Simulate Priority-based CPU scheduling
- `paging [algorithm] [processes] [frames]`: Simulate memory management with paging
  - Algorithms: FIFO (default), LRU
- `philosophers [num] [time]`: Simulate the Dining Philosophers synchronization problem


## Contributing
Contributions are welcome! 😊

