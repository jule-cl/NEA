# cw_controller.py

import pygame
from pygame.locals import *
import threading

class CW_Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.running = True
        
    def process_input(self):
        # pygame event queue
        for event in pygame.event.get():
            if event.type == QUIT: self.running = False
