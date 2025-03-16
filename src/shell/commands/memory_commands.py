"""Memory management simulation commands"""
import time
import random
from collections import deque

class Page:
    """Memory page representation"""
    def __init__(self, page_id, process_id, content=""):
        self.page_id = page_id
        self.process_id = process_id
        self.content = content
        self.last_accessed = 0
        
    def __str__(self):
        return f"P{self.process_id}:Page{self.page_id}"
        
    def access(self):
        self.last_accessed = time.time()

class PageFrame:
    """Physical memory frame"""
    def __init__(self, frame_id):
        self.frame_id = frame_id
        self.page = None
        self.allocated_time = 0
        
    def load_page(self, page):
        self.page = page
        self.allocated_time = time.time()
        page.access()
        
    def is_free(self):
        return self.page is None
        
    def __str__(self):
        return f"Frame{self.frame_id}[{self.page if self.page else 'empty'}]"

class PageReplacement:
    """Base page replacement algorithm"""
    def __init__(self, algorithm="FIFO"):
        self.name = algorithm
        if algorithm == "FIFO":
            self.page_queue = deque()
            self.add = self._add_fifo
            self.get_victim = self._get_fifo_victim
        else:  # LRU
            self.frames = []
            self.add = self._add_lru
            self.get_victim = self._get_lru_victim
    
    def _add_fifo(self, frame):
        if frame not in self.page_queue:
            self.page_queue.append(frame)
            
    def _get_fifo_victim(self):
        return self.page_queue.popleft() if self.page_queue else None
    
    def _add_lru(self, frame):
        if frame not in self.frames:
            self.frames.append(frame)
            
    def _get_lru_victim(self):
        if not self.frames:
            return None
        victim = min(self.frames, key=lambda f: f.page.last_accessed if f.page else float('inf'))
        self.frames.remove(victim)
        return victim

class Process:
    """Process with memory pages"""
    def __init__(self, process_id, num_pages):
        self.process_id = process_id
        self.pages = [Page(i, process_id, f"Data for P{process_id}, page {i}") for i in range(num_pages)]
        self.page_table = {i: None for i in range(num_pages)}
        
    def get_page(self, page_id):
        return self.pages[page_id] if 0 <= page_id < len(self.pages) else None

class PhysicalMemory:
    """Physical memory with page frames"""
    def __init__(self, num_frames, replacement_algorithm="FIFO"):
        self.frames = [PageFrame(i) for i in range(num_frames)]
        self.replacement_algorithm = PageReplacement(replacement_algorithm)
        self.page_faults = self.hits = 0
        
    def get_free_frame(self):
        return next((frame for frame in self.frames if frame.is_free()), None)
        
    def load_page(self, page, process):
        page_id = page.page_id
        
        # Check if page is already in memory
        if process.page_table[page_id] is not None:
            frame_id = process.page_table[page_id]
            self.frames[frame_id].page.access()
            self.hits += 1
            return frame_id
        
        # Page fault - page not in memory
        self.page_faults += 1
        
        # Get a free frame or use replacement algorithm
        frame = self.get_free_frame()
        if frame is None:
            frame = self.replacement_algorithm.get_victim()
            
            # Update page table of the process owning the evicted page
            if frame and frame.page:
                old_pid, old_page_id = frame.page.process_id, frame.page.page_id
                for p in self.processes:
                    if p.process_id == old_pid:
                        p.page_table[old_page_id] = None
                        break
                print(f"Replacing {frame.page} with {page} using {self.replacement_algorithm.name}")
        
        # Load page into frame and update page table
        frame.load_page(page)
        self.replacement_algorithm.add(frame)
        process.page_table[page_id] = frame.frame_id
        return -1  # Indicating page fault
        
    def print_state(self):
        print("\nPhysical Memory State:")
        print("--------------------")
        for frame in self.frames:
            print(frame)

def simulate_memory_paging(args):
    """Simulate memory management using paging"""
    # Parse arguments with defaults
    replacement_algo = args[0].upper() if args and args[0].upper() in ["FIFO", "LRU"] else "FIFO"
    try:
        num_processes = max(1, int(args[1])) if len(args) > 1 else 4
        memory_size = max(1, int(args[2])) if len(args) > 2 else 10
    except (ValueError, IndexError):
        num_processes, memory_size = 4, 10
    
    print(f"\nStarting Memory Paging Simulation:")
    print(f"- Algorithm: {replacement_algo}, Processes: {num_processes}, Memory: {memory_size} frames")
    
    # Initialize memory and processes
    memory = PhysicalMemory(memory_size, replacement_algo)
    processes = [Process(i, random.randint(2, 5)) for i in range(num_processes)]
    memory.processes = processes
    pages_in_memory = {p.process_id: 0 for p in processes}
    
    print("\nProcesses created:")
    for p in processes:
        print(f"Process {p.process_id}: {len(p.pages)} pages")
    
    # Run simulation
    total_references = 30
    print(f"\nSimulating {total_references} memory references...")
    time.sleep(1)
    
    for i in range(total_references):
        # Select random process and page
        process = random.choice(processes)
        page_id = random.randint(0, len(process.pages) - 1)
        page = process.get_page(page_id)
        
        print(f"\nReference #{i+1}: Process {process.process_id} requests Page {page_id}")
        
        # Access the page
        result = memory.load_page(page, process)
        if result == -1:
            print(f"PAGE FAULT: Page {page_id} of Process {process.process_id} not in memory")
            pages_in_memory[process.process_id] += 1
        else:
            print(f"PAGE HIT: Page {page_id} of Process {process.process_id} found in frame {result}")
        
        memory.print_state()
        time.sleep(0.5)
    
    # Print statistics
    print("\n\nSimulation Complete!")
    print("===================")
    print(f"Algorithm: {memory.replacement_algorithm.name}")
    print(f"Page Faults: {memory.page_faults}, Hits: {memory.hits}")
    hit_ratio = memory.hits / total_references if total_references > 0 else 0
    print(f"Hit Ratio: {hit_ratio:.2f} ({hit_ratio*100:.2f}%)")
    
    print("\nMemory Usage by Process:")
    for p_id, pages in pages_in_memory.items():
        process = next(p for p in processes if p.process_id == p_id)
        print(f"Process {p_id}: {pages} pages in memory out of {len(process.pages)} total")
    
    return "Memory paging simulation completed."