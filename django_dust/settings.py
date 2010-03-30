'''
Default values for settings.
If you want to change these settings define them in your project's settings
file.
'''

def getsetting(name, defaults=locals()):
    '''
    Tries to get a setting from Django's default settings object. If not
    available returns a local default.
    '''
    from django.conf import settings
    return getattr(settings, name, defaults.get(name))

# Retry storage backend setting -- import path for storage module
# Default is DB backend
DUST_RETRY_STORAGE_BACKEND = 'django_dust.backends.db'

# Timeout in seconds for accessing hosts over network. Defaults to 2.
DUST_TIMEOUT = 2

# List of file storage hosts
DUST_HOSTS = ['127.0.0.1']

# Whether to use a local file system. If files are stored on those same
# servers that handle web requests then setting this flag to True
# allows django_dust to access files locally saving time and bandwidth
# on existence checking operations. Defaults to False.
DUST_USE_LOCAL_FS = False
