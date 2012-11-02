import argparse
import logging
import os
import Queue
import threading

from pyinotify import IN_CLOSE_WRITE, IN_MODIFY, Notifier, WatchManager

from handler import EventHandler
from logs import start_logging
from worker import worker


FIREHOSE = '/var/log/tvrd/tvrd.log'
WEB_LOG = '/var/log/tvrd/web.log'


log = logging.getLogger('tvrd.main')


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('path')
parser.add_argument('--debug', dest='debug', action='store_true')
args = parser.parse_args()


if __name__ == '__main__':
    start_logging(FIREHOSE, WEB_LOG, debug=args.debug)

    q = Queue.Queue()

    config = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.yml'))
    t = threading.Thread(target=worker, args=(q, args.path, config))
    t.daemon = True
    t.start()

    watch_manager = WatchManager()
    handler = EventHandler(args.path, q)

    notifier = Notifier(watch_manager, handler)

    # watch this directory, with mask(s)
    # TODO: Consider IN_MOVED_TO. Deluge doesn't use it but would I?
    mask = IN_MODIFY | IN_CLOSE_WRITE
    wdd = watch_manager.add_watch(args.path, mask, rec=True, auto_add=True)

    # setup options
    notifier.loop(daemonize=False)

