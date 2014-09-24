#!/usr/bin/env python

# from curses import A_BOLD
from git import Git
from log import log
from vi3 import MIDDLE
from vi3 import run, App, View, Color, shrink_str
from vi3_table import Table, Column


class LogView(View):
    def __init__(self, view_stack):
        View.__init__(self, view_stack)

        self._log_entries = []
        self._first_log_entry = 0
        self._selected_log_entry = 0

        self._table = Table()

    @property
    def _last_log_entry(self):
        return self._first_log_entry + self.screen_size.y - 1

    def paint(self):
        self._fetch_log_entries()

        table = self._table
        start = self._first_log_entry
        log_entries = self._log_entries[start:start + self.screen_size.y]

        table.columns.clear()
        table.columns.append(Column("commit", 10, Color.YELLOW))
        table.columns.append(Column("date", 25, Color.BLUE))
        table.columns.append(Column("author_name", 20, Color.MAGENTA))
        table.columns.append(Column("message", self.screen_size.x - 58, Color.WHITE))

        table.rows.clear()
        table.rows.extend(log_entries)
        table.selected_row_index = self._selected_log_entry - start
        table.paint(self.screen)

    def navigate(self):
        log_entry = self._log_entries[self._selected_log_entry]
        view = LogEntryView(self.view_stack, log_entry)
        self.view_stack.push(view)

    def up(self):
        self._selected_log_entry -= 1
        self._do_pagination()
        self.repaint()

    def down(self):
        self._selected_log_entry += 1
        self._do_pagination()
        self.repaint()

    def page_up(self):
        self._selected_log_entry -= self.screen_size.y - 1
        self._do_pagination()
        self.repaint()

    def page_down(self):
        self._selected_log_entry += self.screen_size.y - 1
        self._do_pagination()
        self.repaint()

    def start(self):
        self._selected_log_entry = 0
        self._do_pagination()
        self.repaint()

    def end(self):
        self._selected_log_entry = len(self._log_entries) - 1
        self._do_pagination()
        self.repaint()

    def _fetch_log_entries(self):
        if self._last_log_entry >= len(self._log_entries):
            self._log_entries = git.log(self._selected_log_entry + self.screen_size.y)

    def _do_pagination(self):
        if self._selected_log_entry < 0:
            self._selected_log_entry = 0

        if self._selected_log_entry > self._last_log_entry:
            self._first_log_entry = self._selected_log_entry - self.screen_size.y + 1

        if self._selected_log_entry < self._first_log_entry:
            self._first_log_entry = self._selected_log_entry


class LogEntryView(View):
    def __init__(self, view_stack, log_entry):
        View.__init__(self, view_stack)

        self._log_entry = log_entry
        # show commit header + files: git show f4ec586 --format=medium --name-only
        # show only files in commit: git diff-tree --no-commit-id --name-only -r f4ec58

    def paint(self):
        log_entry = self._log_entry

        self.screen.addstr(0, 0, 'Commit:', Color.YELLOW)
        self.screen.addstr(0, 9, log_entry.commit, Color.BLUE)

        self.screen.addstr(1, 0, 'Author:', Color.YELLOW)
        self.screen.addstr(1, 9, log_entry.author_name, Color.BLUE)

        self.screen.addstr(2, 0, 'Date:', Color.YELLOW)
        self.screen.addstr(2, 9, log_entry.date, Color.BLUE)

        message = log_entry.message
        lines = (len(message) + self.screen_size.x - 1) // self.screen_size.x
        for i in range(0, lines):
            start = i * self.screen_size.x
            end = start + self.screen_size.x

            self.screen.addstr(4 + i, 0, log_entry.message[start:end])

        log('lines: ', lines)

        for i, changed_file in enumerate(self._log_entry.changed_files, 5 + lines):
            changed_file = shrink_str(changed_file, self.screen_size.x, MIDDLE)
            self.screen.addstr(i, 0, changed_file, Color.MAGENTA)


class GitonApp(App):
    def __init__(self):
        App.__init__(self)

    def create_initial_view(self, view_stack_index):
        return LogView(view_stack_index)


git = Git('.')
run(GitonApp())
