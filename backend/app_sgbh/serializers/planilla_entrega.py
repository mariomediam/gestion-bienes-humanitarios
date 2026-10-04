from rest_framework import serializers


class PlanillaEntregaTotalSerializer(serializers.Serializer):
    """Count of rows in S43bah_planilla_entrega."""

    total = serializers.IntegerField(min_value=0)
