# -*- coding:utf-8 -*-
'''
Command for processing a queue of failed media distribution operations
(puts and deletes). It's expected to be called periodically by a scheduler.

Reports are sent to a logger named 'django_dust'.
'''
import socket
import logging

from django.core.management.base import NoArgsCommand

from django_dust import retry_storage
from django_dust.storage import DistributedStorage
from django_dust.http import HTTPError

logger = logging.getLogger('django_dust')

def _to_unicode(retry):
    return u'%(operation)s %(target_host)s %(filename)s' % retry

class Command(NoArgsCommand):
    help = "Retries failed attempts to distribute media files among media servers"

    def handle_noargs(self, **options):
        logger.info('Initializing storage')
        storage = DistributedStorage()
        retries = retry_storage.all()
        logger.info('Retries to process: %s' % len(retries))
        for retry in retries:
            logger.info('Retry: %s' % _to_unicode(retry))
            try:
                if retry['operation'] == 'put':
                    body = storage.transport.get(retry['source_host'], retry['filename'])
                    storage.transport.put(retry['target_host'], retry['filename'], body)
                if retry['operation'] == 'delete':
                    storage.transport.delete(retry['target_host'], retry['filename'])
                retry_storage.delete(retry)
            except (socket.error, HTTPError), e:
                logger.warning('Retry <%s> not processed: %s' % (_to_unicode(retry), e))
                pass
        logger.info('Done processing retries. Remaning: %s' % retry_storage.count())
