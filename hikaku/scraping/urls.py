from django.urls import path
from . import views

app_name = "scraping"
urlpatterns = [
    path('', IndexViews.as_view(), name="index")
]