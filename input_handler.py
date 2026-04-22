"""input_handler.py — Decoupled input polling with event buffer"""
import pygame

class InputHandler:
    def __init__(self):
        self.key_buffer  = []   # keydown + mouse events this frame
        self.prev_state  = None
        self.curr_state  = None

    def poll(self):
        """Call once per frame before processing input."""
        self.key_buffer = []
        self.prev_state = self.curr_state
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.key_buffer.append(event)
        self.curr_state = pygame.key.get_pressed()
        return True

    def is_pressed(self, key):
        """True only on the frame the key was first pressed."""
        return any(
            e.type == pygame.KEYDOWN and e.key == key
            for e in self.key_buffer
        )

    def is_held(self, key):
        if self.curr_state:
            return bool(self.curr_state[key])
        return False

    @property
    def events(self):
        return self.key_buffer

    @property
    def events(self):
        return self.key_buffer
