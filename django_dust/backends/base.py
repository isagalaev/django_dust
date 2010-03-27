
class BaseRetryStorage(object):
    fields = ['operation', 'target_host', 'source_host', 'filename']
    
    def count(self):
        raise NotImplementedError

    def all(self):
        raise NotImplementedError

    def create(self, **kwargs):
        raise NotImplementedError

    def delete(self, retry):
        raise NotImplementedError

    def filter_by_filename(self, filename):
        raise NotImplementedError