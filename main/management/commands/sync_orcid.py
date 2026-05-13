"""
Sync publications and grants from an ORCID public profile.

Usage:
    python manage.py sync_orcid
    python manage.py sync_orcid --orcid-id 0000-0000-0000-0000
    python manage.py sync_orcid --highlight-name "Correia R" --dry-run
    python manage.py sync_orcid --no-authors   # skip per-work fetches, faster
    python manage.py sync_orcid --skip-works   # only sync grants
    python manage.py sync_orcid --skip-grants  # only sync works
"""
import time
import logging

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from main.models import Publication, Grant

logger = logging.getLogger(__name__)

ORCID_API = "https://pub.orcid.org/v3.0"
HEADERS   = {"Accept": "application/json"}

WORK_TYPE_MAP = {
    "journal-article":     "journal",
    "conference-paper":    "conference",
    "conference-abstract": "conference",
    "conference-poster":   "conference",
    "preprint":            "preprint",
    "dissertation-thesis": "thesis",
    "book-chapter":        "book_chapter",
}


def _get(url, session):
    resp = session.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.json()


def _extract_doi(external_ids):
    for eid in (external_ids or {}).get("external-id", []):
        if eid.get("external-id-type") == "doi":
            return eid.get("external-id-value", "").strip()
    return ""


def _extract_authors(work_detail):
    contributors = (work_detail.get("contributors", {}).get("contributor") or [])
    names = []
    for c in contributors:
        role = (c.get("contributor-attributes", {}).get("contributor-role") or "").upper()
        if role in ("AUTHOR", ""):
            name = (c.get("credit-name") or {}).get("value", "").strip()
            if name:
                names.append(name)
    return ", ".join(names)


def _year(date_obj):
    if not date_obj:
        return None
    val = (date_obj.get("year") or {}).get("value")
    return int(val) if val else None


