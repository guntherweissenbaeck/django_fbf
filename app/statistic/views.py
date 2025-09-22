"""Django view implementations for the statistics dashboard.

The view logic delegates heavy lifting to ``StatisticsBuilder`` to keep the
class small and easy to reason about while also improving performance.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .services import StatisticsBuilder


class StatisticView(LoginRequiredMixin, TemplateView):
    """Render the statistics overview with yearly and cumulative summaries."""

    template_name = "statistic/overview.html"

    def get_context_data(self, **kwargs):
        """Return the template context with aggregated statistics.

        :param kwargs: Basiskontext von ``TemplateView``.
        :returns: Dictionary mit Kennzahlen, Diagrammdaten und Metadaten.
        """

        context = super().get_context_data(**kwargs)
        builder = StatisticsBuilder(self.request.GET.get("year"))
        context.update(builder.build_context())
        return context
