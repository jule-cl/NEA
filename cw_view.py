# cw_view.py

from app_settings import App_settings
import sys
from PyQt5.QtWidgets import QMainWindow
from page_handler import Page_Handler
        
class CW_View(QMainWindow):    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.broadcast_destinations = []
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Crossword Generator")
        self.setGeometry(200, 200, 800, 600)
        
        self.page_handler = Page_Handler(self.controller)
        self.page_handler.setParent(self)
        self.broadcast_destinations.append(self.page_handler)
        
    def broadcast(self, message, info):
        for dest in self.broadcast_destinations:
            dest.handle_broadcast(message, info)
        
    def handle_broadcast(self, message, info):
        if message == App_settings.messages.GRID_SIZE_CHOSEN:
            self.broadcast(App_settings.messages.GRID_SIZE_CHOSEN, info)
            return

