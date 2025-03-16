"""
Command parsing functionality
"""
from typing import List, Tuple

class CommandParser:
    def parse(self, input_string):
        """
        Parse input string into command and arguments
        
        Args:
            input_string: User input string
            
        Returns:
            tuple: (command, list_of_args)
        """
        parts = input_string.strip().split()
        if not parts:
            return "", []
        
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        return command, args
    
    def parse_pipeline(self, input_string) -> List[Tuple[str, List[str]]]:
        """
        Parse input string into a pipeline of commands
        
        Args:
            input_string: User input string (may contain pipes)
            
        Returns:
            List of (command, args) tuples representing the pipeline
        """
        # Split the input by pipe symbol
        pipeline_parts = input_string.split('|')
        pipeline = []
        
        for part in pipeline_parts:
            part = part.strip()
            if not part:
                continue
                
            command, args = self.parse(part)
            pipeline.append((command, args))
        
        return pipeline

    def validate_command(self, command):
        """Validates the command against a list of allowed commands."""
        allowed_commands = [
            'cd', 'pwd', 'exit', 'echo', 'clear', 
            'ls', 'cat', 'mkdir', 'rmdir', 'rm', 
            'touch', 'kill', 'sleep', 'jobs', 'bg',
            'fg', 'roundrobin', 'priority', 'paging',
            'philosophers', 'history', 'grep', 'sort',
            'wc', 'head', 'tail', 'useradd', 'userdel', 
            'passwd', 'chmod', 'whoami', 'logout', 'users',
            'help'# Added user management commands
        ]
        if command in allowed_commands:
            return True
        return False