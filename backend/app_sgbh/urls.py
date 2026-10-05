from django.urls import path

from .views import (
    DistritoBuscarView,
    EmergenciaBuscarView,
    EmergenciaDetailView,
    EmergenciaListView,
    EmergenciaTotalPorTipoPeligroView,
    EmergenciaTotalView,
    Formulario2ABuscarView,
    Formulario2ACreateView,
    Formulario2AIntegranteTotalView,
    Formulario2ATotalView,
    PersonalBuscarView,
    PersonalEncargadosAlmacenBuscarView,
    PersonalEvaluadoresBuscarView,
    PlanillaEntregaTotalView,
    TipoPeligroListView,
    TipoSeguroView,
)

app_name = 'sgbh'

urlpatterns = [
    path('personal/buscar/', PersonalBuscarView.as_view(), name='personal-buscar'),
    path(
        'personal/buscar/evaluadores/',
        PersonalEvaluadoresBuscarView.as_view(),
        name='personal-evaluadores-buscar',
    ),
    path(
        'personal/buscar/encargados-almacen/',
        PersonalEncargadosAlmacenBuscarView.as_view(),
        name='personal-encargados-almacen-buscar',
    ),
    path('tipo-seguro/', TipoSeguroView.as_view(), name='tipo-seguro'),
    path('tipos-peligro/', TipoPeligroListView.as_view(), name='tipos-peligro'),
    path('distritos/buscar/', DistritoBuscarView.as_view(), name='distritos-buscar'),
    path('emergencias/', EmergenciaListView.as_view(), name='emergencias'),
    path(
        'emergencias/<int:emergencia_id>/',
        EmergenciaDetailView.as_view(),
        name='emergencias-detalle',
    ),
    path('emergencias/buscar/', EmergenciaBuscarView.as_view(), name='emergencias-buscar'),
    path('emergencias/total/', EmergenciaTotalView.as_view(), name='emergencias-total'),
    path(
        'emergencias/total-por-tipo-peligro/',
        EmergenciaTotalPorTipoPeligroView.as_view(),
        name='emergencias-total-por-tipo-peligro',
    ),
    path(
        'formularios-2a/',
        Formulario2ACreateView.as_view(),
        name='formularios-2a',
    ),
    path(
        'formularios-2a/buscar/',
        Formulario2ABuscarView.as_view(),
        name='formularios-2a-buscar',
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

