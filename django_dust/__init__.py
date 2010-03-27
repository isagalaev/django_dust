from django.conf import settings
from django.utils.importlib import import_module

retry_backend = import_module(settings.DUST_RETRY_STORAGE_BACKEND)
