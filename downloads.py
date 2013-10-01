"""
API Access to Synology Download Station

http://ukdl.synology.com/download/ds/userguide/Synology_Download_Station_Official_API.pdf
"""
import logging
import os

import requests


auth_api = 'SYNO.API.Auth'
dl_api = 'SYNO.DownloadStation.Task'
base = os.environ.get('DOWNLOAD_STATION_URL', 'https://localhost:5001/webapi/{}')
log = logging.getLogger('tvrd.downloads')
password = os.environ.get('SYNOLOGY_PASSWORD')
s = requests.Session()
username = os.environ.get('SYNOLOGY_USERNAME')


def get_api_info():
    url = base.format('query.cgi')
    params = {
        'api': 'SYNO.API.Info',
        'version': 1,
        'method': 'query',
        'query': '{},{}'.format(auth_api, dl_api),
    }
    r = s.get(url, verify=False, params=params)
    if not r.ok:
        msg = 'Listing API endpoints failed with {}: {}'
        raise Exception(msg.format(r.status_code, r.content))
    return r.json()['data'][auth_api], r.json()['data'][dl_api]


def authorize(auth_api_details):
    url = base.format(auth_api_details['path'])
    params = {
        'api': auth_api,
        'version': auth_api_details['maxVersion'],
        'method': 'login',
        'account': username,
        'passwd': password,
        'session': 'DownloadStation',
        'format': 'sid',
    }
    r = s.get(url, verify=False, params=params)
    if not r.ok:
        msg = 'Authorizing with API failed with {}: {}'
        raise Exception(msg.format(r.status_code, r.content))
    return r.cookies['id']


def delete_torrent(sid, dl_api_details, path):
    params = {
        'api': dl_api,
        '_sid': sid,
        'version': dl_api_details['maxVersion'],
        'method': 'list',
    }
    url = base.format(dl_api_details['path'])
    r = s.get(url, verify=False, params=params)
    if not r.ok:
        msg = 'Getting download id failed with {}: {}'
        raise Exception(msg.format(r.status_code, r.content))

    fn = os.path.split(path)[1]
    def filter_downloads(d):
        for x in d:
            if x['title'] == fn:
                return x['id']
    dl_id = filter_downloads(r.json()['data']['tasks'])

    params.update({
        'method': 'delete',
        'id': dl_id,
    })
    r = s.get(url, verify=False, params=params)
    if not r.ok:
        msg = 'Deleting download failed with {}: {}'
        raise Exception(msg.format(r.status_code, r.content))


def remove_torrent(path):
    auth_api_details, dl_api_details = get_api_info()
    sid = authorize(auth_api_details)
    delete_torrent(sid, dl_api_details, path)
