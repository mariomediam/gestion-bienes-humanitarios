from django.urls import path

from .views import (
    CondicionViviendaListView,
    DistritoBuscarView,
    EmergenciaBuscarView,
    EmergenciaDetailView,
    EmergenciaListView,
    EmergenciaTotalPorTipoPeligroView,
    EmergenciaTotalView,
    Formulario2ABuscarView,
    Formulario2ACreateView,
    Formulario2ADetailView,
    Formulario2AIntegranteTotalView,
    Formulario2ATotalView,
    MaterialParedListView,
    MaterialPisoListView,
    MaterialTechoListView,
    PersonalBuscarView,
    PersonalEncargadosAlmacenBuscarView,
    PersonalEvaluadoresBuscarView,
    PlanillaEntregaTotalView,
    TipoPeligroListView,
    TipoSeguroView,
    TipoUsoInstalacionListView,
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
    path(
        'tipos-uso-instalacion/',
        TipoUsoInstalacionListView.as_view(),
        name='tipos-uso-instalacion',
    ),
    path(
        'condiciones-vivienda/',
        CondicionViviendaListView.as_view(),
        name='condiciones-vivienda',
    ),
    path(
        'materiales-pared/',
        MaterialParedListView.as_view(),
        name='materiales-pared',
    ),
    path(
        'materiales-piso/',
        MaterialPisoListView.as_view(),
        name='materiales-piso',
    ),
    path(
        'materiales-techo/',
        MaterialTechoListView.as_view(),
        name='materiales-techo',
    ),
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
        'formularios-2a/<int:formulario_2a_id>/',
        Formulario2ADetailView.as_view(),
        name='formularios-2a-detalle',
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

