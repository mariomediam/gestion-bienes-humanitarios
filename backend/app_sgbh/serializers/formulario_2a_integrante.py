from rest_framework import serializers


class Formulario2AIntegranteTotalSerializer(serializers.Serializer):
    """Count of rows in S43edan_formulario_2a_integrantes."""

    total = serializers.IntegerField(min_value=0)
