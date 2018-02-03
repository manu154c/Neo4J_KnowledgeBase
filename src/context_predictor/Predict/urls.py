from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.predict_context, name='predict_context'),
]