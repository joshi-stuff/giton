#!/usr/bin/env python

from curses import A_REVERSE
from git import Git
# from log import log
from vi3 import MIDDLE
from vi3 import run, shrink_str
from vi3 import App, View, Color, Command
from vi3_table import Table, Column


class LogView(View):
    def __init__(self, view_stack):
        View.__init__(self, view_stack)

        self._log_entries = []
        self._first_log_entry = 0
        self._selected_log_entry = 0
        self._table = Table()

        self.add_command(Command('d', 'd', 'Delete commit', self._delete_commit))
        self.add_command(Command('i', 'i', 'Interactive rebase', self._interactive_rebase))
        self.add_command(Command('s', 's', 'Squash with previous', self._squash))

    @property
    def _last_log_entry(self):
        return self._first_log_entry + self.screen_size.y - 1

    def paint(self):
        self._fetch_log_entries()

        table = self._table
        start = self._first_log_entry
        screen_size = self.screen_size
        log_entries = self._log_entries[start:start + screen_size.y]

        table.columns.clear()
        table.columns.append(Column("commit", 10, Color.YELLOW))
        table.columns.append(Column("date", 25, Color.BLUE))
        table.columns.append(Column("author_name", 20, Color.MAGENTA))
        table.columns.append(Column("message", screen_size.x - 58, Color.WHITE))

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
        while self._last_log_entry >= len(self._log_entries):
            prev_log_entries_count = len(self._log_entries)

            self._log_entries = git.log(self._selected_log_entry + self.screen_size.y)

            if len(self._log_entries) == prev_log_entries_count:
                break

    def _do_pagination(self):
        if self._selected_log_entry < 0:
            self._selected_log_entry = 0

        if self._selected_log_entry > self._last_log_entry:
            self._first_log_entry = self._selected_log_entry - self.screen_size.y + 1

        if self._selected_log_entry >= len(self._log_entries):
            self._selected_log_entry = len(self._log_entries) - 1

        if self._selected_log_entry < self._first_log_entry:
            self._first_log_entry = self._selected_log_entry

    def _reload(self):
        self._log_entries = []
        self._fetch_log_entries()
        self.repaint()

    def _interactive_rebase(self):
        log_entry = self._log_entries[self._selected_log_entry]
        git.interactive_rebase(log_entry)
        self._reload()

    def _squash(self):
        log_entry = self._log_entries[self._selected_log_entry]
        prev_log_entry = git.log(2, log_entry.commit)[1]
        git.squash(log_entry, prev_log_entry.message)
        self._reload()

    def _delete_commit(self):
        log_entry = self._log_entries[self._selected_log_entry]
        git.delete(log_entry)
        self._reload()


class LogEntryView(View):
    def __init__(self, view_stack, log_entry):
        View.__init__(self, view_stack)

        self._log_entry = log_entry
        self._file_statuses = log_entry.file_statuses
        self._selected_file_status = 0
        # show commit header + files: git show f4ec586 --format=medium --name-only
        # show only files in commit: git diff-tree --no-commit-id --name-only -r f4ec58

    def paint(self):
        log_entry = self._log_entry
        screen = self.screen
        screen_size = self.screen_size

        screen.addstr(0, 0, 'Commit:', Color.YELLOW)
        screen.addstr(0, 9, log_entry.commit, Color.BLUE)

        screen.addstr(1, 0, 'Author:', Color.YELLOW)
        screen.addstr(1, 9, log_entry.author_name, Color.BLUE)

        screen.addstr(2, 0, 'Date:', Color.YELLOW)
        screen.addstr(2, 9, log_entry.date, Color.BLUE)

        message = log_entry.message
        lines = (len(message) + screen_size.x - 1) // screen_size.x
        for i in range(0, lines):
            start = i * screen_size.x
            end = start + screen_size.x

            screen.addstr(4 + i, 0, log_entry.message[start:end])

        for i, file_status in enumerate(self._file_statuses):
            attr = 0

            if i == self._selected_file_status:
                attr |= A_REVERSE

            changed_file = shrink_str(file_status.path, screen_size.x, MIDDLE)
            screen.addstr(lines + 5 + i, 0, changed_file, Color.MAGENTA | attr)

    def up(self):
        self._selected_changed_file -= 1
        if self._selected_changed_file < 0:
            self._selected_changed_file = 0
        self.repaint()

    def down(self):
        self._selected_file_status += 1

        file_statuses_count = len(self._file_statuses)
        if self._selected_file_status > (file_statuses_count - 1):
            self._selected_file_status = file_statuses_count - 1

        self.repaint()

    def navigate(self):
        log_entry = self._log_entry
        file_status = self._file_statuses[self._selected_file_status]
        prev_log_entry = git.log(2, log_entry.commit)[1]

        git.difftool(log_entry.commit, prev_log_entry.commit, file_status.path)
        # git difftool -y -t vimdiff f78df48..2fb0c73 <file>


class GitonApp(App):
    def __init__(self):
        App.__init__(self)

    def create_initial_view(self, view_stack_index):
        return LogView(view_stack_index)


git = Git('.')
run(GitonApp())
