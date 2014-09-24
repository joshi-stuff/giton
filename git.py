import subprocess
import os


class Git:
    def __init__(self, dir):
        self.dir = dir

    def log(self, count):
        GIT_COMMIT_FIELDS = ['id', 'author_name', 'author_email', 'date', 'message']
        GIT_LOG_FORMAT = ['%h', '%an', '%ae', '%ci', '%s']
        GIT_LOG_FORMAT = '%x1f'.join(GIT_LOG_FORMAT) + '%x1e'

        output = self._git('log -n ' + str(count) + ' --format="%s"' % GIT_LOG_FORMAT)

        output = str(output)
        output = output.strip('\n\x1e').split("\x1e")
        output = [row.strip().split("\x1f") for row in output]
        output = [dict(zip(GIT_COMMIT_FIELDS, row)) for row in output]

        log_entries = []
        for entry in output:
            log_entries.append(LogEntry(self, entry['id'], entry['author_name'], entry['date'],
                                        entry['message']))

        return log_entries

    def _get_changed_files(self, log_entry):
        output = self._git('diff-tree --no-commit-id --name-only -r ' + log_entry.commit)
        return output.split('\n')

    def _git(self, gitcmd):
        old_dir = os.getcwd()
        os.chdir(self.dir)

        p = subprocess.Popen('git ' + gitcmd, shell=True, stdout=subprocess.PIPE,
                             universal_newlines=True)
        (output, _) = p.communicate()

        os.chdir(old_dir)

        return output


class LogEntry:
    def __init__(self, git, commit, author_name, date, message):
        self._git = git
        self.commit = commit
        self.author_name = author_name
        self.date = date
        self.message = message
        self._changed_files = None

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
    def changed_files(self):
        if self._changed_files is None:
            self._changed_files = self._git._get_changed_files(self)

        return self._changed_files
