"""
System-related commands implementation
"""
import os
import sys
import signal
import time
import subprocess
import threading
from collections import namedtuple
from utils.error_handler import handle_error

# Global job management
Job = namedtuple('Job', ['id', 'pid', 'command', 'process', 'status'])
_jobs = {}
_job_counter = 0

def echo(args):
    """
    Display a line of text
    
    Args:
        args: Command arguments
    """
    print(" ".join(args))

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def kill_process(args):
    """
    Kill a process by PID
    
    Args:
        args: Command arguments
    """
    if not args:
        print("Error: kill requires a PID")
        return
    
    try:
        pid = int(args[0])
        
        if os.name == 'nt':
            # On Windows, we use taskkill
            os.system(f"taskkill /F /PID {pid}")
        else:
            # On Unix-like systems, we can use the signal module
            os.kill(pid, signal.SIGKILL)
        print(f"Process {pid} terminated")
    except ValueError:
        print(f"Error: Invalid PID: {args[0]}")
    except ProcessLookupError:
        print(f"Error: No process with PID {pid}")
    except PermissionError:
        print(f"Error: Permission denied to kill process {pid}")
    except Exception as e:
        handle_error(e)

def pwd_command():
    """Returns the current working directory."""
    return os.getcwd()

def exit_command():
    """Exits the shell."""
    raise SystemExit("Exiting the shell.")

def ls_command():
    """Lists files in the current directory."""
    return os.listdir('.')

def mkdir_command(directory):
    """Creates a new directory."""
    try:
        os.makedirs(directory)
        return f"Directory '{directory}' created."
    except FileExistsError:
        return f"Error: Directory '{directory}' already exists."
    except Exception as e:
        return f"Error: {str(e)}"

def rmdir_command(directory):
    """Removes a directory."""
    try:
        os.rmdir(directory)
        return f"Directory '{directory}' removed."
    except FileNotFoundError:
        return f"Error: Directory '{directory}' not found."
    except OSError:
        return f"Error: Directory '{directory}' is not empty."
    except Exception as e:
        return f"Error: {str(e)}"


def run_in_background(command, args):
    """
    Run a command in the background
    
    Args:
        command: The command to run
        args: Arguments for the command
    
    Returns:
        Job ID of the background process
    """
    global _job_counter, _jobs
    
    # Create the full command
    cmd = [command] + args
    cmd_str = ' '.join(cmd)
    
    try:
        # Start the process in the background
        if os.name == 'nt':
            # Windows doesn't have good POSIX job control
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            # Unix-like systems
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setpgrp
            )
        
        # Increment job counter and add to jobs list
        _job_counter += 1
        job_id = _job_counter
        _jobs[job_id] = Job(
            id=job_id,
            pid=process.pid,
            command=cmd_str,
            process=process,
            status="running"
        )
        
        # Start a thread to monitor process completion
        def monitor_job():
            process.wait()
            if job_id in _jobs:
                _jobs[job_id] = _jobs[job_id]._replace(status="completed")
        
        monitor_thread = threading.Thread(target=monitor_job)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return f"[{job_id}] {process.pid}"
    
    except Exception as e:
        handle_error(e)
        return f"Error starting background job: {str(e)}"

def sleep_command(args):
    """
    Sleep for specified seconds
    
    Args:
        args: Command arguments [seconds, &]
    
    Returns:
        Output message
    """
    if not args:
        return "Error: sleep requires seconds argument"
    
    try:
        seconds = float(args[0])
        
        # Check if we need to run in background
        if len(args) > 1 and args[-1] == '&':
            return run_in_background('sleep', [str(seconds)])
        
        # Foreground sleep
        time.sleep(seconds)
        return f"Slept for {seconds} seconds"
    
    except ValueError:
        return f"Error: Invalid time value: {args[0]}"
    except Exception as e:
        handle_error(e)
        return f"Error in sleep command: {str(e)}"

def jobs_command(_=None):
    """
    List all background jobs
    
    Returns:
        List of all background jobs
    """
    if not _jobs:
        return "No jobs running"
    
    result = []
    for job_id, job in _jobs.items():
        # Check if process is still running
        if job.process.poll() is not None and job.status == "running":
            _jobs[job_id] = job._replace(status="completed")
        
        result.append(f"[{job.id}] {job.status} {job.pid} {job.command}")

    return "\n".join(result)

def bg_command(args):
    """
    Resume a stopped background job
    
    Args:
        args: Command arguments [job_id]
    
    Returns:
        Output message
    """
    if not args:
        return "Error: bg requires a job ID"
    
    try:
        job_id = int(args[0].strip("[]"))
        if job_id not in _jobs:
            return f"Error: No such job {job_id}"
        
        job = _jobs[job_id]
        if job.status != "stopped":
            return f"Job {job_id} is already running"
        
        # Continue the process
        if os.name == 'nt':
            # Windows has limited job control
            return f"Error: bg not fully supported on Windows"
        else:
            os.killpg(os.getpgid(job.pid), signal.SIGCONT)
            _jobs[job_id] = job._replace(status="running")
            return f"[{job_id}] {job.command} &"
    
    except ValueError:
        return f"Error: Invalid job ID: {args[0]}"
    except Exception as e:
        handle_error(e)
        return f"Error in bg command: {str(e)}"

def fg_command(args):
    """
    Bring a background job to the foreground
    
    Args:
        args: Command arguments [job_id]
    
    Returns:
        Output message
    """
    if not args:
        return "Error: fg requires a job ID"
    
    try:
        job_id = int(args[0].strip("[]"))
        if job_id not in _jobs:
            return f"Error: No such job {job_id}"
        
        job = _jobs[job_id]
        
        # Continue the process if stopped
        if job.status == "stopped" and os.name != 'nt':
            os.killpg(os.getpgid(job.pid), signal.SIGCONT)
        
        # Wait for the process
        print(f"{job.command}")
        
        # Check if process is still running
        if job.process.poll() is None:
            try:
                job.process.wait()
            except KeyboardInterrupt:
                # Handle Ctrl+Z to stop the job
                if os.name != 'nt':
                    os.killpg(os.getpgid(job.pid), signal.SIGTSTP)
                    _jobs[job_id] = job._replace(status="stopped")
                    return f"\n[{job_id}] Stopped {job.command}"
        
        # If we get here, the process completed
        output, error = job.process.communicate()
        if job.process.returncode == 0:
            del _jobs[job_id]
            return f"{output.decode('utf-8').strip()}"
        else:
            _jobs[job_id] = job._replace(status="completed")
            return f"Job exited with status {job.process.returncode}\n{error.decode('utf-8').strip()}"
    
    except ValueError:
        return f"Error: Invalid job ID: {args[0]}"
    except Exception as e:
        handle_error(e)
        return f"Error in fg command: {str(e)}"

def execute_with_background(command, args):
    """
    Execute a command, possibly in the background
    
    Args:
        command: The command function to execute
        args: Command arguments
    
    Returns:
        Command output or job ID if running in background
    """
    if args and args[-1] == '&':
        # Run in background
        args.pop()  # Remove the &
        return run_in_background(command.__name__.replace('_command', ''), args)
    else:
        # Run in foreground
        return command(args)