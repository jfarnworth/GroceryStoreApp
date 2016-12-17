from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
    url(r'^$', views.sign_in, name='sign-in'),
    # url(r'^reservations/(?P<user_name>\[\w|\W]+)/(?P<user_id>\d+)/$', views.reservations, name='product-reservations'),
    url(r'^reservations/(?P<user_name>.*)/(?P<user_id>\d+)/$', views.reservations, name='product-reservations'),
    url(r'^reservations/(?P<user_name>.*)/(?P<user_id>\d+)/(?P<reservation_id>\d+)/$', views.reservations, name='product-reservations-reserved'),
]

urlpatterns += staticfiles_urlpatterns()
