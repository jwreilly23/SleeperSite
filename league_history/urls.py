from django.urls import path
from . import views

app_name = "league_history"
urlpatterns = [
    path("", views.index, name="index"),
    path("history", views.history, name="history")
]