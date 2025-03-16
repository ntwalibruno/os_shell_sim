"""
Utilities package initialization
"""
import sys
import traceback

class ErrorHandler:
    def log_error(self, error_message):
        with open("error_log.txt", "a") as log_file:
            log_file.write(f"ERROR: {error_message}\n")

    def display_error(self, error_message):
        print(f"An error occurred: {error_message}")

def handle_error(error, show_traceback=False):
    """
    Handle errors with appropriate messages
    
    Args:
        error: The exception that was raised
        show_traceback: Whether to show the full traceback
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    if error_msg:
        print(f"Error ({error_type}): {error_msg}")
    else:
        print(f"An error occurred: {error_type}")
    
    if show_traceback:
        traceback.print_exception(type(error), error, error.__traceback__)