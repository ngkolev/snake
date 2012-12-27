"""Snake game module with the basic business logic

This module contains several classes to be used to simulate the game.
It allow us game level loading from external files in specific format.
Additionaly the game state could be saved and loaded as well.

"""

import pickle, random

class LevelManager:
    """This class is used to manage the levels.
    It is used to load all the levels from the selected level directory
    and it keeps track of the current level.

    """
    def __init__(self, level_path):
        """Initialize a new instance of a LevelManager
        level_path - the path where is the level directory

        """
        self.current_file = 1
        self.current_level = None
        self.level_path = level_path

    def load_next_level(self):
        """Loads the next level in current_level property
        If such doesn't exist LastLevelError is raised.

        """
        filename = "{0}/{1}.level".format(self.level_path, self.current_file)
        self.current_level = Level(self.current_file)
        self.current_file += 1
        try:
            with open(filename) as file:
                self.__read_level_properties(file)
                maze_lines = file.readlines()
        except IOError as ex:
            if ex.errno == 2: # the file was not found
                raise LastLevelError()
            else:
                raise LevelIOError()
        self.__read_level_maze(maze_lines)
        self.__read_level_snake(maze_lines)
        if not self.__are_all_objects_in_maze(self.current_level.snake)\
            or not self.__are_all_objects_in_maze(self.current_level.barrier):
            raise LevelFormatError('Incorrect width or height')
        self.current_level.move_apple()
        self.current_level.state = LevelState.RUNNING
        return self.current_level

    def reset(self):
        """Loads the first game level

        """
        self.current_file = 1
        self.load_next_level()

    def __read_level_properties(self, file):
        """Reads and validated the properties stored into the config file

        file - open level config file

        """
        snake_max_length = None
        maze_width = None
        maze_height = None
        for line in file:
            if line.startswith('snake max length:'):
                snake_max_length = _parse_int_config(line, 'snake max length:')
            elif line.startswith('width:'):
                maze_width =_parse_int_config(line, 'width:')
            elif line.startswith('height:'):
                maze_height =_parse_int_config(line, 'height:')
            elif line.startswith('level:'):
                break;
        if snake_max_length == None:
            raise LevelFormatError("Snake max length is not specified")
        elif maze_width == None:
            raise LevelFormatError('Maze width was not specified')
        elif maze_height == None:
            raise LevelFormatError('Maze height was not specified')
        self.current_level.snake_max_length = snake_max_length
        self.current_level.maze_width = maze_width
        self.current_level.maze_height = maze_height

    def __read_level_maze(self, lines):
        """Reads the bricks and the snake's head

        """
        for i, line in enumerate(lines):
            for j, char in enumerate(line):
                if char == '#':
                    self.current_level.barrier.append((i, j))
                elif char == '@':
                    self.current_level.snake.append((i, j))
        if len(self.current_level.snake) != 1:
            raise LevelFormatError('The snake head could not be found')

    def __read_level_snake(self, lines):
        """Reads the snake. This function relies on that the head
        is already founded

        lines - list of strings representing the maze
        """
        snake = self.current_level.snake
        height = self.current_level.maze_height
        width = self.current_level.maze_width
        snake_head = snake[0]
        x, y = snake_head[0], snake_head[1]
        while True:
            if x > 0 and\
                self.__is_not_visited(lines, x - 1, y):
                x -= 1
            elif x < height - 1 and\
                self.__is_not_visited(lines, x + 1, y):
                x += 1
            elif y > 0 and\
                self.__is_not_visited(lines, x, y - 1):
                y -= 1
            elif y < width - 1 and\
                self.__is_not_visited(lines, x, y + 1):
                y += 1
            else:
                break
            snake.append((x, y))
        if len(snake) < 2:
            raise LevelFormatError('Snake must be at least with two elements')
        x_direction = snake[0][0] - snake[1][0]
        y_direction = snake[0][1] - snake[1][1]
        self.current_level.snake_direction = (x_direction, y_direction)

    def __are_all_objects_in_maze(self, objects):
        """Checks if all objects are in the bounds of the maze

        objects - list of tuples

        """
        return any(item[0] < self.current_level.maze_height or\
                   item[1] < self.current_level.maze_width
                   for item in objects)

    def __is_not_visited(self, lines, x, y):
        """Checks if the sneak block is not visited. If there is no
        snake block on (x, y) then this method returns false

        lines - list of strings representing the maze

        """
        snake = self.current_level.snake
        return (x, y) not in snake and lines[x][y] == '%'


