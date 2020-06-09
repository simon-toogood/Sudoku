import tkinter as tk
import random


WHITE = "#ffffff"
RED = "#ffb5b5"
ORANGE = "#ffdeb5"
YELLOW = "#fff980"
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


class Cell(tk.Canvas):
    def __init__(self, master, position, fixed=None, size=50, bg="white", **kwargs):
        super().__init__(master, width=size, height=size, bg=bg, highlightthickness=0, **kwargs)
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

    def add_corner_note(self, event):
        if event.keysym == "BackSpace":
            self.cornernotes = []
            self._refresh()
            return
        num = event.char
        if num not in "123456789":
            return
        if num in self.cornernotes:
            self.remove_corner_note(num)
        elif len(self.cornernotes) == 8:
            raise ValueError("Corner cells full!")
        else:
            self.cornernotes.append(num)
        self._refresh()

    def remove_corner_note(self, num):
        self.cornernotes.remove(num)
        self._refresh()

    def add_centre_note(self, event):
        if event.keysym == "BackSpace":
            self.cornernotes = []
            self._refresh()
            return
        num = event.char
        if num not in "123456789":
            return
        if num in self.centrenotes:
            self.remove_centre_note(num)
        else:
            self.centrenotes.append(num)
        self._refresh()

    def remove_centre_note(self, num):
        self.centrenotes.remove(num)
        self._refresh()

    def set_num(self, event):
        num = event.char
        if self.number == num or event.keysym == "BackSpace":
            self.number = None
        elif num in "123456789":
            self.number = num
        self._refresh()

    def set_colour(self, event):
        if event.keysym == "BackSpace":
            self.colour = WHITE
            self._refresh()
            return
        if event.char in "123456789":
            self.colour = COLOURS[int(event.char) - 1]
        self._refresh()

    def set_mode(self, mode):
        self.mode = mode
        self._set_binds()

    def _refresh(self):
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
        self.config(bg="#fffcb5")
        self._set_binds()

    def _focusout(self, _):
        self.config(bg=self.colour)
        self.unbind("<Key>")

    def _set_binds(self):
        self.unbind("<Key>")
        if not self.fixed:
            if self.mode == NORMAL:
                self.bind("<Key>", self.set_num)
            elif self.mode == CORNER:
                self.bind("<Key>", self.add_corner_note)
            elif self.mode == CENTRE:
                self.bind("<Key>", self.add_centre_note)
        if self.mode == COLOUR:
            self.bind("<Key>", self.set_colour)


class Sudoku(tk.Frame):
    def __init__(self, master, cellsize=50, fixednumbers=None, **kwargs):
        super().__init__(master, **kwargs)
        self.cellsize = cellsize
        self.cellFrame = tk.Frame(self, bg="grey")
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
        self.cellFrame.grid(row=0, column=1, rowspan=99)
        for i, m in enumerate(self.modebuttons):
            m.grid(row=i, column=2)
        self.master.bind("<Key>", self.move_focus)

    def load(self, grid):
        for x, row in enumerate(grid):
            for y, num in enumerate(row):
                if num is not None:
                    c = self.cells[x][y]
                    c.number = num
                    c.fixed = True
                    c._refresh()

    def get_row(self, row):
        return self.cells[row]

    def get_column(self, col):
        return [row[col] for row in self.cells]

    def get_box(self, box):
        # what's a good way of doing this then?
        pass

    def change_mode(self, mode):
        for row in self.cells:
            for cell in row:
                cell.set_mode(mode)

    def move_focus(self, event):
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


if __name__ == "__main__":
    root = tk.Tk()
    s = Sudoku(root)
    s.pack()
    s.load([[random.choices(population=[None,1,2,3,4,5,6,7,8,9], weights=[20,1,1,1,1,1,1,1,1,1])[0] for x in range(9)] for y in range(9)])
    root.mainloop()
