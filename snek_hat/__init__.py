from threading import Lock
from threading import Thread
import random
import signal
from time import sleep
from sense_hat import SenseHat


class GracefulInterruptHandler(object):
    def __init__(self, sig=signal.SIGINT):
        self.sig = sig

    def __enter__(self):
        self.interrupted = False
        self.released = False

        self.original_handler = signal.getsignal(self.sig)

        def handler(signum, frame):
            self.release()
            self.interrupted = True

        signal.signal(self.sig, handler)

        return self

    def __exit__(self, type, value, tb):
        self.release()

    def release(self):
        if self.released:
            return False

        signal.signal(self.sig, self.original_handler)
        self.released = True
        return True


class Position():
    def __init__(self):
        self.x = 0
        self.y = 0


class Color(Position):
    def __init__(self):
        super().__init__()
        self.r = 0
        self.g = 0
        self.b = 0


class SnekNode(Color):
    """A snek node.

    Attributes:
        direction (int): 0 = up, 1 = right, 2 = down, 3 = left
    """

    def __init__(self):
        super().__init__()
        self.direction = 0


class AppleNode(Color):
    def __init__(self):
        super().__init__()
        self.r = 100


class SnekBoard():
    def __init__(self):
        self.snek = []
        self.apple = None
        self.mutex = Lock()
        self.next_direction = -1
        self.running = False
        self.sense = SenseHat()
        self.tick_rate = 4

    def gen_apple(self):
        x = random.randint(0, 7)
        y = random.randint(0, 7)
        while True:
            valid = True
            for node in self.snek:
                if not valid:
                    break
                if node.x == x and node.y == y:
                    valid = False
            if not valid:
                x = random.randint(0, 7)
                y = random.randint(0, 7)
            else:
                break
        self.apple = AppleNode()
        self.apple.x = x
        self.apple.y = y

    def _is_coord_in_snek(self, x, y):
        for node in self.snek:
            if node.x == x and node.y == y:
                return True
        return False

    def _next_pos(self, direction, node):
        next_x = node.x
        next_y = node.y
        if direction == 0:
            next_y -= 1
        elif direction == 1:
            next_x += 1
        elif direction == 2:
            next_y += 1
        else:
            next_x -= 1
        return next_x, next_y

    def _is_valid_move(self, x, y):
        if x < 0 or x > 7:
            return False
        elif y < 0 or y > 7:
            return False
        elif self._is_coord_in_snek(x, y):
            return False
        return True

    def move_snek(self):
        """move_snek will attempt to move the snek.

        Returns:
            True if the snake was moved, False otherwise.
        """
        next_direction = self.snek[0].direction if self.next_direction == - \
            1 else self.next_direction
        next_x, next_y = self._next_pos(next_direction, self.snek[0])
        if not self._is_valid_move(next_x, next_y):
            return False

        for index, node in reversed(list(enumerate(self.snek))):
            if index > 0:
                node.x = self.snek[index - 1].x
                node.y = self.snek[index - 1].y
                node.direction = self.snek[index - 1].direction
            else:
                node.x = next_x
                node.y = next_y
                node.direction = next_direction

        return True

    def read_input(self):
        while self.running:
            event = self.sense.stick.wait_for_event()
            # for event in self.sense.stick.get_events():
            if event.action in ['held', 'pressed']:
                if event.direction == 'up':
                    self.next_direction = 0
                elif event.direction == 'right':
                    self.next_direction = 1
                elif event.direction == 'down':
                    self.next_direction = 2
                elif event.direction == 'left':
                    self.next_direction = 3

    def ate_apple(self):
        return self.apple.x == self.snek[0].x and self.apple.y == self.snek[0].y

    def init_snek(self):
        snek_head = SnekNode()
        snek_head.g = 100
        snek_head.direction = 1
        self.snek.append(snek_head)

    def add_snek_node(self):
        next_direction = (self.snek[-1].direction + 2) % 4
        next_x, next_y = self._next_pos(next_direction, self.snek[-1])
        if self._is_valid_move(next_x, next_y):
            new_node = SnekNode()
            new_node.x = next_x
            new_node.y = next_y
            new_node.direction = (next_direction + 2) % 4
            new_node.g = 100
            self.snek.append(new_node)

    def draw(self):
        self.sense.clear()
        for node in self.snek:
            self.sense.set_pixel(node.x, node.y, (node.r, node.g, node.b))
        self.sense.set_pixel(self.apple.x, self.apple.y,
                             (self.apple.r, self.apple.b, self.apple.g))

    def win(self):
        self.sense.clear()
        self.sense.show_message('You win!', text_colour=[100, 100, 100])
        self.running = False

    def lose(self):
        self.sense.clear()
        self.sense.show_message('You lose!', text_colour=[100, 100, 100])
        self.running = False

    def tick(self):
        if self.move_snek():
            if self.ate_apple():
                self.add_snek_node()
                self.gen_apple()
            if len(self.snek) == 64:
                self.win()
                return False
            else:
                self.next_direction = -1
                self.draw()
                return True
        else:
            self.lose()
            return False

    def init_board(self):
        self.snek.clear()
        self.next_direction = -1
        self.init_snek()
        self.gen_apple()
        self.draw()
        self.running = True
        input_thread = Thread(target=self.read_input)
        input_thread.daemon = True
        input_thread.start()

    def easy(self):
        self.tick_rate = 4

    def medium(self):
        self.tick_rate = 6

    def hard(self):
        self.tick_rate = 8

    def countdown(self):
        countdown = 3
        for index in reversed(range(countdown)):
            for num in reversed([temp for temp in range(100)]):
                self.sense.show_letter(
                    str(index + 1), text_colour=[num, num, num])
                sleep(1/100)

    def run(self):
        self.init_board()
        self.countdown()
        update = False
        with GracefulInterruptHandler() as interrupt:
            try:
                while not interrupt.interrupted:
                    if update:
                        if not self.tick():
                            break
                    else:
                        update = True
                    sleep(1 / self.tick_rate)
            except KeyboardInterrupt:
                pass
            self.running = False
            self.sense.clear()
