"""
Regenerate the CV PDF Wagtail Document from the live CMS data.

Run on a schedule (e.g. a daily/weekly cron or k8s CronJob) to keep the cached
CV fresh, or manually:

    python manage.py gen_cv
    python manage.py gen_cv --force   # ignore the daily/weekly staleness window
"""
from django.core.management.base import BaseCommand

from main.cv import get_cv_document, regenerate_cv_document
from main.models import SiteContent


class Command(BaseCommand):
    help = "Regenerate the cached CV PDF document from CMS data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force", action="store_true",
            help="Regenerate even if the cached CV is still within its refresh window.",
        )

    def handle(self, *args, **options):
        sc = SiteContent.objects.first()
        if not sc:
            self.stderr.write("No SiteContent configured.")
            return
        try:
            doc = regenerate_cv_document(sc) if options["force"] else get_cv_document(sc)
        except RuntimeError as exc:
            self.stderr.write(str(exc))
            return
        if doc:
            self.stdout.write(self.style.SUCCESS(f"CV document ready → {doc.url}"))
        else:
            self.stdout.write("CV is disabled or unavailable.")
