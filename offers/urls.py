from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^offers/$', views.OffersListView.as_view(), name='offers-list'),

]