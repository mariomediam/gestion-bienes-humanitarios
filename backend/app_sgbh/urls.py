from django.urls import path

from .views import EmergenciaTotalView, TipoSeguroView

app_name = 'sgbh'

urlpatterns = [
    path('tipo-seguro/', TipoSeguroView.as_view(), name='tipo-seguro'),
    path('emergencias/total/', EmergenciaTotalView.as_view(), name='emergencias-total'),
]

