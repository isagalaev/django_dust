## SUMMARY

File backend django_dust (Distributed Upload STorage) can store files coming
into a Django site on several servers simultaneously. This works for files
uploaded by users from admin or custom Django forms and also files created
in application code provided it uses standrad [Storage API][1].

The backend is needed for sites working in multi-server environment in order
to accept uploaded files and have them available on all media servers
immediately for subsequent web requests that could be routed to any machine.

The backend can also work in a completely remote mode when files are stored
on different servers than those that handle web requests.

Django_dust nicely handles situation when some of media servers are unavailable
by keeping a queue of failed operations to repeat them afterwards.


## INSTALLATION AND SETUP

1.  Download and install python package in usual way. Django_dust requires
    [httplib2][2] library version at least 0.4.

2.  Put django_dust into INSTALLED_APPS:

        INSTALLED_APPS = (
            ...

            'django_dust',
        )

3.  Create the retry queue table with `syncdb`.

4.  Setup a scheduled task to run a command for processing the queue:

        ./manage.py process_failed_media

5.  Set django_dust as a default file backend:

        DEFAULT_FILE_STORAGE = 'django_dust.storage.DistributedStorage'

    Strictly speaking this is not obligatory. If needed the backend can be used
    for only particular file model fields or manually anywhere in code.

6.  Define backend settings:

        # Importing default Dust settings
        from django_dust.settings import *

    Configure hosts:

        # List of file storage hosts
        DUST_HOSTS = [
            'hostname1',
            'hostanem2',
            # ...
        ]

    Other optional settings:

        # Retry storage backend setting -- import path for storage module.
        # Default is DB backend. See django_dust/backends/base for class
        # and method reference
        DUST_RETRY_STORAGE_BACKEND = 'django_dust.backends.db'

        # Whether to use a local file system. If files are stored on those same
        # servers that handle web requests then setting this flag to True
        # allows django_dust to access files locally saving time and bandwidth
        # on existence checking operations. Defaults to False.
        DUST_USE_LOCAL_FS = True

        # Timeout in seconds for accessing hosts over network. Defaults to 2.
        DUST_TIMEOUT = 2

    When using local file system make sure that `MEDIA_ROOT` points to the same
    place where a web server looks for files under `MEDIA_URL`. This is usually
    already the case.

## SETTING UP HTTP SERVERS

The backend uses HTTP to transfer files to media servers. For this to work
those servers should support HTTP methods PUT and DELETE. Despite of them
being part of HTTP itself they are traditionally implemented by external
modules supporting WebDAV. Hence make sure that  web servers have this module
enabled. For security reasons it's better to enable it only for internal IPs
to prevent external users from being able to write and delete server files.

An example of lighttpd config:

    server.modules += (
      "mod_webdav",
    )

    $HTTP["remoteip"] ~= "^192\.168\.0\.[0-9]+$" {
      "webdav.activate = "enable"
    }

Note that URLs for PUTting and DELETEing files are built using `MEDIA_URL` and
are essentially the same URLs that browsers use to access them.


[1]: http://docs.djangoproject.com/en/dev/ref/files/storage/
[2]: http://code.google.com/p/httplib2/
