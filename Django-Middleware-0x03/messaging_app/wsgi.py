<<<<<<< HEAD
"""
WSGI config for messaging_app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messaging_app.settings')

application = get_wsgi_application()
=======
"""
WSGI config for messaging_app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messaging_app.settings')

application = get_wsgi_application()
>>>>>>> 63d17a02b66d463ff6ec115078bd66d1f2cf1483
