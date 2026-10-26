from rest_framework import serializers


class Formulario2AArchivoSerializer(serializers.Serializer):
    """One file row returned after it is stored.

    ruta_archivo stays out of the response because it is an internal path.
    """

    archivo_id = serializers.IntegerField()
    formulario_2a_id = serializers.IntegerField()
    nombre_original = serializers.CharField()
    nombre_archivo = serializers.CharField()
    extension = serializers.CharField(allow_null=True)
    tamano_bytes = serializers.IntegerField(allow_null=True)
    esta_activo = serializers.BooleanField()
    fecha_registro = serializers.DateTimeField()
    c_usuari_login = serializers.CharField()
