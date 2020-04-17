from django.urls import path
from . import views

app_name = "scraping"
urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('itemregister/', views.favorite_item_register, name='register_favorite_item' ),
    path('itemdelete/', views.favorite_item_delete, name='delete_favorite_item'),
]