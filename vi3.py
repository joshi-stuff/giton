#!/usr/bin/env python

import curses
from log import log


class Position:
    def __init__(self, y, x):
        self.y = y
        self.x = x


class App:
    def __init__(self):
        self.commands = CommandRegistry()

        self.add_command(Command('h', 'h', 'Help', self.help))
        self.add_command(Command('q', 'q', 'Quit', self.quit))

    def create_view_stack(self, index):
        view_stack = ViewStack(self, index)
        view_stack.push(self.create_initial_view(view_stack))
        return view_stack

    def create_initial_view(self, view_stack):
        return View(view_stack)

    def run(self, screen):
        self.screen = screen
        maxyx = self.screen.getmaxyx()
        self.screen_size = Position(maxyx[0], maxyx[1])
        self.view_stacks = {0: self.create_view_stack(0)}
        self.selected_view_stack = None
        self.select_view_stack(0)

        while True:
            self.selected_view_stack.repaint()
            screen.refresh()
            key = screen.getkey()

            if key == ' ':
                self.run_command()

            elif key == '\x7f':  # Backspace
                self.back()

            elif key == '\n':
                self.navigate()

            elif key == 'KEY_UP':
                self.up()

            elif key == 'KEY_DOWN':
                self.down()

            elif key == 'KEY_LEFT':
                self.left()

            elif key == 'KEY_RIGHT':
                self.right()

            elif key == '\x02':  # Ctrl-B
                self.page_up()

            elif key == '\x06':  # Ctrl-F
                self.page_down()

            elif key == 'g':
                if screen.getkey() == 'g':
                    self.start()

            elif key == 'G':
                self.end()

            elif key.startswith('KEY_F('):
                index = int(key[6:-1]) - 1
                self.select_view_stack(index)

            else:
                command = self.get_command(key)

                if command is not None:
                    command.run()

    def run_command(self):
        x = self.screen_size.x // 8
        y = self.screen_size.y // 3 - 1
        w = 6 * self.x // 8
        h = 3

        helpmsg = "(search for command; try help)"

        box = curses.newwin(h, w, y, x)
        box.border()
        box.addstr(1, 1, '_', Color.WHITE | curses.A_BLINK | curses.A_UNDERLINE)
        box.addstr(1, w - len(helpmsg) - 1, helpmsg, Color.YELLOW)
        box.refresh()

        cbox = curses.newwin(14, w, y+3, x)

        pattern = ''
        commands = []
        selected_command_index = -1

        while True:
            key = self.screen.getkey()

            if key == '\x7f':  # Backspace
                pattern = pattern[:-1]

            elif key == '\x1b':  # Esc
                break

            elif key == 'KEY_UP':
                selected_command_index -= 1
                if selected_command_index == -1:
                    selected_command_index = 0

            elif key == 'KEY_DOWN':
                selected_command_index += 1
                if selected_command_index >= len(commands):
                    selected_command_index = len(commands) - 1

            elif key == '\n':

                break

            else:
                # if len(key)==1:
                pattern += key
                selected_command_index = -1

            box.clear()
            box.border()

            if len(pattern) == 0:
                box.addstr(1, w - len(helpmsg) - 1, helpmsg, Color.YELLOW)
                box.addstr(1, 1, '_', Color.WHITE | curses.A_BLINK | curses.A_UNDERLINE)

            else:
                box.addnstr(1, 1, pattern[-w+3:], w-2, Color.WHITE)
                box.addstr(1, min(len(pattern)+1, w-2), '_',
                           Color.WHITE | curses.A_BLINK | curses.A_UNDERLINE)

            commands = []

            if len(pattern) > 0:
                commands = self.search_commands(pattern)

            if (len(commands) > 0) and (selected_command_index == -1):
                selected_command_index = 0

            cbox.clear()
            cbox.border()

            for i, command in enumerate(commands):
                text = '[' + command.shortcut + '] ' + command.name
                if i == selected_command_index:
                    cbox.addnstr(i+1, 1, text, w-2, Color.YELLOW | curses.A_REVERSE)

                else:
                    cbox.addnstr(i+1, 1, text, w-2, Color.YELLOW)

            box.refresh()
            cbox.refresh()

        box.erase()
        cbox.erase()

        box.refresh()
        cbox.refresh()

        if selected_command_index != -1:
            commands[selected_command_index].run()

    def back(self):
        pass

    def navigate(self):
        pass

    def up(self):
        self.selected_view_stack.up()

    def down(self):
        self.selected_view_stack.down()

    def left(self):
        pass

    def right(self):
        pass

    def page_up(self):
        pass

    def page_down(self):
        pass

    def start(self):
        self.selected_view_stack.start()

    def end(self):
        self.selected_view_stack.end()

    def select_view_stack(self, index):
        log('select_view_stack ', index)
        if self.view_stacks.get(index) is self.selected_view_stack:
            return

        if self.view_stacks.get(index) is None:
            log('select_view_stack ', 'create_view_stack')
            self.view_stacks[index] = self.create_view_stack(index)

        if self.selected_view_stack is not None:
            log('select_view_stack ', 'deactivate')
            self.selected_view_stack.deactivate()

        self.selected_view_stack = self.view_stacks[index]
        self.selected_view_stack.activate()
        log('select_view_stack ', 'clear + activate')

    def add_command(self, command):
        self.commands.add(command)

    def get_commands(self):
        commands = self.selected_view_stack.get_commands()
        commands += self.commands.get_all()
        return commands

    def search_commands(self, pattern):
        commands = self.selected_view_stack.search_commands(pattern)
        commands += self.commands.search(pattern)
        return commands

    def get_command(self, key):
        command = self.selected_view_stack.get_command(key)

        if command is None:
            command = self.commands.get(key)

        return command

    def quit(self):
        exit()

    def help(self):
        x = self.y // 8
        y = self.y // 8
        w = 6 * self.y // 8
        h = 6 * self.y // 8

        helpmsg = '(press ESC to close)'

        box = curses.newwin(h, w, y, x)
        box.border()
        box.addstr(h-2, w - len(helpmsg) - 1, helpmsg, Color.YELLOW)
        box.addstr(2, 3, 'Available commands:', Color.WHITE)

        commands = self.get_commands()
        for i, command in enumerate(commands):
            box.addstr(i+4, 7, '[' + command.shortcut + '] ' + command.name)

        box.refresh()

        while self.screen.getkey() != '\x1b':
            pass

        box.erase()
        box.refresh()


