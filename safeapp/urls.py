from django.urls import path
from . import views

urlpatterns = [
    path('',views.accesssafeway,name='accsafe'),
    path('runing/',views.runsafeway,name=('runsafeway')),
    path('runing/display/',views.imagedisplay,name="imagedisplay")
]