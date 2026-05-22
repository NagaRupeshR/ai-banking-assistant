from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('pdf/<int:analysis_id>/', views.download_pdf, name='download_pdf'),
]