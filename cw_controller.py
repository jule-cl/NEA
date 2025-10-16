# cw_controller.py

from PyQt6.QtCore import QObject, Qt

class CW_Controller(QObject):
    def __init__(self, model, view):
        super().__init__()
        self.model = model
        self.view = view

    def handle_mouse_clicked(self, scene_pos):
        row, col = self.view.rect_at(scene_pos)
        self.model.change_selection(row, col)
        self.view.draw()
        
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
        
    def __move_selected_cell(self, dr, dc):
        selected = self.model.get_selected_cell()
        if not selected: return
        
        grid_size = self.model.get_grid_size()
        new_row, new_col = selected[0]+dr, selected[1]+dc
        if not (0 <= new_row <= grid_size-1 and 0 <= new_col <= grid_size-1): return
        
        if dr==0: self.model.change_selection(new_row, new_col, "A")
        elif dc==0: self.model.change_selection(new_row, new_col, "D")
        self.view.draw()
