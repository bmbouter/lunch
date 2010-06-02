from django.conf.urls.defaults import *

urlpatterns = patterns('lunch',
    (r'^order$', 'views.placeOrder'),
    (r'^$', 'views.placeOrder'),
    (r'^thanks$', 'views.thanks'),
    (r'^orders/$', 'views.viewOrders'),
    (r'^orders/today$', 'views.viewOrders'),
    (r'^orders/(?P<date>(\d{4}-\d{2}-\d{2}){1})$', 'views.viewOrders'),
)
