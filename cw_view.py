# cw_view.py

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsSimpleTextItem
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QPen, QFont
from app_settings import *

BUFFER = 0.9
SELECTED_OUTLINE = 0.08
CLUE_NUMBER_BUFFER = 0.06
CLUE_NUMBER_SIZE = 0.25

class CW_View(QGraphicsView):
    cell_clicked = pyqtSignal(int, int)
    move_selected = pyqtSignal(int, int)

    def __init__(self, model):
        super().__init__()
        self.widget_width = int(WINDOW_W*2/3)
        self.widget_height = int(WINDOW_H*4/5)
        self.setFixedWidth(self.widget_width)
        self.setFixedHeight(self.widget_height)
        
        self.model = model
        
        self.grid_size = self.model.get_grid_size()
        self.cell_size = int(self.widget_width*BUFFER/self.grid_size)
        self.grid_left = (self.widget_width - self.grid_size * self.cell_size ) / 2
        self.grid_top = (self.widget_height - self.grid_size * self.cell_size ) / 2
        
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setSceneRect(self.rect().toRectF())
        
    def draw(self, editing_mode):
        self.scene.clear()
        self.setStyleSheet(f"background: transparent; border: none;")
        grid = self.model.get_grid()
        selected = self.model.get_selected_cell()
        selected_word = self.model.get_cells_in_selected_word()
        
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if selected == (r, c): continue # do the selected one last, so layering is right
                # colour of cell
                if grid[r][c] == BLOCKED_CELL: colour = Theme.BLOCKED_CELL
                elif editing_mode == CW_MODE.CLUES and (r, c) in selected_word: colour = Theme.SELECTED_WORD
                else: colour = Theme.CELL_BASE
                
                x, y = c * self.cell_size + self.grid_left, r * self.cell_size + self.grid_top
                rect = QGraphicsRectItem(x, y, self.cell_size, self.cell_size)
                rect.setBrush(QBrush(QColor(colour)))
                rect.setPen(QPen(QColor(Theme.BLOCKED_CELL)))
                rect.setData(0, (r, c))
                self.scene.addItem(rect)

        # if there is a selected cell..
        if selected:
            r, c = selected
            # colour of cell
            if grid[r][c] == BLOCKED_CELL: colour = Theme.BLOCKED_CELL
            elif editing_mode == CW_MODE.CLUES: colour = Theme.SELECTED_CELL
            else: colour = Theme.CELL_BASE
            
            x, y = c * self.cell_size + self.grid_left, r * self.cell_size + self.grid_top
            rect = QGraphicsRectItem(x, y, self.cell_size, self.cell_size)
            rect.setBrush(QBrush(QColor(colour)))
            rect.setPen(QPen(QColor(Theme.HIGHLIGHT), self.cell_size*SELECTED_OUTLINE))
            rect.setData(0, selected)
            self.scene.addItem(rect)
            
        # draw clue numbers
        numbered_cells = self.model.get_numbered_cells()
        for index, (row, col, direction) in enumerate(numbered_cells):
            x, y = (col+CLUE_NUMBER_BUFFER) * self.cell_size + self.grid_left, (row+CLUE_NUMBER_BUFFER) * self.cell_size + self.grid_top
            
            text_item = QGraphicsSimpleTextItem(str(index+1))
            text_item.setPos(x, y)
            text_item.setBrush(QColor("black"))  # Text color
            text_item.setFont(QFont("Arial", max(8, int(self.cell_size*CLUE_NUMBER_SIZE))))

            self.scene.addItem(text_item)
            

    def rect_at(self, pos):
        item = self.itemAt(pos.toPoint())
        if isinstance(item, QGraphicsRectItem):
            return item.data(0)
        
        return (-1, -1)
            
