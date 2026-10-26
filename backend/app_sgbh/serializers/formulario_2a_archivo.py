from rest_framework import serializers


class Formulario2AArchivoSerializer(serializers.Serializer):
    """One file row returned after it is stored.

    ruta_archivo stays out of the response because it is an internal path.
    """

    archivo_id = serializers.UUIDField()
    formulario_2a_id = serializers.IntegerField()
    nombre_original = serializers.CharField()
    nombre_archivo = serializers.CharField()
    extension = serializers.CharField(allow_null=True)
    tamano_bytes = serializers.IntegerField(allow_null=True)
    esta_activo = serializers.BooleanField()
    fecha_registro = serializers.DateTimeField()
    c_usuari_login = serializers.CharField()


class Formulario2AArchivoBusquedaSerializer(serializers.Serializer):
    """One file row from the search.

    ruta_archivo stays out of the response because it is an internal path.
    emergencia_id and codigo_sinpad come from the parent formulario.
    codigo_sinpad is null when the emergency has no SINPAD code.
    """

    archivo_id = serializers.UUIDField()
    formulario_2a_id = serializers.IntegerField()
    nombre_original = serializers.CharField()
    nombre_archivo = serializers.CharField()
    extension = serializers.CharField(allow_null=True)
    tamano_bytes = serializers.IntegerField(allow_null=True)
    esta_activo = serializers.BooleanField()
    fecha_registro = serializers.DateTimeField()
    c_usuari_login = serializers.CharField()
    emergencia_id = serializers.IntegerField(source='formulario_2a.emergencia_id')
    codigo_sinpad = serializers.CharField(
        source='formulario_2a.emergencia.codigo_sinpad',
        allow_null=True,
    )
