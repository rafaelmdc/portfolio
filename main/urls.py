from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from main import views

urlpatterns = [
    # Headless backend: the public site is the React frontend. Only the CV PDF
    # endpoint and a root redirect to the CMS remain here.
    path("", views.root, name="home"),
    path("resume/pdf/", views.resume_pdf, name="resume-pdf"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
