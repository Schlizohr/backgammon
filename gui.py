import logging
import tkinter as tk
from enum import Enum
from tkinter import font

from PIL import Image
from PIL import ImageTk

from Backgammon import Player, Game, Checker as EngineChecker, Die, Board
from move_generator import generate_moves


class Setting(Enum):
    CONE_HEIGHT_MULTIPLIER = 0.80
    CONE_WIDTH_MULTIPLIER = 0.9
    CONE_COLOR_DARK = "#4b2829"
    CONE_COLOR_LIGHT = "#9e9e9e"
    BOARD_BORDER_SIZE = 50
    BOARD_BORDER_COLOR = "#64553e"
    BOARD_BACKGROUND_COLOR = "#100e0b"
    CHECKER_LIGHT_COLOR = "#FFFFFF"
    CHECKER_DARK_COLOR = "#000000"
    CHECKER_MAPPING_X = CHECKER_DARK_COLOR
    CHECKER_MAPPING_O = CHECKER_LIGHT_COLOR
    CONTROL_PANEL_WIDTH = 300


class Items(Enum):
    BOARD = "BOARD"
    CURRENT_PLAYER_NAME = "CURRENT_PLAYER_NAME"
    CURRENT_PLAYER = "CURRENT_PLAYER"
    CURRENT_DIE = "CURRENT_DIE"
    PLACED_CHECKER = "PLACED_CHECKER"
    NEXT_PLAYER_BUTTON = "NEXT_PLAYER_BUTTON"
    BOARD_WIDTH = "BOARD_WIDTH"
    BOARD_HEIGHT = "BOARD_HEIGHT"
    CONTROL_HEIGHT = "CONTROL_HEIGHT"
    OFF_BOARD = "OFF_BOARD"
    CHECKER_DIAMETER = "CHECKER_DIAMETER"
    CHECKER_BUFFER = "CHECKER_BUFFER"
    LATEST_MOVE = "LATEST_MOVE"
    DONE_MOVES = "DONE_MOVES"
    CURRENT_MOVE = "CURRENT_MOVE"
    POSSIBLE_MOVES = "POSSIBLE_MOVES"


class GameObject(object):
    def __init__(self, canvas, item):
        self.frame = canvas
        self.item = item


def to_checker_color(checker: EngineChecker) -> str:
    return Setting[f"CHECKER_MAPPING_{checker.value.upper()}"].value


