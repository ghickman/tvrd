import logging
import os
import time

from tvrenamr.config import Config
from tvrenamr.episode import Episode
from tvrenamr.main import TvRenamr
from watchdog.events import FileSystemEventHandler

from .downloads import remove_torrent


class CreatedFileEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        q.put(event.src_path)


def start_logging(debug):
    # add the custom levels
    logging.addLevelName(22, 'MINIMAL')
    logging.addLevelName(26, 'SHORT')

    logging.config.dictConfig({
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "simple": {
                    "format": '%(asctime)-15s %(levelname)-10s %(name)-11s %(message)s',
                },
            },
            "handlers": {
                "console": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "simple",
                },
            },
            "loggers": {
                "requests": {
                    "propagate": False,
                },
            },
            "root": {
                "level": logging.DEBUG if debug else logging.CRITICAL,
                "handlers": ["console"],
            },
        })


def worker(queue, working_dir, config_path):
    log = logging.getLogger('tvrd.worker')
    while True:
        item = queue.get()  # should be file or folder
        if os.path.isfile(item):
            item = os.path.split(item)[1]
        log.debug('Found: {0}'.format(item))
        try:
            tv = TvRenamr(working_dir, Config(config_path))
            episode = Episode(**tv.extract_details_from_file(item))
            episode.title = tv.retrieve_episode_name(episode)
            episode.show_name = tv.format_show_name(episode.show_name)
            destination = tv.rename(item, tv.build_path(episode))

            remove_torrent(item)

            log.log(21, os.path.splitext(os.path.split(destination)[1])[0])
        except Exception as e:
            for msg in e.args:
                kwargs = {'type': e.__repr__()[:e.__repr__().index('(')], 'error': msg}
                log.critical('{type}: {error}'.format(**kwargs))
            continue
        time.sleep(1)  # don't use 100% cpu
        queue.task_done()
