import argparse
import logging
import os
import Queue as queue
import sys
import time
import threading

from watchdog.observers import Observer

from .utils import CreatedFileEventHandler, start_logging, worker


log = logging.getLogger('tvrd.main')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('path')
    parser.add_argument('--debug', dest='debug', action='store_true')
    args = parser.parse_args()

    start_logging(args.debug)

    config = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.yml'))
    q = queue.Queue()

    t = threading.Thread(target=worker, args=(q, args.path, config))
    t.daemon = True
    t.start()

    observer = Observer()
    observer.schedule(CreatedFileEventHandler(), path=sys.argv[1], recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
