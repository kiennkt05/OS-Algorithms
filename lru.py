def lru(pages, frames):
    memory, faults, hits, stack, memory_states = ['-']*frames, 0, 0, [], []
    
    idx = 0
    for page in pages:
        if page not in memory:
            if memory[-1] == '-':
                memory[idx] = page
                idx += 1
                stack.append(page)
            else:
                lru_page = stack.pop(0)
                memory.remove(lru_page)
                memory.append(page)
                stack.append(page)
            faults += 1
        else:
            hits += 1
            stack.remove(page)
            stack.append(page)
            memory.remove(page)
            memory.append(page)
        memory_states.append(list(memory))  # Capture memory state
    hit_ratio = hits / len(pages)
    return (memory, faults, hits, hit_ratio, memory_states)