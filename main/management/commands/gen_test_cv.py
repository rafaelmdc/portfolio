"""
Generate a test CV PDF with artificial data (no DB required).

Usage:
    python manage.py gen_test_cv
    python manage.py gen_test_cv --output /tmp/cv_test.pdf
"""
from types import SimpleNamespace

from django.core.management.base import BaseCommand


# ── Mock helpers ──────────────────────────────────────────────────────────────

def _ns(**kw):
    return SimpleNamespace(**kw)


class _BulletSet:
    def __init__(self, *texts):
        self._items = [_ns(text=t) for t in texts]

    def all(self):
        return self._items


def _exp(role, company, start, end, location="Lisbon, PT", blurb="", bullets=()):
    return _ns(
        role=role, company=company, location=location,
        start_year=start, end_year=end, blurb=blurb,
        bullets=_BulletSet(*bullets),
    )


def _edu(title, institution, start, end, location="", blurb=""):
    return _ns(
        title=title, institution=institution, location=location,
        start_year=start, end_year=end, blurb=blurb,
    )


def _lang(name, level_display):
    return _ns(name=name, get_level_display=lambda ld=level_display: ld)


def _pub(title, authors, year, venue, pub_type="journal", doi="", cit=0):
    display = authors.replace("Correia R", "<strong>Correia R</strong>", 1)
    return _ns(
        title=title, authors=authors, authors_display=display,
        year=year, venue=venue,
        doi=doi, link=f"https://doi.org/{doi}" if doi else "",
        citation_count=cit,
    )


def _grant(title, funder, role, amount, start, end=None, desc=""):
    return _ns(
        title=title, funder=funder, role=role, amount=amount,
        start_year=start, end_year=end, description=desc,
    )


def _award(title, issuer, year, desc=""):
    return _ns(title=title, issuer=issuer, year=year, description=desc)


# ── Artificial data ───────────────────────────────────────────────────────────

SKILLS = [
    "Python", "Django", "Wagtail", "PostgreSQL", "Docker", "Kubernetes",
    "FastAPI", "NumPy", "Pandas", "PyTorch", "scikit-learn", "R",
    "JavaScript", "TypeScript", "React", "HTML/CSS", "Git", "CI/CD",
    "Linux", "REST APIs", "GraphQL", "Redis", "Celery", "Nginx",
]

LANGUAGES = [
    _lang("Portuguese", "Native"),
    _lang("English", "Fluent"),
    _lang("Spanish", "Intermediate"),
]

EXPERIENCES = [
    _exp(
        "Senior Software Engineer", "Acme Research Ltd", 2022, None,
        location="London, UK",
        blurb="Led backend development of a large-scale data pipeline serving 50 M+ requests/day.",
        bullets=(
            "Designed and implemented a distributed task queue reducing processing latency by 40%.",
            "Migrated monolithic Django app to microservices, improving deployment frequency 3×.",
            "Mentored a team of four junior engineers; introduced code-review standards.",
            "Drove adoption of automated integration testing, raising coverage from 42% to 87%.",
        ),
    ),
    _exp(
        "Research Software Engineer", "Institute for Computational Science", 2019, 2022,
        location="Porto, PT",
        blurb="Built high-throughput bioinformatics pipelines and analysis tooling for wet-lab teams.",
        bullets=(
            "Developed Python library for genome annotation adopted by three external collaborators.",
            "Optimised SQL queries on 200 GB+ clinical database, cutting report generation from 8 h to 25 min.",
            "Containerised legacy Fortran simulation code, enabling reproducible runs on HPC clusters.",
        ),
    ),
    _exp(
        "Full-Stack Developer", "StartupXYZ", 2017, 2019,
        location="Lisbon, PT",
        blurb="Sole developer responsible for customer-facing web platform and internal tooling.",
        bullets=(
            "Built React SPA with Django REST backend serving 5 000 daily active users.",
            "Integrated Stripe payment flow, increasing conversion rate by 18%.",
            "Implemented JWT-based auth and role-based access control.",
        ),
    ),
    _exp(
        "Junior Developer (Internship)", "Tech Agency Portugal", 2016, 2017,
        location="Lisbon, PT",
        bullets=(
            "Developed CMS-driven landing pages for six client campaigns.",
            "Automated weekly reporting with Python scripts, saving 3 h/week.",
        ),
    ),
    _exp(
        "Research Assistant", "Faculty of Sciences, University of Lisbon", 2015, 2016,
        location="Lisbon, PT",
        blurb="Assisted in data collection and analysis for a computational neuroscience project.",
    ),
]

EDUCATIONS = [
    _edu(
        "PhD in Computer Science", "University of Lisbon", 2017, 2021,
        location="Lisbon, PT",
        blurb="Thesis: 'Efficient Approximate Inference for Large-Scale Probabilistic Graphical Models'. "
              "Supervised by Prof. Jane Doe. FCT scholarship holder.",
    ),
    _edu(
        "MSc in Bioinformatics", "University of Porto", 2015, 2017,
        location="Porto, PT",
        blurb="Final project on protein structure prediction using deep learning. Grade: 19/20.",
    ),
    _edu(
        "BSc in Computer Science", "NOVA University Lisbon", 2012, 2015,
        location="Lisbon, PT",
        blurb="Graduated with distinction (18/20). Erasmus semester at TU Delft (2014).",
    ),
]