class Checker(GameObject):

    def __init__(self, canvas, color):
        self.canvas = canvas
        self.color = color
        self.top_left_x = 0
        self.top_left_y = 0
        self.bottom_right_x = 0
        self.bottom_right_y = 0
        self.d = 0
        self.image = None
        self.raw_image = None

    def set_image(self):
        img = self.raw_image.resize((self.d, self.d), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(img)

    def draw_at(self, x, y, d):
        self.init_positions(x, y, d)
        if not self.raw_image:
            self.set_raw_image()
        if d != self.d:
            self.d = int(d)
            self.set_image()
        self.canvas.create_image(x, y, image=self.image)

    def init_positions(self, x, y, d):
        r = d / 2
        self.top_left_x = x - r
        self.top_left_y = y - r
        self.bottom_right_x = x + r
        self.bottom_right_y = y + r

    def is_at(self, x, y):
        return self.top_left_x <= x <= self.bottom_right_x and \
               self.top_left_y <= y <= self.bottom_right_y

    def set_raw_image(self):
        if self.color == Setting.CHECKER_DARK_COLOR.value:
            self.raw_image = Image.open("resources/CHECKER_DARK.png")
        else:
            self.raw_image = Image.open("resources/CHECKER_LIGHT.png")

    def __repr__(self):
        return self.color


class HumanPlayer(Player):

    def __init__(self, color, ui_board, items, name=None):
        self.name = name
        if not name:
            self.name = color
        self.items = items
        self.color_ui = Setting[f"CHECKER_MAPPING_{color.value.upper()}"]
        self.uiBoard: GameBoard = ui_board
        super().__init__(color)

    def calculate_moves(self, dices: Die, board) -> [(int, int)]:
        self.items[Items.CURRENT_PLAYER_NAME].set(self.name)
        self.items[Items.CURRENT_PLAYER] = self
        self.items[Items.CURRENT_DIE].set(str(dices.get_roll()))
        self.uiBoard.draw_game_state(board)

        possible_moves = generate_moves(self, dices, board)
        moves = []
        if possible_moves:
            for i in range(len(possible_moves[0])):
                self.items[Items.NEXT_PLAYER_BUTTON].wait_variable(self.items[Items.PLACED_CHECKER])
                moves.append(self.items[Items.LATEST_MOVE])
                print(self.items[Items.LATEST_MOVE])
                self.items[Items.PLACED_CHECKER].set(0)
        print(moves)
        if any(t < 0 for _, t in moves):
            moves = self.map_out_moves(moves, possible_moves)
        return moves

    def map_out_moves(self, moves: [(int, int)], possible_moves: [[(int, int)]]):
        sources = [s for s, _ in moves]
        chosen_moves = list(filter(lambda ms: all([s in sources for s, _ in ms]), possible_moves))
        if sorted(moves) != sorted(chosen_moves):
            chosen_moves = moves
        return chosen_moves


class Cone(GameObject):
    def __init__(self, canvas, n, x, y, width, height, light=True, upwards=False):
        self.number = n
        self.canvas = canvas
        self.item = {}
        self.checkers: [Checker] = []
        self.x = x
        self.y = y
        self.checker_diameter = height / 6
        self.is_upwards = upwards
        self.x_offset = x + width * (1 - Setting.CONE_WIDTH_MULTIPLIER.value) / 2
        self.max_width = width
        self.width = self.max_width * Setting.CONE_WIDTH_MULTIPLIER.value
        self.max_height = height
        self.height = height * Setting.CONE_HEIGHT_MULTIPLIER.value
        self.light = light
        self.upwards = upwards
        self.color = Setting.CONE_COLOR_LIGHT.value
        if not self.light:
            self.color = Setting.CONE_COLOR_DARK.value
        logging.debug(
            f"x: {str(x)}, y: {str(y)}, width: {str(width)}, height: {str(height)}, light: {str(light)}, upwards: {str(upwards)}")
        self.draw_cone()
        super(Cone, self).__init__(self.canvas, self.item)

    def draw_cone(self):
        self.canvas.create_rectangle(self.x, self.y,
                                     self.x + self.max_width, self.y + (-1) ** self.is_upwards * self.max_height,
                                     fill=Setting.BOARD_BACKGROUND_COLOR.value,
                                     outline=Setting.BOARD_BACKGROUND_COLOR.value
                                     )
        points = [
            self.x_offset, self.y,
            self.x_offset + self.width, self.y,
            self.x_offset + self.width / 2, self.y + (-1) ** self.is_upwards * self.height
        ]
        logging.debug("points: " + str(points))
        self.canvas.create_polygon(points, fill=self.color, outline=self.color)
        self.draw_checkers()

    def add_checker(self, checker):
        self.checkers.append(checker)
        self.draw_cone()

    def remove_checker(self, checker):
        self.checkers.remove(checker)
        self.draw_cone()

    def pop_first_checker(self):
        checker = self.checkers[0]
        self.remove_checker(checker)
        return checker

    def draw_checkers(self):
        for index, checker in enumerate(self.checkers):
            if index < 6:
                x = self.x + self.max_width / 2
                y = self.y + (-1) ** self.is_upwards * (index * self.checker_diameter + self.checker_diameter / 2)
                logging.debug(f"x: {x}, y: {y}")
                checker.draw_at(x, y, self.checker_diameter)

    def is_responsible(self, x, y):
        return self.x <= x <= self.x + self.max_width and \
               (self.y <= y <= self.y + (-1) ** self.is_upwards * self.max_height or
                self.y >= y >= self.y + (-1) ** self.is_upwards * self.max_height)

    def get_checker_at(self, x, y):
        for i, c in enumerate(self.checkers):
            i = i + 1
            upperbound = self.y + (-1) ** self.is_upwards * i * self.checker_diameter
            if self.x <= x <= self.x + self.max_width and (self.y <= y <= upperbound or upperbound <= y <= self.y):
                return c
        # if self.is_responsible(x,y) and len()
        return None

    def reset(self, checkers: [Checker]):
        self.checkers = []
        self.checkers.extend(checkers)
        self.draw_cone()

    def can_add(self, checker: Checker) -> bool:
        return not (len(self.checkers) >= 2 and self.checkers[0].color != checker.color)

    def need_to_throw_if_add(self, checker: Checker):
        if not self.checkers:
            return False
        return self.checkers[0].color != checker.color

    def equals_to_engine_field(self, field: [EngineChecker]):
        return list(map(lambda c: c.color, self.checkers)) == \
               list(map(lambda c: to_checker_color(c), field))


class OutBar(GameObject):

    def __init__(self, canvas, items):
        super().__init__(canvas, items)
        self.items = items
        self.bar: [Checker] = []
        self.out: [Checker] = []

    def draw_out_bar(self):
        self.draw_out()
        self.draw_bar()

    def draw_out(self):
        self.__draw(self.out, self.__draw_out)

    def __draw_out(self, checkers, is_bottom):
        for i, c in enumerate(checkers):
            border_size = Setting.BOARD_BORDER_SIZE.value
            x = border_size * 1.5 + i * border_size
            y = border_size / 2 - (-1) * is_bottom * (self.items[Items.BOARD_HEIGHT] - border_size)
            c.draw_at(x, y, border_size)

    def draw_bar(self):
        self.__draw(self.bar, self.__draw_bar)

    def __draw(self, checkers, draw_function):
        if not checkers:
            return
        is_white = self.items[Items.CURRENT_PLAYER].color_ui == Setting.CHECKER_LIGHT_COLOR
        draw_function([c for c in checkers if c.color == Setting.CHECKER_LIGHT_COLOR.value], is_white)
        draw_function([c for c in checkers if c.color == Setting.CHECKER_DARK_COLOR.value], not is_white)

    def __draw_bar(self, checkers, is_top):
        for i, c in enumerate(checkers):
            c: Checker = c
            border_size = Setting.BOARD_BORDER_SIZE.value
            x = self.items[Items.BOARD_WIDTH] / 2
            y = self.items[Items.BOARD_HEIGHT] / 2 - (-1) ** is_top * (border_size / 2 + i * border_size)
            c.draw_at(x, y, border_size)

    def add_to_out(self, checker):
        self.out.append(checker)
        self.draw_out_bar()

    def reset_out(self, checkers=None):
        if checkers is None:
            checkers = []
        self.out = checkers
        self.draw_out()

    def add_to_bar(self, checker_to_bar):
        self.bar.append(checker_to_bar)
        self.draw_out_bar()

    def reset_bar(self, checkers=None):
        if checkers is None:
            checkers = []
        self.bar = checkers
        self.draw_bar()

    def take_checker_from_bar_at(self, x, y) -> Checker:
        checker = self.get_checker_from_bar(x, y)
        if checker:
            self.remove_checker_from_bar(checker)
        self.draw_out_bar()
        return checker

    def get_checker_from_bar(self, x, y) -> Checker:
        return next(iter(c for c in self.bar if c.is_at(x, y)), None)

    def remove_checker_from_bar(self, checker):
        self.bar.remove(checker)
        self.draw_out_bar()


class GameBoard(GameObject):
    def __init__(self, canvas, items):
        self.canvas = canvas
        self.items = items
        self.width = self.items[Items.BOARD_WIDTH]
        self.height = self.items[Items.BOARD_HEIGHT]
        self.border_size = Setting.BOARD_BORDER_SIZE.value
        self.cones = {}
        self.out_board = OutBar(self.canvas, self.items)
        # self.canvas = tk.Canvas(self.parent_canvas, bg=Setting.BOARD_BACKGROUND_COLOR.value, width=self.width,
        #                         height=self.height)
        self.draw_board()
        self.fix_cone_positions()
        self.canvas.bind('<Button-1>', self.handle_mouse_click)
        super(GameBoard, self).__init__(self.canvas, self.items)

    def draw_board(self):
        self.draw_background()
        self.draw_cones()
        self.draw_borders()

    def draw_borders(self):
        color_settings = {
            "fill": Setting.BOARD_BORDER_COLOR.value,
            'outline': Setting.BOARD_BORDER_COLOR.value
        }

        self.canvas.create_rectangle(
            0, 0,
            self.width, self.border_size,
            color_settings
        )
        self.canvas.create_rectangle(
            self.width - self.border_size, 0,
            self.width, self.height,
            color_settings
        )
        self.canvas.create_rectangle(
            0, 0,
            self.border_size, self.height,
            color_settings
        )
        self.canvas.create_rectangle(
            0, self.height - self.border_size,
            self.width, self.height,
            color_settings
        )
        self.canvas.create_rectangle(
            self.width / 2 - self.border_size / 2, 0,
            self.width / 2 + self.border_size / 2, self.height,
            color_settings
        )
        self.out_board.draw_out_bar()

    def draw_cones(self):
        cone_width = (self.width / 2 - self.border_size / 2 - self.border_size) / 6
        cone_height = self.height / 2 - self.border_size
        self.__bottom_left_cones(cone_width, cone_height)
        self.__bottom_right_cones(cone_width, cone_height)
        self.__top_left_cones(cone_width, cone_height)
        self.__top_right_cones(cone_width, cone_height)

    def cone_for_position(self, x, y) -> Cone:
        return next(iter(c for c in self.cones.values() if c.is_responsible(x, y)), None)

    def __bottom_left_cones(self, cone_width, cone_height):
        for i in range(6):
            cone = Cone(self.canvas, i + 1,
                        self.border_size + (cone_width * i), self.height - self.border_size,
                        cone_width, cone_height,
                        bool(i % 2), True
                        )
            self.cones[cone.number] = cone

    def __bottom_right_cones(self, cone_width, cone_height):
        for i in range(6):
            cone = Cone(self.canvas, i + 7,
                        self.width / 2 + self.border_size / 2 + (cone_width * i), self.height - self.border_size,
                        cone_width, cone_height,
                        bool(i % 2), True
                        )
            self.cones[cone.number] = cone

    def __top_left_cones(self, cone_width, cone_height):
        for i in range(6):
            cone = Cone(self.canvas, i + 13,
                        self.border_size + (cone_width * i), self.border_size,
                        cone_width, cone_height,
                        bool((i + 1) % 2), False
                        )
            self.cones[cone.number] = cone

    def __top_right_cones(self, cone_width, cone_height):
        for i in range(6):
            cone = Cone(self.canvas, i + 19,
                        self.width / 2 + self.border_size / 2 + (cone_width * i), self.border_size,
                        cone_width, cone_height,
                        bool((i + 1) % 2), False
                        )
            self.cones[cone.number] = cone

    def draw_background(self):
        self.canvas.create_rectangle(0, 0, self.width, self.height, outline=Setting.BOARD_BACKGROUND_COLOR.value,
                                     fill=Setting.BOARD_BACKGROUND_COLOR.value)

    def pickup_checker(self, x, y):
        logging.debug(f"hold checker from pos: x: {x}, y: {y}")
        if cone := self.cone_for_position(x, y):
            self.pickup_checker_from_cone(cone, x, y)
        if self.location_is_bar(x, y):
            self.pickup_checker_from_bar(x, y)

    def place_checker(self, x, y):
        logging.debug(f"pace checker at pos: x: {x}, y: {y}")
        if cone := self.cone_for_position(x, y):
            self.place_checker_at_cone(cone)
        if self.location_is_out(x, y):
            self.place_checker_to_out()

    def place_checker_at_cone(self, cone):
        logging.debug(f"cone: {cone.number}")
        checker = self.items[Items.CHECKER_BUFFER]
        if cone.can_add(checker):
            if cone.need_to_throw_if_add(checker):
                checker_to_bar = cone.pop_first_checker()
                self.out_board.add_to_bar(checker_to_bar)
            checker.canvas = self.canvas
            cone.add_checker(checker)
            self.items[Items.CHECKER_BUFFER] = None
            self.items[Items.LATEST_MOVE] = (self.items[Items.LATEST_MOVE][0], cone.number)
            self.items[Items.PLACED_CHECKER].set(1)

    def handle_mouse_click(self, event):
        if self.items[Items.CHECKER_BUFFER]:
            self.place_checker(event.x, event.y)
        else:
            self.pickup_checker(event.x, event.y)

    def location_is_out(self, x, y) -> bool:
        return x < Setting.BOARD_BORDER_SIZE.value and y < self.items[Items.BOARD_HEIGHT]

    def place_checker_to_out(self):
        logging.debug(f"pace checker in out")
        self.out_board.add_to_out(self.items[Items.CHECKER_BUFFER])
        self.items[Items.CHECKER_BUFFER] = None
        self.items[Items.LATEST_MOVE] = (self.items[Items.LATEST_MOVE][0], 0)
        self.items[Items.PLACED_CHECKER].set(1)

    def pickup_checker_from_cone(self, cone, x, y):
        logging.debug(f"cone: {cone.number}")
        checker = cone.get_checker_at(x, y)
        logging.debug(f"checker: {str(checker)}")
        if checker:
            cone.remove_checker(checker)
            self.items[Items.CHECKER_BUFFER] = checker
            self.items[Items.LATEST_MOVE] = (cone.number, None)

    def pickup_checker_from_bar(self, x, y):
        checker = self.out_board.take_checker_from_bar_at(x, y)
        self.items[Items.CHECKER_BUFFER] = checker
        self.items[Items.LATEST_MOVE] = (0, None)

    def location_is_bar(self, x, y):
        middle = self.items[Items.BOARD_WIDTH] / 2
        half_border_size = Setting.BOARD_BORDER_SIZE.value / 2
        return middle - half_border_size < x < middle + half_border_size

    def draw_game_state(self, board: Board):
        # TODO Map checkers to correct checkers
        #  -> self.out_board.reset_bar(board.board[0].content)
        light_count = 0
        dark_count = 0
        for i, cone in board.board.items():
            if i == 0:
                self.out_board.reset_bar()
                for checker in cone:
                    color = Setting[f"CHECKER_MAPPING_{checker.value.upper()}"].value
                    self.out_board.add_to_bar(Checker(self.canvas, color))
                continue
            checkers = []
            for checker in cone:
                color = Setting[f"CHECKER_MAPPING_{checker.value.upper()}"].value
                counter = light_count if color == Setting.CHECKER_LIGHT_COLOR.value else dark_count
                counter += 1
                checkers.append(Checker(self.canvas, color))
            self.cones[i].reset(checkers)

        self.out_board.reset_out()
        for _ in range(light_count):
            self.out_board.add_to_out(Checker(self.canvas, Setting.CHECKER_LIGHT_COLOR.value))

        for _ in range(light_count):
            self.out_board.add_to_out(Checker(self.canvas, Setting.CHECKER_DARK_COLOR.value))

    def fix_cone_positions(self):
        cones = list(self.cones.values())
        upper_bound = len(cones) - 1
        lower_bound = int((upper_bound + 1) / 2)
        for i in range(int(lower_bound / 2)):
            lower_cone_index = i + lower_bound
            upper_cone_index = upper_bound - i

            lower_cone = cones[lower_cone_index]
            lower_cone.number = upper_cone_index + 1

            upper_cone = cones[upper_cone_index]
            upper_cone.number = lower_cone_index + 1

            cones[lower_cone_index] = upper_cone
            cones[upper_cone_index] = lower_cone
        self.cones = {k + 1: v for k, v in enumerate(cones)}


class ControlPanel(GameObject):

    def __init__(self, canvas, item):
        self.canvas = canvas
        self.items = item
        self.playerName = tk.StringVar()
        self.items[Items.CURRENT_PLAYER_NAME] = self.playerName
        self.current_die_roll = tk.StringVar()
        self.items[Items.CURRENT_DIE] = self.current_die_roll
        self.possible_moves = tk.StringVar()
        self.items[Items.POSSIBLE_MOVES] = self.possible_moves
        self.done_moves = tk.StringVar()
        self.items[Items.DONE_MOVES] = self.done_moves
        self.current_move = tk.StringVar()
        self.items[Items.CURRENT_MOVE] = self.current_move
        self.items[Items.LATEST_MOVE] = (None, None)
        self.font = font.Font(family="Helvetica", size=40, weight="bold")
        self.player_name_label = tk.Label(
            self.canvas,
            textvariable=self.playerName,
            font=self.font,
            anchor="n"
        )
        self.player_name_label.grid(row=0, column=0)
        self.next_player_var = tk.IntVar()
        self.next_player_var.set(0)
        self.items[Items.PLACED_CHECKER] = self.next_player_var

        self.die_label = tk.Label(
            self.canvas,
            textvariable=self.current_die_roll,
            anchor="n"
        )
        self.die_label.grid(row=2, column=1)

        self.next_player_button = tk.Button(self.canvas, text="Next Player",
                                            command=lambda: self.next_player_var.set(1))
        self.next_player_button.grid(row=1, column=0)
        self.items[Items.NEXT_PLAYER_BUTTON] = self.next_player_button

        super().__init__(canvas, self.items)


class GameUi(tk.Frame):
    def __init__(self, master):
        super(GameUi, self).__init__(master)
        self.width = 1920
        self.height = 1080
        self.items = {
            Items.BOARD_WIDTH: self.width * 0.8,
            Items.BOARD_HEIGHT: self.height * 0.8,
            Items.CONTROL_HEIGHT: self.height * 0.8,
            Items.CHECKER_DIAMETER: self.height * 0.8 / 6,
            Items.CHECKER_BUFFER: None
        }

        self.board_canvas = tk.Canvas(
            self, bg='#966F33',
            width=self.items[Items.BOARD_WIDTH],
            height=self.items[Items.BOARD_HEIGHT]
        )
        self.board_canvas.grid(row=0, column=0, sticky="n", rowspan=2)
        self.board: GameBoard = GameBoard(self.board_canvas, items=self.items)
        self.items[Items.BOARD] = self.board

        self.control_panel_frame = tk.Frame(
            self, bg="red",
            width=Setting.CONTROL_PANEL_WIDTH.value,
            height=self.items[Items.BOARD_HEIGHT] / 2
        )
        self.control_panel_frame.grid_propagate(False)
        self.control_panel_frame.grid(row=0, column=1, sticky="n")
        self.control_panel = ControlPanel(self.control_panel_frame, self.items)

        self.offBoard_canvas = tk.Canvas(
            self, bg="blue",
            width=Setting.CONTROL_PANEL_WIDTH.value,
            height=self.items[Items.BOARD_HEIGHT] / 2
        )
        # self.offBoard_canvas.grid(row=1, column=1, sticky="n")
        # self.offBoard = OffBoard(self.offBoard_canvas, self.items)
        # self.items[Items.OFF_BOARD] = self.offBoard

        self.pack()
        self.setup_game()
        self.board_canvas.focus_set()
        self.player_1 = HumanPlayer(EngineChecker.BLACK, self.board, self.items)
        self.player_2 = HumanPlayer(EngineChecker.WHITE, self.board, self.items)
        self.game = Game(self.player_1, self.player_2, False)
        self.game.run()
        ###### TEST ######
        self.toggle = False
        self.checker = Checker(self.board.canvas, "red")
        self.board_canvas.bind('<Up>', lambda _: self.test_add_checker())
        self.board_canvas.bind('<Down>', lambda _: self.test_remove_checker())
        #### END TEST ####

    def setup_game(self):
        self.board_canvas.bind('<space>',
                               lambda _: self.start_game())

    def test_add_checker(self):
        logging.debug(str(self.checker))
        self.board.cones[2].add_checker(self.checker)

    def test_remove_checker(self):
        self.board.cones[2].remove_checker(self.checker)

    def start_game(self):
        print("start")
        self.offBoard.add_checker(Checker(self.offBoard_canvas, "red"))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    root = tk.Tk()
    root.title('Hello, Pong!')
    game = GameUi(root)
    game.mainloop()
