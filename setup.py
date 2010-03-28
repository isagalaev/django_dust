from distutils.core import setup

setup(
    name='django_dust', 
    description='Distributed Upload STorage for Django. A file backend that mirrors all incoming media files to several servers',
    packages=[
        'django_dust',
        'django_dust.management',
        'django_dust.management.commands',
        'django_dust.backends'
    ],
)
