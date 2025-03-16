def kill_process(pid):
    import os
    import signal
    try:
        if os.name == 'nt':  # Windows
            os.kill(pid, signal.SIGTERM)
        else:  # Unix/Linux
            os.kill(pid, signal.SIGKILL)
        return f"Process {pid} terminated successfully."
    except ProcessLookupError:
        return f"Error: No such process with PID {pid}."
    except PermissionError:
        return f"Error: Permission denied to kill process {pid}."
    except Exception as e:
        return f"Error: {str(e)}"

def list_processes():
    import psutil
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            processes.append(proc.info)
        return processes
    except Exception as e:
        return f"Error: {str(e)}"