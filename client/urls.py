from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^clients/$', views.ClientListView.as_view(), name='clients-list'),

]