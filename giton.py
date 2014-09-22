#!/usr/bin/env python

from curses import A_BOLD, A_REVERSE
from vi3 import run, App, View, Color
from git import Git, LogEntry
from log import log


class GitonView(View):
    def __init__(self, view_stack):
        View.__init__(self, view_stack)
        self.selected_log_entry = 0
        self.log_entries = git.log(self.screen_size.y)

    def paint(self):
        View.paint(self)

        start = self.selected_log_entry - self.screen_size.y + 1
        if start < 0:
            start = 0

        log_entries = self.log_entries[start:start + self.screen_size.y]

        max_commit_len = 10
        max_date_len = 25
        max_author_name_len = 20

        for i, log_entry in enumerate(log_entries):
            attr = 0

            if self.selected_log_entry == (start + i):
                attr |= A_REVERSE

            y = i
            x = 0

            self.screen.addnstr(y, x, log_entry.commit, max_commit_len, Color.YELLOW | attr)
            x += max_commit_len + 1

            self.screen.addnstr(y, x, log_entry.date, Color.BLUE | attr)
            x += max_date_len + 1

            self.screen.addnstr(y, x, log_entry.author_name, max_author_name_len,
                                Color.MAGENTA | attr)
            x += max_author_name_len + 1

            self.screen.addnstr(y, x, log_entry.message, self.screen_size.x - x - 1, A_BOLD | attr)

    def start(self):
        self.selected_log_entry = 0
        self.repaint()

    def down(self):
        self.selected_log_entry += 1

        if self.selected_log_entry >= len(self.log_entries):
            self._fetch_log_entries()

        self.repaint()

    def up(self):
        self.selected_log_entry -= 1

        if self.selected_log_entry < 0:
            self.selected_log_entry = 0

        self.repaint()

    def _fetch_log_entries(self):
        self.log_entries = git.log(self.selected_log_entry + self.screen_size.y + 1)
        log("fetched ", len(self.log_entries))


class GitonApp(App):
    def __init__(self):
        App.__init__(self)

    def create_initial_view(self, view_stack_index):
        return GitonView(view_stack_index)


git = Git('/Users/ivan/Liferay/devel/current/liferay-portal')
run(GitonApp())
