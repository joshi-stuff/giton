#!/usr/bin/env python

from vi3 import run, App, View, Color
from vi3_table import Table, Column
from git import Git
# from log import log


class GitonView(View):
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


class GitonApp(App):
    def __init__(self):
        App.__init__(self)

    def create_initial_view(self, view_stack_index):
        return GitonView(view_stack_index)


git = Git('/Users/ivan/Liferay/devel/current/liferay-portal')
run(GitonApp())
