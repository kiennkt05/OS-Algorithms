import tkinter as tk
from tkinter import ttk, messagebox

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
    memory, faults, hits, memory_states = ['-'] * frames, 0, 0, []

    for i in range(len(pages)):
        if pages[i] not in memory:
            if '-' in memory:
                memory[memory.index('-')] = pages[i]
            else:
                farthest = -1
                replace_index = -1
                for j in range(len(memory)):
                    if memory[j] not in pages[i + 1:]:
                        replace_index = j
                        break
                    else:
                        next_use = pages[i + 1:].index(memory[j])
                        if next_use > farthest:
                            farthest = next_use
                            replace_index = j
                memory[replace_index] = pages[i]
            faults += 1
        else:
            hits += 1
        memory_states.append(list(memory))

    hit_ratio = hits / len(pages)
    return (memory, faults, hits, hit_ratio, memory_states)

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

class PageReplacementSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Page Replacement Simulator")

        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        self.pages_entry = ttk.Entry(frame, width=50)
        self.pages_entry.grid(row=0, column=1)
        self.pages_entry.insert(0, "7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1")

        self.frame_size_entry = ttk.Entry(frame, width=10)
        self.frame_size_entry.grid(row=1, column=1, sticky=tk.W)
        self.frame_size_entry.insert(0, "3")

        self.algorithm_combobox = ttk.Combobox(frame, values=["FIFO", "Optimal", "LRU"], state="readonly")
        self.algorithm_combobox.grid(row=2, column=1, sticky=tk.W)
        self.algorithm_combobox.set("FIFO")

        ttk.Label(frame, text="Page Sequence:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(frame, text="Frame Size:").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(frame, text="Algorithm:").grid(row=2, column=0, sticky=tk.W)

        run_button = ttk.Button(frame, text="Run Simulation", command=self.run_simulation)
        run_button.grid(row=2, column=2, sticky=tk.W, padx=10)

        self.run_simulation()

    def run_simulation(self):
        pages = self.pages_entry.get().split()
        frames = int(self.frame_size_entry.get())
        algorithm = self.algorithm_combobox.get()

        if algorithm == "FIFO":
            _, faults, hits, hit_ratio, memory_states = fifo(pages, frames)
        elif algorithm == "Optimal":
            _, faults, hits, hit_ratio, memory_states = optimal(pages, frames)
        elif algorithm == "LRU":
            _, faults, hits, hit_ratio, memory_states = lru(pages, frames)
        else:
            messagebox.showerror("Error", "Please select a valid algorithm")
            return

        self.plot_memory_states(memory_states, faults, hits, hit_ratio, algorithm)

    def plot_memory_states(self, memory_states, faults, hits, hit_ratio, algorithm):
        # Define cell dimensions and offsets
        cell_width = 40
        cell_height = 50
        offset_x = 50
        offset_y = 70

        # Calculate the required canvas width dynamically
        num_columns = len(memory_states)
        canvas_width = max(800, offset_x + num_columns * cell_width + 50)  # Ensure a minimum width of 800
        canvas_height = offset_y + len(memory_states[0]) * cell_height + 150  # Add space for statistics

        # Clear any existing canvas
        if hasattr(self, 'canvas_widget'):
            self.canvas_widget.destroy()

        # Create a new canvas for visualization
        self.canvas_widget = tk.Canvas(self.root, width=canvas_width, height=canvas_height, bg="white")
        self.canvas_widget.grid(row=4, column=0, pady=10)

        # Draw the title
        self.canvas_widget.create_text(canvas_width // 2, 20, text=f"Method: {algorithm}", fill="black", font=("Arial", 16, "bold"))

        # Draw column headers (page sequence)
        for step, page in enumerate(self.pages_entry.get().split()):
            x = offset_x + step * cell_width
            y = offset_y
            self.canvas_widget.create_text(x + cell_width // 2, y - 20, text=str(page), fill="black", font=("Arial", 12))

        # Draw memory states in columns
        previous_frame = []  # Initialize an empty previous frame
        for col, frame in enumerate(memory_states):
            # Adjust the size of previous_frame to match the current frame
            if len(previous_frame) < len(frame):
                previous_frame.extend([None] * (len(frame) - len(previous_frame)))

            for row, page in enumerate(frame):
                x = offset_x + col * cell_width
                y = offset_y + row * cell_height
                # Highlight new pages in red
                color = "red" if frame[row] not in previous_frame and frame[row] != '-' else "white"
                text_color = "black" if color == "red" else "black"
                self.canvas_widget.create_rectangle(x, y, x + cell_width, y + cell_height, outline="black", fill=color)
                self.canvas_widget.create_text(x + cell_width // 2, y + cell_height // 2, text=str(page) if page is not None else "-", fill=text_color, font=("Arial", 12))

            # Update the previous frame state
            previous_frame = frame[:]

        # Display statistics below the grid
        stats_y = offset_y + len(memory_states[0]) * cell_height + 20
        self.canvas_widget.create_text(canvas_width // 2, stats_y, text=f"Page Faults: {faults}", fill="red", font=("Arial", 14, "bold"))
        self.canvas_widget.create_text(canvas_width // 2, stats_y + 30, text=f"Number of Hits: {hits}", fill="green", font=("Arial", 14, "bold"))
        self.canvas_widget.create_text(canvas_width // 2, stats_y + 60, text=f"Hit Rate: {hit_ratio:.2%}", fill="blue", font=("Arial", 14, "bold"))

if __name__ == "__main__":
    root = tk.Tk()
    app = PageReplacementSimulator(root)
    root.mainloop()