#!/usr/bin/env python

import subprocess
import os


class Git:
    def __init__(self, dir):
        self.dir = dir

    def log(self, count):
        GIT_COMMIT_FIELDS = ['id', 'author_name', 'author_email', 'date', 'message']
        GIT_LOG_FORMAT = ['%h', '%an', '%ae', '%ci', '%s']
        GIT_LOG_FORMAT = '%x1f'.join(GIT_LOG_FORMAT) + '%x1e'

        old_dir = os.getcwd()

        os.chdir(self.dir)
        p = subprocess.Popen('git log -n ' + str(count) + ' --format="%s"' % GIT_LOG_FORMAT,
                             shell=True, stdout=subprocess.PIPE, universal_newlines=True)

        (output, _) = p.communicate()

        output = str(output)
        output = output.strip('\n\x1e').split("\x1e")
        output = [row.strip().split("\x1f") for row in output]
        output = [dict(zip(GIT_COMMIT_FIELDS, row)) for row in output]

        os.chdir(old_dir)

        log_entries = []

        for entry in output:
            log_entries.append(LogEntry(entry['id'], entry['author_name'], entry['date'],
                                        entry['message']))

        return log_entries


class LogEntry:
    def __init__(self, commit, author_name, date, message):
        self.commit = commit
        self.author_name = author_name
        self.date = date
        self.message = message
