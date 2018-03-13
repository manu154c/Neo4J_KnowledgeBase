from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.predict_context, name='predict_context'),
    url(r'^list/', views.list_all_nodes, name='list_all_nodes'),
]