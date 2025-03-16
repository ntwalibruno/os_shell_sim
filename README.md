# Python Shell Simulator

## Overview
The Python Shell Simulator is a terminal shell simulator that allows users to execute basic commands similar to those found in Unix/Linux and Windows environments. The simulator supports commands such as `cd`, `pwd`, `exit`, `echo`, `clear`, `ls`, `cat`, `mkdir`, `rmdir`, `rm`, `touch`, and `kill`. It is designed to be cross-platform, functioning seamlessly on both Windows and Linux systems.

## Features
- Execute basic shell commands.
- Cross-platform compatibility (Windows and Linux).
- Error handling for command execution.
- Modular design with separate files for command handling.
- Unit tests to ensure functionality and reliability.

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

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To run the shell simulator, execute the following command in your terminal:
```
python src/main.py
```

Once the shell is running, you can enter commands directly. Here are some examples of commands you can use:

- `pwd`: Print the current working directory.
- `ls`: List files in the current directory.
- `cd <directory>`: Change the current directory.
- `mkdir <directory>`: Create a new directory.
- `touch <file>`: Create a new file.
- `cat <file>`: Display the contents of a file.
- `rm <file>`: Remove a file.
- `rmdir <directory>`: Remove an empty directory.
- `clear`: Clear the terminal screen.
- `kill <pid>`: Terminate a process by its process ID.
- `exit`: Exit the shell simulator.

## Testing
To run the unit tests for the shell simulator, use the following command:
```
pytest tests/
```

## Contributing
Contributions are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.