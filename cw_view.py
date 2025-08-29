# cw_view.py

import pygame
from pygame.locals import *

FRAMERATE = 60

# colours
BLACK = "#453245"
WHITE = "#e5fff6"

class CW_View:
    
    BG_COLOUR = WHITE
    BORDER_COLOUR = BLACK
    GRID_CELL_COLOUR = WHITE
    
    def __init__(self, model):
        # a reference to the model, keeping track of the information and knowing what to display
        self.model = model
        model.register_listener(self.model_event)
        
        # window properties
        self.__window_width = 1366
        self.__window_height = 768
        self.__window_size = (self.__window_width, self.__window_height)
        self.__window_title = "Crossword editor"

        # initialize pygame and window
        pygame.init()
        self.window = pygame.display.set_mode(self.__window_size)
        pygame.display.set_caption(self.__window_title)
        self.clock = pygame.time.Clock()
        
        self.game_surf = pygame.Surface(self.__window_size)
        self.game_surf.set_colorkey(BLACK)
        
        self.__text_font = pygame.font.Font("Hack-Regular.ttf", 24)
        
    """
    DRAWING METHODS
    """
    def __draw_grid(self, center, grid_side_length):
        grid = self.model.get_grid()
        grid_size = self.model.get_grid_size()
        
        square_side_length = grid_side_length/grid_size
        grid_left = center.x - grid_side_length//2
        grid_right = center.x + grid_side_length//2
        grid_top = center.y - grid_side_length//2
        grid_bottom = center.y + grid_side_length//2
        
        for row in range(grid_size):
            for col in range(grid_size):
                letter = grid[row][col]
                
                # draw squares
                rect_obj = pygame.Rect(0, 0, square_side_length, square_side_length)
                rect_obj.centerx = (col-(grid_size-1)/2) * square_side_length + center.x
                rect_obj.centery = (row-(grid_size-1)/2) * square_side_length + center.y
                
                if letter == '-':
                    # draw blocked cell (skip the next parts)
                    pygame.draw.rect(self.game_surf, self.BORDER_COLOUR, rect_obj)
                    continue
                if letter == '.':
                    # doesn't draw anything
                    continue
                else:
                    pygame.draw.rect(self.game_surf, self.GRID_CELL_COLOUR, rect_obj)
                                   
                # draw letters
                text = self.__text_font.render(letter, True, BLACK)
                text_rect = text.get_rect(center=rect_obj.center)
                self.game_surf.blit(text, text_rect)
                
        # draw borders
        for col in range(grid_size+1):
            line_x = (grid_right - grid_left) * col/grid_size + grid_left
            pygame.draw.line(self.game_surf, self.BORDER_COLOUR, (line_x, grid_top), (line_x, grid_bottom), width=4)
        for row in range(grid_size+1):
            line_y = (grid_bottom - grid_top) * row/grid_size + grid_top
            pygame.draw.line(self.game_surf, self.BORDER_COLOUR, (grid_left, line_y), (grid_right, line_y), width=4)
        
    def draw_screen(self):
        self.game_surf.fill(self.BG_COLOUR)
        
        self.__draw_grid(Coord(self.__window_width//2, self.__window_height//2), 400)
        
        self.window.blit(self.game_surf, (0, 0))
        pygame.display.flip()
        
    # model calls this function when an event happpens (even when the event isn't for the view)
    def model_event(self, event):
        if event.message == "DRAW":
            self.draw_game()
     
# just to make dealing with coordinates easier   
class Coord:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        

