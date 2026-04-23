import tkinter as tk
from tkinter import messagebox, ttk
import random
import math

# ─────────────────────────────────────────────
#  CSP SOLVER
# ─────────────────────────────────────────────

def is_valid(region, color, assignment, neighbors):
    for neighbor in neighbors.get(region, []):
        if assignment.get(neighbor) == color:
            return False
    return True

def backtrack(regions, neighbors, colors, assignment):
    if len(assignment) == len(regions):
        return assignment
    # Pick next unassigned region
    unassigned = [r for r in regions if r not in assignment]
    region = unassigned[0]
    for color in colors:
        if is_valid(region, color, assignment, neighbors):
            assignment[region] = color
            result = backtrack(regions, neighbors, colors, assignment)
            if result is not None:
                return result
            del assignment[region]
    return None

def solve_map_coloring(regions, neighbors, colors):
    return backtrack(regions, neighbors, colors, {})

# ─────────────────────────────────────────────
#  GUI
# ─────────────────────────────────────────────

COLOR_MAP = {
    "Red":    "#e74c3c",
    "Green":  "#2ecc71",
    "Blue":   "#3498db",
    "Yellow": "#f1c40f",
}

class MapColoringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Map Coloring – CSP Solver")
        self.root.geometry("900x620")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(True, True)

        self.regions = []
        self.neighbors = {}
        self.region_positions = {}

        self._build_ui()

    # ── Layout ──────────────────────────────────
    def _build_ui(self):
        title = tk.Label(self.root, text="🗺  Map Coloring – CSP Solver",
                         font=("Helvetica", 18, "bold"),
                         bg="#1e1e2e", fg="#cdd6f4")
        title.pack(pady=(14, 4))

        subtitle = tk.Label(self.root,
                            text="Add regions, connect neighbors, then solve!",
                            font=("Helvetica", 10), bg="#1e1e2e", fg="#a6adc8")
        subtitle.pack()

        main = tk.Frame(self.root, bg="#1e1e2e")
        main.pack(fill="both", expand=True, padx=16, pady=10)

        # Left panel
        left = tk.Frame(main, bg="#313244", bd=0, relief="flat",
                        width=280)
        left.pack(side="left", fill="y", padx=(0, 12), pady=4)
        left.pack_propagate(False)

        self._build_left_panel(left)

        # Right canvas
        right = tk.Frame(main, bg="#181825")
        right.pack(side="left", fill="both", expand=True, pady=4)

        self.canvas = tk.Canvas(right, bg="#181825", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Bottom result bar
        self.result_var = tk.StringVar(value="Result will appear here.")
        result_bar = tk.Label(self.root, textvariable=self.result_var,
                              font=("Helvetica", 11), bg="#11111b",
                              fg="#a6e3a1", anchor="w", padx=12)
        result_bar.pack(fill="x", side="bottom", pady=(4, 0))

    def _build_left_panel(self, parent):
        def section(text):
            tk.Label(parent, text=text, font=("Helvetica", 10, "bold"),
                     bg="#313244", fg="#89b4fa").pack(anchor="w",
                                                       padx=12, pady=(14, 2))

        def entry_row(parent, label, default=""):
            f = tk.Frame(parent, bg="#313244")
            f.pack(fill="x", padx=12, pady=2)
            tk.Label(f, text=label, font=("Helvetica", 9),
                     bg="#313244", fg="#cdd6f4", width=10,
                     anchor="w").pack(side="left")
            e = tk.Entry(f, font=("Helvetica", 10), bg="#45475a",
                         fg="#cdd6f4", insertbackground="white",
                         relief="flat", bd=4)
            e.insert(0, default)
            e.pack(side="left", fill="x", expand=True)
            return e

        # ── Add Region ──
        section("➕  Add Region")
        self.region_entry = entry_row(parent, "Region:", "A")
        self._btn(parent, "Add Region", self._add_region, "#89b4fa")

        # ── Add Neighbor ──
        section("🔗  Add Neighbor Link")
        self.n1_entry = entry_row(parent, "Region 1:", "A")
        self.n2_entry = entry_row(parent, "Region 2:", "B")
        self._btn(parent, "Add Neighbor", self._add_neighbor, "#89dceb")

        # ── Colors ──
        section("🎨  Colors Available")
        self.color_vars = {}
        for c in COLOR_MAP:
            var = tk.BooleanVar(value=True)
            self.color_vars[c] = var
            cb = tk.Checkbutton(parent, text=c, variable=var,
                                bg="#313244", fg=COLOR_MAP[c],
                                selectcolor="#45475a",
                                activebackground="#313244",
                                font=("Helvetica", 10, "bold"))
            cb.pack(anchor="w", padx=20)

        # ── Solve / Reset ──
        self._btn(parent, "▶  Solve", self._solve, "#a6e3a1", pady=16)
        self._btn(parent, "🔄  Reset", self._reset, "#f38ba8", pady=2)

        # ── Region list ──
        section("📋  Regions & Neighbors")
        self.info_text = tk.Text(parent, height=8, font=("Courier", 9),
                                 bg="#1e1e2e", fg="#cdd6f4",
                                 relief="flat", bd=4, state="disabled")
        self.info_text.pack(fill="both", expand=True, padx=12, pady=(4, 12))

    def _btn(self, parent, text, cmd, color, pady=4):
        tk.Button(parent, text=text, command=cmd,
                  font=("Helvetica", 10, "bold"),
                  bg=color, fg="#1e1e2e", relief="flat",
                  bd=0, pady=6, cursor="hand2").pack(
            fill="x", padx=12, pady=pady)

    # ── Actions ─────────────────────────────────
    def _add_region(self):
        name = self.region_entry.get().strip().upper()
        if not name:
            messagebox.showwarning("Input Error", "Enter a region name.")
            return
        if name in self.regions:
            messagebox.showinfo("Info", f"Region '{name}' already exists.")
            return
        self.regions.append(name)
        self.neighbors[name] = []
        self._place_region(name)
        self._refresh_info()
        self._redraw()

    def _place_region(self, name):
        """Place region at a random position on canvas (circle node)."""
        w = self.canvas.winfo_width() or 580
        h = self.canvas.winfo_height() or 480
        margin = 60
        # Spread in a circle pattern
        n = len(self.regions)
        idx = n - 1
        angle = (2 * math.pi * idx) / max(n, 1)
        cx = w // 2 + int((w // 2 - margin) * 0.65 * math.cos(angle))
        cy = h // 2 + int((h // 2 - margin) * 0.65 * math.sin(angle))
        self.region_positions[name] = (cx, cy)

    def _add_neighbor(self):
        r1 = self.n1_entry.get().strip().upper()
        r2 = self.n2_entry.get().strip().upper()
        if r1 not in self.regions or r2 not in self.regions:
            messagebox.showwarning("Error", "Both regions must exist first.")
            return
        if r1 == r2:
            messagebox.showwarning("Error", "A region cannot neighbor itself.")
            return
        if r2 not in self.neighbors[r1]:
            self.neighbors[r1].append(r2)
            self.neighbors[r2].append(r1)
        self._refresh_info()
        self._redraw()

    def _solve(self):
        if not self.regions:
            messagebox.showwarning("Empty", "Add at least one region first.")
            return
        colors = [c for c, v in self.color_vars.items() if v.get()]
        if not colors:
            messagebox.showwarning("No Colors", "Select at least one color.")
            return
        solution = solve_map_coloring(self.regions, self.neighbors, colors)
        if solution is None:
            self.result_var.set("❌  No solution found — try adding more colors!")
            messagebox.showerror("No Solution",
                                 "Cannot color this map with selected colors.\nTry enabling more colors.")
        else:
            self.assignment = solution
            self.result_var.set(
                "✅  Solved!  " +
                "   ".join(f"{r} → {solution[r]}" for r in self.regions))
            self._redraw(solution)

    def _reset(self):
        self.regions.clear()
        self.neighbors.clear()
        self.region_positions.clear()
        self.result_var.set("Result will appear here.")
        self._refresh_info()
        self._redraw()

    # ── Drawing ──────────────────────────────────
    def _redraw(self, solution=None):
        self.canvas.delete("all")
        if not self.regions:
            self.canvas.create_text(
                self.canvas.winfo_width() // 2 or 290,
                self.canvas.winfo_height() // 2 or 240,
                text="Add regions to get started →",
                fill="#45475a", font=("Helvetica", 13))
            return

        # Recompute positions based on current canvas size
        w = self.canvas.winfo_width() or 580
        h = self.canvas.winfo_height() or 480
        n = len(self.regions)
        margin = 70
        for idx, name in enumerate(self.regions):
            angle = (2 * math.pi * idx) / n
            cx = w // 2 + int((min(w, h) // 2 - margin) * math.cos(angle))
            cy = h // 2 + int((min(w, h) // 2 - margin) * math.sin(angle))
            self.region_positions[name] = (cx, cy)

        # Draw edges
        drawn_edges = set()
        for r, nbs in self.neighbors.items():
            for nb in nbs:
                edge = tuple(sorted([r, nb]))
                if edge in drawn_edges:
                    continue
                drawn_edges.add(edge)
                x1, y1 = self.region_positions[r]
                x2, y2 = self.region_positions[nb]
                self.canvas.create_line(x1, y1, x2, y2,
                                        fill="#585b70", width=2)

        # Draw nodes
        r = 30
        for name in self.regions:
            cx, cy = self.region_positions[name]
            fill = "#45475a"
            if solution and name in solution:
                fill = COLOR_MAP.get(solution[name], "#89b4fa")
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                    fill=fill, outline="#cdd6f4", width=2)
            self.canvas.create_text(cx, cy, text=name,
                                    font=("Helvetica", 13, "bold"),
                                    fill="white")
            if solution and name in solution:
                self.canvas.create_text(cx, cy + r + 12,
                                        text=solution[name],
                                        font=("Helvetica", 9),
                                        fill="#cdd6f4")

    def _refresh_info(self):
        self.info_text.config(state="normal")
        self.info_text.delete("1.0", "end")
        for r in self.regions:
            nbs = ", ".join(self.neighbors[r]) if self.neighbors[r] else "—"
            self.info_text.insert("end", f"{r}: [{nbs}]\n")
        self.info_text.config(state="disabled")


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = MapColoringApp(root)

    # Load sample data from assignment
    sample_regions = ["A", "B", "C", "D"]
    sample_neighbors = {
        "A": ["B", "C"],
        "B": ["A", "C", "D"],
        "C": ["A", "B", "D"],
        "D": ["B", "C"],
    }
    app.regions = sample_regions
    app.neighbors = sample_neighbors
    app._refresh_info()
    root.after(100, app._redraw)  # wait for canvas to size before drawing

    root.mainloop()
