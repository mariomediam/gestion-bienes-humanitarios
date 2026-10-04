from django.urls import path

from .views import (
    EmergenciaListView,
    EmergenciaTotalPorTipoPeligroView,
    EmergenciaTotalView,
    Formulario2AIntegranteTotalView,
    Formulario2ATotalView,
    PlanillaEntregaTotalView,
    TipoPeligroListView,
    TipoSeguroView,
)

app_name = 'sgbh'

urlpatterns = [
    path('tipo-seguro/', TipoSeguroView.as_view(), name='tipo-seguro'),
    path('tipos-peligro/', TipoPeligroListView.as_view(), name='tipos-peligro'),
    path('emergencias/', EmergenciaListView.as_view(), name='emergencias'),
    path('emergencias/total/', EmergenciaTotalView.as_view(), name='emergencias-total'),
    path(
        'emergencias/total-por-tipo-peligro/',
        EmergenciaTotalPorTipoPeligroView.as_view(),
        name='emergencias-total-por-tipo-peligro',
    ),
    path(
        'formularios-2a/total/',
        Formulario2ATotalView.as_view(),
        name='formularios-2a-total',
    ),
    path(
        'planillas-bah/total/',
        PlanillaEntregaTotalView.as_view(),
        name='planillas-bah-total',
    ),
    path(
        'integrantes/total/',
        Formulario2AIntegranteTotalView.as_view(),
        name='integrantes-total',
    ),
]

