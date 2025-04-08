import heapq

def fifo(pages, frames):
    memory, faults, hits, memory_states = ['-'] * frames, 0, 0, []

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
    return faults, hits, hit_ratio, memory_states

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
    return faults, hits, hit_ratio, memory_states

def mru(pages, frames):
    memory, faults, hits, stack, memory_states = ['-']*frames, 0, 0, [], []
    
    idx = 0
    for page in pages:
        if page not in memory:
            if memory[-1] == '-':
                memory[idx] = page
                idx += 1
                stack.append(page)
            else:
                mru_page = stack.pop(-1)
                memory.remove(mru_page)
                stack.append(page), memory.append(page)
                
            faults += 1
        else:
            hits += 1
            stack.remove(page), memory.remove(page)
            stack.append(page), memory.append(page)

        memory_states.append(list(memory))  # Capture memory state
    hit_ratio = hits / len(pages)
    return faults, hits, hit_ratio, memory_states

def lfu(pages, frames):
    memory, faults, hits, memory_states, frequency_states = ['-'] * frames, 0, 0, [], []
    frequency = {}

    idx = 0
    for page in pages:
        if page in frequency:
            frequency[page] += 1
        else:
            frequency[page] = 1

        if page not in memory:
            if memory[-1] == '-':  # If there is an empty slot in memory
                memory[idx] = page
            else:
                # Find the least frequently used page
                lfu_page = min(memory, key=lambda p: (frequency[p], (memory.index(p) - idx) % frames))
                frequency[lfu_page] = 0
                idx = memory.index(lfu_page)
                memory[idx] = page  # Replace the LFU page
            idx = (idx + 1) % frames
            faults += 1
        else:
            hits += 1

        memory_states.append(list(memory))
        frequency_states.append([frequency[p] if p != '-' else '' for p in memory])

    # Calculate hit ratio
    hit_ratio = hits / len(pages)
    return faults, hits, hit_ratio, memory_states, frequency_states

def mfu(pages, frames):
    memory, faults, hits, memory_states, frequency_states = ['-'] * frames, 0, 0, [], []
    frequency = {}

    idx = 0
    for page in pages:
        if page in frequency:
            frequency[page] += 1
        else:
            frequency[page] = 1

        if page not in memory:
            if memory[-1] == '-':  # If there is an empty slot in memory
                memory[idx] = page
            else:
                # Find the least frequently used page
                lfu_page = max(memory, key=lambda p: (frequency[p], -((memory.index(p) - idx) % frames)))
                frequency[lfu_page] = 0
                idx = memory.index(lfu_page)
                memory[idx] = page  # Replace the LFU page
            idx = (idx + 1) % frames
            faults += 1
        else:
            hits += 1

        memory_states.append(list(memory))
        frequency_states.append([frequency[p] if p != '-' else '' for p in memory])

    # Calculate hit ratio
    hit_ratio = hits / len(pages)
    return faults, hits, hit_ratio, memory_states, frequency_states

def secondChance(pages, frames):
    memory, faults, hits, memory_states, reference_bits_states = ['-'] * frames, 0, 0, [], []
    reference_bits = [''] * frames  # Reference bits for each frame
    pointer = 0  # Points to the next frame to be replaced

    for page in pages:
        if page in memory:
            # Page hit: Set the reference bit of the page to 1
            hits += 1
            reference_bits[memory.index(page)] = 1
        else:
            # Page fault occurs
            while True:
                # Check the reference bit of the frame at the pointer
                if reference_bits[pointer] == '' or reference_bits[pointer] == 0:
                    # Replace the page at the pointer
                    memory[pointer] = page
                    reference_bits[pointer] = 1  # Set the reference bit for the new page
                    pointer = (pointer + 1) % frames  # Move the pointer to the next frame
                    break
                else:
                    # Give the page a second chance by resetting its reference bit
                    reference_bits[pointer] = 0
                    pointer = (pointer + 1) % frames  # Move the pointer to the next frame
            faults += 1

        # Capture the current memory state and reference bits state
        memory_states.append(list(memory))
        reference_bits_states.append(list(reference_bits))

    # Calculate hit ratio
    hit_ratio = hits / len(pages)
    return faults, hits, hit_ratio, memory_states, reference_bits_states

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
    
    j = 0
    for i in range(n):
        if pages[i] not in memory[0]:
            if memory[0][-1] == '-':
                memory[0][j] = pages[i]
                memory[1][j] = next_index[i]
                j += 1
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
    return faults, hits, hit_ratio, memory_states, next_states


if __name__ == "__main__":
    pages = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1, 2]
    frames = 3
    faults, hits, hit_ratio, memory_states, frequency_states = lfu(pages, frames)
    for i in range(len(pages)):
        print(pages[i], memory_states[i], frequency_states[i])