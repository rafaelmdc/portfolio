# main/admin.py
# All of these models are now managed in the Wagtail admin:
#   - CV models (Education, Experience, Publication, Grant, Award, Language, Skill)
#     are registered as snippets in main/wagtail_hooks.py.
#   - Site copy / profile images live on the SiteContent Wagtail settings object.
# Nothing is registered with the Django admin here.
