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