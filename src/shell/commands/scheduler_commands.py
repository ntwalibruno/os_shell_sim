"""
Process scheduling simulation commands
"""
import time
import random
from collections import deque
from dataclasses import dataclass
from typing import List

@dataclass
class Process:
    """Process representation for scheduling simulations"""
    id: int
    burst_time: int  # Time required to complete the process (in seconds)
    priority: int = 0  # Lower value means higher priority
    wait_time: int = 0  # Time spent waiting
    turnaround_time: int = 0  # Total time from arrival to completion
    remaining_time: int = None  # Remaining execution time
    
    def __post_init__(self):
        if self.remaining_time is None:
            self.remaining_time = self.burst_time

def simulate_round_robin(args):
    """
    Simulate Round Robin scheduling algorithm
    
    Args:
        args: Command arguments [num_processes=10, time_quantum=1]
        
    Returns:
        Simulation results
    """
    # Parse arguments
    num_processes = 10  # Default
    time_quantum = 1  # Default time quantum in seconds
    
    if args and len(args) >= 1:
        try:
            num_processes = int(args[0])
        except ValueError:
            return f"Error: Invalid number of processes: {args[0]}"
    
    if args and len(args) >= 2:
        try:
            time_quantum = int(args[1])
        except ValueError:
            return f"Error: Invalid time quantum: {args[1]}"
    
    # Create processes with random burst times between 1-5 seconds
    processes = [
        Process(id=i, burst_time=random.randint(1, 5))
        for i in range(1, num_processes + 1)
    ]
    
    total_processes = len(processes)
    print(f"Simulating Round Robin scheduling with {total_processes} processes and time quantum = {time_quantum}s")
    print("\nProcess ID\tBurst Time\tRemaining Time")
    for p in processes:
        print(f"{p.id}\t\t{p.burst_time}s\t\t{p.remaining_time}s")
    print("\nStarting simulation...\n")
    
    # Prepare process queue
    ready_queue = deque(processes)
    completed_processes = []
    current_time = 0
    
    # Run the simulation
    while ready_queue:
        current_process = ready_queue.popleft()
        
        # If this is the final execution for this process
        if current_process.remaining_time <= time_quantum:
            execution_time = current_process.remaining_time
            print(f"Running Process {current_process.id} for {execution_time}s [COMPLETING]")
            
            # Simulate process running
            time.sleep(execution_time)
            
            # Update metrics
            current_time += execution_time
            current_process.remaining_time = 0
            current_process.turnaround_time = current_time
            
            # Add to completed list
            completed_processes.append(current_process)
            
        else:
            # Process needs more time
            execution_time = time_quantum
            print(f"Running Process {current_process.id} for {execution_time}s [remaining: {current_process.remaining_time - execution_time}s]")
            
            # Simulate process running
            time.sleep(execution_time)
            
            # Update metrics
            current_time += execution_time
            current_process.remaining_time -= execution_time
            
            # Add back to queue
            ready_queue.append(current_process)
            
        # Update wait times for all processes in the queue
        for p in ready_queue:
            p.wait_time += execution_time
    
    # Calculate and print metrics
    print("\nSimulation complete!\n")
    print("Process metrics:")
    print("Process ID\tBurst Time\tWait Time\tTurnaround Time")
    
    total_wait_time = 0
    total_turnaround_time = 0
    
    for p in completed_processes:
        print(f"{p.id}\t\t{p.burst_time}s\t\t{p.wait_time}s\t\t{p.turnaround_time}s")
        total_wait_time += p.wait_time
        total_turnaround_time += p.turnaround_time
    
    avg_wait_time = total_wait_time / total_processes
    avg_turnaround_time = total_turnaround_time / total_processes
    
    print(f"\nAverage Wait Time: {avg_wait_time:.2f}s")
    print(f"Average Turnaround Time: {avg_turnaround_time:.2f}s")
    
    return "Round Robin scheduling simulation completed."

def simulate_priority(args):
    """
    Simulate Priority scheduling algorithm
    
    Args:
        args: Command arguments [num_processes=10]
        
    Returns:
        Simulation results
    """
    # Parse arguments
    num_processes = 10  # Default
    
    if args and len(args) >= 1:
        try:
            num_processes = int(args[0])
        except ValueError:
            return f"Error: Invalid number of processes: {args[0]}"
    
    # Create processes with random burst times and priorities
    processes = [
        Process(
            id=i, 
            burst_time=random.randint(1, 5),
            priority=random.randint(1, 10)  # 1 is highest priority, 10 is lowest
        )
        for i in range(1, num_processes + 1)
    ]
    
    total_processes = len(processes)
    print(f"Simulating Priority scheduling with {total_processes} processes")
    print("\nProcess ID\tBurst Time\tPriority (lower is higher)")
    for p in processes:
        print(f"{p.id}\t\t{p.burst_time}s\t\t{p.priority}")
    print("\nStarting simulation...\n")
    
    # Sort processes by priority (lower value = higher priority)
    sorted_processes = sorted(processes, key=lambda p: p.priority)
    
    completed_processes = []
    current_time = 0
    
    # Run the simulation
    for process in sorted_processes:
        print(f"Running Process {process.id} (priority: {process.priority}) for {process.burst_time}s")
        
        # Calculate wait time for this process
        process.wait_time = current_time
        
        # Simulate process running
        time.sleep(process.burst_time)
        
        # Update metrics
        current_time += process.burst_time
        process.turnaround_time = current_time
        process.remaining_time = 0
        
        # Add to completed list
        completed_processes.append(process)
    
    # Calculate and print metrics
    print("\nSimulation complete!\n")
    print("Process metrics:")
    print("Process ID\tBurst Time\tPriority\tWait Time\tTurnaround Time")
    
    total_wait_time = 0
    total_turnaround_time = 0
    
    for p in completed_processes:
        print(f"{p.id}\t\t{p.burst_time}s\t\t{p.priority}\t\t{p.wait_time}s\t\t{p.turnaround_time}s")
        total_wait_time += p.wait_time
        total_turnaround_time += p.turnaround_time
    
    avg_wait_time = total_wait_time / total_processes
    avg_turnaround_time = total_turnaround_time / total_processes
    
    print(f"\nAverage Wait Time: {avg_wait_time:.2f}s")
    print(f"Average Turnaround Time: {avg_turnaround_time:.2f}s")
    
    return "Priority scheduling simulation completed."