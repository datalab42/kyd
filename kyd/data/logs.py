
from datetime import datetime

import pytz

from google.cloud import datastore


def _create_downloadlog_key(data):
    return '{}:{:.0f}'.format(data['name'], data['time'].timestamp())


def _format(data):
    data['refdate'] = data['refdate'] and datetime.strptime(data['refdate'], '%Y-%m-%dT%H:%M:%S.%f%z')
    if data['refdate']:
        data['refdate'].replace(tzinfo=pytz.timezone('America/Sao_Paulo'))
    data['time'] = datetime.strptime(data['time'], '%Y-%m-%dT%H:%M:%S.%f%z')


def save_download_logs(data):
    _format(data)

    client = datastore.Client()
    key = client.key('DownloadLog', _create_downloadlog_key(data))
    log_entry = datastore.Entity(key)
    log_entry.update(data)
    client.put(log_entry)


def save_process_logs(data):
    parent = data['parent']
    _format(parent)

    client = datastore.Client()
    parent_key = client.key('DownloadLog', _create_downloadlog_key(parent))
    # parent = client.get(parent_key)
    if data.get('results'):
        for pr in data['results']:
            key = client.key('ProcessorLog', parent=parent_key)
            # if parent:
            # else:
            #     key = client.key('ProcessorLog')
            log_entry = datastore.Entity(key)
            pr['time'] = data['time']
            pr['processor_name'] = data['processor_name']
            log_entry.update(pr)
            client.put(log_entry)
    else:
        key = client.key('ProcessorLog', parent=parent_key)
        # if parent:
        # else:
        #     key = client.key('ProcessorLog')
        log_entry = datastore.Entity(key)
        log_entry.update({
            'error': data['error'],
            'time': data['time'],
            'processor_name': data['processor_name'],
        })
        client.put(log_entry)
