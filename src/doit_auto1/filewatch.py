"""Watch for modifications of file-system
use by cmd_auto module
"""

import os.path
import watchfiles


class FileModifyWatcher(object):
    """Use watchfiles to watch file-system for file modifications

    Usage:
    1) subclass the method handle_event, action to be performed
    2) create an object passing a list of files to be watched
    3) call the loop method
    """

    def __init__(self, path_list):
        """@param file_list (list-str): files to be watched"""
        self.file_list = set()
        self.watch_dirs = set()  # all dirs to be watched
        self.notify_dirs = set()  # dirs that generate notification whatever file
        for filename in path_list:
            path = os.path.abspath(filename)
            if os.path.isfile(path):
                self.file_list.add(path)
                self.watch_dirs.add(os.path.dirname(path))
            else:
                self.notify_dirs.add(path)
                self.watch_dirs.add(path)

    def _handle(self, changes):
        """calls implementation handler"""
        if any(
            change[1] in self.file_list
            or os.path.dirname(change[1]) in self.notify_dirs
            for change in changes
        ):
            return self.handle_event(changes)

    def handle_event(self, event):  # pragma: no cover
        """this should be sub-classed """
        raise NotImplementedError

    def loop(self):
        """Infinite loop watching for file modifications"""

        for changes in watchfiles.watch(*self.watch_dirs):
            self._handle(changes)
