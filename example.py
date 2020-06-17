import tkinter as tk
import sudoku


root = tk.Tk()
s = sudoku.Sudoku(root)
s.pack()

# Here I'm using 0's to indicate empty spaces to make it easier to read. This puzzle is from www.websudoku.com
grid = [[6,4,9,0,0,0,0,5,0],
        [0,0,0,0,0,4,8,0,0],
        [2,0,0,0,0,6,0,0,9],
        [0,0,4,0,0,7,0,0,5],
        [0,0,0,4,5,3,0,0,0],
        [3,0,0,8,0,0,9,0,0],
        [1,0,0,6,0,0,0,0,4],
        [0,0,8,2,0,0,0,0,0],
        [0,5,0,0,0,0,6,7,1]]

solved = [[6,4,9,1,2,8,3,5,7],
          [5,3,1,7,9,4,8,6,2],
          [2,8,7,5,3,6,4,1,9],
          [8,2,4,9,6,7,1,3,5],
          [9,1,6,4,3,5,7,2,8],
          [3,7,5,8,1,2,9,4,6],
          [1,9,3,6,7,5,2,8,4],
          [7,6,8,2,4,1,5,9,3],
          [4,5,2,3,8,9,6,7,1]]

# To load it, the 0's need to be replaced with None objects
grid = [[cell if cell != 0 else None for cell in row] for row in solved]

s.load(grid)
root.mainloop()
