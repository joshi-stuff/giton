import subprocess
import os
import curses


class Git:
    def __init__(self, dir):
        self.dir = dir

    def log(self, count, start_commit=''):
        GIT_COMMIT_FIELDS = ['id', 'author_name', 'author_email', 'date', 'message']
        GIT_LOG_FORMAT = ['%h', '%an', '%ae', '%ci', '%s']
        GIT_LOG_FORMAT = '%x1f'.join(GIT_LOG_FORMAT) + '%x1e'

        output = self._git('log -n ' + str(count) + ' ' + start_commit +
                           ' --format="%s"' % GIT_LOG_FORMAT)

        output = str(output)
        output = output.strip('\n\x1e').split("\x1e")
        output = [row.strip().split("\x1f") for row in output]
        output = [dict(zip(GIT_COMMIT_FIELDS, row)) for row in output]

        log_entries = []
        for entry in output:
            log_entries.append(LogEntry(self, entry['id'], entry['author_name'], entry['date'],
                                        entry['message']))

        return log_entries

    def status(self):
        output = self._git('status --porcelain')
        lines = output.split('\n')

        index_file_statuses = []
        working_file_statuses = []

        for line in lines:
            index_status = line[0:1]
            working_status = line[1:2]
            path = line[3:]

            index_file_statuses.append(FileStatus(path, index_status))
            working_file_statuses.append(FileStatus(path, working_status))

        return Status(index_file_statuses, working_file_statuses)

    def difftool(self, start_commit, end_commit, file):
        self._git_exec('difftool -y -t vimdiff ' + start_commit + '..' + end_commit + ' ' + file)

    def interactive_rebase(self, log_entry):
        self._git_exec('rebase -i ' + log_entry.commit)

    def squash(self, log_entry, message):
        pass

    def delete(self, log_entry):
        pass

    def _get_file_statuses(self, log_entry):
        output = self._git('diff-tree --no-commit-id --name-only -r ' + log_entry.commit)
        changed_files = output.split('\n')

        if changed_files[-1] == '':
            changed_files = changed_files[:-1]

        file_statuses = []
        for changed_file in changed_files:
            file_statuses.append(FileStatus(changed_file, FileStatus.MODIFIED))

        return file_statuses

    def _git(self, gitcmd):
        old_dir = os.getcwd()
        os.chdir(self.dir)

        p = subprocess.Popen('git ' + gitcmd, shell=True, stdout=subprocess.PIPE,
                             universal_newlines=True)
        (output, _) = p.communicate()

        os.chdir(old_dir)

        return output

    def _git_exec(self, gitcmd):
        # TODO: resetear el terminal en curses
        old_dir = os.getcwd()
        os.chdir(self.dir)

        p = subprocess.Popen('git ' + gitcmd, shell=True)
        p.wait()

        os.chdir(old_dir)

        curses.reset_prog_mode()


class LogEntry:
    def __init__(self, git, commit, author_name, date, message):
        self._git = git
        self.commit = commit
        self.author_name = author_name
        self.date = date
        self.message = message
        self._file_statuses = None

    def __getitem__(self, key):
        if key == 'commit':
            return self.commit
        elif key == 'author_name':
            return self.author_name
        elif key == 'date':
            return self.date
        elif key == 'message':
            return self.message
        else:
            raise Exception("Unknown attribute: " + key)

    @property
    def file_statuses(self):
        if self._file_statuses is None:
            self._file_statuses = self._git._get_file_statuses(self)

        return self._file_statuses


class Status:
    def __init__(self, index_file_statuses, working_file_statuses):
        self.index_file_statuses = index_file_statuses
        self.working_file_statuses = working_file_statuses


class FileStatus:
    UNMODIFIED = ' '
    MODIFIED = 'M'
    ADDED = 'A'
    DELETED = 'D'
    RENAMED = 'R'
    COPIED = 'C'
    UPDATED = 'U'

    def __init__(self, path, status):
        self.path = path
        self.status = status
