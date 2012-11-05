import logging
import os
import time

from tvrenamr.config import Config
from tvrenamr.episode import Episode
from tvrenamr.main import TvRenamr

from deluge import remove_torrent


log = logging.getLogger('tvrd.worker')


def rename(item, working_dir, config_path):
    tv = TvRenamr(working_dir, Config(config_path))

    episode = Episode(**tv.extract_details_from_file(item))
    episode.title = tv.retrieve_episode_name(episode)
    episode.show_name = tv.format_show_name(episode.show_name)

    path = tv.build_path(episode)

    return tv.rename(item, path)


def worker(queue, working_dir, config_path):
    while True:
        item = queue.get()  # should be file or folder
        if os.path.isfile(item):
            item = os.path.split(item)[1]
        log.debug('Found: {0}'.format(item))
        try:
            remove_torrent(item)
            destination = rename(item, working_dir, config_path)
            log.log(90, os.path.split(destination)[1])
        except Exception as e:
            for msg in e.args:
                kwargs = {'type': e.__repr__()[:e.__repr__().index('(')], 'error': msg}
                log.critical('{type}: {error}'.format(**kwargs))
            continue
        time.sleep(1)  # don't use 100% cpu
        queue.task_done()

