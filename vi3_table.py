from curses import A_REVERSE
from vi3 import Color


class Column:
    def __init__(self, name, width, color=Color.WHITE):
        self.name = name
        self.width = width
        self.color = color


class Table:
    def __init__(self):
        self.selected_row_index = 0
        self.columns = []
        self.rows = []

    def paint(self, screen):
        for i, row in enumerate(self.rows):
            attr = 0

            if self.selected_row_index == i:
                attr |= A_REVERSE

            x = 0

            for column in self.columns:
                screen.addnstr(i, x, self.rows[i][column.name], column.width,
                               column.color | attr)
                x += column.width + 1
