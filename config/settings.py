from pathlib import Path

from decouple import config, Csv
from mypy.plugins import default

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-=wkh6th=r$yevt0dsmll6uprl9ou_^flvkm07-#ug^lb+#^614')

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # my_app
    'ckeditor',
    'home.apps.HomeConfig',
    'accounts.apps.AccountsConfig',
    'shop.apps.ShopConfig',
    'cart.apps.CartConfig',
    'dashboard.apps.DashboardConfig',
    'order.apps.OrderConfig',
    'payment.apps.PaymentConfig',
    'blogs.apps.BlogsConfig',
    'abouts.apps.AboutsConfig',
    'contactus.apps.ContactusConfig',
    'adminpanel.apps.AdminpanelConfig',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'shop.context_processors.category_menu',
                "cart.context_processors.cart_session"
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = config('TIME_ZONE', default='UTC')

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

AUTH_USER_MODEL = 'accounts.User'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# zarinpal
ZARINPAL_MERCHANT_ID = config("ZARINPAL_MERCHANT_ID", default="d8abf83c-d62a-4bde-889d-628b3812a99d")

ZARINPAL_REQUEST_URL = config("ZARINPAL_REQUEST_URL", default="https://sandbox.zarinpal.com/pg/v4/payment/request.json")

ZARINPAL_VERIFY_URL = config("ZARINPAL_VERIFY_URL", default="https://sandbox.zarinpal.com/pg/v4/payment/verify.json")

ZARINPAL_STARTPAY_URL = config("ZARINPAL_STARTPAY_URL", default="https://sandbox.zarinpal.com/pg/StartPay/")

# CSRF_TRUSTED_ORIGINS = config(
#     'CSRF_TRUSTED_ORIGINS',
#     default='https://shop-project.liara.run,https://fiuragallery.ir',
#     cast=lambda v: [item.strip() for item in v.split(',')])

# BASE_URL = config('BASE_URL', default='https://fiuragallery.ir')
