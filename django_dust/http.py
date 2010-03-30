# -*- coding:utf-8 -*-
import httplib2
from urlparse import urlsplit

from django_dust.settings import getsetting


class HTTPError(Exception):
    pass


class HTTPTransport(object):
    '''
    Transport for doing actual saving and deleting files on remote machines.
    Uses httplib2 and expects that target HTTP host support PUT and DELETE
    methods (apart from the all usual).
    '''
    timeout = getsetting('DUST_TIMEOUT')

    def __init__(self, base_url):
        scheme, host, path, query, fragment = urlsplit(base_url)
        self.scheme = scheme or 'http'
        self.url_path = path or '/'

    def _get_url(self, host, name):
        '''
        Constructs a full URL for a given host and file name.
        '''
        return '%s://%s%s%s' % (self.scheme, host, self.url_path, name)

    def _headers(self, host, name):
        '''
        Gets headers of an HTTP response for a given file name using HEAD
        request. Used in `exists` and `size`.
        '''
        http = httplib2.Http(timeout=self.timeout)
        url = self._get_url(host, name)
        response, response_body = http.request(url, 'HEAD')
        if response.status >= 400 and response.status != 404:
            raise HTTPError('HEAD', url, response.status)
        return response

    # Public interface of a transport. Transport should support following
    # methods:
    #
    # - put     uploading a file
    # - delete  deleting a file
    # - get     getting a file's contents
    # - exists  test if a file exists
    # - size    get a file size
    #
    # All methods are free to raise appropriate exceptions if some functionality
    # is not supported.

    def put(self, host, name, body):
        http = httplib2.Http(timeout=self.timeout)
        url = self._get_url(host, name)
        response, response_body = http.request(url, 'PUT',
            body=body,
            headers={'Content-type': 'application/octet-stream'}
        )
        if response.status >= 400:
            raise HTTPError('PUT', url, response.status)

    def delete(self, host, name):
        http = httplib2.Http(timeout=self.timeout)
        url = self._get_url(host, name)
        response, response_body = http.request(url, 'DELETE')
        if response.status >= 400 and response.status != 404:
            raise HTTPError('DELETE', url, response.status)

    def get(self, host, name):
        http = httplib2.Http(timeout=self.timeout)
        url = self._get_url(host, name)
        response, response_body = http.request(url, 'GET')
        if response.status >= 400:
            raise HTTPError('GET', url, response.status)
        return response_body

    def exists(self, host, name):
        response = self._headers(host, name)
        return response.status == 200

    def size(self, host, name):
        response = self._headers(host, name)
        try:
            return int(response['content-length'])
        except (KeyError, ValueError):
            raise Exception('Invalid or missing content length for %s: "%s"' % (
                name,
                response.get('content-length'),
            ))
