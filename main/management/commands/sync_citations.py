"""
Sync citation counts from Semantic Scholar for all publications with a DOI.

Usage:
    python manage.py sync_citations
    python manage.py sync_citations --dry-run
"""
import time
import logging

from django.core.management.base import BaseCommand, CommandError

from main.models import Publication

logger = logging.getLogger(__name__)

S2_API = "https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}"


class Command(BaseCommand):
    help = "Sync citation counts from Semantic Scholar for publications that have a DOI."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        try:
            import requests
        except ImportError:
            raise CommandError("requests is required: pip install requests")

        qs = Publication.objects.exclude(doi="")
        self.stdout.write(f"{qs.count()} publication(s) with a DOI.")
        dry_run = options["dry_run"]
        updated = errors = 0

        session = requests.Session()

        for pub in qs:
            url = S2_API.format(doi=pub.doi)
            try:
                resp = session.get(url, params={"fields": "citationCount"}, timeout=10)
                if resp.status_code == 404:
                    self.stderr.write(f"  not found  {pub.doi}")
                    continue
                resp.raise_for_status()
                count = resp.json().get("citationCount", 0) or 0
            except Exception as exc:
                self.stderr.write(f"  error  {pub.doi}: {exc}")
                errors += 1
                time.sleep(1)
                continue

            if dry_run:
                self.stdout.write(f"  {pub.doi} → {count} citations")
            else:
                if pub.citation_count != count:
                    pub.citation_count = count
                    pub.save(update_fields=["citation_count"])
                    self.stdout.write(f"  updated  {pub.doi} → {count}")
                    updated += 1

            time.sleep(0.35)  # ~3 req/s, well within the free tier limit

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run — nothing written."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Done — {updated} updated, {errors} error(s)."))
