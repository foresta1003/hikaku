"""hikaku URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import static
from . import settings
from accounts import views
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls), #
    path('', include('scraping.urls')),
    path('accounts/signup/', views.SignupView.as_view(template_name = 'account/signup.html'), name='account_signup'),
    path('accounts/home/', views.home, name='home'),
    path('accounts/', include('allauth.urls')),   
]

#メディアを配信できるようにする設定
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
