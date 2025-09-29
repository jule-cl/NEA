# pages.py

from app_settings import App_settings
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from abc import abstractmethod
from crossword_elements import Crossword_Grid

class Page(QWidget):
    def __init__(self, page_handler):
        super().__init__()
        
        self.page_handler = page_handler
        self.broadcast_destinations = [self.page_handler]
        
    @abstractmethod
    def setup_ui():
        pass
    
    @abstractmethod
    def update_ui():
        pass
    
    def broadcast(self, message, info):
        for dest in self.broadcast_destinations:
            dest.handle_broadcast(message, info)

class Grid_Size_Page(Page):
    def __init__(self, page_handler):
        super().__init__(page_handler)
        self.setup_ui()
        
    def setup_ui(self):
        overall_layout = QVBoxLayout(self)
        
        # explainatory text 
        text = QLabel("Choose a board size:")
        overall_layout.addWidget(text)
        
        # option buttons
        buttons = []
        for size in App_settings.grid_sizes:
            new_button = QPushButton(f"Grid size {size}")
            new_button.clicked.connect(self.grid_size_chosen(size))
            buttons.append(new_button)
        
        button_layout = QHBoxLayout()
        for button in buttons:
            button_layout.addWidget(button)
        overall_layout.addLayout(button_layout)
            
    def grid_size_chosen(self, size):
        def return_func():
            self.broadcast(App_settings.messages.GRID_SIZE_CHOSEN, size)
            # print(f"Size chosen: {size}")
        return return_func
    
    def update_ui(self):
        pass
     
class Editing_Page(Page):
    def __init__(self, page_handler):
        super().__init__(page_handler)
        self.setup_ui()
        
    def setup_ui(self):
        overall_layout = QVBoxLayout(self)
        
        # text
        buttons = []
        button_layout = QVBoxLayout()
        print_grid = QPushButton("Print grid")
        clear_grid = QPushButton("Clear grid")
        generate_layout = QPushButton("Generate layout")
        buttons = [print_grid, clear_grid, generate_layout]
        
        for b in buttons:
            button_layout.addWidget(b)
        
        overall_layout.addLayout(button_layout)

    def update_ui(self):
        pass
    
