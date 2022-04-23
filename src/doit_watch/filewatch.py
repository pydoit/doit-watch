"""Watch for modifications of file-system
use by cmd_watch module
"""

import os.path
from typing import Iterable, Set, Tuple
import watchfiles

Change = Tuple[watchfiles.Change, str]
ChangeSet = Set[Change]


class FileModifyWatcher(object):
    """Use watchfiles to watch file-system for file modifications

    Usage:
    1) subclass the method handle_event, action to be performed
    2) create an object passing a list of files to be watched
    3) call the loop method
    """

    #: explicit file paths to watch
    file_list: Set[str]
    #: all dirs to be watched
    watch_dirs: Set[str]
    #: dirs that generate notification whatever file
    notify_dirs: Set[str]

    def __init__(self, path_list: Iterable[str]):
        """@param file_list (list-str): files to be watched"""
        self.file_list = set()
        self.watch_dirs = set()
        self.notify_dirs = set()

        for filename in path_list:
            path = os.path.abspath(filename)
            if os.path.isfile(path):
                self.file_list.add(path)
                self.watch_dirs.add(os.path.dirname(path))
            else:
                self.notify_dirs.add(path)
                self.watch_dirs.add(path)

    def _handle(self, changes: ChangeSet) -> bool:
        """calls implementation handler"""
        if any(
            change[1] in self.file_list
            or os.path.dirname(change[1]) in self.notify_dirs
            for change in changes
        ):
            self.handle_event(changes)
            return True
        return False

    def handle_event(self, event: ChangeSet) -> bool:  # pragma: no cover
        """this should be sub-classed"""
        raise NotImplementedError

    def loop(self) -> None:
        """Infinite loop watching for file modifications"""

        for changes in watchfiles.watch(*self.watch_dirs):
            self._handle(changes)
