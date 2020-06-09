import tkinter as tk
import functools
from helpers import *


WHITE = "#ffffff"
RED = "#ffb5b5"
ORANGE = "#ffdeb5"
YELLOW = "#fffca1"
GREEN = "#b7ffb5"
BLUE = "#b0fff4"
PURPLE = "#d4b0ff"
PINK = "#ffc7f2"
GREY = "#bbbbbb"
COLOURS = [WHITE, RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, PINK, GREY]

NORMAL = "normal"
CORNER = "corner"
CENTRE = "centre"
COLOUR = "colour"
MODES = [NORMAL, CORNER, CENTRE, COLOUR]


@functools.total_ordering
class Cell(tk.Canvas):
    """A single Sudoku cell. Supports Snyder (corner) notes, centre notes and cell colouring. Can be compared against
    other cells and integers (for example in pseudocode: Cell() == Cell(5) and Cell() == 5 are both supported. A Cell
    can be fixed (value cannot be changed by the user) or it can be changed"""
    def __init__(self, master, position, fixed=None, size=50, bg=WHITE):
        super().__init__(master, width=size, height=size, bg=bg, highlightthickness=0)
        self.position = position
        self.size = size
        self.colour = bg
        self.mode = NORMAL
        self.corners = list((size*(x/8), size*(y/8)) for y in (1,4,7) for x in (1,4,7))
        self.centre = self.size/2, self.size/2
        del self.corners[4]
        self.cornernotes = []
        self.centrenotes = []
        if fixed is not None:
            self.number = fixed
            self.fixed = True
        else:
            self.number = None
            self.fixed = False
        self.bind("<1>", lambda e: self.focus_set())
        self.bind("<FocusIn>", self._focusin)
        self.bind("<FocusOut>", self._focusout)
        self._refresh()

    def __repr__(self):
        return f"<Cell: n={self.number}>"

    def __eq__(self, other):
        """Compare the number in this Cell against the number in another Cell or an integer"""
        if isinstance(other, Cell):
            return self.number == other.number
        elif other is None:
            return self.number is None
        elif isinstance(other, int):
            return self.number == other
        else:
            raise NotImplementedError(f"Cannot compare {type(self)} and {type(other)}")

    def __lt__(self, other):
        """Compare the number in this Cell against the number in another Cell or an integer"""
        if isinstance(other, Cell):
            try:
                return self.number < other.number
            except TypeError:
                # if one of the cells is None
                return False
        elif other is None:
            return self.number is None
        elif isinstance(other, int):
            return self.number < other
        else:
            raise NotImplementedError(f"Cannot compare {type(self)} and {type(other)}")

    def add_corner_note(self, num):
        """Add the given integer to the corner notes of the Cell"""
        if num in self.cornernotes:
            self.remove_corner_note(num)
        elif len(self.cornernotes) == 8:
            raise ValueError("Corner cells full!")
        else:
            self.cornernotes.append(num)
        self.cornernotes.sort()
        self._refresh()

    def remove_corner_note(self, num):
        """Remove the given integer from the corner notes of the Cell"""
        self.cornernotes.remove(num)
        self.cornernotes.sort()
        self._refresh()

    def add_centre_note(self, num):
        """Add the given integer to the centre notes of the Cell"""
        if num in self.centrenotes:
            self.remove_centre_note(num)
        else:
            self.centrenotes.append(num)
        self.centrenotes.sort()
        self._refresh()

    def remove_centre_note(self, num):
        """Remove the given integer from the centre notes of the Cell"""
        self.centrenotes.remove(num)
        self.centrenotes.sort()
        self._refresh()

    def set_num(self, num):
        """Set the Cell to be this number, if it is not fixed"""
        if not self.fixed:
            if self.number == num:
                self.number = None
            else:
                self.number = num
        self._refresh()

    def set_colour(self, colour):
        """Set the Cell background to be the colour supplied"""
        self.colour = colour
        self._refresh()

    def _translate(self, event):
        """Translate a tkinter keyboard Event object to a call to the action desired by the user"""
        if event.keysym == "BackSpace":
            self.cornernotes = []
            self.centrenotes = []
            self.set_num(None)
            self._refresh()
        elif event.char not in "123456789":
            return
        else:
            num = int(event.char)
            if self.mode == NORMAL:
                self.set_num(num)
            elif self.mode == CORNER:
                self.add_corner_note(num)
            elif self.mode == CENTRE:
                self.add_centre_note(num)
            elif self.mode == COLOUR:
                self.set_colour(COLOURS[int(num) - 1])

    def _refresh(self):
        """Refresh the Cell to update the Cell on screen to display changes to the notes, colour and number"""
        self.delete(tk.ALL)
        if self.number is not None:
            if not self.fixed:
                textcolour = "#006eba"
            else:
                textcolour = "black"
            self.create_text(*self.centre, text=str(self.number), font=("Arial", int(self.size*3/4)), fill=textcolour)
        else:
            for i, n in enumerate(self.cornernotes):
                self.create_text(*self.corners[i], text=str(n), font=("Arial", int(self.size*1/5)))
            self.create_text(*self.centre, text="".join(map(str, self.centrenotes)))

    def _focusin(self, _):
        """When the Cell has focus, highlight it and allow it to take keyboard input"""
        self.config(bg=average_colours("#fffcb5", self.colour))
        self.bind("<Key>", self._translate)

    def _focusout(self, _):
        """When the Cell loses focus, revert the colour to the original and disable keyboard input to the Cell"""
        self.config(bg=self.colour)
        self.unbind("<Key>")