class Command(BaseCommand):
    help = "Sync publications and grants from an ORCID public profile."

    def add_arguments(self, parser):
        parser.add_argument(
            "--orcid-id",
            default=getattr(settings, "ORCID_ID", ""),
            help="ORCID iD (e.g. 0000-0001-2345-6789). Falls back to settings.ORCID_ID.",
        )
        parser.add_argument(
            "--highlight-name",
            default=getattr(settings, "ORCID_HIGHLIGHT_NAME", ""),
            help="Author name string to bold in the CV (e.g. 'Correia R').",
        )
        parser.add_argument("--no-authors",   action="store_true", help="Skip per-work author fetch.")
        parser.add_argument("--skip-works",   action="store_true", help="Skip works/publications sync.")
        parser.add_argument("--skip-grants",  action="store_true", help="Skip funding/grants sync.")
        parser.add_argument("--dry-run",      action="store_true", help="Print changes without writing.")

    def handle(self, *args, **options):
        try:
            import requests
        except ImportError:
            raise CommandError("requests is required: pip install requests")

        orcid_id = options["orcid_id"].strip()
        if not orcid_id:
            raise CommandError(
                "No ORCID iD supplied. Pass --orcid-id or set ORCID_ID in settings/env."
            )

        session  = requests.Session()
        dry_run  = options["dry_run"]

        if not options["skip_works"]:
            self._sync_works(session, orcid_id, options, dry_run)

        if not options["skip_grants"]:
            self._sync_grants(session, orcid_id, dry_run)

    # ── Works ────────────────────────────────────────────────────────────────

    def _sync_works(self, session, orcid_id, options, dry_run):
        highlight  = options["highlight_name"].strip()
        no_authors = options["no_authors"]

        self.stdout.write(f"\nFetching works for {orcid_id}…")
        try:
            data = _get(f"{ORCID_API}/{orcid_id}/works", session)
        except Exception as exc:
            self.stderr.write(f"Works API error: {exc}")
            return

        groups  = data.get("group") or []
        created = updated = skipped = 0

        for group in groups:
            summaries = group.get("work-summary") or []
            if not summaries:
                continue
            summary  = summaries[0]
            put_code = str(summary.get("put-code", ""))
            title    = ((summary.get("title") or {}).get("title") or {}).get("value", "").strip()
            if not title or not put_code:
                continue

            pub_type = WORK_TYPE_MAP.get(summary.get("type", ""), "other")
            year     = _year(summary.get("publication-date"))
            venue    = ((summary.get("journal-title") or {}).get("value") or "").strip()
            doi      = _extract_doi(summary.get("external-ids"))

            authors = ""
            if not no_authors:
                try:
                    detail  = _get(f"{ORCID_API}/{orcid_id}/work/{put_code}", session)
                    authors = _extract_authors(detail)
                    time.sleep(0.2)
                except Exception as exc:
                    self.stderr.write(f"  Could not fetch work {put_code}: {exc}")

            defaults = {
                "title":          title,
                "venue":          venue or "",
                "year":           year or 0,
                "pub_type":       pub_type,
                "doi":            doi,
                "highlight_name": highlight,
            }
            if authors:
                defaults["authors"] = authors

            existing = Publication.objects.filter(orcid_put_code=put_code).first()

            if dry_run:
                action = "UPDATE" if existing else "CREATE"
                self.stdout.write(f"  [work {action}] {year} — {title[:70]}")
                skipped += 1
                continue

            if existing:
                for k, v in defaults.items():
                    setattr(existing, k, v)
                existing.save()
                updated += 1
            else:
                defaults["orcid_put_code"] = put_code
                defaults.setdefault("authors", "")
                Publication.objects.create(**defaults)
                created += 1

        if dry_run:
            self.stdout.write(self.style.WARNING(f"  Works dry run: {skipped} would be processed."))
        else:
            self.stdout.write(self.style.SUCCESS(f"  Works: {created} created, {updated} updated."))

    # ── Grants ───────────────────────────────────────────────────────────────

    def _sync_grants(self, session, orcid_id, dry_run):
        self.stdout.write(f"\nFetching fundings for {orcid_id}…")
        try:
            data = _get(f"{ORCID_API}/{orcid_id}/fundings", session)
        except Exception as exc:
            self.stderr.write(f"Fundings API error: {exc}")
            return

        groups  = data.get("group") or []
        created = updated = skipped = 0

        for group in groups:
            summaries = group.get("funding-summary") or []
            if not summaries:
                continue
            summary  = summaries[0]
            put_code = str(summary.get("put-code", ""))
            title    = ((summary.get("title") or {}).get("title") or {}).get("value", "").strip()
            if not title or not put_code:
                continue

            funder     = ((summary.get("organization") or {}).get("name") or "").strip()
            start_year = _year(summary.get("start-date"))
            end_year   = _year(summary.get("end-date"))

            # Fetch full detail for amount + description
            amount = description = ""
            try:
                detail      = _get(f"{ORCID_API}/{orcid_id}/funding/{put_code}", session)
                amt_obj     = detail.get("amount") or {}
                amt_val     = (amt_obj.get("value") or "").strip()
                amt_cur     = (amt_obj.get("currency-code") or "").strip()
                if amt_val:
                    amount = f"{amt_cur} {amt_val}".strip() if amt_cur else amt_val
                description = (detail.get("description") or "").strip()
                time.sleep(0.2)
            except Exception as exc:
                self.stderr.write(f"  Could not fetch funding {put_code}: {exc}")

            defaults = {
                "title":       title,
                "funder":      funder,
                "start_year":  start_year,
                "end_year":    end_year,
                "amount":      amount,
                "description": description,
            }

            existing = Grant.objects.filter(orcid_put_code=put_code).first()

            if dry_run:
                action = "UPDATE" if existing else "CREATE"
                self.stdout.write(f"  [grant {action}] {start_year} — {title[:70]}")
                skipped += 1
                continue

            if existing:
                for k, v in defaults.items():
                    setattr(existing, k, v)
                existing.save()
                updated += 1
            else:
                defaults["orcid_put_code"] = put_code
                Grant.objects.create(**defaults)
                created += 1

        if dry_run:
            self.stdout.write(self.style.WARNING(f"  Grants dry run: {skipped} would be processed."))
        else:
            self.stdout.write(self.style.SUCCESS(f"  Grants: {created} created, {updated} updated."))
