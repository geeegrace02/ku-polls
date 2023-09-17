from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = "polls"
urlpatterns = [
    path("", views.index, name="index"),
    path('<int:pk>/', views.detail, name='detail'),
    path('results/<int:question_id>/', views.results, name='results'),
    # path('<int:pk>/results/', views.results, name='results'),
    path("<int:question_id>/vote/", login_required(views.vote), name="vote"),
]


