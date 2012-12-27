"""GUI snake game. It uses external Snake library and pyGame

"""

import sys, pygame, glob
from constants import *
from pygame.locals import *
from snakecore import *
from pygame import Color, display, time, font, draw, Surface, image

class MainUI:
    """The game's user interface class

    """
    def __init__(self):
        """Creates new MainUI object

        state - state to be visualized

        """
        pygame.init()
        display.set_caption("Snake Game")
        self.surface = display.set_mode((1200, 650))
        self.fpsClock = time.Clock()
        self.state = None
        self.frame = 0
        self.green_color = Color(0, 200, 0)

    def start(self):
        """Starts the drawing and event handling of the game

        """
        while True:
            self.surface.fill(self.green_color)
            self.state.draw()
            self.state.handle_events()
            display.update()
            self.fpsClock.tick(30)
            self.frame += 1


class Menu:
    """Class used to draw a menu and handle menu events

    """
    def __init__(self, menu_text_list, font_size=100,\
        distance=140, first=100, cursor=30):
        self.menu_items_pos = [x * distance + first\
            for x in range(len(menu_text_list))]
        self.menu_text_list= menu_text_list
        if len(menu_text_list) > 0:
            self.selected_index = 0
        else:
            self.selected_index = -1
        self.menu_font = font.Font(None, font_size)
        self.orange_color = Color(224, 76, 27)
        self.green_color = Color(42, 77, 6)
        self.cursor = cursor

    def draw(self, surface):
        if self.selected_index != -1:
            self.__draw_menu_cursor(surface)
            for i, text in enumerate(self.menu_text_list):
                self.__draw_menu_item(surface, text, i)

    def get_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif  event.type == KEYDOWN:
                return self.__handle_key_press(event.key)

    def __handle_key_press(self, key):
            if key == K_UP:
                if self.selected_index > 0:
                    self.selected_index -= 1
            elif key == K_DOWN:
                if self.selected_index < len(self.menu_text_list) - 1:
                    self.selected_index += 1
            elif key == K_RETURN:
                return self.selected_index
            elif key == K_ESCAPE:
                return -1

    def __draw_menu_cursor(self, surface):
        cursor_height = self.menu_items_pos[self.selected_index]
        draw.polygon(surface, self.orange_color, [
            (400, cursor_height),
            (400, cursor_height + self.cursor * 2),
            (400 + self.cursor, cursor_height + self.cursor)])
        draw.polygon(surface, self.orange_color, [
            (780, cursor_height),
            (780, cursor_height + self.cursor * 2),
            (780 - self.cursor, cursor_height + self.cursor)])

    def __draw_menu_item(self, surface, text, item_pos):
        menu_item = self.menu_font.render(text, False, self.green_color)
        menu_start_pos =\
            (surface.get_width() / 2 - menu_item.get_width() / 2,
             self.menu_items_pos[item_pos])
        surface.blit(menu_item, menu_start_pos)


class MainMenuUI:
    """Snake's game main menu
    (The menu which is shown when the game is firstly opened)

    """
    def __init__(self, main_ui):
        self.main_ui = main_ui
        menu_text_list = ["START", "LOAD", "EXIT"]
        self.menu = Menu(menu_text_list)
        self.white_color = Color(255, 255, 255)

    def draw(self):
        self.menu.draw(self.main_ui.surface)

    def handle_events(self):
        index = self.menu.get_events()
        if index == 0:
            snake_ui= SnakeUI(self.main_ui)
            self.main_ui.state = snake_ui
        elif index == 1:
            load_ui = LoadMenuUI(self.main_ui)
            self.main_ui.state = load_ui
        elif index == 2:
            pygame.quit()
            sys.exit()


class LoadMenuUI:
    """The game's menu which is shown to load saved game

    """
    def __init__(self, main_ui):
        self.main_ui = main_ui
        self.filenames = glob.glob(SAVE_FILE_TEMPLATE.format('*'))
        names = [name[name.rindex('\\') + 1:name.rindex('.')]
            for name in self.filenames]
        self.menu = Menu(names, 50, 40, 3, 16)

    def draw(self):
        self.menu.draw(self.main_ui.surface)

    def handle_events(self):
        index = self.menu.get_events()
        if index == -1:
            self.main_ui.state = MainMenuUI(self.main_ui)
        elif index != None:
            filename = self.filenames[index]
            game = Game.load_game_from_file(filename)
            game_ui = SnakeUI(self.main_ui, game)
            self.main_ui.state = game_ui


