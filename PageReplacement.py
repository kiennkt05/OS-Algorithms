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

def optimal(pages, frames):
    n = len(pages)

    next_index = [float('inf')] * n
    last_seen = {}

    for i in range(n - 1, -1, -1):
        if pages[i] in last_seen:
            next_index[i] = last_seen[pages[i]]
        last_seen[pages[i]] = i

    memory, memory_states, next_states = [['-'] * frames, [''] * frames], [], []
    faults, hits = 0, 0
    
    for i in range(n):
        if pages[i] not in memory[0]:
            if '-' in memory[0]:
                idx = memory[0].index('-')
                memory[0][idx] = pages[i]
                memory[1][idx] = next_index[i]
            else:
                farthest = max(memory[1])
                replace_index = memory[1].index(farthest)
                memory[0][replace_index] = pages[i]
                memory[1][replace_index] = next_index[i]
            faults += 1
        else:
            hits += 1
            idx = memory[0].index(pages[i])
            memory[1][idx] = next_index[i]

        memory_states.append(memory[0].copy())
        next_states.append(memory[1].copy())

    # Calculate hit ratio
    hit_ratio = hits / n
    return memory, faults, hits, hit_ratio, memory_states, next_states

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