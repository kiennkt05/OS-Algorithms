import heapq
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from PageReplacement import fifo, lru, mru, lfu, mfu, secondChance, optimal

page_sequence_history = []

class PageReplacementSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Page Replacement Simulator")

        # Set minimum width and height for the window
        self.root.wm_minsize(950, 900)  # Minimum width and height set to 800px

        # Create a canvas and a scrollbar
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        # Configure the canvas
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack the canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Add widgets to the scrollable frame
        frame = ttk.Frame(self.scrollable_frame, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Page Sequence Combobox
        self.pages_combobox = ttk.Combobox(frame, width=50, values=page_sequence_history)
        self.pages_combobox.grid(row=0, column=1, sticky=tk.W)
        if page_sequence_history:
            self.pages_combobox.set(page_sequence_history[0])

        self.frame_size_entry = ttk.Entry(frame, width=10)
        self.frame_size_entry.grid(row=0, column=3, sticky=tk.W)
        self.frame_size_entry.insert(0, "3")

        self.algorithm_combobox = ttk.Combobox(frame, values=["FIFO", "LRU", "MRU", "LFU", "MFU", "Second Chance", "Optimal"], state="readonly")
        self.algorithm_combobox.grid(row=0, column=5, sticky=tk.W)
        self.algorithm_combobox.set("Optimal")

        ttk.Label(frame, text="Page Sequence:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(frame, text="\tFrame Size:").grid(row=0, column=2, sticky=tk.W)
        ttk.Label(frame, text="\tAlgorithm:").grid(row=0, column=4, sticky=tk.W)

        run_button = ttk.Button(frame, text="Run Simulation", command=self.run_simulation)
        run_button.grid(row=1, column=0, sticky=tk.W, pady=10)

        graph_button = ttk.Button(frame, text="Show Graph", command=self.show_graph)
        graph_button.grid(row=1, column=1, sticky=tk.W, pady=10)

        self.graph_canvas = None  # Placeholder for the graph canvas
        self.run_simulation()

    def run_simulation(self):
        pages = self.pages_combobox.get().strip()
        frames = self.frame_size_entry.get().strip()
        algorithm = self.algorithm_combobox.get()

        # Validate inputs
        if not pages or not frames.isdigit() or int(frames) <= 0:
            messagebox.showerror("Error", "Please enter a valid page sequence and frame size.")
            return

        frames = int(frames)

        # Update suggestions for Page Sequence and Frame Size
        if pages not in page_sequence_history:
            heapq.heappush(page_sequence_history, pages)
            self.pages_combobox['values'] = page_sequence_history  # Update Combobox values

        optional = None
        if algorithm == "FIFO":
            faults, hits, hit_ratio, memory_states = fifo(pages.split(), frames)
        elif algorithm == "LRU":
            faults, hits, hit_ratio, memory_states = lru(pages.split(), frames)
        elif algorithm == "MRU":
            faults, hits, hit_ratio, memory_states = mru(pages.split(), frames)
        elif algorithm == "LFU":
            faults, hits, hit_ratio, memory_states, optional = lfu(pages.split(), frames)
        elif algorithm == "MFU":
            faults, hits, hit_ratio, memory_states, optional = mfu(pages.split(), frames)
        elif algorithm == "Second Chance":
            faults, hits, hit_ratio, memory_states, optional = secondChance(pages.split(), frames)
        elif algorithm == "Optimal":
            faults, hits, hit_ratio, memory_states, optional = optimal(pages.split(), frames)
        else:
            messagebox.showerror("Error", "Please select a valid algorithm")
            return

        self.plot_memory_states(memory_states, faults, hits, hit_ratio, algorithm, optional)
        self.show_graph()

    def show_graph(self):
        pages = self.pages_combobox.get().strip()
        algorithm = self.algorithm_combobox.get()

        # Validate inputs
        if not pages:
            messagebox.showerror("Error", "Please enter a valid page sequence.")
            return

        max_frames = 15  # Fixed maximum frame size
        pages = pages.split()

        # Calculate page faults for each frame size
        frame_sizes = list(range(1, max_frames + 1))
        page_faults = []

        for frames in frame_sizes:
            if algorithm == "FIFO":
                faults, _, _, _ = fifo(pages, frames)
            elif algorithm == "LRU":
                faults, _, _, _ = lru(pages, frames)
            elif algorithm == "MRU":
                faults, _, _, _ = mru(pages, frames)
            elif algorithm == "LFU":
                faults, _, _, _, _ = lfu(pages, frames)
            elif algorithm == "MFU":
                faults, _, _, _, _ = mfu(pages, frames)
            elif algorithm == "Second Chance":
                faults, _, _, _, _ = secondChance(pages, frames)
            elif algorithm == "Optimal":
                faults, _, _, _, _ = optimal(pages, frames)
            else:
                messagebox.showerror("Error", "Please select a valid algorithm")
                return
            page_faults.append(faults)

        # Plot the graph
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(frame_sizes, page_faults, marker="o", label="Page Faults")
        ax.set_title(f"Page Faults vs Frame Size ({algorithm})")
        ax.set_xlabel("Frame Size")
        ax.set_ylabel("Page Faults")
        ax.grid(True)
        ax.legend()

        # Clear any existing graph canvas
        if self.graph_canvas:
            self.graph_canvas.get_tk_widget().destroy()

        # Embed the graph below the simulation
        self.graph_canvas = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        self.graph_canvas.draw()
        self.graph_canvas.get_tk_widget().grid(row=6, column=0, columnspan=3, pady=10)

    def plot_memory_states(self, memory_states, faults, hits, hit_ratio, algorithm, optional):
        cell_width, cell_height = 40, 60
        offset_x, offset_y = 50, 70

        # Calculate the required canvas width dynamically
        num_columns = len(memory_states)
        canvas_width = max(800, offset_x + num_columns * cell_width + 50)  # Ensure a minimum width of 800
        canvas_height = offset_y + len(memory_states[0]) * cell_height + 50  # Add space for statistics

        # Clear any existing canvas
        if hasattr(self, 'canvas_widget'):
            self.canvas_widget.destroy()

        # Create a new canvas for visualization
        self.canvas_widget = tk.Canvas(self.scrollable_frame, width=canvas_width, height=canvas_height, bg="white")
        self.canvas_widget.grid(row=5, column=0, pady=10, columnspan=3)

        # Draw the title
        self.canvas_widget.create_text(canvas_width // 2, 20, text=f"Method: {algorithm}", fill="black", font=("Arial", 16, "bold"))

        # Draw column headers (page sequence)
        for step, page in enumerate(self.pages_combobox.get().split()):
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
                # Highlight new pages in green
                color = "spring green" if frame[row] not in previous_frame and frame[row] != '-' else "white"
                text_color = "black" if color == "spring green" else "black"
                self.canvas_widget.create_rectangle(x, y, x + cell_width, y + cell_height, outline="black", fill=color)
                self.canvas_widget.create_text(x + cell_width // 2, y + cell_height // 2, text=str(page) if page is not None else "-", fill=text_color, font=("Arial", 12))

                # Display the next state as a subscript
                if optional and row < len(optional[col]) and optional[col][row] != '':
                    next_state = optional[col][row]
                    self.canvas_widget.create_text(x + cell_width // 2, y + cell_height - 5, text=f"{next_state}", fill="blue", font=("Arial", 8))

            # Update the previous frame state
            previous_frame = frame[:]

        # Display statistics below the grid
        stats_y = offset_y + len(memory_states[0]) * cell_height + 20
        self.canvas_widget.create_text(canvas_width // 4, stats_y, text=f"Page Faults: {faults}", fill="red", font=("Arial", 14, "bold"))
        self.canvas_widget.create_text(canvas_width // 2, stats_y, text=f"Number of Hits: {hits}", fill="green", font=("Arial", 14, "bold"))
        self.canvas_widget.create_text(canvas_width * 3 // 4, stats_y, text=f"Hit Rate: {hit_ratio:.2%}", fill="blue", font=("Arial", 14, "bold"))

if __name__ == "__main__":
    with open("input.txt", "r") as file:
        page_sequence_history = [line.strip() for line in file if line.strip()]

    root = tk.Tk()
    app = PageReplacementSimulator(root)
    root.mainloop()

    with open("input.txt", "w") as file:
        for sequence in page_sequence_history:
            file.write(sequence + "\n")