class Level:
    """This class holds all the information about snake's level
    and the logic about it

    """
    def __init__(self, level):
        self.level = level
        self.snake_max_length = 0
        self.snake = []
        self.barrier = []
        self.maze_width = 0
        self.maze_height = 0
        self.apple = (0, 0)
        self.snake_direction = (0, 0)

    @property
    def snake_length(self):
        """The current snake length

        """
        return len(self.snake)

    def move(self, game_move):
        """Change the state of the game using the specified move

        """
        result = LevelState.RUNNING
        self.__calculate_new_direction(game_move)
        self.__move_snake_head()
        if self.__snake_barrier_collision() or self.__snake_snake_collision():
            result = LevelState.LOSE
        elif self.__snake_apple_colission():
            if self.snake_length == self.snake_max_length:
                result = LevelState.WIN
            else:
                self.move_apple()
        else:
            self.__move_snake_tail()
        return result

    def move_apple(self):
        """Moves the apple at random position

        """
        while True:
            x_apple = random.randint(0, self.maze_height - 1)
            y_apple = random.randint(0, self.maze_width - 1)
            self.apple = (x_apple, y_apple)
            if not self.__apple_colission():
                break

    def __calculate_new_direction(self, game_move):
        """This method calculates the snake direction after a game move

        game_move - GameMove's constant

        """
        if self.snake_direction[0] == 0:
            if game_move == GameMoves.UP:
                self.snake_direction = (-1, 0)
            elif game_move == GameMoves.DOWN:
                self.snake_direction = (1, 0)
        elif self.snake_direction[1] == 0:
            if game_move == GameMoves.LEFT:
                self.snake_direction = (0, -1)
            elif game_move == GameMoves.RIGHT:
                self.snake_direction = (0, 1)

    def __move_snake_head(self):
        """Move the snake head using the current snake direction

        """
        old_head = self.snake[0]
        x_new_head = old_head[0] + self.snake_direction[0]
        y_new_head = old_head[1] + self.snake_direction[1]
        self.snake.insert(0, (x_new_head, y_new_head))

    def __move_snake_tail(self):
        """Move the snake tail

        """
        self.snake.pop()

    def __snake_barrier_collision(self):
        """Checks if there is collision between the snake and the
        barrier's bricks

        """
        head = self.snake[0]
        x_head = head[0]
        y_head = head[1]
        if x_head < 0 or x_head >= self.maze_height or\
           y_head < 0 or y_head >= self.maze_width:
            return True
        else:
            return any(brick == block for block in self.snake
                                      for brick in self.barrier)

    def __snake_apple_colission(self):
        """Checks if there is collision between the snake and the apple

        """
        return any(self.apple == block for block in self.snake)

    def __apple_colission(self):
        """Checks if there is collision between the apple and snake
        or between the apple and the barrier

        """
        return any(self.apple == block for block in self.snake)\
            or any(self.apple == brick for brick in self.barrier)

    def __snake_snake_collision(self):
        """Checks if there is collision between the snake itself

        """
        return any(i != j and block1 == block2
            for i, block1 in enumerate(self.snake)
            for j, block2 in enumerate(self.snake))

class Game:
    """This class is used to simulate the snake game move by move.
    It uses the Level class to initialize itself.

    """
    def __init__(self, level_manager):
        """Initialize a new game class

        level_manager - manager to provide the parsed levels

        """
        self.level_manager = level_manager
        self.level_manager.load_next_level()

    @property
    def current_level(self):
        """Returns current level object

        """
        return self.level_manager.current_level

    @staticmethod
    def load_game_from_file(filename):
        """Factory method to desirialize a game from file

        """
        with open(filename, 'rb') as file:
            return pickle.load(file)

    def save(self, filename):
        """Save the state of the game

        filename - file to store the serialized game

        """
        with open(filename, 'wb') as file:
            pickle.dump(self, file)

    def move(self, game_move):
        """Change the state of the game using the specified move

        """
        result = self.current_level.move(game_move)
        if result == LevelState.WIN:
            try:
                self.level_manager.load_next_level()
            except LastLevelError:
                self.level_manager.reset();
        elif result == LevelState.LOSE:
            self.level_manager.reset();
        return result

def _parse_int_config(string, config):
    """This funciton extracts value from config file.

    string - str in this format: '<config>: <value>'
    config - the name of the config section

    """
    if string.startswith(config):
        value_string = string[len(config):]
        try:
            value = int(value_string)
        except ValueError:
            raise LevelFormatError("Numeric value is in incorrect format")
        return value


class LevelState:
    """This are all states in which a game level could be.

    """
    RUNNING = 1
    WIN = 2
    LOSE = 3


class GameMoves:
    """This are the moves than can be done after each game itearation

    """
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    PASS = 5

class LevelError(Exception):
    """Base level related error class"""
    pass

class LevelIOError(LevelError):
    """This expcetion is raised when there is problem with reading
    the level files

    """
    def __init__(self):
        super().__init__('Unexpected error during reading of a level')

class LastLevelError(LevelError):
    """This expcetion is raised when there is no more levels

    """
    def __init__(self):
        super().__init__('There are no more level in the level directory')


class LevelFormatError(LevelError):
    """This exception is raised when the level text is in incorrect format

    """
    pass

