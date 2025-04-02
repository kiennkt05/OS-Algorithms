def fifo(pages, frames):
    memory, faults, hits, memory_states = ['-']*frames, 0, 0, []

    idx = 0
    for page in pages:
        if page not in memory:
            memory[idx%frames] = page
            faults += 1
            idx += 1    
        else:
            hits += 1
        memory_states.append(list(memory))  # Capture memory state
    hit_ratio = hits / len(pages)
    return (memory, faults, hits, hit_ratio, memory_states)