class ViewStack:
    def __init__(self, app, index):
        self.app = app
        self.index = index
        self.views = []
        self.commands = CommandRegistry()

    def push(self, view):
        if len(self.views) > 0:
            self.views[-1].deactivate()

        self.views.append(view)

        self.views[-1].activate()

    def repaint(self):
        self.views[-1].repaint()

    def paint(self):
        self.views[-1].paint()

    def activate(self):
        self.views[-1].activate()

    def deactivate(self):
        self.views[-1].deactivate()

    def up(self):
        self.views[-1].up()

    def down(self):
        self.views[-1].down()

    def start(self):
        self.views[-1].start()

    def end(self):
        self.views[-1].end()

    def add_command(self, command):
        self.commands.add(command)

    def get_commands(self):
        commands = self.views[-1].get_commands()
        commands += self.commands.get_all()
        return commands

    def search_commands(self, pattern):
        commands = self.views[-1].search_commands(pattern)
        commands += self.commands.search(pattern)
        return commands

    def get_command(self, key):
        command = self.views[-1].get_command(key)

        if command is None:
            command = self.commands.get(key)

        return command


class View:
    def __init__(self, view_stack):
        self.view_stack = view_stack
        self.app = view_stack.app
        self.screen = view_stack.app.screen
        self.screen_size = view_stack.app.screen_size
        self.commands = CommandRegistry()

    def repaint(self):
        self.screen.clear()
        self.paint()

    def paint(self):
        pass

    def activate(self):
        self.repaint()

    def deactivate(self):
        pass

    def up(self):
        pass

    def down(self):
        pass

    def start(self):
        pass

    def end(self):
        pass

    def add_command(self, command):
        self.commands.add(command)

    def get_commands(self):
        return self.commands.get_all()

    def search_commands(self, pattern):
        return self.commands.search(pattern)

    def get_command(self, key):
        return self.commands.get(key)


class Command:
    def __init__(self, key, shortcut, name, handler):
        self.key = key
        self.shortcut = shortcut
        self.name = name
        self._handler = handler

    def run(self):
        self._handler()


class CommandRegistry:
    def __init__(self):
        self.commands = []

    def add(self, command):
        self.commands.append(command)

    def get_all(self):
        return self.commands[:]

    def search(self, pattern):
        commands = []

        for command in self.commands:
            if command.name.lower().startswith(pattern.lower()):
                commands.append(command)

        for command in self.commands:
            if (pattern.lower() in command.name.lower()) and (command not in commands):
                commands.append(command)

        return commands

    def get(self, key):
        for command in self.commands:
            if command.key == key:
                return command

        return None


class Color:
    WHITE = None
    BLUE = None
    GREEN = None
    RED = None
    YELLOW = None
    CYAN = None
    MAGENTA = None

    @staticmethod
    def init():
        curses.ESCDELAY = 25

        curses.init_pair(curses.COLOR_BLUE, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(curses.COLOR_GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(curses.COLOR_RED, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(curses.COLOR_YELLOW, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(curses.COLOR_CYAN, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(curses.COLOR_MAGENTA, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

        Color.WHITE = curses.color_pair(0)
        Color.BLUE = curses.color_pair(curses.COLOR_BLUE)
        Color.GREEN = curses.color_pair(curses.COLOR_GREEN)
        Color.RED = curses.color_pair(curses.COLOR_RED)
        Color.YELLOW = curses.color_pair(curses.COLOR_YELLOW)
        Color.CYAN = curses.color_pair(curses.COLOR_CYAN)
        Color.MAGENTA = curses.color_pair(curses.COLOR_MAGENTA)


_app = None


def _main(screen):
    global _app

    Color.init()
    curses.curs_set(0)

    _app.run(screen)


def run(app):
    global _app

    _app = app
    curses.wrapper(_main)
