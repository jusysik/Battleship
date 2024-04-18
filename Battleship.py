from random import randint


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Выстрел за пределами игрового поля"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, ship_length, orientation):
        self.bow = bow
        self.ship_length = ship_length
        self.orientation = orientation
        self.lives = ship_length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.ship_length):
            current_x = self.bow.x
            current_y = self.bow.y

            if self.orientation == 0:
                current_x += i

            elif self.orientation == 1:
                current_y += i

            ship_dots.append(Dot(current_x, current_y))

        return ship_dots

    def shooting(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hide=False, size=6):
        self.size = size
        self.hide = hide

        self.count_of_dead = 0  # Количество пораженных кораблей?

        self.field = [["O"] * size for _ in range(size)]

        self.busy_dots = []
        self.ships = []

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hide:
            res = res.replace("■", "O")
        return res

    def out_of_field(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out_of_field(cur)) and cur not in self.busy_dots:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy_dots.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out_of_field(d) or d in self.busy_dots:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy_dots.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out_of_field(d):
            raise BoardOutException()

        if d in self.busy_dots:
            raise BoardUsedException()

        self.busy_dots.append(d)

        for ship in self.ships:
            if ship.shooting(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count_of_dead += 1
                    self.contour(ship, verb=True)
                    print("Корабль полностью потоплен")
                    return False
                else:
                    print("Вы ранили корабль")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy_dots = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход противника: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            coordinates = input("Ваш ход: ").split()

            if len(coordinates) != 2:
                print(" Введите две координаты! ")
                continue

            x, y = coordinates

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        self.list_of_navy = [4, 3, 2, 2, 1, 1, 1]
        pl = self.random_board()
        co = self.random_board()
        co.hide = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        board = Board(size=self.size)
        attempts = 0
        for ship_length in self.list_of_navy:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), ship_length, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    @staticmethod
    def greeting():
        print("-------------------")
        print("    МОРСКОЙ БОЙ    ")
        print("-------------------")
        print(" Формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def print_boards(self):
        print("-" * 20)
        print("Поле Игрока:")
        print(self.us.board)
        print("-" * 20)
        print("Поле противника:")
        print(self.ai.board)
        print("-" * 20)

    def loop(self):
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print("Ходит Игрок!")
                repeat = self.us.move()
            else:
                print("Ходит Противник!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count_of_dead == 7:
                self.print_boards()
                print("-" * 20)
                print("Игрок выиграл!")
                break

            if self.us.board.count_of_dead == 7:
                self.print_boards()
                print("-" * 20)
                print("Противник выиграл!")
                break
            num += 1

    def start(self):
        self.greeting()
        self.loop()


g = Game()
g.start()