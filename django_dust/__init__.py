from django.utils.importlib import import_module

from django_dust.settings import getsetting

backend_module = import_module(getsetting('DUST_RETRY_STORAGE_BACKEND'))
retry_storage = backend_module.RetryStorage()
