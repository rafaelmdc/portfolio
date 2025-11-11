from django.shortcuts import render
from .models import Education, Experience

# Create your views here.
def index(request): 
    return render(request, "index.html")

def about(request):
    return render(request, "about.html")

def resume(request):
    ctx = {}
    ctx["educations"] = Education.objects.all()
    ctx["experiences"] = Experience.objects.prefetch_related("bullets").all()  # if you added bullets
    return render(request, "resume.html", ctx)

def services(request): 
    return render(request, "services.html")

def service_details(request): 
    return render(request, "service-details.html")

def portfolio(request): 
    return render(request, "portfolio.html")

def portfolio_details(request): 
    return render(request, "portfolio-details.html")

def contact(request): 
    return render(request, "contact.html")

def starter(request): 
    return render(request, "starter.html")