GRANTS = [
    _grant(
        "Explainable AI for Clinical Decision Support",
        "Fundação para a Ciência e a Tecnologia (FCT)", "Principal Investigator",
        "€120,000", 2023, 2026,
        desc="3-year grant to develop interpretable ML models for ICU patient outcome prediction.",
    ),
    _grant(
        "EU Horizon HEALTH-DATA Consortium",
        "European Commission (Horizon Europe)", "Work Package Lead",
        "€45,000", 2022, 2025,
        desc="Federated learning infrastructure for privacy-preserving clinical data analysis.",
    ),
    _grant(
        "Genomics Data Integration Platform",
        "Welcome Trust", "Co-Investigator",
        "€30,000", 2020, 2022,
    ),
]

AWARDS = [
    _award("Best Paper Award", "ICML 2023 Workshop on Interpretability", 2023,
           "Awarded for outstanding contribution to the field of explainable AI."),
    _award("FCT PhD Scholarship", "Fundação para a Ciência e a Tecnologia", 2017),
    _award("Dean's List", "NOVA University Lisbon", 2015,
           "Top 5% of graduating class in Computer Science."),
    _award("Best Poster", "BioInformatics Portugal Conference", 2016),
]

_JOURNALS = [
    _pub(
        "Scalable Approximate Inference via Stochastic Gradient Descent",
        "Correia R, Smith J, Oliveira M", 2023,
        "Journal of Machine Learning Research", doi="10.5555/jmlr.2023.001", cit=34,
    ),
    _pub(
        "Privacy-Preserving Federated Learning in Healthcare: A Systematic Review",
        "Santos A, Correia R, Ferreira P, Costa L", 2022,
        "Nature Machine Intelligence", doi="10.1038/s42256-022-001", cit=87,
    ),
    _pub(
        "Efficient Neural Architecture Search under Memory Constraints",
        "Correia R, Pereira T", 2021,
        "IEEE Transactions on Neural Networks and Learning Systems",
        doi="10.1109/tnnls.2021.00001", cit=19,
    ),
    _pub(
        "Genome-Wide Association Studies: Computational Challenges and Opportunities",
        "Almeida C, Correia R, Rodrigues J", 2020,
        "Bioinformatics (Oxford)", doi="10.1093/bioinformatics/2020", cit=52,
    ),
]

_CONFERENCES = [
    _pub(
        "Sparse Transformers for Long Clinical Notes",
        "Correia R, Wang H, Nguyen T", 2023,
        "NeurIPS 2023", doi="10.5555/neurips.2023.001", cit=11,
    ),
    _pub(
        "Adaptive Sampling Strategies for Active Learning",
        "Correia R, Lopes R", 2022,
        "ICML 2022", doi="10.5555/icml.2022.002", cit=28,
    ),
    _pub(
        "Contrastive Self-Supervised Learning for Medical Imaging",
        "Lima F, Correia R, Gomes S", 2021,
        "MICCAI 2021", doi="10.1007/978-3-030-87001-0_001", cit=41,
    ),
    _pub(
        "Graph Neural Networks for Drug Interaction Prediction",
        "Correia R, Tavares M, Sousa A", 2020,
        "EMNLP 2020", doi="10.18653/v1/2020.emnlp-main.001", cit=15,
    ),
    _pub(
        "Multi-Modal Fusion for Radiology Report Generation",
        "Chen Y, Correia R", 2019,
        "ACL 2019", cit=7,
    ),
]

_PREPRINTS = [
    _pub(
        "Towards Unified Foundation Models for Biomedical Text",
        "Correia R, Kim J, Patel S, Gonzalez R", 2024,
        "arXiv", doi="10.48550/arXiv.2401.00001",
    ),
]

PUB_GROUPS = [
    {"label": "Journal Articles",  "pubs": _JOURNALS},
    {"label": "Conference Papers", "pubs": _CONFERENCES},
    {"label": "Preprints",         "pubs": _PREPRINTS},
]


# ── Command ───────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = "Render resume.tex.j2 with artificial data and write a test PDF via XeLaTeX"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output", default="test_cv.pdf",
            help="Output path for the generated PDF (default: test_cv.pdf)",
        )

    def handle(self, *args, **options):
        from main.cv_pdf import render_cv_pdf

        ctx = {
            "name":       "Jane Researcher",
            "title":      "Software Developer & Researcher",
            "email":      "jane@example.com",
            "github":     "github.com/janeresearcher",
            "linkedin":   "linkedin.com/in/janeresearcher",
            "skills":     [_ns(name=s) for s in SKILLS],
            "languages":  LANGUAGES,
            "experiences": EXPERIENCES,
            "educations": EDUCATIONS,
            "grants":     GRANTS,
            "awards":     AWARDS,
            "pub_groups": PUB_GROUPS,
        }

        try:
            pdf = render_cv_pdf(ctx)
        except RuntimeError as exc:
            self.stderr.write(str(exc))
            return

        output = options["output"]
        with open(output, "wb") as fh:
            fh.write(pdf)

        self.stdout.write(self.style.SUCCESS(f"PDF written → {output}"))
