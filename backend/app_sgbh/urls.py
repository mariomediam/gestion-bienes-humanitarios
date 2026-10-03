from django.urls import path

from .views import TipoSeguroView

app_name = 'sgbh'

urlpatterns = [
    path('tipo-seguro/', TipoSeguroView.as_view(), name='tipo-seguro'),
]

