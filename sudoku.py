import tkinter as tk


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
    def __init__(self, master, position, size=50, bg="white", **kwargs):
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
        self.number = None
        self.bind("<1>", lambda e: self.focus_set())
        self.bind("<FocusIn>", self._focusin)
        self.bind("<FocusOut>", self._focusout)
        self._refresh()

    def add_corner_note(self, num):
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

    def add_centre_note(self, num):
        if num in self.centrenotes:
            self.remove_centre_note(num)
        else:
            self.centrenotes.append(num)
        self._refresh()

    def remove_centre_note(self, num):
        self.centrenotes.remove(num)
        self._refresh()

    def set_num(self, num):
        if self.number == num:
            self.number = None
        elif num in "123456789":
            self.number = num
        self._refresh()

    def set_colour(self, colour):
        self.colour = colour
        self.config(bg=self.colour)

    def set_mode(self, mode):
        self.mode = mode
        self._set_binds()

    def _refresh(self):
        self.delete(tk.ALL)
        if self.number is not None:
            self.create_text(*self.centre, text=str(self.number), font=("Arial", int(self.size*3/4)))
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
        if self.mode == NORMAL:
            self.bind("<Key>", lambda e: self.set_num(e.char))
        elif self.mode == CORNER:
            self.bind("<Key>", lambda e: self.add_corner_note(e.char))
        elif self.mode == CENTRE:
            self.bind("<Key>", lambda e: self.add_centre_note(e.char))
        elif self.mode == COLOUR:
            self.bind("<Key>", lambda e: self.set_colour(COLOURS[int(e.char) - 1]))


class Sudoku(tk.Frame):
    def __init__(self, master, cellsize=50, **kwargs):
        super().__init__(master, **kwargs)
        self.cellFrame = tk.Frame(self, bg="grey")
        self.cells = [[Cell(self.cellFrame, (x,y), size=cellsize) for y in range(9)] for x in range(9)]
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

    def change_mode(self, mode):
        for row in self.cells:
            for cell in row:
                cell.set_mode(mode)

    def move_focus(self, event):
        pos = self.focus_get().position
        key = event.keysym
        if key == "Up":
            pos = pos[0] - 1, pos[1]
        elif key == "Down":
            pos = pos[0] + 1, pos[1]
        elif key == "Left":
            pos = pos[0], pos[1] - 1
        elif key == "Right":
            pos = pos[0], pos[1] + 1
        self.cells[pos[0]][pos[1]].focus_set()


if __name__ == "__main__":
    root = tk.Tk()
    s = Sudoku(root)
    s.pack()
    root.mainloop()