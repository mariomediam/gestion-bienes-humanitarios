from rest_framework import serializers


class Formulario2AUbicacionSerializer(serializers.Serializer):
    """Location fields of a Formulario 2A nested in an emergency."""

    distrito_nombre = serializers.CharField(allow_null=True)
    localidad = serializers.CharField(allow_null=True)
    barrio_sector_urbanizacion = serializers.CharField(allow_null=True)
    centro_poblado = serializers.CharField(allow_null=True)
    caserio = serializers.CharField(allow_null=True)
    anexo = serializers.CharField(allow_null=True)
    calle_manzana = serializers.CharField(allow_null=True)
    edificio_piso_dpto = serializers.CharField(allow_null=True)
    otros_ubicacion = serializers.CharField(allow_null=True)


class Formulario2ATotalSerializer(serializers.Serializer):
    """Count of rows in S43edan_formulario_2a."""

    total = serializers.IntegerField(min_value=0)
