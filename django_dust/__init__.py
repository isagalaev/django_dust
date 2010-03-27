from django.conf import settings
from django.utils.importlib import import_module

backend_module = import_module(settings.DUST_RETRY_STORAGE_BACKEND)
retry_backend = backend_module.RetryStorage()
