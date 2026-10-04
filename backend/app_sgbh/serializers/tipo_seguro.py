from rest_framework import serializers

from ..models import TipoSeguro


class TipoSeguroSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoSeguro
        fields = '__all__'
