from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from main import views

urlpatterns = [
    path("", views.index, name="home"),
    path("about/", views.about, name="about"),
    path("resume/", views.resume, name="resume"),
    path("contact/", views.contact, name="contact"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)