import argparse
import logging
import os
import Queue
import threading

from pyinotify import IN_CLOSE_WRITE, IN_MODIFY, Notifier, WatchManager

from handler import EventHandler
from logs import start_logging
from worker import worker


EXCLUDES = '.AppleDouble'
LOG_FILE = '/var/log/tvrd/tvrd.log'


log = logging.getLogger('tvrd.main')


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('path')
parser.add_argument('--debug', dest='debug', action='store_true')
args = parser.parse_args()


def exclude(path):
    for e in EXCLUDES:
        if e in path:
            return True


if __name__ == '__main__':
    start_logging(LOG_FILE, debug=args.debug)

    q = Queue.Queue()

    config = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.yml'))
    t = threading.Thread(target=worker, args=(q, args.path, config))
    t.daemon = True
    t.start()

    watch_manager = WatchManager()
    handler = EventHandler(args.path, q)

    notifier = Notifier(watch_manager, handler)

    # watch this directory, with mask(s)
    mask = IN_MODIFY | IN_CLOSE_WRITE
    wdd = watch_manager.add_watch(args.path, mask, rec=True, auto_add=True)

    # setup options
    notifier.loop(daemonize=False)

