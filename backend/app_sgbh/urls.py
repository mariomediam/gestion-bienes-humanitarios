import uuid

from django.urls import path, register_converter

from .views import (
    BienBuscarView,
    BienCreateView,
    BienDetailView,
    CategoriaBienListView,
    CategoriaMedioVidaListView,
    CondicionPersonaListView,
    CondicionViviendaListView,
    DistritoBuscarView,
    EmergenciaBuscarView,
    EmergenciaDetailView,
    EmergenciaListView,
    EmergenciaTotalPorTipoPeligroView,
    EmergenciaTotalView,
    EnfermedadCronicaListView,
    Formulario2AArchivoCreateView,
    Formulario2AArchivoDetailView,
    Formulario2ABuscarView,
    Formulario2ACreateView,
    Formulario2ADetailView,
    Formulario2AReporteView,
    Formulario2AFamiliaBuscarView,
    Formulario2AFamiliaCreateView,
    Formulario2AFamiliaDetailView,
    Formulario2AIntegranteBuscarView,
    Formulario2AIntegranteCreateView,
    Formulario2AIntegranteDetailView,
    Formulario2AIntegranteTotalView,
    Formulario2AMedioVidaBuscarView,
    Formulario2AMedioVidaCreateView,
    Formulario2AMedioVidaDetailView,
    Formulario2ATienePlanillaBahView,
    Formulario2ATotalView,
    Formulario2AViviendaBuscarView,
    Formulario2AViviendaCreateView,
    Formulario2AViviendaDetailView,
    AlmacenKardexBuscarView,
    GradoLesionListView,
    MaterialParedListView,
    MaterialPisoListView,
    MaterialTechoListView,
    PersonaBuscarView,
    PersonaCreateView,
    PersonaDetailView,
    PersonalBuscarView,
    PersonalEncargadosAlmacenBuscarView,
    PersonalEvaluadoresBuscarView,
    PlanillaEntregaCreateView,
    PlanillaEntregaDetailView,
    PlanillaEntregaReporteView,
    PlanillaEntregaTotalView,
    RolFamiliarListView,
    StockActualListView,
    TipoDanioPersonalListView,
    TipoDiscapacidadListView,
    TipoDocumentoListView,
    TipoMedioVidaListView,
    MovimientoBuscarView,
    MovimientoCreateView,
    MovimientoDetailView,
    MovimientoPlanillaBahBuscarView,
    TipoMovimientoListView,
    TipoPeligroListView,
    TipoSeguroView,
    TipoUsoInstalacionListView,
    UnidadMedidaListView,
    ReniecConsultarView,
)


class _ArchivoUUIDConverter:
    """UUID in either case. SQL Server returns uniqueidentifier in uppercase."""

    regex = (
        '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-'
        '[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
    )

    def to_python(self, value):
        return uuid.UUID(value)

    def to_url(self, value):
        return str(value)


register_converter(_ArchivoUUIDConverter, 'archivo_uuid')

app_name = 'sgbh'

