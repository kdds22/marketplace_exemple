from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^proposals/$', views.ProposalsListView.as_view(), name='proposals-list'),

]