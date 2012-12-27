import unittest
from snakecore import *
from snakegui import transform
from constants import *

class TestLevelManager(unittest.TestCase):
    """Tests of the LevelManager class

    """
    def test_correct_levels_loading(self):
        """Testing loading of levels from the level directory

        """
        #initialization
        manager = LevelManager("testdata/correctlevels")
        manager.load_next_level()
        first_level = manager.current_level
        second_level = manager.load_next_level()
        #check first level
        self.assertEqual(first_level.level, 1)
        self.assertEqual(first_level.snake_max_length, 15)
        self.assertEqual(first_level.maze_width, 23)
        self.assertEqual(first_level.maze_height, 8)
        self.assertEqual(first_level.snake_length, 6)
        self.assertEqual(first_level.snake_direction, (0, 1))
        self.assertEqual(first_level.snake,
            [(1, 8), (1, 7), (1, 6), (1, 5), (1, 4), (1, 3)])
        self.assertEqual(first_level.barrier,
            [(1, 14), (2, 14), (3, 15), (3, 16), (3, 17), (3, 18), (3, 19)])
        #check second level
        self.assertEqual(second_level.level, 2)
        self.assertEqual(second_level.snake_max_length, 10)
        self.assertEqual(second_level.maze_width, 10)
        self.assertEqual(second_level.maze_height,10)
        self.assertEqual(second_level.snake_length, 5)
        self.assertEqual(first_level.snake_direction, (0, 1))
        self.assertEqual(second_level.snake,
            [(3, 2), (3, 3), (3, 4), (4, 4), (5, 4)])
        self.assertEqual(second_level.barrier,
            [(1, 4), (6, 4)])
        #test that end of level exception is raised
        self.assertRaises(LastLevelError, manager.load_next_level)

    def test_incorrect_levels_loading(self):
        """Testing loading of incorrect formated levels
        and checking if the correct error is raised

        """
        manager = LevelManager("testdata/incorrectlevels")
        #width is missing
        self.assertRaises(LevelFormatError, manager.load_next_level)
        #height is missing
        self.assertRaises(LevelFormatError, manager.load_next_level)
        #snake's head is missing
        self.assertRaises(LevelFormatError, manager.load_next_level)
        #snake is too short
        self.assertRaises(LevelFormatError, manager.load_next_level)


class DummyLevelManager:
    """Dummy level manager used to tests the Game class

    """
    def __init__(self):
        self.current_level = None

    def load_next_level(self):
        self.current_level = Level(0)
        self.current_level.snake_max_length = 15
        self.current_level.maze_width = 23
        self.current_level.maze_height = 8
        self.current_level.apple = (0, 9)
        self.current_level.snake_direction = (0, 1)
        self.current_level.snake =\
            [(1, 8), (1, 7), (1, 6), (1, 5), (1, 4), (1, 3)]
        self.current_level.barrier =\
            [(1, 14), (2, 14), (3, 15), (3, 16), (3, 17), (3, 18), (1, 10)]

    def reset(self):
        pass


class TestGame(unittest.TestCase):
    """Tests of the Game class

    """
    def test_incorrect_move(self):
        """Testing of incorrect game move in the current state

        """
        manager = DummyLevelManager()
        game = Game(manager)
        state = game.move(GameMoves.LEFT)
        self.assertEqual(state, LevelState.RUNNING)
        self.assertEqual(game.current_level.snake_length, 6)
        self.assertEqual(game.current_level.snake_direction, (0, 1))
        self.assertEqual(game.current_level.snake,
            [(1, 9), (1, 8), (1, 7), (1, 6), (1, 5), (1, 4)])

    def test_up_move(self):
        """Testing standart up move and
         the recalculation of the snake position

        """
        manager = DummyLevelManager()
        game = Game(manager)
        state = game.move(GameMoves.UP)
        self.assertEqual(state, LevelState.RUNNING)
        self.assertEqual(game.current_level.snake_length, 6)
        self.assertEqual(game.current_level.snake_direction, (-1, 0))
        self.assertEqual(game.current_level.snake,
            [(0, 8), (1, 8), (1, 7), (1, 6), (1, 5), (1, 4)])

    def test_down_move(self):
        """Testing standart down move and
         the recalculation of the snake position

        """
        manager = DummyLevelManager()
        game = Game(manager)
        state = game.move(GameMoves.DOWN)
        self.assertEqual(state, LevelState.RUNNING)
        self.assertEqual(game.current_level.snake_length, 6)
        self.assertEqual(game.current_level.snake_direction, (1, 0))
        self.assertEqual(game.current_level.snake,
            [(2, 8), (1, 8), (1, 7), (1, 6), (1, 5), (1, 4)])

    def test_pass_move(self):
        """Testing standart pass move and
         the recalculation of the snake position

        """
        manager = DummyLevelManager()
        game = Game(manager)
        state = game.move(GameMoves.PASS)
        self.assertEqual(state, LevelState.RUNNING)
        self.assertEqual(game.current_level.snake_length, 6)
        self.assertEqual(game.current_level.snake_direction, (0, 1))
        self.assertEqual(game.current_level.snake,
            [(1, 9), (1, 8), (1, 7), (1, 6), (1, 5), (1, 4)])

    def test_take_apple(self):
        """Testing the snake enlargment after taking of the apple

        """
        manager = DummyLevelManager()
        game = Game(manager)
        game.move(GameMoves.PASS)
        state = game.move(GameMoves.UP)
        self.assertEqual(state, LevelState.RUNNING)
        self.assertEqual(game.current_level.snake_length, 7)
        self.assertEqual(game.current_level.snake_direction, (-1, 0))
        self.assertEqual(game.current_level.snake,
            [(0, 9), (1, 9), (1, 8), (1, 7), (1, 6), (1, 5), (1, 4)])

    def test_brick_colision(self):
        """Testing the game state after brick colision

        """
        manager = DummyLevelManager()
        game = Game(manager)
        game.move(GameMoves.PASS)
        state = game.move(GameMoves.PASS)
        self.assertEqual(state, LevelState.LOSE)

    def test_out_of_maze_colision(self):
        """Testing the game after the snake has leaved the game field

        """
        manager = DummyLevelManager()
        game = Game(manager)
        game.move(GameMoves.DOWN)
        for i in range(5):
            state = game.move(GameMoves.PASS)
            self.assertEquals(state, LevelState.RUNNING)
        state = game.move(GameMoves.PASS)
        self.assertEqual(state, LevelState.LOSE)

    def test_snake_snake_colision(self):
        """Testing if the snake is colliding with itself

        """
        manager = DummyLevelManager()
        game = Game(manager)
        state = game.move(GameMoves.DOWN)
        self.assertEqual(state, LevelState.RUNNING)
        state = game.move(GameMoves.LEFT)
        self.assertEqual(state, LevelState.RUNNING)
        state= game.move(GameMoves.UP)
        self.assertEqual(state, LevelState.LOSE)

class TestTransformCoordinates(unittest.TestCase):
    """Testing transform function

    """
    def test_transform_default(self):
        """Testing transform functions with default transformation

        """
        result = transform((1, 2))
        self.assertEqual(result, (2 * PIXEL, 1 * PIXEL))

    def test_transform(self):
        """Testing transform with explicit transformation

        """
        result = transform((1, 2) ,2, 2)
        self.assertEqual(result, (4 * PIXEL, 3 * PIXEL))

if __name__ == '__main__':
    unittest.main()
