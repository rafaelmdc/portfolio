from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from main import views
from main.views import portfolio_detail

urlpatterns = [
    path("", views.index, name="home"),
    path("about/", views.about, name="about"),
    path("resume/", views.resume, name="resume"),
    path("portfolio/", views.portfolio, name="portfolio"),
    path("portfolio/<slug:slug>/", portfolio_detail, name="portfolio_detail"),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("contact/", views.contact, name="contact"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)