import tkinter as tk
import sudoku


root = tk.Tk()
s = sudoku.Sudoku(root)
s.pack()

s.loadstr("...9.....85...4..9.7.8.2..3.9...7....25...16....1...2.4..6.9.8.6..5...41.....1...")
root.mainloop()
