from django.urls import path
from main import views

urlpatterns = [
    path("", views.index, name="home"),
    path("about/", views.about, name="about"),
    path("resume/", views.resume, name="resume"),
    path("services/", views.services, name="services"),
    path("services/details/", views.service_details, name="service_details"),
    path("portfolio/", views.portfolio, name="portfolio"),
    path("portfolio/details/", views.portfolio_details, name="portfolio_details"),
    path("contact/", views.contact, name="contact"),
    path("starter/", views.starter, name="starter"),
]
