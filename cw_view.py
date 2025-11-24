# cw_view.py

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsSimpleTextItem
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QPen, QFont
from app_settings import *

class CW_View(QGraphicsView):
    def __init__(self, model):
        super().__init__()
        self.__widget_width = int(WINDOW_W*0.6)
        self.__widget_height = int(WINDOW_H*0.8)
        self.setFixedWidth(self.__widget_width)
        self.setFixedHeight(self.__widget_height)
        
        self.model = model
        
        self.grid_size = self.model.get_grid_size()
        self.cell_size = int(min(self.__widget_width, self.__widget_height)*BUFFER/self.grid_size)
        self.grid_left = (self.__widget_width - self.grid_size * self.cell_size) / 2
        self.grid_top = (self.__widget_height - self.grid_size * self.cell_size) / 2
        
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setSceneRect(self.rect().toRectF())
        
    def draw(self, editing_mode):
        self.scene.clear()
        self.setStyleSheet(f"background: transparent; border: none;")
        grid = self.model.get_grid()
        selected_cell = self.model.get_selected_cell()
        selected_word = self.model.get_cells_in_selected_word()
        
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                # colour of cell
                colour = Theme.CELL_BASE
                if grid[r][c] == BLOCKED_CELL: colour = Theme.BLOCKED_CELL
                elif editing_mode == CW_MODE.CLUES:
                    if (r, c) == selected_cell: colour = Theme.SELECTED_CELL
                    elif (r, c) in selected_word: colour = Theme.SELECTED_WORD
                    
                x, y = c * self.cell_size + self.grid_left, r * self.cell_size + self.grid_top
                
                # draw cell
                rect = QGraphicsRectItem(x, y, self.cell_size, self.cell_size)
                rect.setBrush(QBrush(QColor(colour)))
                if (r, c) == selected_cell: rect.setPen(QPen(QColor(Theme.HIGHLIGHT), self.cell_size*SELECTED_OUTLINE))
                else: rect.setPen(QPen(QColor(Theme.BLOCKED_CELL)))
                rect.setData(0, (r, c))
                if (r, c) == selected_cell: rect.setZValue(100) # move selected to top
                self.scene.addItem(rect)
                
                # draw letter in cell (if present)
                if not(grid[r][c] == BLOCKED_CELL or grid[r][c] == EMPTY_CELL): 
                    letter = QGraphicsSimpleTextItem(grid[r][c].upper())
                    letter.setFont(QFont(TEXT_FONT, int(self.cell_size*CLUE_LETTER_SIZE)))
                    letter.setBrush(QColor(Theme.FOREGROUND))
                    bounding_rect = letter.boundingRect()
                    letter.setPos(x + self.cell_size/2 - bounding_rect.width()/2, y + self.cell_size/2 - bounding_rect.height()/2)
                    if (r, c) == selected_cell: letter.setZValue(100) # move selected to top
                    self.scene.addItem(letter)

        # draw clue numbers
        numbered_cells = self.model.get_numbered_cells()
        for index, (row, col, _) in enumerate(numbered_cells):
            x, y = (col+CLUE_NUMBER_BUFFER) * self.cell_size + self.grid_left, (row+CLUE_NUMBER_BUFFER) * self.cell_size + self.grid_top
            
            number = QGraphicsSimpleTextItem(str(index+1))
            number.setBrush(QColor(Theme.FOREGROUND))
            number.setFont(QFont(TEXT_FONT, max(10, int(self.cell_size*CLUE_NUMBER_SIZE))))
            number.setPos(x, y)

            if (row, col) == selected_cell: 
                number.setZValue(100)
            self.scene.addItem(number)
            

    def rect_at(self, pos):
        item_list = self.items(pos.toPoint()) # need to get all items, in case clicked on the number
        if not item_list: return (-1, -1)
        
        if isinstance(item_list[-1], QGraphicsRectItem):
            return item_list[-1].data(0)
        
        return (-1, -1)
            
