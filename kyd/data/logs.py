
from datetime import datetime, timezone

import pytz

from google.cloud import datastore


def _create_downloadlog_key(data):
    return '{}:{:.0f}'.format(data['name'], data['time'].timestamp())


def save_download_logs(data):
    data['refdate'] = data['refdate'] and datetime.strptime(data['refdate'], '%Y-%m-%dT%H:%M:%S.%f%z')
    if data['refdate']:
        data['refdate'].replace(tzinfo=pytz.timezone('America/Sao_Paulo'))
    data['time'] = datetime.strptime(data['time'], '%Y-%m-%dT%H:%M:%S.%f%z')

    client = datastore.Client()
    key = client.key('DownloadLog', _create_downloadlog_key(data))
    log_entry = datastore.Entity(key)
    log_entry.update(data)
    client.put(log_entry)


def save_process_logs(data):
    data['refdate'] = data['refdate'] and datetime.strptime(data['refdate'], '%Y-%m-%dT%H:%M:%S.%f%z')
    if data['refdate']:
        data['refdate'].replace(tzinfo=pytz.timezone('America/Sao_Paulo'))
    data['time'] = datetime.strptime(data['time'], '%Y-%m-%dT%H:%M:%S.%f%z')

    client = datastore.Client()
    key = client.key('DownloadLog', _create_downloadlog_key(data))
    log_entry = datastore.Entity(key)
    log_entry.update(data)
    client.put(log_entry)
