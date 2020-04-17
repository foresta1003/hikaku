"""
Django settings for hikaku project.

Generated by 'django-admin startproject' using Django 3.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import environ

#環境変数用のBASE_DIR
ENV_BASE_DIR = environ.Path(__file__) - 3 #.envファイルのディレクトリ
env = environ.Env(DEBUG=(bool, False),) #デフォルトの値を設定している DEBUG=(キャスト, False)
env_file = str(ENV_BASE_DIR.path('.env'))

env.read_env(env_file)





# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'scraping.apps.ScrapingConfig',
    'accounts.apps.AccountsConfig',
    'inquiry.apps.InquiryConfig',

    'django.contrib.sites',
    'allauth',
    'allauth.account',
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

ROOT_URLCONF = 'hikaku.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hikaku.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'), #本番では変更
    }
}

#新規でデータベース作成時は環境変数を使用する事

"""
DATABASES = {
    'default': {
        環境変数を使用する事
        'ENGINE': 環境変数を使用する事
        'NAME':
        'USER':
        'PASSWORD':　
        'HOST':
        'PORT':
    }
}
"""
# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
#静的ファイルを読み込むための設定
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'




#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#mail(メール)設定

EMAIL_BACKEND= 'django.core.mail.backends.smtp.EmailBackend'     #実際にメールを送信する(以下gmailで送信する場合) 

EMAIL_HOST = 'smtp.gmail.com' #gmail使用時はこのまま
EMAIL_PORT = 587
EMAIL_HOST_USER = env("EMAIL_ADDRESS") #環境変数を使用する事
EMAIL_HOST_PASSWORD = env("EMAIL_PASSWORD") #二段階認証時は二段階目のパスを入れること ※設定時は環境変数から読み込み直接記入しない事
EMAIL_USE_TLS = True    


# 開発環境において(コンソールに表示させる)
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#以下は認証機能

#アカウントユーザーモデルの拡張 指定する事によってこのモデルを使用するアカウントが作成される
AUTH_USER_MODEL = 'accounts.CustomUser'

#django-allauthで利用するdjango.contrib.sitesを使うためにサイト識別用IDを設定
SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'allauth.account.auth_backends.AuthenticationBackend', #一般ユーザー用(メールアドレス認証)
    'django.contrib.auth.backends.ModelBackend', #管理サイト用(ユーザー名認証)
)


#メールアドレス認証に変更する設定
#ACCOUNT_AUTHENTICATION_METHOD ='email'
#ACCOUNT_USERNAME_REQUIRED = False


#サインアップにメールアドレス確認を挟むよう設定
#ACCOUNT_EMAIL_VERIFICATION = 'none' #有効化する際は'mandatory'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory' #有効化する際は'mandatory'
ACCOUNT_EMAIL_REQUIRED = True

#ログイン/ログアウト後の遷移先を設定
LOGIN_REDIRECT_URL = 'scraping:index'
ACCOUNT_LOGOUT_REDIRECT_URL ='account_login'

#ログアウトリンクのクリック一発でログアウトする設定
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_FORMS = {
    'signup': 'accounts.forms.MyCustomSignupForm'
}

ACCOUNT_ADAPTER = 'accounts.adapter.AccountAdapter'

