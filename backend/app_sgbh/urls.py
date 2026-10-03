from django.urls import path

from .views import EmergenciaTotalView, Formulario2ATotalView, TipoSeguroView

app_name = 'sgbh'

urlpatterns = [
    path('tipo-seguro/', TipoSeguroView.as_view(), name='tipo-seguro'),
    path('emergencias/total/', EmergenciaTotalView.as_view(), name='emergencias-total'),
    path(
        'formularios-2a/total/',
        Formulario2ATotalView.as_view(),
        name='formularios-2a-total',
    ),
]

