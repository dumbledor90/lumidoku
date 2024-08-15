import threading, random, requests
import pygame


class Board:

    _PALETTE = {
        'white': (250, 250, 250),
        'black': (20, 20, 20),
        'red': (150, 0, 0),
        'green': (0, 150, 0),
        'beige': (248, 237, 237),
        'orange': (255, 130, 37),
        'dark red': (180, 63, 63),
        'dark green': (60, 61, 55),
        'cyan': (23, 155, 174),
        'dark cyan': (10, 60, 90),
        'light green': (136, 214, 108),
    }

    # No longer wokring
    # _API_URL = 'https://sudoku-api.vercel.app/api/dosuku?query={newboard(limit:1){grids{value,difficulty}}}'
    
    _API_URL = 'https://sudoku-game-and-api.netlify.app/api/sudoku'

    _SAMPLE_PUZZLES = {
        'Easy': [
            [7, 0, 9, 0, 0, 1, 6, 3, 0],
            [0, 5, 1, 6, 8, 4, 9, 0, 0],
            [0, 8, 6, 0, 0, 7, 0, 0, 0],
            [5, 1, 0, 7, 2, 0, 3, 0, 9],
            [4, 6, 7, 8, 3, 9, 2, 1, 5],
            [9, 3, 0, 0, 0, 5, 7, 0, 6],
            [0, 0, 5, 0, 0, 0, 0, 7, 3],
            [8, 7, 0, 0, 6, 0, 0, 9, 1],
            [1, 9, 4, 5, 7, 3, 8, 0, 2]
        ],
        'Medium': [
            [9, 0, 5, 4, 8, 0, 0, 0, 3],
            [2, 1, 0, 0, 0, 9, 6, 5, 8],
            [0, 0, 0, 0, 2, 5, 0, 0, 4],
            [0, 9, 7, 0, 6, 0, 0, 0, 5],
            [0, 0, 8, 0, 0, 0, 3, 0, 0],
            [5, 0, 0, 0, 4, 0, 7, 8, 0],
            [8, 0, 0, 6, 1, 0, 0, 0, 0],
            [7, 5, 6, 2, 0, 0, 0, 1, 9],
            [1, 0, 0, 0, 9, 8, 4, 0, 7]
        ],
        'Hard': [
            [0, 0, 0, 0, 0, 0, 4, 0, 8],
            [7, 0, 0, 0, 3, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 6, 0, 0],
            [5, 0, 0, 8, 0, 0, 0, 0, 0],
            [0, 0, 0, 6, 0, 9, 0, 0, 0],
            [0, 3, 0, 0, 0, 0, 0, 7, 0],
            [0, 9, 6, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 5, 0, 0, 2, 0],
            [4, 0, 8, 0, 0, 0, 0, 0, 0]
        ],
    }

    def __init__(
            self,
            screen_size,
            cell_size,
            small_gap,
            big_gap,
            font=None
    ) -> None:

        self._CELL_SIZE = cell_size
        self._SMALL_GAP = small_gap
        self._ADDITIONAL_GAP = (big_gap - small_gap) if big_gap > small_gap else 0
        self._SCREEN_WIDTH, self._SCREEN_HEIGHT = screen_size
        self._BOARD_SIZE = 9 * self._CELL_SIZE + 8 * self._SMALL_GAP + 2 * self._ADDITIONAL_GAP
        self._PADDING = (self._SCREEN_HEIGHT - self._BOARD_SIZE) // 2
        self._FONT = pygame.font.SysFont('roboto', 60)

        self._FULL_SET = {1, 2, 3, 4, 5, 6, 7, 8, 9}
        self._values = [[0 for i in range(9)] for j in range(9)]
        self._board = []
        self.difficulty = ''
        self.message = ''

        self._whole_board_rect = pygame.Rect(
            self._PADDING, self._PADDING, 
            self._BOARD_SIZE, self._BOARD_SIZE
        )
        self._board_border_rect = pygame.Rect(
            self._PADDING - 2 * self._ADDITIONAL_GAP, 
            self._PADDING - 2 * self._ADDITIONAL_GAP, 
            self._BOARD_SIZE + 4 * self._ADDITIONAL_GAP, 
            self._BOARD_SIZE + 4 * self._ADDITIONAL_GAP
        )
        
        self._hover_mode = False
        self._mouse_clicked = False
        self._select_multiple_mode = False
        self._value_selected = 0

        self._current_loc = ()
        self._selected_cells = []
        
        self._status_solving = False
        self._status_solved = False
        self._status_fetching = False

        self._user_input = False

        # Set up and initilize all the rects that will be used to draw cells
        for i in range(9):
            row = []
            for j in range(9):
                cell = pygame.Rect(
                    self._PADDING + (self._CELL_SIZE + self._SMALL_GAP) * j + self._ADDITIONAL_GAP * (j // 3), 
                    self._PADDING + (self._CELL_SIZE + self._SMALL_GAP) * i + self._ADDITIONAL_GAP * (i // 3), 
                    self._CELL_SIZE, self._CELL_SIZE
                )
                row.append({
                    'rect': cell,
                    'player_input': True,
                })
            self._board.append(row)
        
        # Choose one sample puzzle for the initial launch
        self.get_api_puzzles()


    def draw(self, screen):
        '''Draw cells and their number (if any)'''
        
        # Draw the board border
        pygame.draw.rect(screen, self._PALETTE['black'], self._board_border_rect)

        mouse = pygame.mouse.get_pos()
        
        for i in range(9):
            for j in range(9):
                
                current_cell = self._board[i][j]

                # Registering the coordination of a cell
                # to draw the cell's highlight border when mouse hovers over a cell
                if current_cell['rect'].collidepoint(mouse):
                    self._current_loc = (i, j)

                    if self._mouse_clicked:
                        # Clicking on a number will highlight all the cells will the same number
                        if not self._select_multiple_mode and self._values[i][j] > 0:
                            self._value_selected = self._values[i][j]
                        # Clicking on empty cells will remove the highlight
                        else:
                            self._value_selected = 0

                        # Click again to already selected cell would deselect that cell 
                        if (i, j) in self._selected_cells:
                            self._selected_cells.remove((i, j))
                        
                        else:
                            # If you hold CTRL, you can select multiple cells
                            if self._select_multiple_mode:
                                self._selected_cells.append((i, j))
                            
                            # If you don't hold CTRL, then each mouse click to a different cell 
                            # would deselect the old ones 
                            else:
                                self._selected_cells = [(i, j)]
    
                        self._mouse_clicked = False

                # Cell color depends on if current cell is selected or not
                cell_color = self._PALETTE['dark cyan'] if (i, j) in self._selected_cells\
                         else self._PALETTE['dark green']
                pygame.draw.rect(screen, cell_color, current_cell['rect'], 0)

                # Only draw cell number if it's not 0 (empty cell)
                if self._values[i][j] > 0:
                    if self._value_selected == self._values[i][j]:
                        text_color = self._PALETTE['orange']
                    else:
                    # Number color depends on if it's player answer or not
                        text_color = self._PALETTE['beige'] if not current_cell['player_input'] else self._PALETTE['light green']

                    text = self._FONT.render(str(self._values[i][j]), True, text_color)
                    
                    text_rect = text.get_rect()
                    text_rect.center = current_cell['rect'].center
                    screen.blit(text, text_rect)

        # Draw the cell's highlight border base on registered mouse location
        if self._hover_mode:
            i, j = self._current_loc
            pygame.draw.rect(screen, self._PALETTE['green'], self._board[i][j]['rect'], 4)

        if self._selected_cells:
            for (i, j) in self._selected_cells:
                pygame.draw.rect(screen, self._PALETTE['orange'], self._board[i][j]['rect'], 4)


    def handle_events(self, events):
        '''Determine how mouse and keys affect the board'''

        mouse = pygame.mouse.get_pos()

        mouse_inside_board = self._whole_board_rect.collidepoint(mouse)

        # Turn on hover mode when mouse is inside board
        self._hover_mode = mouse_inside_board 
        
        for event in events:

            # Turn on/off select multiple mode when Ctrl key is held or not
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RCTRL, pygame.K_LCTRL):
                self._select_multiple_mode = True
                
            elif event.type == pygame.KEYUP and event.key in (pygame.K_RCTRL, pygame.K_LCTRL):
                self._select_multiple_mode = False

            # Each mouse click would select or deselect cells
            if event.type == pygame.MOUSEBUTTONUP and mouse_inside_board:
                self._mouse_clicked = True

            # Click outside board, or press ESC would deselect cells
            elif (event.type == pygame.MOUSEBUTTONUP and not mouse_inside_board) or\
                (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
                self._selected_cells = []

            # Backspace and Del key would remove value in the already input cells
            elif event.type == pygame.KEYUP and event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                for i, j in self._selected_cells:
                    self._values[i][j] = 0

            # Register player input
            if event.type == pygame.TEXTINPUT and self._selected_cells and not self._status_fetching:
                if event.text and (text := event.text[-1]).isdigit():
                    
                    value = int(text)

                    for i, j in self._selected_cells:
                        if self._board[i][j]['player_input'] and\
                            (value == 0 or value in self._find_available((i, j), self._values)):
                            self._values[i][j] = value

    # Board status would determine button functions
    def get_status(self):
        if self._status_fetching:
            return 'fetching'
        elif self._user_input:
            return 'user'
        elif self._status_solved:
            return 'solved'
        elif self._status_solving:
            return 'solving'
        else:
            return 'normal'
        
    def auto_solve(self, run=True):
        '''Run the algorithm in a new thread'''
        if run:
            self._status_solving = True
            solve_thread = threading.Thread(target=self._solve_wrapper, daemon=True)
            solve_thread.start()
        else:
            self._status_solving = False

    def reset(self):
        '''Undo player answers back to initial puzzle'''
        self.message = ''
        self._status_solved = False
        for i in range(9):
            for j in range(9):
                if self._board[i][j]['player_input']:
                    self._values[i][j] = 0 

    def empty_board(self):
        '''Return a black board for user to fill in custom puzzle'''
        self.message = ''
        self._status_solved = False
        for i in range(9):
            for j in range(9):
                self._values[i][j] = 0
                self._board[i][j]['player_input'] = True

    def update(self, values):
        '''Copy puzzle from a different source'''
        try:
            for i in range(9):
                for j in range(9):
                    if values[i][j]:
                        self._values[i][j] = values[i][j]
                        self._board[i][j]['player_input'] = False
        except:
            self.get_sample_puzzles()

    def get_sample_puzzles(self):
        self.message = ''
        self._status_solved = False
        self.difficulty = random.choice(('Easy', 'Medium', 'Hard'))
        self.update(self._SAMPLE_PUZZLES[self.difficulty])

    def get_api_puzzles(self):
        '''Send a request to an Api to get a new board'''

        self._status_solved = False
        self.message = ''
        self.difficulty = ''

        if not self._status_fetching:
            self._status_fetching = True
            self.empty_board()

            # Because fetching data take some times, so we start a new thread
            # to avoid freeze the game
            fetch_thread = threading.Thread(target=self._fetching_data, daemon=True)
            fetch_thread.start()

    def enable_user_input(self, user_input=True):
        '''
        Enable users to input their custom puzzles on an empty board
        User flag user_input to turn on/off this mode
        '''

        if user_input:
            self.difficulty = ''
            self._user_input = True
            self.empty_board()

        else:
            self._user_input = False
            for i in range(9):
                for j in range(9):
                    if self._values[i][j] > 0:
                        self._board[i][j]['player_input'] = False
    
    def _solve_wrapper(self):
        '''
        Wrapper function for the main algorithm
        Use to config some flags, messages
        '''
        self.message = ''

        self._solve(self._values)

        # After the process, if the message is neither about successfull nor stop solving
        # then it means we could not find a solution
        if not self.message:
            self._status_solving = False
            self._status_solved = False
            self.message = 'Could Not Find Soluion'

    def _find_available(self, coord, grid):
        '''Find available numbers for a given cell'''
        row, col = coord
        avai = {grid[i][j] for i in range(row - row % 3, row - row % 3 + 3)
                            for j in range(col - col % 3, col - col % 3 + 3)}\
                | {grid[row][j] for j in range(9)}\
                | {grid[i][col] for i in range(9)}
        return self._FULL_SET - avai 
    
    def _find_empty_cell(self, grid):
        '''Return the coordination of the first empty (value 0) cell'''
        for i in range(9):
            for j in range(9):
                if grid[i][j] == 0:
                    return (i, j)
        return None

    def _solve(self, grid):
        '''
        Find and fill in the possible numbers for the first empty cell,
        then recursively do the same with all the empty cells after that,
        until the grid is filled with numbers from 1-9 following Sudoku rule 
        '''

        if not self._status_solving and not self._status_solved:
            self.message = 'Stop Finding Solution'
            return False

        # If there's no empty cell, the puzzle is solved
        if not (coord := self._find_empty_cell(grid)):
            self._status_solved = True
            self._status_solving = False
            self.message = 'Puzzle Finished'
            return True
        
        possible_set = self._find_available(coord, grid)
        i, j = coord

        # Loop through all possible candidates for the cell
        for number in possible_set:

            # Fill in the possible candidate
            grid[i][j] = number

            # Run the algorithm on the new grid
            solved = self._solve(grid)

            if solved:
                return True
            
            # If it's the wrong candidate, empty the cell again
            else: 
                grid[i][j] = 0

        return False
        
    def _fetching_data(self):
        '''
        Make an API call to get new boards
        Verify its difficulty and return
        '''

        values = []
        
        try:
            response = requests.get(self._API_URL)
            
            if response.status_code == 200:
                difficulty = random.choice(('easy', 'medium', 'hard'))
        
                values = response.json()[difficulty]
                self.difficulty = difficulty.capitalize()
        
                self.update(values)
        except:
            pass

        # In case fetching failed, then return 1 of 3 sample puzzles
        if not values:
            self.get_sample_puzzles()

        self._status_fetching = False