class SaveMenuUI:
    """The game's menu which is used to save a game's state

    """
    def __init__(self, main_ui, snake_ui):
        self.main_ui = main_ui
        self.snake_ui= snake_ui
        self.name = ''
        self.text_font = font.Font(None, 50)
        self.black_color = Color(0, 0, 0)
        self.green_color = Color(42, 77, 6)

    def draw(self):
        text = self.name
        message_surface = self.text_font.render("Save name: ",\
            False, self.green_color)
        text_surface = self.text_font.render(text, False, self.black_color)
        self.main_ui.surface.blit(message_surface, (0, 3))
        text_pos = (message_surface.get_width(), 3)
        self.main_ui.surface.blit(text_surface, text_pos)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                self.__handle_key_down(event.key)

    def __handle_key_down(self, key):
        if key == K_ESCAPE:
            self.main_ui.state = self.snake_ui
            self.snake_ui.is_running = True
        elif key == K_RETURN:
            if len(self.name) >= MIN_SAVEFILE_LEN:
                game = self.snake_ui.snake_game
                self.snake_ui.is_running = True
                filename = SAVE_FILE_TEMPLATE.format(self.name)
                game.save(filename)
                self.main_ui.state = self.snake_ui
        elif key == K_BACKSPACE:
            self.name = self.name[:-1]
        else:
            if len(self.name) <= MAX_SAVEFILE_LEN:
                key_press = key
                if key_press  >= 32 and key_press  <= 126 and\
                    key_press not in INVALID_SAVEFILE_CHARACTERS:
                    key_input = pygame.key.get_pressed()
                    if key_input[K_LSHIFT]:
                        self.name += chr(key_press).upper()
                    else:
                        self.name += chr(key_press)


class GameMenuUI:
    """The menu which is shown when user press 'esc' in game mode

    """
    def __init__(self, main_ui, snake_ui):
        self.main_ui = main_ui
        self.snake_ui = snake_ui
        menu_text_list = ["SAVE", "EXIT", "CLOSE"]
        self.menu = Menu(menu_text_list)
        self.white_color = Color(255, 255, 255)

    def draw(self):
        self.snake_ui.is_running = False
        self.snake_ui.draw()
        self.menu.draw(self.main_ui.surface)

    def handle_events(self):
        index = self.menu.get_events()
        if index == 0:
            self.main_ui.state = SaveMenuUI(self.main_ui, self.snake_ui)
        elif index == 1:
            self.main_ui.state = MainMenuUI(self.main_ui)
        elif index == 2 or index == -1:
            self.main_ui.state = self.snake_ui
            self.snake_ui.is_running = True


class ErrorUI:
    """The UI state used to display critical error message

    """
    def __init__(self, main_ui, message):
        self.main_ui = main_ui
        self.message = message
        self.menu_font = font.Font(None, 50)
        self.red_color = Color(255, 0, 0)

    def draw(self):
        text = self.menu_font.render(self.message, False, self.red_color)
        text_width = text.get_width()
        text_height = text.get_height()
        surface_width = self.main_ui.surface.get_width()
        surface_height = self.main_ui.surface.get_height()
        position = (surface_width / 2 - text_width / 2,
                   surface_height / 2 -text_height / 2)
        self.main_ui.surface.blit(text, position)

    def handle_events(self):
        for current_event in event.get():
            if current_event.type == QUIT:
                pygame.quit()
                sys.exit()

