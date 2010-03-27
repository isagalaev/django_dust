# -*- coding:utf-8 -*-
from threading import Thread
import socket
import random
import urlparse

from django.core.files import base
from django.core.files.storage import Storage, FileSystemStorage
from django.conf import settings

from django_dust import http


class DistributionError(IOError):
    pass


class DistributedStorage(Storage):
    '''
    DistributedStorage saves files by copying them on several servers listed
    in settings.DUST_HOSTS.
    '''
    def __init__(self, hosts=None, use_local=None, base_url=settings.MEDIA_URL, **kwargs):
        super(DistributedStorage, self).__init__(**kwargs)
        if hosts is None:
            hosts = getattr(settings, 'DUST_HOSTS', ['127.0.0.1'])
        self.hosts = hosts
        if use_local is None:
            use_local = getattr(settings, 'DUST_USE_LOCAL_FS', False)
        self.local_storage = use_local and FileSystemStorage(base_url=base_url, **kwargs)
        self.base_url = base_url
        self.transport = http.HTTPTransport(base_url=base_url)

    def _execute(self, func, name, args):
        '''
        Runs an operation (put or delete) over several hosts at once in multiple
        threads.
        '''
        def run(index, host):
            try:
                results[index] = func(host, name, *args)
            except Exception, e:
                results[index] = (e)

        # Run distribution threads keeping result of each operation in `results`.
        results = [None] * len(self.hosts)
        threads = [Thread(target=run, args=(index, h)) for index, h in enumerate(self.hosts)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        exceptions = []
        for host, result in zip(self.hosts, results):
            if result is None: # no errors, remember successful_host to use in retries
                successful_host = host
                break
        else:
            successful_host = None

        # All `socket.error` exceptions are not fatal meaning that a host might
        # be temporarily unavailable. Those operations are kept in a queue in
        # database to be retried later.
        # All other errors mean in most casess misconfigurations and are fatal
        # for the whole distributed operation.
        for host, result in zip(self.hosts, results):
            if isinstance(result, socket.error):
                if successful_host is not None:
                    from django_dust import retry_storage # this causes errors when imported at module level
                    retry_storage.create(
                        operation=func.__name__,
                        target_host=host,
                        source_host=successful_host,
                        filename=name,
                    )
                else:
                    exceptions.append(result)
            elif isinstance(result, Exception):
                exceptions.append(result)
        if exceptions:
            raise DistributionError(*exceptions)

    def _open(self, name, mode='rb'):
        if mode != 'rb':
            # In future when allowed to operate locally (self.local_storage)
            # all modes can be allowed. However this will require executing
            # distribution upon closing file opened for updates. This worth
            # evaluating.
            raise IOError('Illegal mode "%s". Only "rb" is supported.')
        if self.local_storage:
            return self.local_storage.open(name, mode)
        host = random.choice(self.hosts)
        return base.ContentFile(self.transport.get(host, name))

    def _save(self, name, content):
        name = self.get_available_name(name)
        content.seek(0)
        body = content.read()
        self._execute(self.transport.put, name, [body])
        return name

    def get_available_name(self, name):
        from django_dust import retry_storage # this causes errors when imported at module level
        while self.exists(name) or retry_storage.filter_by_filename(name):
            try:
                dot_index = name.rindex('.')
            except ValueError: # filename has no dot
                name += '_'
            else:
                name = name[:dot_index] + '_' + name[dot_index:]
        return name

    def path(self, name):
        if self.local_storage:
            return self.local_storage.path(name)
        return super(DistributedStorage, self).path(name)

    def delete(self, name):
        self._execute(self.transport.delete, name, [])

    def exists(self, name):
        if self.local_storage:
            return self.local_storage.exists(name)
        return self.transport.exists(random.choice(self.hosts), name)

    def listdir(self, path):
        if self.local_storage:
            return self.local_storage.listdir(path)
        raise NotImplementedError()

    def size(self, name):
        if self.local_storage:
            return self.local_storage.size(name)
        return self.transport.size(random.choice(self.hosts), name)

    def url(self, name):
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")
        return urlparse.urljoin(self.base_url, name).replace('\\', '/')
