"""
Process synchronization simulation commands
"""
import time
import random
import threading
from enum import Enum

class State(Enum):
    THINKING = 1
    HUNGRY = 2
    EATING = 3

class Fork:
    """Represents a fork (mutex)"""
    def __init__(self, id):
        self.id = id
        self.lock = threading.Lock()
        self.owner = None

    def pick_up(self, philosopher_id):
        if self.lock.acquire(blocking=False):
            self.owner = philosopher_id
            return True
        return False

    def put_down(self):
        self.owner = None
        self.lock.release()

class Philosopher(threading.Thread):
    """Represents a philosopher in the dining philosophers problem"""
    def __init__(self, id, left_fork, right_fork, state_lock, run_time, monitor):
        super().__init__()
        self.id = id
        self.left_fork = left_fork
        self.right_fork = right_fork
        self.state = State.THINKING
        self.state_lock = state_lock
        self.run_time = run_time
        self.eating_count = 0
        self.thinking_time = self.hungry_time = self.eating_time = 0
        self.monitor = monitor
        # Prevent deadlock - philosophers pick up forks in different orders
        self.first_fork, self.second_fork = (right_fork, left_fork) if id % 2 == 0 else (left_fork, right_fork)

    def think(self):
        self.change_state(State.THINKING)
        think_time = random.uniform(0.5, 2)
        time.sleep(think_time)
        self.thinking_time += think_time

    def eat(self):
        self.change_state(State.EATING)
        eat_time = random.uniform(0.5, 1.5)
        time.sleep(eat_time)
        self.eating_time += eat_time
        self.eating_count += 1

    def change_state(self, new_state):
        with self.state_lock:
            self.state = new_state
            self.monitor.update_display()

    def try_to_eat(self):
        self.change_state(State.HUNGRY)
        hungry_start = time.time()

        # Try to get first fork
        if not self.first_fork.pick_up(self.id):
            self.hungry_time += time.time() - hungry_start
            return False
            
        time.sleep(0.1)  # Visualization delay

        # Try to get second fork
        if not self.second_fork.pick_up(self.id):
            self.first_fork.put_down()
            self.hungry_time += time.time() - hungry_start
            return False

        self.eat()
        self.second_fork.put_down()
        self.first_fork.put_down()
        return True

    def run(self):
        start_time = time.time()
        while time.time() - start_time < self.run_time:
            self.think()
            while not self.try_to_eat():
                time.sleep(0.1)

class DiningPhilosophersMonitor:
    """Displays the state of the dining philosophers"""
    def __init__(self, philosophers, forks):
        self.philosophers = philosophers
        self.forks = forks
        self.display_lock = threading.Lock()

    def update_display(self):
        with self.display_lock:
            print("\033[H\033[J", end="")  # Clear screen
            print("\n=== DINING PHILOSOPHERS SIMULATION ===\n")
            
            for i, p in enumerate(self.philosophers):
                left = "🍴" if self.forks[i].owner == p.id else "  "
                right = "🍴" if self.forks[(i+1) % len(self.forks)].owner == p.id else "  "
                
                # Show state with emoji
                if p.state == State.THINKING:
                    state = "🤔 Thinking"
                elif p.state == State.HUNGRY:
                    state = "😋 Hungry  "
                else:
                    state = "🍽️  Eating  "
                
                print(f"Philosopher {i}: {left} {state} {right} | Meals: {p.eating_count}")
            
            print("----------------------------------------")

def simulate_dining_philosophers(args):
    """Simulate the dining philosophers problem"""
    # Parse args with defaults
    num_philosophers = 5
    simulation_time = 20
    
    if args:
        try:
            num_philosophers = max(2, min(20, int(args[0])))
        except ValueError:
            pass
    
    if len(args) > 1:
        try:
            simulation_time = max(5, min(120, int(args[1])))
        except ValueError:
            pass
    
    print(f"\nStarting Dining Philosophers simulation with {num_philosophers} philosophers for {simulation_time} seconds\n")
    time.sleep(1)
    
    # Create resources
    forks = [Fork(i) for i in range(num_philosophers)]
    state_lock = threading.Lock()
    monitor = DiningPhilosophersMonitor([], forks)
    
    # Create and start philosophers
    philosophers = [
        Philosopher(i, forks[i], forks[(i+1) % num_philosophers], 
                   state_lock, simulation_time, monitor)
        for i in range(num_philosophers)
    ]
    monitor.philosophers = philosophers
    
    try:
        for p in philosophers:
            p.start()
        
        # Main simulation loop
        start_time = time.time()
        while time.time() - start_time < simulation_time:
            monitor.update_display()
            time.sleep(0.5)
        
        for p in philosophers:
            p.join()
        
        # Final stats
        monitor.update_display()
        print("\nSimulation complete!\n")
        
        # Print concise stats
        print("Philosopher Statistics:")
        print("------------------------")
        for i, p in enumerate(philosophers):
            print(f"Phil {i}: {p.eating_count} meals | Think: {p.thinking_time:.1f}s | "
                  f"Hungry: {p.hungry_time:.1f}s | Eating: {p.eating_time:.1f}s")
        
        # Check for starvation
        meals = [p.eating_count for p in philosophers]
        if max(meals) - min(meals) > 3:
            print("\nWARNING: Possible starvation detected! Meal count difference > 3")
        else:
            print("\nResource distribution was fair. No starvation detected.")
            
    except KeyboardInterrupt:
        print("\nSimulation interrupted!")
    
    return "Dining Philosophers simulation completed."


