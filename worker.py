import logging
import os
import time

from tvrenamr.config import Config
from tvrenamr.episode import Episode
from tvrenamr.main import TvRenamr

from deluge import remove_torrent


log = logging.getLogger('Watcher')


class Worker(object):
    def __call__(self, queue, working_dir, config_path):
        while True:
            item = os.path.split(queue.get())[1]
            log.debug('Found: {0}'.format(item))
            try:
                path = ''
                remove_torrent(path)
                self.rename(item, working_dir, config_path)
                # TODO: log destination of renamed file
            except Exception as e:
                for msg in e.args:
                    log.critical('Error: {0}'.format(msg))
                continue
            time.sleep(1)  # don't use 100% cpu
            queue.task_done()

    def rename(self, item, working_dir, config_path):
        tv = TvRenamr(working_dir, Config(config_path))

        episode = Episode(**tv.extract_details_from_file(item))
        episode.title = tv.retrieve_episode_name(episode)
        episode.show_name = tv.format_show_name(episode.show_name)

        path = tv.build_path(episode)

        tv.rename(item, path)

