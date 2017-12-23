from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.translation import ugettext as _

from utils.views import JsonDataResponseView
from tournaments.mixins import TournamentMixin


class LatestActionsView(TournamentMixin, JsonDataResponseView):

    def get_data(self):
        if not self.request.user.is_authenticated():
            return [{
                'user': "", 'type': "", 'timestamp': "", 'id': 0,
                'param': "You have been logged out. Log In to resume updates."
            }]

        actions = self.get_tournament().actionlogentry_set.prefetch_related(
                'content_object').order_by('-timestamp')[:15]

        action_objects = []
        for a in actions:
            action_objects.append({
                'user': a.user.username if a.user else a.ip_address or _("anonymous"),
                'type': a.get_type_display(),
                'param': a.get_content_object_display(),
                'timestamp': naturaltime(a.timestamp),
                'id': a.id
            })
        return action_objects
