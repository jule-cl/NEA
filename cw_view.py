# cw_view.py

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QStackedWidget, QGridLayout, QHBoxLayout,
                            QVBoxLayout, QLabel, QPushButton, QLineEdit)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

FRAMERATE = 60

# colours
BLACK = "#453245"
WHITE = "#e5fff6"
        
class CW_View(QMainWindow):    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Crossword Generator")
        self.setGeometry(200, 200, 700, 800)
        
        # self.page_handler = Page_Handler()
           
class Page_Handler(QStackedWidget): 
    def __init__(self):
        super().__init__()
        self.setup_pages()
    
    def setup_pages(self):
        self.pages = {"Grid": Grid_Size_Page()}
        
        # create pages
        self.pages = {
            "Grid size": Grid_Size_Page()
        }
        # add to stacked widget
        for page in self.pages.values():
            page.setParent(self)  # let pages call parent()
            self.addWidget(page)

        self.page_indices = {name: i for i, name in enumerate(self.pages.keys())}
        self.switch_page("Grid size")
        
        self.update_all()
        
    def update_all(self):
        for page in self.pages.values():
            page.update_display()
    
    def goto_page(self, page_name):
        try:
            self.setCurrentIndex(self.pages[page_name])
        except KeyError:
            raise Exception("Page doesn't exist")
            
class Grid_Size_Page(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        overall_layout = QVBoxLayout(self)
        
        # explainatory text 
        text = QLabel("Choose a board size:")
        overall_layout.addWidget(text)
        
    def update_display(self):
        pass
            
class CrosswordCell(QPushButton):
    """A single cell in the crossword grid"""
    cell_clicked = pyqtSignal(int, int)  # row, col
    
    def __init__(self, row, col, is_blocked=False):
        super().__init__()
        self.row = row
        self.col = col
        self.is_blocked = is_blocked
        self.letter = ""
        
        self.setup_cell()
        self.clicked.connect(self.on_clicked)
    
    def setup_cell(self):
        # Set fixed size for square cells
        self.setFixedSize(40, 40)
        
        # Set font
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.setFont(font)
        
        if self.is_blocked:
            # Black cell (blocked)
            self.setStyleSheet("""
                QPushButton {
                    background-color: black;
                    border: 1px solid #333;
                }
            """)
            self.setEnabled(False)
        else:
            # White cell (can contain letters)
            self.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: 1px solid black;
                    color: black;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
                QPushButton:pressed {
                    background-color: #e0e0e0;
                }
            """)
    
    def set_letter(self, letter):
        """Set the letter in this cell"""
        if not self.is_blocked:
            self.letter = letter.upper()
            self.setText(self.letter)
    
    def get_letter(self):
        """Get the letter in this cell"""
        return self.letter
    
    def clear_letter(self):
        """Clear the letter from this cell"""
        self.letter = ""
        self.setText("")
    
    def on_clicked(self):
        """Handle cell click"""
        if not self.is_blocked:
            self.cell_clicked.emit(self.row, self.col)

class CrosswordGrid(QWidget):
    """The main crossword grid widget"""
    cell_selected = pyqtSignal(int, int, str)  # row, col, current_letter
    
    def __init__(self, rows=15, cols=15):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.cells = {}  # Dictionary to store cells by (row, col)
        self.selected_cell = None
        
        self.setup_grid()
    
    def setup_grid(self):
        """Create the grid layout and cells"""
        layout = QGridLayout()
        layout.setSpacing(0)  # No space between cells
        
        # Example pattern - you can modify this to create your crossword pattern
        blocked_cells = {}
        
        for row in range(self.rows):
            for col in range(self.cols):
                is_blocked = (row, col) in blocked_cells
                cell = CrosswordCell(row, col, is_blocked)
                cell.cell_clicked.connect(self.on_cell_clicked)
                
                self.cells[(row, col)] = cell
                layout.addWidget(cell, row, col)
        
        self.setLayout(layout)
        
    def on_cell_clicked(self, row, col):
        """Handle when a cell is clicked"""
        # Highlight the selected cell
        if self.selected_cell:
            self.selected_cell.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: 1px solid black;
                    color: black;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)
        
        cell = self.cells[(row, col)]
        self.selected_cell = cell
        
        # Highlight selected cell
        cell.setStyleSheet("""
            QPushButton {
                background-color: #87CEEB;
                border: 2px solid #4169E1;
                color: black;
            }
        """)
        
        # Emit signal with cell info
        self.cell_selected.emit(row, col, cell.get_letter())
    
    def set_cell_letter(self, row, col, letter):
        """Set letter in a specific cell"""
        if (row, col) in self.cells:
            self.cells[(row, col)].set_letter(letter)
    
    def get_cell_letter(self, row, col):
        """Get letter from a specific cell"""
        if (row, col) in self.cells:
            return self.cells[(row, col)].get_letter()
        return ""
    
    def clear_grid(self):
        """Clear all letters from the grid"""
        for cell in self.cells.values():
            cell.clear_letter()

# just to make dealing with coordinates easier   
class Coord:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        

