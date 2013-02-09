import logging
import os
import time

from pyinotify import ProcessEvent


log = logging.getLogger('tvrd.handler')


class EventHandler(ProcessEvent):
    excludes = ('.AppleDouble',)
    types = ('.avi', '.mkv', '.mp4')

    def __init__(self, working_dir, queue):
        log.debug('create handler')
        self.queue = queue
        self.working_dir = working_dir

    def is_excluded(self, path):
        for e in self.excludes:
            if e in path:
                yield True

    def is_valid(self, path):
        if os.path.isdir(path) and not self.is_excluded(path):
            for fn in os.listdir(path):
                if os.path.splitext(path)[1] in self.types:
                    log.debug('folder: {0}'.format(path))
                    return True
        return os.path.splitext(path)[1] in self.types

    def process_IN_MOVED_TO(self, event):
        log.debug('Detected file: {0}'.format(event.name))
        if self.is_valid(event.name):
            log.info('Queued file: {0}'.format(event.name))
            self.queue.put(event.pathname)
        time.sleep(0.5)

