# main/signals.py
# Previously held SiteAsset file-cleanup handlers. SiteAsset has been replaced by
# Wagtail-managed images (SiteContent), which handle their own file lifecycle, so
# there are no signal receivers here anymore. The module is kept because
# MainConfig.ready() imports it.
