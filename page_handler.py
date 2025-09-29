# page_handler.py

from app_settings import App_settings
import sys
from PyQt5.QtWidgets import QStackedWidget

from pages import *

class Page_Handler(QStackedWidget): 
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_pages()
    
    def setup_pages(self):
        self.page_indices = {
            "Grid size": 0,
            "Editing": 1
        }
        
        # create pages
        self.pages = {
            "Grid size": Grid_Size_Page(self.controller),
            "Editing": Editing_Page(self.controller)
        }
        
        # add to stacked widget, and get the order
        for page in self.pages.values():
            page.setParent(self)  # let pages call parent()
            self.addWidget(page)
        
        self.__goto_page("Grid size")
        self.update_all()
        
    def broadcast(self, message, info):
        for dest in self.broadcast_destinations:
            dest.handle_broadcast(message, info)
        
    def handle_broadcast(self, message, info):
        if message == App_settings.messages.GRID_SIZE_CHOSEN:
            self.__goto_page("Editing")
            return

    def update_all(self):
        for page in self.pages.values():
            page.update_ui()
    
    def __goto_page(self, page_name):
        try:
            self.setCurrentIndex(self.page_indices[page_name])
        except KeyError:
            raise Exception("Page doesn't exist")
        
