"""
Populate the dev database with Rafael's real portfolio content plus a blog post
that exercises every StreamField block type. Idempotent: clears and recreates the
demo records each run. Dev/demo only — never run against production data.

    python manage.py seed_demo
"""
from datetime import date

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from wagtail.images import get_image_model
from wagtail.models import Collection
from wagtail.documents import get_document_model

from main.models import (
    SiteContent, Skill, Education, Experience, ExperienceBullet,
    Award, Language,
)
from cms.models import BlogIndexPage, BlogPage, PortfolioIndexPage, PortfolioProjectPage

SKILLS = [
    ("Python", "Data analysis, automation, and building research and personal applications."),
    ("General Bioinformatics", "Sequence analysis, NGS workflows, and bioinformatics pipelines."),
    ("SQL & Databases", "Schema design and complex querying with PostgreSQL and SQLite."),
    ("Docker", "Containerised, reproducible development and deployment environments."),
    ("Data Science", "Predictive models on real-world datasets; small AI/analytical projects."),
    ("Git & Version Control", "Version control and collaboration for academic and personal code."),
    ("Rust", "Learning Rust through small projects, focused on performance and systems."),
    ("R", "Statistical analysis, modelling, and data visualisation in academic projects."),
    ("Genetics & Molecular Biology", "Molecular biology, population genetics, and cytogenetics."),
    ("Organism Biology & Taxonomy", "Plant, vertebrate and invertebrate biology and classification."),
    ("Ecology & Evolution", "Ecology, biogeography, macroecology, and evolution."),
    ("Physiology & Microbiology", "Animal and plant physiology with solid molecular biology."),
]

EDUCATION = [
    ("MSc, Bioinformatics", "Faculdade de Ciências da Universidade do Porto", "Porto", 2025, None),
    ("BSc, Biology", "Faculdade de Ciências da Universidade do Porto", "Porto", 2022, 2025),
    ("Technological Course, Biotechnology", "Colégio Internato dos Carvalhos", "Porto", 2019, 2022),
]

EXPERIENCE = [
    ("Researcher", "Escola Superior de Saúde", "Porto", 2025, None, [
        "Designed and curated a structured database unifying microbiome–disease associations from the literature.",
        "Ran preliminary analyses on microbiome datasets for diversity trends and candidate biomarkers.",
    ]),
    ("Research Trainee", "i3S — Instituto de Investigação e Inovação em Saúde", "Porto", 2024, 2025, [
        "Built Python pipelines for large-scale detection of polyQ sequences.",
        "Integrated an SQLite database and statistical framework comparing codon usage across taxa.",
        "Best Poster Communication, 18th IJUP Young Researchers Meeting.",
    ]),
    ("Research Trainee", "ICBAS — Instituto de Ciências Biomédicas Abel Salazar", "Porto", 2021, 2022, [
        "Chromatographic isolation and purification; NMR and mass spectrometry analysis.",
    ]),
]


