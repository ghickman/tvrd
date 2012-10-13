import json
import logging
import os

import requests


log = logging.getLogger('Watcher')


def remove_torrent(self, path):
    url = 'http://192.168.0.2:1337/json'
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

    def get_payload(method, params):
        return {'method': method, 'params': params, 'id': 1}

    # login
    payload = get_payload('auth.login', [os.environ['DELUGE_PASSWORD']])
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    cookies = r.cookies
    if r.ok:
        log.debug('Deluge: Logged In')

    def request(method, params=None):
        if not params:
            params = []
        payload = get_payload(method, params)
        return requests.post(url, data=json.dumps(payload), headers=headers, cookies=cookies)

    r = request('web.update_ui', ['name', {}])
    torrent_dict = json.loads(r.content)['result']['torrents']
    torrents = {t[1]['name']: t[0] for t in torrent_dict.iteritems()}
    request('core.remove_torrent', [torrents[path], False])

