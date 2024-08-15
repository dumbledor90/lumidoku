import pygame
import sudoku_board


class Game:

    _PALETTE = {
        'white': (250, 250, 250),
        'beige': (248, 237, 237),
        'black': (20, 20, 20),
        'grey': (200, 200, 200),
        'grey': (100, 100, 100),
        'red': (150, 0, 0),
        'green': (0, 150, 0),
    }

    _SCREEN_WIDTH, _SCREEN_HEIGHT = 1280, 720
    _BUTTON_WIDTH, _BUTTON_HEIGHT = 400, 75
    _BUTTON_GAP = 10

    def __init__(self):
        
        pygame.init()

        self.screen = pygame.display.set_mode((self._SCREEN_WIDTH, self._SCREEN_HEIGHT))

        self._board = sudoku_board.Board(
            (self._SCREEN_WIDTH, self._SCREEN_HEIGHT),
            cell_size=70, small_gap=2, big_gap=6,
        )
        
        self._LARGE_FONT = pygame.font.SysFont(None, 60)
        self._SMALL_FONT = pygame.font.SysFont(None, 40)

        self._left_align = (self._SCREEN_WIDTH + self._SCREEN_HEIGHT - self._BUTTON_WIDTH) // 2
        self._button_vertical_spacing = self._BUTTON_HEIGHT + self._BUTTON_GAP
        self._bottom_align = self._SCREEN_HEIGHT - self._board._PADDING
        self._message_vertical_spacing = self._BUTTON_HEIGHT / 2

        # Register rects for buttons, to check for mouse input later
        self._button_rects = []

        for i in range(4):
            rect = pygame.Rect(
                self._left_align,
                self._board._PADDING + i * self._button_vertical_spacing,
                self._BUTTON_WIDTH, self._BUTTON_HEIGHT
            )
            self._button_rects.append({
                'rect': rect,
                'execute': None
            })

    def draw_interface(self, board_status):
        '''Draw interface elements (buttons and messages)'''
        self.draw_auto_button(board_status)
        self.draw_reset_button(board_status)
        self.draw_user_input_button(board_status)
        self.draw_get_more_puzzles_button(board_status)
        self.draw_message()
    
    def draw_board(self, screen):
        self._board.draw(screen)

    def handle_buttons(self, board_status):
        if not self._board._status_fetching:
            mouse = pygame.mouse.get_pos()

            for button in self._button_rects:
                if button['rect'].collidepoint(mouse):
                    button['execute'](board_status) 

    def handle_events(self, events):
        self._board.handle_events(events)

    def draw_auto_button(self, board_status, pos=0):
        button_rect = self._button_rects[pos]['rect']
        color = self._PALETTE['black'] if board_status == 'normal' else self._PALETTE['grey']
        
        pygame.draw.rect(self.screen, color, button_rect, 5, 100)
        
        buttonText = self._LARGE_FONT.render('Solve', True, color)
        buttonTextRect = buttonText.get_rect()
        buttonTextRect.center = button_rect.center
        self.screen.blit(buttonText, buttonTextRect)
        
        self._button_rects[pos]['execute'] = self.auto_button

    def draw_reset_button(self, board_status, pos=1):
        button_rect = self._button_rects[pos]['rect']
        
        color = self._PALETTE['black'] if board_status in ('normal', 'solving', 'solved') else self._PALETTE['grey']
        
        pygame.draw.rect(self.screen, color, button_rect, 5, 100)
        
        text_to_render = 'Stop' if board_status == 'solving' else 'Reset'
        buttonText = self._LARGE_FONT.render(text_to_render, True, color)
        buttonTextRect = buttonText.get_rect()
        buttonTextRect.center = button_rect.center
        
        self.screen.blit(buttonText, buttonTextRect)
        
        self._button_rects[pos]['execute'] = self.reset_button

    def draw_user_input_button(self, board_status, pos=2):
        button_rect = self._button_rects[pos]['rect']

        color = self._PALETTE['black'] if board_status in ('normal', 'user', 'solved') else self._PALETTE['grey']
        
        pygame.draw.rect(self.screen, color, button_rect, 5, 100)
        
        text_to_render = 'Custom Puzzle' if board_status != 'user' else 'Play'
        buttonText = self._LARGE_FONT.render(text_to_render, True, color)
        buttonTextRect = buttonText.get_rect()
        buttonTextRect.center = button_rect.center
        
        self.screen.blit(buttonText, buttonTextRect)
        
        self._button_rects[pos]['execute'] = self.user_input_button

    def draw_get_more_puzzles_button(self, board_status, pos=3):
        button_rect = self._button_rects[pos]['rect']

        color = self._PALETTE['black'] if board_status in ('normal', 'solved') else self._PALETTE['grey']
        pygame.draw.rect(self.screen, color, button_rect, 5, 100)
        
        buttonText = self._LARGE_FONT.render('New puzzle', True, color)
        buttonTextRect = buttonText.get_rect()
        buttonTextRect.center = button_rect.center
        
        self.screen.blit(buttonText, buttonTextRect)
        
        self._button_rects[pos]['execute'] = self.get_more_puzzles

    def draw_message(self):
        '''Draw the difficulty of puzzle and its status message (if any)'''

        if self._board.difficulty:
            rect = pygame.Rect(
                    self._left_align,
                    self._bottom_align - self._message_vertical_spacing,
                    self._BUTTON_WIDTH, self._message_vertical_spacing
                )
            
            text = self._SMALL_FONT.render(self._board.difficulty, True, self._PALETTE['red'])
            textRect = text.get_rect()
            textRect.center = rect.center
            self.screen.blit(text, textRect)
        
        if self._board.message:
            rect = pygame.Rect(
                    self._left_align,
                    self._bottom_align - 2 * self._message_vertical_spacing,
                    self._BUTTON_WIDTH, self._message_vertical_spacing
                )
            
            text = self._SMALL_FONT.render(self._board.message, True, self._PALETTE['red'])
            textRect = text.get_rect()
            textRect.center = rect.center
            self.screen.blit(text, textRect)
    
    def auto_button(self, board_status):
        '''Call the algorithm to solve the puzzle'''
        if board_status == 'normal':
            self._board.auto_solve()    
    
    def reset_button(self, board_status):
        '''Remove player answers back to puzzle"initial state'''
        if board_status == ('solving'):
            self._board.auto_solve(False)
        elif board_status in ('normal', 'solved'):
            self._board.reset()
            
    def user_input_button(self, board_status):
        '''Turn on user input mode for custom puzzles'''

        if board_status in ('normal', 'solved'):
            self._board.enable_user_input()

        elif board_status == 'user':
            self._board.enable_user_input(False)

    def get_more_puzzles(self, board_status):
        '''Get new puzzle using API'''
        if board_status in ('normal', 'solved'):
            self._board.get_api_puzzles()

    def main_loop(self):

        while True:
            events = pygame.event.get()
                
            self.screen.fill(self._PALETTE['white'])

            # Board status will determine which buttons would function
            board_status = self._board.get_status()
            
            # Handle mousehover and click to insert number
            self.handle_events(events)
            
            self.draw_board(self.screen)
            
            self.draw_interface(board_status)
            
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.handle_buttons(board_status)
            
            pygame.display.update()


def main():
    game = Game()
    game.main_loop()


if __name__ == '__main__':
    main()