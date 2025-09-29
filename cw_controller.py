# cw_controller.py

from cw_view import CW_View
from app_settings import App_settings

class CW_Controller:
    def __init__(self):
        self.view = CW_View(self)
        
        self.broadcast_destinations = [self.view]
        
    def show_window(self):
        self.view.show()
        
    def broadcast(self, message, info):
        for dest in self.broadcast_destinations:
            dest.handle_broadcast(message, info)
        
    def handle_broadcast(self, message, info):
        if message == App_settings.messages.GRID_SIZE_CHOSEN:
            self.broadcast(App_settings.messages.GRID_SIZE_CHOSEN, info)
            return
