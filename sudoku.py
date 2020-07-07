import tkinter as tk
import random
import datetime as dt
from helpers import *

BACK = "#122b42"
LINE = "#65727d"
TEXT = "#cccccc"
FIXED = "#5a97cc"
SELECT = "#648eb5"

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


class Position:
    def __init__(self, row, column):
        self.row = row
        self.column = column
        rtrans = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
        ctrans = {(0, 1, 2): (0, 3, 6), (3, 4, 5): (1, 4, 7), (6, 7, 8): (2, 5, 8)}
        for row in range(9):
            for column in range(9):
                for rt in rtrans:
                    if self.row in rt:
                        br = rt
                for ct, cv in ctrans.items():
                    if self.column in ct:
                        bc = cv
        self.box, = set(br) & set(bc)

    def __repr__(self):
        return f"r{self.row}c{self.column}b{self.box}"

    def dcopy(self):
        return Position(self.row, self.column)


class Cell(tk.Canvas):
    """A single Sudoku cell. Supports Snyder (corner) notes, centre notes and cell colouring. Can be cast to an int for
    comparison (eg. int(Cell)). A Cell can be fixed (value cannot be changed by the user) or it can be changed"""
    def __init__(self, master, row, column, fixed=None, size=50, bg=BACK):
        super().__init__(master, width=size, height=size, bg=bg, highlightthickness=0)
        self.position = Position(row, column)
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
        if self.number is not None:
            return f"<{self.number}>"
        else:
            return "< >"
    __str__ = __repr__

    def __int__(self):
        if self.number is None:
            return -1
        else:
            return int(self.number)

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
        elif event.char not in list("123456789") or event.char == "":
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
        if self.master.focus_get() == self and self.master.focus_get() is not None:
            self.config(bg=average_colours(SELECT, self.colour))
        else:
            self.config(bg=self.colour)
        if self.number is not None:
            if not self.fixed:
                textcolour = TEXT
            else:
                textcolour = FIXED
            self.create_text(*self.centre, text=str(self.number), font=("Helvetica Light", int(self.size*3/4)), fill=textcolour)
        else:
            for i, n in enumerate(self.cornernotes):
                self.create_text(*self.corners[i], text=str(n), font=("Helvetica Light", int(self.size*1/4)), fill=TEXT)
            self.create_text(*self.centre, text="".join(map(str, self.centrenotes)), fill=TEXT)

    def _focusin(self, _):
        """When the Cell has focus, highlight it and allow it to take keyboard input"""
        self.config(bg=average_colours(SELECT, self.colour))
        self.bind("<Key>", self._translate)

    def _focusout(self, _):
        """When the Cell loses focus, revert the colour to the original and disable keyboard input to the Cell"""
        self.config(bg=self.colour)
        self.unbind("<Key>")


