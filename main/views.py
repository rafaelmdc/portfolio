from django.shortcuts import render
from .models import Education, Experience, Skill, SiteCopy

# Create your views here.
def index(request): 
    return render(request, "index.html")

def _copy_dict():
    # latest active entry per key
    copy = {}
    for key, _label in SiteCopy.COPY_KEYS:
        row = SiteCopy.objects.filter(key=key, active=True).order_by("-updated_at", "-id").first()
        copy[key] = row.text if row else ""
    return copy

def about(request):
    context = {
        "skills": Skill.objects.filter(active=True).order_by("order", "id"),
        "copy": _copy_dict(),
    }
    return render(request, "about.html", context)

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