class Command(BaseCommand):
    help = "Seed the dev DB with real portfolio content + an all-blocks blog post."

    def handle(self, *args, **options):
        Image = get_image_model()
        Document = get_document_model()

        # ---- Site content / copy ----
        sc = SiteContent.objects.first() or SiteContent()
        sc.about_title = "About"
        sc.about_lead = "I'm a bioinformatics student interested in using data and code to study biological systems."
        sc.about_intro_headline = "Pipelines that connect biology with clean code."
        sc.about_intro_body = "My work focuses on data-driven biology — integrating informatics and evolutionary insight into structured, reproducible analyses."
        sc.about_quote = "At the intersection of biology and data, curiosity leads the way."
        sc.skills_title = "Skills"
        sc.skills_lead = "A mix of computational and wet-lab biology."
        sc.github_username = "rafaelmdc"
        sc.save()
        self.stdout.write("· SiteContent updated")

        # ---- Snippets ----
        Skill.objects.all().delete()
        for i, (name, desc) in enumerate(SKILLS):
            Skill.objects.create(name=name, description=desc, order=i, active=True)

        Education.objects.all().delete()
        for i, (title, inst, loc, sy, ey) in enumerate(EDUCATION):
            Education.objects.create(title=title, institution=inst, location=loc,
                                     start_year=sy, end_year=ey, order=i)

        ExperienceBullet.objects.all().delete()
        Experience.objects.all().delete()
        for i, (role, comp, loc, sy, ey, bullets) in enumerate(EXPERIENCE):
            x = Experience.objects.create(role=role, company=comp, location=loc,
                                          start_year=sy, end_year=ey, order=i)
            for j, b in enumerate(bullets):
                ExperienceBullet.objects.create(experience=x, text=b, order=j)

        Award.objects.all().delete()
        Award.objects.create(title="Best Poster Communication", issuer="18th IJUP, University of Porto",
                             year=2025, order=0)

        Language.objects.all().delete()
        Language.objects.create(name="Portuguese", level="native", order=0)
        Language.objects.create(name="English", level="fluent", order=1)
        self.stdout.write("· Snippets (skills, education, experience, awards, languages)")

        # ---- A couple of Wagtail images + a document for the blocks ----
        root = Collection.get_first_root_node()
        img = Image.objects.first()
        if img is None:
            from PIL import Image as PImage
            import io
            buf = io.BytesIO()
            PImage.new("RGB", (1200, 700), (180, 200, 230)).save(buf, "PNG")
            img = Image(title="Demo image", width=1200, height=700, collection=root)
            img.file.save("demo.png", ContentFile(buf.getvalue()), save=False)
            import hashlib
            img.file_size = buf.getbuffer().nbytes
            img.file_hash = hashlib.sha1(buf.getvalue()).hexdigest()
            img.save()

        doc = Document.objects.filter(title="Demo PDF").first()
        if doc is None:
            doc = Document(title="Demo PDF", collection=root)
            doc.file.save("demo.pdf", ContentFile(b"%PDF-1.4 demo document"), save=True)

        # ---- Portfolio project: PAARTA & PAASTA ----
        portfolio_index = PortfolioIndexPage.objects.first()
        PortfolioProjectPage.objects.exclude(pk=None).filter(slug="paarta-paasta").delete()
        proj = PortfolioProjectPage.objects.first()
        if proj is None:
            proj = PortfolioProjectPage(title="PAARTA & PAASTA")
            portfolio_index.add_child(instance=proj)
        proj.title = "PAARTA & PAASTA"
        proj.slug = "paarta-paasta"
        proj.subtitle = "A web atlas for exploring homorepeats, codon usage and taxonomy across annotated genomes."
        proj.github_url = "https://github.com/rafaelmdc"
        proj.body = [
            ("paragraph", {"text": "<p>A web atlas platform for exploring homorepeats, codon usage, taxonomy, provenance, and repeat-length statistics across annotated genomes, powered by pipeline infrastructure.</p>", "alignment": "left"}),
            ("image", {"image": img, "caption": "Atlas overview", "alignment": "wide", "style": "plain", "width_pct": 100, "radius": "lg", "shadow": "sm", "aspect": "auto"}),
        ]
        rev = proj.save_revision()
        rev.publish()
        for t in ["django", "nextflow", "celery", "redis", "codon-usage", "comparative-genomics"]:
            proj.tags.add(t)
        proj.save_revision().publish()
        self.stdout.write("· Portfolio project: PAARTA & PAASTA")

        # ---- Blog post exercising every block type ----
        blog_index = BlogIndexPage.objects.first()
        for p in BlogPage.objects.filter(slug="every-block-demo"):
            p.delete()
        post = BlogPage(
            title="Every block, rendered",
            slug="every-block-demo",
            date=date(2026, 5, 12),
            intro="A demo post that uses every StreamField block type to validate the headless renderer.",
            reading_time_minutes=4,
            featured=True,
            body=[
                ("heading", {"level": "h2", "text": "Headings and text"}),
                ("paragraph", {"text": "<p>This paragraph has <b>bold</b>, <i>italic</i> and a <a href='https://example.com'>link</a>, plus a list:</p><ul><li>One</li><li>Two</li></ul>", "alignment": "left"}),
                ("quote", "Curiosity leads the way."),
                ("callout", {"style": "tip", "title": "Tip", "text": "<p>Callouts highlight asides.</p>"}),
                ("code", {"title": "pipeline.py", "language": "python", "style": "terminal", "code": "def detect_polyq(seq):\n    return seq.count('Q')"}),
                ("image", {"image": img, "caption": "An inline image", "alignment": "center", "style": "plain", "width_pct": 80, "radius": "lg", "shadow": "sm", "aspect": "auto"}),
                ("gallery", {"title": "Gallery", "width_pct": 100, "autoplay": True, "images": [img, img]}),
                ("embed", {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "caption": "A video", "width": "md", "align": "center", "style": "card"}),
                ("button", {"text": "Read the paper", "url": "https://example.com", "variant": "primary"}),
                ("divider", None),
                ("spacer", "md"),
                ("section", {"background": "soft", "inner": [
                    ("heading", {"level": "h3", "text": "Nested section"}),
                    ("paragraph", {"text": "<p>Blocks can nest inside a section.</p>", "alignment": "left"}),
                ]}),
                ("pdfs", {"title": "Downloads", "description": "Supporting files", "documents": [
                    {"document": doc, "label": "Poster", "note": "IJUP 2025", "open_in_new": True},
                ]}),
            ],
        )
        blog_index.add_child(instance=post)
        post.save_revision().publish()
        for t in ["bioinformatics", "python", "demo"]:
            post.tags.add(t)
        post.save_revision().publish()
        self.stdout.write("· Blog post: every-block-demo")

        self.stdout.write(self.style.SUCCESS("Seed complete."))
