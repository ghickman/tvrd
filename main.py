import argparse
import logging
import os
import Queue
import threading
import time

from pyinotify import IN_CLOSE_WRITE, IN_MODIFY, Notifier, WatchManager
from tvrenamr.config import Config
from tvrenamr.episode import Episode
from tvrenamr.main import TvRenamr

from handler import EventHandler
from logs import start_logging


EXCLUDES = '.AppleDouble'
LOG_FILE = '/var/log/tvrd/tvrd.log'


log = logging.getLogger('Watcher')


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('path')
parser.add_argument('--debug', dest='debug', action='store_true')
args = parser.parse_args()


def worker(working_dir, config_path):
    while True:
        item = os.path.split(q.get())[1]
        log.debug('Found: {0}'.format(item))
        try:
            tv = TvRenamr(working_dir, Config(config_path))

            episode = Episode(**tv.extract_details_from_file(item))
            episode.title = tv.retrieve_episode_name(episode)
            episode.show_name = tv.format_show_name(episode.show_name)

            path = tv.build_path(episode)

            tv.rename(item, path)
            # TODO: log destination of renamed file
        except Exception as e:
            for msg in e.args:
                log.critical('Error: {0}'.format(msg))
            continue
        time.sleep(1)  # don't use 100% cpu
        q.task_done()


def exclude(path):
    for e in EXCLUDES:
        if e in path:
            return True


if __name__ == '__main__':
    start_logging(LOG_FILE, debug=args.debug)

    q = Queue.Queue()

    config = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.yml'))
    t = threading.Thread(target=worker, args=(args.path, config))
    t.daemon = True
    t.start()

    watch_manager = WatchManager()
    handler = EventHandler(args.path, q)

    notifier = Notifier(watch_manager, handler)

    # watch this directory, with mask(s)
    mask = IN_MODIFY | IN_CLOSE_WRITE
    wdd = watch_manager.add_watch(args.path, mask, rec=True)

    # setup options
    notifier.loop(daemonize=False)

