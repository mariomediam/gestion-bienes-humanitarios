from .condicion_vivienda_view import CondicionViviendaListView
from .distrito_view import DistritoBuscarView
from .emergencia_view import (
    EmergenciaBuscarView,
    EmergenciaDetailView,
    EmergenciaListView,
    EmergenciaTotalPorTipoPeligroView,
    EmergenciaTotalView,
)
from .formulario_2a_familia_view import (
    Formulario2AFamiliaBuscarView,
    Formulario2AFamiliaCreateView,
    Formulario2AFamiliaDetailView,
)
from .formulario_2a_integrante_view import Formulario2AIntegranteTotalView
from .formulario_2a_view import (
    Formulario2ABuscarView,
    Formulario2ACreateView,
    Formulario2ADetailView,
    Formulario2ATotalView,
)
from .formulario_2a_vivienda_view import (
    Formulario2AViviendaBuscarView,
    Formulario2AViviendaCreateView,
    Formulario2AViviendaDetailView,
)
from .material_pared_view import MaterialParedListView
from .material_piso_view import MaterialPisoListView
from .material_techo_view import MaterialTechoListView
from .persona_view import PersonaCreateView
from .personal_view import (
    PersonalBuscarView,
    PersonalEncargadosAlmacenBuscarView,
    PersonalEvaluadoresBuscarView,
)
from .planilla_entrega_view import PlanillaEntregaTotalView
from .tipo_peligro_view import TipoPeligroListView
from .tipo_seguro_view import TipoSeguroView
from .tipo_uso_instalacion_view import TipoUsoInstalacionListView