class Sudoku(tk.Frame):
    """A class that contains a 9x9 grid of Cells for a classic Sudoku. Contains methods for getting regions of the grid
    and checking for duplicates"""
    def __init__(self, master, cellsize=50, fixednumbers=None, **kwargs):
        super().__init__(master, **kwargs)
        self.cellsize = cellsize
        self.cellFrame = tk.Frame(self, bg="black")
        if fixednumbers is None:
            self.cells = [[Cell(self.cellFrame, (x,y), size=cellsize) for y in range(9)] for x in range(9)]
        else:
            self.load(fixednumbers)
        for r, row in enumerate(self.cells):
            for c, cell in enumerate(row):
                if c % 3 == 0:
                    px = (3,0)
                elif c == 8:
                    px = (1,3)
                else:
                    px = (1,0)
                if r % 3 == 0:
                    py = (3,0)
                elif r == 8:
                    py = (1,3)
                else:
                    py = (1,0)
                cell.grid(row=r, column=c, padx=px, pady=py)
        self.mode = tk.StringVar()
        self.mode.set(NORMAL)
        self.mode.trace("w", lambda *a: self.change_mode(self.mode.get()))
        self.modebuttons = [tk.Radiobutton(self, variable=self.mode, value=MODES[n], text=MODES[n].title()) for n in range(4)]
        self.checkbutton = tk.Button(self, text="Check", command=lambda: print(self.check()))
        self.cellFrame.grid(row=0, column=1, rowspan=99)
        for i, m in enumerate(self.modebuttons):
            m.grid(row=i, column=2)
        self.checkbutton.grid(row=4, column=2)
        self.master.bind("<Key>", self.move_focus)

    def load(self, grid):
        """Load a Sudoku grid from a 2D list of numbers (None for an empty cell). The cell numbers loaded here are
        fixed, meaning they cannot be changed by the user"""
        for x, row in enumerate(grid):
            for y, num in enumerate(row):
                if num is not None:
                    c = self.cells[x][y]
                    c.number = num
                    c.fixed = True
                    c._refresh()

    def export(self):
        return [list(map(lambda c: c.number, r)) for r in self.cells]

    def get_row(self, row):
        """Get row n of the grid. Note that it starts at 0 on the left"""
        return self.cells[row]

    def get_column(self, col):
        """Get column n of the grid. Note that it starts at 0 on the left"""
        return [row[col] for row in self.cells]

    def get_box(self, box):
        """Get box n of the grid. Note that it starts at 0 in the top-left and down to 8 in the bottom right"""
        trans = [[0,1,2], [3,4,5], [6,7,8]]
        rows, columns = trans[box%3], trans[box//3]
        out = []
        for r in rows:
            for c in columns:
                out.append(self.cells[r][c])
        return out

    def check(self):
        """Check for and highlight any duplicate cells in regions"""
        for n in range(9):
            regions = [self.get_row(n), self.get_column(n), self.get_box(n)]
            for r in regions:
                duplicates = check_duplicates(r)
                if len(duplicates) != 0:
                    for cell in r:
                        if cell.number in duplicates:
                            cell.config(bg=RED)

    def change_mode(self, mode):
        """Change the global input mode for the grid"""
        for row in self.cells:
            for cell in row:
                cell.mode = mode

    def move_focus(self, event):
        """Use the arrow keys to move focus around the grid"""
        pos = self.focus_get().position
        key = event.keysym
        if key == "Up":
            pos = (pos[0] - 1) % 9, pos[1]
        elif key == "Down":
            pos = (pos[0] + 1) % 9, pos[1]
        elif key == "Left":
            pos = pos[0], (pos[1] - 1) % 9
        elif key == "Right":
            pos = pos[0], (pos[1] + 1) % 9
        self.cells[pos[0]][pos[1]].focus_set()
