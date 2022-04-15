# TODO

- [ ]  finish adding in public methods to `propay_ui_public` app.
    - [ ]  hosted transaction page
    - [ ]  card addtion to account without other context

-----

# about 
django-propay is a collection of django apps meant to be added into a larger django project.  The three work independently from the rest of the project but rely on each other to an extent.  

 `propay_ui_public` is a limited version of the ui that works on it's own when just paired with the api app. `propay_ui` uses portions of `propay_ui_public` so needs both of the other apps to be installed to work.

`propay_api` works independent of the other two,  it is set up to handle http GET and POST requests to all of the calls to Propay, but thus far doesn't do anything extra to handle the security of those requests.  As is, it's fine to use on internal networks that aren't externally accessible, but would not be safe to put on a public site.  More work will be done to incorporate that later but for now everything works using direct function calls from the ui to the api.

The public ui will be extended so as to be fully accessible from a public website as I finish this up.

-----

# authtokens.py
`authtokens.py` is a file that needs to be added inside of the `propay_api` app.  this includes app-level variables that define tokens and other configurations needed by Propay.

the following  string values will be required:

	BILLER_ID
	AUTH_TOKEN
	MERCHANT_PROFILE_ID


## --- TESTING CREDENTIALS ---
optional (test credentials):

	TEST_BILLER_ID
	TEST_AUTH_TOKEN
	TEST_MERCHANT_PROFILE_ID

I got these by emailing  *clientsupport@propay.com* and requesting for the
integration URI https://xmltestapi.propay.com/ProtectPay/

The whole process in getting test credentials turned out to be rather difficult, I kept getting the wrong info until I gave examples of the calls I was trying to make and the full api url.  Propay has different services being run so you need to specify that this is for the *ProtectPay* api.


# additional project requirements
these might already be installed for other apps, but need to be there for the django-propay app collection to work as intended

	django==3.2
	requests
	django-crispy-forms
	django-redis==5.2.0
	json2html
	nested_lookup
	django-phonenumber-field
	phonenumbers

**django\=\=3.2**: current version is set at 3.2, other versions untested

**requests**: needed for `propay_api` app

**django-crispy-forms**: needed for displaying forms in `propay_ui` and `propay_ui_public`

**django-redis-5.2.0**: needed for `propay_ui`

**json2html, nested_lookup, django-phonenumber-field, phonenumbers**: all needed in `propay_ui` and `propay_ui_public`

-----

# urls and user login
the `propay_ui` app is set up to require logged in users in order to access any of the pages.  The plan is to not need that for the public ui.  If you are only using `propay_api` this part can be ignored.

Include whatever method you use for user authentication.  If you don't have anything set up you can copy the following parts into your main project urls.py as needed

```python
from django.contrib import admin
from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'login', auth_views.LoginView.as_view(), name="login"),
    re_path(r'logout', auth_views.LogoutView.as_view(), name='logout'),
    re_path(r'^/?', include('propay_ui.urls')),
]
```

you will need a login page template under your main app if not there already.

	main/
		templates/
			registration/
				login.html

-----

# project `settings.py` things
```python

import os

INSTALLED_APPS = [
	# ...
	# --- imported django apps ---
	'cripsy_forms',
	# --- project apps ---
	'propay_api',
	'propay_ui',
	'propay_ui_public',
	'main',  ### or name of main project app...
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'  # crispy_forms

# you can change templates to what you normally do, i always add the following to the 'DIRS'
# os.path.join(BASE_DIR, 'templates')

# --- project log dir, (this can be changed) ---
LOG_DIR = os.path.join(BASE_DIR, 'logs')

def project_logfile_path(pathname):
    """
    set up log directories if not there and return full relative path from project
    root
    """
    log_subdirs = os.path.join(LOG_DIR, os.path.dirname(pathname))
    if not os.path.exists(log_subdirs):
        os.makedirs(log_subdirs, exist_ok=True)

    return os.path.join(LOG_DIR, pathname)

# --- logging dictconfig, set up to use rotating logs but can be changed as needed ---
### see: https://docs.djangoproject.com/en/2.2/topics/logging/ for docs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'simple_timestamp':{
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            # 'filters': ['special']
        },
        'propay_file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': project_logfile_path('propay/propay.log'),
            'formatter': 'simple_timestamp',
            'when': 'w0',  # w6 = rotate on Monday at 12:00AM
            'backupCount': '30', # will store 30 weeks
        },
        'propay_file_DEBUG': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': project_logfile_path('propay/propay.debug.log'),
            'formatter': 'verbose',
            'when': 'w0',
            'backupCount': '30',
        },

    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'propay': {
            'handlers': ['propay_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'propay.debug': {
            'handlers': ['propay_file_DEBUG'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}

WSGI_APPLICATION = 'main.wsgi.application'

# --- chache settings needed for propay_ui ---
# --- caching with redis: https://docs.djangoproject.com/en/4.0/topics/cache/#redis ---
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# --- regular project things, put if not already in place ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
LOGIN_URL = 'login'

```


-----

# logging
Note what is in the `LOGGING` dict in settings.py.  Make sure the named loggers for `propay` and `propay.debug` are present or make sure to edit initializations to whatever you name your loggers.  This is anywhere infologger or debuglogger show up in the code.

-----

# redis
Redis is used in the `propay_ui` app.  This is needed for the app to cache info to memory to minimize unnecessary repeated calls to propay.  Nothing is written to the disk and only logged in users can access any part of the UI that shows payer or card info in the first place.

## installation
### Debian / Ubuntu
	sudo apt install redis-server

### CentOS
	sudo yum install redis

## running

	sudo service redis-server start

for debian / ubuntu this is the command, may differ depending on what distro you host on

-----

