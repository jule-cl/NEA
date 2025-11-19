# cw_controller.py

from PyQt6.QtCore import QObject, Qt, pyqtSignal
from app_settings import *

class CW_Controller(QObject):
    update_info = pyqtSignal()
    
    def __init__(self, model, view, editing_mode):
        super().__init__()
        self.model = model
        self.view = view
        
        self.editing_mode = editing_mode
        self.view.draw(self.editing_mode)

    def handle_mouse_clicked(self, scene_pos):
        row, col = self.view.rect_at(scene_pos)
        self.model.change_selection(row, col)
        
        if self.editing_mode == CW_MODE.LAYOUT and row != -1 and col != -1:
            self.model.toggle_blocked(row, col)
            
        self.draw()
        
    def handle_key_pressed(self, key):
        # arrows keys, for moving the selected cell
        if key == Qt.Key.Key_Up:
            self.__move_selected_cell(-1, 0)
        elif key == Qt.Key.Key_Down:
            self.__move_selected_cell(1, 0)
        elif key == Qt.Key.Key_Left:
            self.__move_selected_cell(0, -1)
        elif key == Qt.Key.Key_Right:
            self.__move_selected_cell(0, 1)
            
        if self.editing_mode == CW_MODE.CLUES:
            self.__type_letter(key)
        
    def __move_selected_cell(self, dr, dc):
        selected = self.model.get_selected_cell()
        if not selected: return
        
        grid_size = self.model.get_grid_size()
        new_row, new_col = selected[0]+dr, selected[1]+dc
        if not (0 <= new_row <= grid_size-1 and 0 <= new_col <= grid_size-1): return
        
        if dr==0: self.model.change_selection(new_row, new_col, "A")
        elif dc==0: self.model.change_selection(new_row, new_col, "D")
        self.draw()
        
    def __type_letter(self, key):
        if Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
            self.model.enter_letter(chr(key))
        self.draw()
    
    def generate_layout(self):
        if not self.model.is_grid_empty(): return False
        self.model.generate_layout()
        self.draw()
        
    def empty_grid(self):
        self.model.empty_grid()
        self.draw()
        
    def draw(self):
        self.view.draw(self.editing_mode)
        self.update_info.emit()
