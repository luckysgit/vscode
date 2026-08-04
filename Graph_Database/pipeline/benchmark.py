import time
import psutil
import os

def measure_execution(func, *args, **kwargs):
    process = psutil.Process(os.getpid())
    
    # Capture starting stats
    start_time = time.time()
    start_mem = process.memory_info().rss / (1024 * 1024)  # MB
    
    # Run the function (Loading or Querying)
    result = func(*args, **kwargs)
    
    # Capture ending stats
    end_time = time.time()
    end_mem = process.memory_info().rss / (1024 * 1024)  # MB
    
    execution_time = end_time - start_time
    peak_mem_diff = end_mem - start_mem
    
    return {
        "result": result,
        "execution_time_sec": round(execution_time, 4),
        "memory_used_mb": round(peak_mem_diff, 2)
    }