urlpatterns = [
    path('personas/', PersonaCreateView.as_view(), name='personas'),
    path(
        'personas/<int:persona_id>/',
        PersonaDetailView.as_view(),
        name='personas-detalle',
    ),
    path('personas/buscar/', PersonaBuscarView.as_view(), name='personas-buscar'),
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
        'tipos-danio-personal/',
        TipoDanioPersonalListView.as_view(),
        name='tipos-danio-personal',
    ),
    path(
        'tipos-discapacidad/',
        TipoDiscapacidadListView.as_view(),
        name='tipos-discapacidad',
    ),
    path(
        'tipos-documento/',
        TipoDocumentoListView.as_view(),
        name='tipos-documento',
    ),
    path(
        'enfermedades-cronicas/',
        EnfermedadCronicaListView.as_view(),
        name='enfermedades-cronicas',
    ),
    path(
        'grados-lesion/',
        GradoLesionListView.as_view(),
        name='grados-lesion',
    ),
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
        'condiciones-persona/',
        CondicionPersonaListView.as_view(),
        name='condiciones-persona',
    ),
    path(
        'unidades-medida/',
        UnidadMedidaListView.as_view(),
        name='unidades-medida',
    ),
    path(
        'categorias-bienes/',
        CategoriaBienListView.as_view(),
        name='categorias-bienes',
    ),
    path('bienes/', BienCreateView.as_view(), name='bienes'),
    path('bienes/<int:bien_id>/', BienDetailView.as_view(), name='bienes-detalle'),
    path('bienes/buscar/', BienBuscarView.as_view(), name='bienes-buscar'),
    path('stock-actual/', StockActualListView.as_view(), name='stock-actual'),
    path('kardex/buscar/', AlmacenKardexBuscarView.as_view(), name='kardex-buscar'),
    path(
        'categorias-medios-vida/',
        CategoriaMedioVidaListView.as_view(),
        name='categorias-medios-vida',
    ),
    path(
        'tipos-medios-vida/',
        TipoMedioVidaListView.as_view(),
        name='tipos-medios-vida',
    ),
    path(
        'tipos-movimiento/',
        TipoMovimientoListView.as_view(),
        name='tipos-movimiento',
    ),
    path(
        'movimientos/',
        MovimientoCreateView.as_view(),
        name='movimientos',
    ),
    path(
        'movimientos/<int:movimiento_id>/',
        MovimientoDetailView.as_view(),
        name='movimientos-detalle',
    ),
    path(
        'movimientos/buscar/',
        MovimientoBuscarView.as_view(),
        name='movimientos-buscar',
    ),
    path(
        'movimientos/buscar-planilla-bah/',
        MovimientoPlanillaBahBuscarView.as_view(),
        name='movimientos-buscar-planilla-bah',
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
    path(
        'roles-familiares/',
        RolFamiliarListView.as_view(),
        name='roles-familiares',
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
        'formularios-2a/<int:formulario_2a_id>/reporte/',
        Formulario2AReporteView.as_view(),
        name='formularios-2a-reporte',
    ),
    path(
        'formularios-2a/<int:formulario_2a_id>/tiene-planilla-bah/',
        Formulario2ATienePlanillaBahView.as_view(),
        name='formularios-2a-tiene-planilla-bah',
    ),
    path(
        'formularios-2a/<int:formulario_2a_id>/archivos/',
        Formulario2AArchivoCreateView.as_view(),
        name='formularios-2a-archivos',
    ),
    path(
        'formularios-2a/<int:formulario_2a_id>/archivos/<archivo_uuid:archivo_id>/',
        Formulario2AArchivoDetailView.as_view(),
        name='formularios-2a-archivos-detalle',
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
        'familias/',
        Formulario2AFamiliaCreateView.as_view(),
        name='familias',
    ),
    path(
        'familias/<int:familia_id>/',
        Formulario2AFamiliaDetailView.as_view(),
        name='familias-detalle',
    ),
    path(
        'familias/buscar/',
        Formulario2AFamiliaBuscarView.as_view(),
        name='familias-buscar',
    ),
    path(
        'viviendas/',
        Formulario2AViviendaCreateView.as_view(),
        name='viviendas',
    ),
    path(
        'viviendas/<int:vivienda_id>/',
        Formulario2AViviendaDetailView.as_view(),
        name='viviendas-detalle',
    ),
    path(
        'viviendas/buscar/',
        Formulario2AViviendaBuscarView.as_view(),
        name='viviendas-buscar',
    ),
    path(
        'planillas-bah/',
        PlanillaEntregaCreateView.as_view(),
        name='planillas-bah',
    ),
    path(
        'planillas-bah/<int:planilla_entrega_id>/',
        PlanillaEntregaDetailView.as_view(),
        name='planillas-bah-detalle',
    ),
    path(
        'planillas-bah/<int:planilla_entrega_id>/reporte/',
        PlanillaEntregaReporteView.as_view(),
        name='planillas-bah-reporte',
    ),
    path(
        'planillas-bah/total/',
        PlanillaEntregaTotalView.as_view(),
        name='planillas-bah-total',
    ),
    path(
        'integrantes/',
        Formulario2AIntegranteCreateView.as_view(),
        name='integrantes',
    ),
    path(
        'integrantes/<int:integrante_id>/',
        Formulario2AIntegranteDetailView.as_view(),
        name='integrantes-detalle',
    ),
    path(
        'integrantes/buscar/',
        Formulario2AIntegranteBuscarView.as_view(),
        name='integrantes-buscar',
    ),
    path(
        'integrantes/total/',
        Formulario2AIntegranteTotalView.as_view(),
        name='integrantes-total',
    ),
    path(
        'medios-vida/',
        Formulario2AMedioVidaCreateView.as_view(),
        name='medios-vida',
    ),
    path(
        'medios-vida/<int:medio_vida_id>/',
        Formulario2AMedioVidaDetailView.as_view(),
        name='medios-vida-detalle',
    ),
    path(
        'medios-vida/buscar/',
        Formulario2AMedioVidaBuscarView.as_view(),
        name='medios-vida-buscar',
    ),
    path('reniec/consultar/', ReniecConsultarView.as_view(), name='reniec-consultar'),
]

