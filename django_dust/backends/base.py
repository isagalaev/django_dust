
class BaseRetryStorage(object):
    fields = ['operation', 'target_host', 'source_host', 'filename']
    
    def count(self):
        """Returs total retry count"""
        raise NotImplementedError

    def all(self):
        """Returns all retries in queue"""
        raise NotImplementedError

    def create(self, **kwargs):
        """Creates new retry object in queue"""
        raise NotImplementedError

    def delete(self, retry):
        """Deletes given retry object from queue"""
        raise NotImplementedError

    def filter_by_filename(self, filename):
        """Returns retry objects for given file name"""
        raise NotImplementedError