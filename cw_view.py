# cw_view.py

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QPen
from app_settings import *

BUFFER = 0.9
SELECTED_OUTLINE = 0.08

class CW_View(QGraphicsView):
    cell_clicked = pyqtSignal(int, int)
    move_selected = pyqtSignal(int, int)

    def __init__(self, model):
        super().__init__()
        self.widget_width = int(WINDOW_W*2/3)
        self.setFixedWidth(self.widget_width)
        
        self.model = model
        
        self.grid_size = self.model.get_grid_size()
        self.cell_size = int(self.widget_width*BUFFER/self.grid_size)
        self.top_left = 0
        
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.draw()
        
    def draw(self):
        self.scene.clear()
        self.setStyleSheet("background: transparent; border: none;")
        grid = self.model.get_grid()
        selected = self.model.get_selected_cell()
        selected_word = self.model.get_cells_in_selected_word()
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if selected == (r, c): continue # do the selected one last, so layering is right
                
                # colour of cell
                if grid[r][c] == BLOCKED_CELL: colour = "black"
                elif (r, c) in selected_word: colour = "orange"
                else: colour = "white"
                
                x, y = c * self.cell_size, r * self.cell_size
                rect = QGraphicsRectItem(x, y, self.cell_size, self.cell_size)
                rect.setBrush(QBrush(QColor(colour)))
                rect.setPen(QPen(QColor("black")))
                rect.setData(0, (r, c))
                self.scene.addItem(rect)

        if selected:
            r, c = selected
            # colour of cell
            if grid[r][c] == BLOCKED_CELL: colour = "black"
            else: colour = "yellow"
            
            x, y = c * self.cell_size, r * self.cell_size
            rect = QGraphicsRectItem(x, y, self.cell_size, self.cell_size)
            rect.setBrush(QBrush(QColor(colour)))
            rect.setPen(QPen(QColor("blue"), self.cell_size*SELECTED_OUTLINE))
            rect.setData(0, selected)
            self.scene.addItem(rect)

    def rect_at(self, pos):
        item = self.itemAt(pos.toPoint())
        if isinstance(item, QGraphicsRectItem):
            return item.data(0)
        
        return (-1, -1)
            
