# cw_controller.py

from PyQt6.QtCore import QObject, Qt, pyqtSignal
from widgets_custom import WarningBox
from app_info import *

class CW_Controller(QObject):
    """
    Acts as the controller in the MVC pattern, handling user input and coordinating updates between the crossword model and view.

    Variables:
        model (CW_Model): The crossword model this controller operates on.
        view (CW_View): The view this controller updates after each action.
        editing_mode (CW_MODE): The current editing mode, either LAYOUT or CLUES.
        parent_screen (QWidget): The parent screen widget, used to retrieve UI state such as symmetry.

    Methods:
        handle_mouse_clicked: Processes a mouse click on the grid.
        handle_key_pressed: Processes a key press event.
        is_grid_empty: Returns whether the grid is completely empty.
        is_grid_clear: Returns whether the grid contains no letters.
        generate_layout: Generates a blocked cell layout on an empty grid.
        autofill: Fills the grid with words using the autofill algorithm.
        empty_grid: Clears all cells including blocked cells.
        clear_grid: Removes all letters while preserving blocked cells.
        get_all_clues: Returns all clues in the crossword.
        get_selected_clue: Returns the currently selected clue.
        draw: Redraws the view and emits the update_info signal.
    """
    update_info = pyqtSignal()
    
    def __init__(self, model, view, editing_mode, parent_screen):
        """
        Initialises the controller with the given model, view, editing mode and parent screen.

        Args:
            model (CW_Model): The crossword model to control.
            view (CW_View): The view to update after each action.
            editing_mode (CW_MODE): The initial editing mode, either LAYOUT or CLUES.
            parent_screen (QWidget): The parent screen, used to access UI state such as symmetry.
        """
        super().__init__()
        self.model = model
        self.view = view
        
        self.editing_mode = editing_mode
        self.view.draw(self.editing_mode)
        
        self.parent_screen = parent_screen

    def handle_mouse_clicked(self, scene_pos):
        """
        Handles a mouse click on the grid.
        If in LAYOUT mode, toggles the clicked cell between blocked and empty with symmetry applied.

        Args:
            scene_pos (QPointF): The position of the click in scene coordinates.
        """
        row, col = self.view.rect_at(scene_pos)
        self.model.change_selection(row, col)
        
        if self.editing_mode == CW_MODE.LAYOUT and row != -1 and col != -1:
            symmetry = self.parent_screen.get_symmetry()
            self.model.flip_blocked_symmetry(row, col, symmetry)
            
        self.draw()
        
    def handle_key_pressed(self, key):
        """
        Handles a key press event. 
        Arrow keys move the selected cell, and letter or backspace keys type into the grid when in CLUES mode.

        Args:
            key (int): The Qt key code of the pressed key.
        """
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
        """
        Moves the selected cell by the given row and column offsets, clamping to grid bounds.
        Updates the selection direction based on the axis of movement.

        Args:
            dr (int): Row offset to move by (-1, 0, or 1).
            dc (int): Column offset to move by (-1, 0, or 1).
        """
        selected = self.model.get_selected_cell()
        if not selected: return
        
        grid_size = self.model.get_grid_size()
        new_row, new_col = selected[0]+dr, selected[1]+dc
        if not (0 <= new_row <= grid_size-1 and 0 <= new_col <= grid_size-1): return
        
        if dr==0: self.model.change_selection(new_row, new_col, "A")
        elif dc==0: self.model.change_selection(new_row, new_col, "D")
        self.draw()
        
    def __type_letter(self, key):
        """
        Enters a letter into the currently selected cell, or clears it on backspace.

        Args:
            key (int): The Qt key code of the pressed key.
        """
        if Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
            self.model.enter_letter(chr(key))
        if key == Qt.Key.Key_Backspace:
            self.model.enter_letter(EMPTY_CELL)
        self.draw()
    
    def is_grid_empty(self):
        """
        Returns whether the grid is completely empty (no letters or blocked cells).

        Returns:
            bool: True if the grid is empty, False otherwise.
        """
        return self.model.is_grid_empty()
    
    def is_grid_clear(self):
        """
        Returns whether the grid contains no letters (only empty or blocked cells).

        Returns:
            bool: True if the grid is clear, False otherwise.
        """
        return self.model.is_grid_clear()
    
    def generate_layout(self, target_ratio, seed, symmetry):
        """
        Generates a blocked cell layout on the grid if it is currently empty.
        Does nothing and returns False if the grid isn't empty.

        Args:
            target_ratio (float): The desired ratio of blocked cells to total cells.
            seed (int): Random seed for reproducible layout generation.
            symmetry (int): Symmetry mode to apply when placing blocked cells.
        """
        if not self.is_grid_empty(): return False
        self.model.generate_layout(target_ratio, seed, symmetry)
        self.draw()
        
    def autofill(self, constraint):
        """
        Fills the grid with words using the autofill algorithm.
        Raises an exception if the grid is not clear before filling.

        Args:
            constraint (int): The maximum number of attempts per clue before backtracking.
        """
        if not self.model.is_grid_clear(): raise Exception("The grid isn't clear")
        self.model.autofill(constraint)
        self.draw()
        
    def empty_grid(self):
        """
        Clears all cells in the grid including blocked cells, resetting it to fully empty.
        """
        warning = WarningBox("Are you sure? This will set all cells in the grid to empty and cannot be undone.")
        if warning.clickedButton() == warning.reject_button: return
        self.model.empty_grid()
        self.draw()
        
    def clear_grid(self):
        """
        Removes all letters from the grid while preserving blocked cells.
        """
        warning = WarningBox("Are you sure? This will remove all letters in the grid and cannot be undone.")
        if warning.clickedButton() == warning.reject_button: return
        self.model.clear_grid()
        self.draw()
      
    def get_errors(self):
        """
        Method used during editing the layout to display errors, if any
        """
        return self.model.get_errors()
      
    def get_all_clues(self):
        """
        Returns all clues in the crossword.

        Returns:
            list[CW_Clue]: List of all clues.
        """
        return self.model.get_all_clues()
        
    def get_selected_clue(self):
        """
        Returns the currently selected clue based on the selected cell and direction.

        Returns:
            CW_Clue: The currently selected clue, or None if no clue is selected.
        """
        return self.model.get_selected_clue()
        
    def draw(self):
        """
        Redraws the view in the current editing mode and emits the update_info signal to notify the info panel to refresh.
        """
        self.view.draw(self.editing_mode)
        self.update_info.emit()
