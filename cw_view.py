# cw_view.py

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsSimpleTextItem
from PyQt6.QtGui import QBrush, QColor, QPen, QFont
from app_info import *

class CW_View(QGraphicsView):
    """
    Renders the crossword grid as a PyQt6 graphics view, drawing cells, letters, and clue numbers based on the current model state.

    Variables:
        model (CW_Model): The crossword model this view reads from.
        grid_size (int): The size of the grid being rendered.
        cell_size (int): The pixel size of each cell.
        grid_left (float): The x offset to center the grid horizontally in the widget.
        grid_top (float): The y offset to center the grid vertically in the widget.
        scene (QGraphicsScene): The scene used to render all grid items.

    Methods:
        draw: Clears and redraws the entire grid based on current model state.
        rect_at: Returns the grid coordinates of the cell at a given widget position.
    """
    def __init__(self, model):
        """
        Initialises the view with the given model, setting up the scene.

        Args:
            model (CW_Model): The crossword model to render.
        """
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
        
    def draw(self, editing_mode, errors=None):
        """
        Clears and redraws the entire grid, including cell colours, letters, and clue numbers. 
        The cell colour is decided by whether the cell is blocked, selected, or part of the selected word, depending on the editing mode.

        Args:
            editing_mode (CW_MODE): The current editing mode, either LAYOUT or CLUES.
            errors (dict or None): displaying any errors on the grid layout, if any. Used in the grid layout generation stage.
        """
        self.scene.clear()
        self.setStyleSheet(f"background: transparent; border: none;")
        grid = self.model.get_grid()
        selected_cell = self.model.get_selected_cell()
        cells_in_selected_clue = self.model.get_cells_in_selected_clue()
        
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                # set colour of cell
                colour = Theme.CELL_BASE
                if grid[r][c] == BLOCKED_CELL: colour = Theme.BLOCKED_CELL
                elif editing_mode == CW_MODE.CLUES:
                    if (r, c) == selected_cell: colour = Theme.SELECTED_CELL
                    elif (r, c) in cells_in_selected_clue: colour = Theme.SELECTED_WORD
                    
                # draw cell
                x, y = c * self.cell_size + self.grid_left, r * self.cell_size + self.grid_top
                rect = QGraphicsRectItem(x, y, self.cell_size, self.cell_size)
                rect.setBrush(QBrush(QColor(colour)))
                if (r, c) == selected_cell: rect.setPen(QPen(QColor(Theme.HIGHLIGHT), self.cell_size*SELECTED_OUTLINE))
                else: rect.setPen(QPen(QColor(Theme.BLOCKED_CELL), CELL_BORDER_WIDTH))
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
            
        # draw errors
        if errors:
            for r, c in [cell for _ in errors.values() for cell in _]:
                x, y = c * self.cell_size + self.grid_left, r * self.cell_size + self.grid_top
                rect = QGraphicsRectItem(x, y, self.cell_size, self.cell_size)
                rect.setBrush(QBrush(QColor(Theme.ERROR_COLOUR)))
                rect.setPen(QPen(QColor(Theme.ERROR_HIGHLIGHT), self.cell_size*SELECTED_OUTLINE))
                rect.setData(0, (r, c))
                rect.setZValue(200)
                self.scene.addItem(rect)
                
                # draw '!'
                symbol = QGraphicsSimpleTextItem('!')
                symbol.setFont(QFont(TEXT_FONT, int(self.cell_size*CLUE_LETTER_SIZE)))
                symbol.setBrush(QColor(Theme.ERROR_HIGHLIGHT))
                bounding_rect = symbol.boundingRect()
                symbol.setPos(x + self.cell_size/2 - bounding_rect.width()/2, y + self.cell_size/2 - bounding_rect.height()/2)
                symbol.setZValue(200) # move selected to top
                self.scene.addItem(symbol)

    def rect_at(self, pos):
        """
        Returns the grid coordinates of the cell at the given widget position.
        Returns (-1, -1) if no cell exists at that position.

        Args:
            pos (QPointF): The position in screen coordinates.

        Returns:
            tuple[int, int]: The (row, col) of the cell at the position, or (-1, -1) if no cell was found.
        """
        item_list = self.items(pos.toPoint()) # get all items, in case it found the number
        if not item_list: return (-1, -1)
        
        if isinstance(item_list[-1], QGraphicsRectItem):
            return item_list[-1].data(0)
        
        return (-1, -1)    