class SnakeUI:
    """Snake's game menu

    """
    def __init__(self, main_ui, game=None):
        if game != None:
            self.snake_game = game
        else:
            level_manager = LevelManager(LEVELS_DIRECTORY)
            self.snake_game = Game(level_manager)
        self.last_move = GameMoves.PASS
        self.main_ui = main_ui
        level = self.snake_game.current_level
        self.maze_size = (level.maze_height, level.maze_width)
        self.game_surface = Surface(transform(self.maze_size, 2, 2))
        #colors and images
        self.green_color = Color(151, 255, 148)
        self.white_color = Color(255, 255, 255)
        self.black_color = Color(0, 0, 0)
        self.apple = image.load('images/apple.png')
        self.block = image.load('images/block.png')
        self.brick = image.load('images/brick.jpg')
        #fonts
        self.info_font = font.Font(None, 23)
        self.is_running = True

    def draw(self):
        if self.is_running and self.main_ui.frame % GUI_GAME_SPEED == 0:
            self.snake_game.move(self.last_move)
            self.last_move = GameMoves.PASS
        level = self.snake_game.current_level
        if self.maze_size != (level.maze_width, level.maze_height):
            self.maze_size = (level.maze_height, level.maze_width)
            self.game_surface = Surface(transform(self.maze_size, 2, 2))
        self.game_surface.fill(self.green_color)
        self.__draw_apple()
        self.__draw_snake()
        self.__draw_barrier()
        self.__draw_level_info()
        surface_width = self.main_ui.surface.get_width()
        surface_height = self.main_ui.surface.get_height()
        game_width = self.game_surface.get_width()
        game_height = self.game_surface.get_height()
        y_pos = surface_width / 2 - game_width / 2
        x_pos  = surface_height / 2 - game_height / 2
        game_surface_pos = (y_pos, x_pos)
        self.main_ui.surface.blit(self.game_surface, game_surface_pos)

    def __draw_apple(self):
        apple_position = transform(self.snake_game.current_level.apple, 1, 1)
        self.game_surface.blit(self.apple, apple_position)

    def __draw_snake(self):
        level = self.snake_game.current_level
        for block in level.snake:
            self.game_surface.blit(self.block, transform(block, 1, 1))

    def __draw_barrier(self):
        level = self.snake_game.current_level
        for brick in level.barrier:
            self.game_surface.blit(self.brick, transform(brick, 1, 1))
        brick_height = self.brick.get_height()
        brick_width = self.brick.get_width()
        maze_height = self.game_surface.get_height()
        maze_width = self.game_surface.get_width()
        for x in range(0, maze_width, brick_width):
            self.game_surface.blit(self.brick, (x, 0))
        for x in range(0, maze_width, brick_width):
            self.game_surface.blit(self.brick, (x, maze_height - brick_height))
        for y in range(0, maze_height, brick_height):
            self.game_surface.blit(self.brick, (0, y))
        for y in range(0, maze_height, brick_height):
            self.game_surface.blit(self.brick, (maze_width - brick_width, y))

    def __draw_level_info(self):
        level = self.snake_game.current_level
        current_level = level.level
        snake_len = level.snake_length
        snake_max_len = level.snake_max_length
        info ='Level: {0} Snake Length: {1}/{2}'\
            .format(current_level, snake_len, snake_max_len)
        info_surface = self.info_font.render(info, False, self.black_color)
        self.main_ui.surface.blit(info_surface, (10, 10))

    def handle_events(self):
        for current_event in pygame.event.get():
            if current_event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif  current_event.type == KEYDOWN:
                if current_event.key == K_LEFT:
                   self.last_move = GameMoves.LEFT
                elif current_event.key == K_RIGHT:
                    self.last_move = GameMoves.RIGHT
                elif current_event.key == K_UP:
                    self.last_move = GameMoves.UP
                elif current_event.key == K_DOWN:
                    self.last_move = GameMoves.DOWN
                elif current_event.key == K_ESCAPE:
                    self.main_ui.state = GameMenuUI(self.main_ui, self)


def transform(coordinates, x_translation=0, y_translation=0):
    """This function transform coordinates from this form which
    is used in BL to the form used in pyGame

    """
    return ((coordinates[1] + x_translation) * PIXEL ,\
            (coordinates[0] + y_translation) * PIXEL)

def show_error(mainUI, text):
    """Shows general error on pyGame screen

    mainUI - the MainUI object
    text - error's description

    """
    error_ui = ErrorUI(mainUI, text)
    mainUI.state = error_ui
    mainUI.start()

def main():
    try:
        main_ui = MainUI()
        menu_ui = MainMenuUI(main_ui)
        main_ui.state = menu_ui
        main_ui.start()
    except LastLevelError:
        show_error(mainUI, 'There are no levels into the level directory')
    except LevelIOError:
        show_error(mainUI, 'Unexpected error while loading level information')
    except LevelFormatError:
        show_error(mainUI, 'Incorrect level syntax: "{0}"'\
            .format(str(LevelFormatError)))
    except pygame.error as ex:
        show_error(mainUI, str(ex))

if __name__ == '__main__':
    main()