class Sudoku(tk.Frame):
    """A class that contains a 9x9 grid of Cells for a classic Sudoku. Contains methods for getting regions of the grid
    and checking for duplicates"""
    def __init__(self, master, cellsize=50, **kwargs):
        super().__init__(master, bg=BACK, **kwargs)
        self.cellsize = cellsize
        self.cellFrame = tk.Frame(self, bg=LINE)
        self.cells = [[Cell(self.cellFrame, r, c, size=cellsize) for c in range(9)] for r in range(9)]
        for r, row in enumerate(self.cells):
            for c, cell in enumerate(row):
                if c % 3 == 0:
                    px = (3, 0)
                elif c == 8:
                    px = (1, 3)
                else:
                    px = (1, 0)
                if r % 3 == 0:
                    py = (3, 0)
                elif r == 8:
                    py = (1, 3)
                else:
                    py = (1, 0)
                cell.grid(row=r, column=c, padx=px, pady=py)
        self.mode = tk.StringVar()
        self.mode.set(NORMAL)
        self.mode.trace("w", lambda *a: self.change_mode(self.mode.get()))
        self.modebuttons = [tk.Radiobutton(self, variable=self.mode, value=MODES[n], text=MODES[n].title(), bg=BACK, fg=TEXT) for n in range(4)]
        self.checkbutton = tk.Button(self, text="Check", command=self.check, width=7)
        self.timeSinceStart = 0
        self.timer = tk.Label(self, text="00:00", font=("Monospace", 24), bg=BACK, fg=TEXT)
        self.after(1000, self.increment_time)
        self.cellFrame.grid(row=0, column=0, rowspan=99)
        self.timer.grid(row=0, column=1, pady=10)
        for i, m in enumerate(self.modebuttons, start=1):
            m.grid(row=i, column=1)
        self.checkbutton.grid(row=5, column=1, pady=15)
        self.master.bind("<Key>", self.move_focus)
        self.master.bind("<space>", lambda e: self.change_mode())

    def loadarr(self, grid, empty="."):
        """Load a Sudoku grid from a 2D list of numbers (None for an empty cell). The cell numbers loaded here are
        fixed, meaning they cannot be changed by the user"""
        for x, row in enumerate(grid):
            for y, num in enumerate(row):
                if num != empty:
                    c = self.cells[x][y]
                    c.number = num
                    c.fixed = True
                    c._refresh()

    def loadstr(self, string, empty="."):
        """Load a Sudoku grid from a single input string of length 81. The cell numbers loaded here are
        fixed, meaning they cannot be changed by the user"""
        l = iter(list(string))
        for x in range(9):
            for y in range(9):
                v = next(l)
                c = self.cells[x][y]
                if v != empty:
                    c.number = v
                    c.fixed = True
                    c._refresh()

    def export(self):
        """Export the current state of the grid as an array of numbers"""
        return [list(map(lambda c: c.number, r)) for r in self.cells]

    def rows(self, values=False):
        if values:
            yield from [[c.number for c in r] for r in self.rows()]
        else:
            yield from self.cells

    def get_row(self, row, values=False):
        return list(self.rows(values=values))[row]

    def columns(self, values=False):
        columns = list(zip(*self.cells))
        if values:
            yield from [[c.number for c in r] for r in self.columns()]
        else:
            yield from columns

    def get_column(self, column, values=False):
        return list(list(self.columns(values=values))[column])

    def boxes(self, values=False):
        for box in range(9):
            out = []
            for row in self.cells:
                for cell in row:
                    if cell.position.box == box:
                        if values:
                            out.append(cell.number)
                        else:
                            out.append(cell)
            yield out

    def get_box(self, box, values=False):
        return list(self.boxes(values=values))[box]

    def find(self, position):
        return self.cells[position.row][position.column]

    def increment_time(self):
        self.timeSinceStart += 1
        hms = (self.timeSinceStart//3600 % 60, self.timeSinceStart//60 % 60, self.timeSinceStart%60)
        if hms[0] == 0:
            self.timer.config(text="{:02}:{:02}".format(hms[1], hms[2]))
        else:
            self.timer.config(text="{}:{:02}:{:02}".format(*hms))
        self.after(1000, self.increment_time)

    def check(self):
        """Check for and highlight any duplicate cells in regions"""
        for n in range(9):
            regions = [self.get_row(n), self.get_column(n), self.get_box(n)]
            for r in regions:
                duplicates = check_duplicates(r)
                if len(duplicates) != 0:
                    for cell in r:
                        if cell.number in duplicates or cell.number is None:
                            cell.config(bg=RED)

    def change_mode(self, mode=None):
        """Change the global input mode for the grid. If a mode is not specified, then cycle to the next mode"""
        if mode is None:
            new = MODES[(MODES.index(self.mode.get()) + 1) % len(MODES)]
            self.change_mode(new)
        else:
            self.mode.set(mode)
            for row in self.cells:
                for cell in row:
                    cell.mode = mode

    def move_focus(self, event):
        """Use the arrow keys to move focus around the grid"""
        pos = self.focus_get().position.dcopy()
        key = event.keysym
        if key == "Up":
            pos.row = (pos.row - 1) % 9
        elif key == "Down":
            pos.row = (pos.row + 1) % 9
        elif key == "Left":
            pos.column = (pos.column - 1) % 9
        elif key == "Right":
            pos.column = (pos.column + 1) % 9
        self.find(pos).focus_set()

