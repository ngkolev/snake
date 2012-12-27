"""Console demo of the Snake Game library

"""

import msvcrt, os
from time import sleep
from constants import *
from sys import *
from snakecore import *

def main():
    """Main entry point

    """
    while True:
        stdout.write('>>>')
        stdout.flush()
        respond = stdin.readline()[:-1].lower().strip()
        print(respond)
        if respond == 'start':
            manage_start_command()
        elif respond.startswith('load '):
            name = respond[5:]
            manage_load_command(name)
        elif respond == 'exit':
            return
        elif respond == 'help':
            print_help()
        else:
            print('Invalid command')

def manage_start_command():
    level_manager = LevelManager(LEVELS_DIRECTORY)
    try:
        game = Game(level_manager)
    except LastLevelError:
        print('There are no levels into the level directory')
    except LevelIOError:
        print('Unexpected error while loading level information')
    except LevelFormatError:
        print('Incorrect level syntax: "{0}"'\
            .format(str(LevelFormatError)))
    else:
        start_game(game)

def manage_load_command(name):
    filename = SAVE_FILE_TEMPLATE.format(name)
    try:
        game = Game.load_game_from_file(filename)
    except IOError as ex:
        if ex.errno == 2:
            print('Save with this name does not exist')
        else:
            print('Unexpected error while loading level information')
    else:
        start_game(game)

def start_game(game):
    """Start game loop

    game - the Game object which will be used into the game cycle

    """
    draw_level(game.current_level)
    while True:
        if msvcrt.kbhit():
            input = ord(msvcrt.getch())
            if input == 27: # esc
                os.system('cls')
                return
            elif input == 115: # s
                os.system('cls')
                save_game(game)
            elif input == 224: # arrows
                input = ord(msvcrt.getch())
                if input == 72:
                    game.move(GameMoves.UP)
                elif input == 80:
                    game.move(GameMoves.DOWN)
                elif input == 75:
                    game.move(GameMoves.LEFT)
                elif input == 77:
                    game.move(GameMoves.RIGHT)
            else:
                game.move(GameMoves.PASS)
        else:
            game.move(GameMoves.PASS)
        draw_level(game.current_level)
        sleep(GAME_SPEED)

def draw_level(level):
    """Draws the game on the console using the level object

    level - the Level object which is painted

    """
    maze =[['-' for x in range(level.maze_width)]
                for y in range(level.maze_height)]
    apple = level.apple
    maze[apple[0]][apple[1]] = 'X'
    for block in level.snake:
        maze[block[0]][block[1]] = 'o'
    for brick in level.barrier:
        maze[brick[0]][brick[1]] = '#'
    os.system('cls')
    for row in maze:
        line = ''.join(row)
        print(line)
    current_level = level.level
    snake_len = level.snake_length
    snake_max_len = level.snake_max_length
    info ='\nLevel: {0} Snake Length: {1}/{2}'\
        .format(current_level, snake_len, snake_max_len)
    print(info)

def save_game(game):
    """Save Game object into file. The name is choosen by the user

    """
    stdout.write('Enter name of the save: ')
    stdout.flush()
    name = stdin.readline()[:-1]
    filename = SAVE_FILE_TEMPLATE.format(name)
    try:
        game.save(filename)
        print('The game is saved.', end=' ')
    except IOError:
        print('Unexpected error while saving game information.', end=' ')
        msvcrt.getch()
    print('Press any key to continue...')
    msvcrt.getch()

def print_help():
    """Prints the game help on the console

    """
    print('''
Commands:
    start - starts new game
    load <name> - loads saved game with the given name
    exit - exit from this program
    help - showing this help\n
Game keys:
    up/left/right/down arrows - move the snake
    s - save the game
    esc - quit the current game to game command prompt''')

if __name__ == '__main__':
    main()
