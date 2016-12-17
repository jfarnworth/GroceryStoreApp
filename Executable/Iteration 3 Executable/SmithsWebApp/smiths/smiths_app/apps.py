from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SmithsAppConfig(AppConfig):
    name = 'smiths_app'
    verbose_name = _('smiths_app')
