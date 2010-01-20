# -*- coding:utf-8 -*-
from datetime import datetime

from django.db import models

FILE_OPERATIONS = (
    ('put', 'put'),
    ('delete', 'delete'),
)


class Retry(models.Model):
    '''
    Failed attempts of file operations on remote hosts that need to
    be retried periodically.
    '''
    created = models.DateTimeField(default=datetime.now)
    operation = models.CharField(max_length=20, choices=FILE_OPERATIONS, blank=True)
    target_host = models.CharField(max_length=50)
    filename = models.CharField(max_length=100)
    source_host = models.CharField(max_length=50)

    def __unicode__(self):
        return u'%s %s %s' % (self.get_operation_display(), self.target_host, self.filename)
