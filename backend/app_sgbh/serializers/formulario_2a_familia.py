from rest_framework import serializers

_INT_MIN = -2147483648
_INT_MAX = 2147483647


class FamiliaCreateSerializer(serializers.Serializer):
    """Validate the body used to insert S43edan_formulario_2a_familias.

    numero_orden is assigned by Formulario2AFamiliaService for the parent
    vivienda. The parent vivienda lock and the Formulario 2A lock are
    checked there. fecha_creacion uses the column default.
    """

    vivienda_id = serializers.IntegerField(
        min_value=_INT_MIN,
        max_value=_INT_MAX,
        error_messages={
            'required': 'El campo vivienda_id es obligatorio',
            'null': 'El campo vivienda_id es obligatorio',
            'invalid': 'El campo vivienda_id debe ser un número entero',
            'min_value': 'El campo vivienda_id debe ser un número entero',
            'max_value': 'El campo vivienda_id debe ser un número entero',
        },
    )


class FamiliaBusquedaSerializer(serializers.Serializer):
    """One familia row returned by the search endpoint.

    formulario_2a_id comes from the vivienda parent, the same column
    reached by joining S43edan_formulario_2a_viviendas and
    S43edan_formulario_2a.
    """

    familia_id = serializers.IntegerField()
    vivienda_id = serializers.IntegerField()
    numero_orden = serializers.IntegerField()
    fecha_creacion = serializers.DateTimeField()
    formulario_2a_id = serializers.IntegerField(source='vivienda.formulario_2a_id')


class FamiliaSerializer(serializers.Serializer):
    """One familia row returned after it is created."""

    familia_id = serializers.IntegerField()
    vivienda_id = serializers.IntegerField()
    numero_orden = serializers.IntegerField()
    fecha_creacion = serializers.DateTimeField()
