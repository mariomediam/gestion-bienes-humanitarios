from rest_framework import serializers

from .movimiento import MovimientoDetalleBusquedaSerializer


class MovimientoPlanillaBahBusquedaSerializer(serializers.Serializer):
    """One planilla BAH linked to a warehouse movement.

    Movement, almacén, tipo, estado and encargado columns come from
    S43alm_movimientos and its catalogs. Planilla columns keep the aliases
    of the search query. codigo_sinpad, distrito_nombre, barrio and lote
    come from the receptor chain. encargado_almacen_nombre and
    integrante_receptor_nombre are apellido paterno, apellido materno and
    nombres. detalles lists the movement lines without repeating the header.
    """

    movimiento_id = serializers.IntegerField(source='movimiento_almacen.movimiento_id')
    almacen_id = serializers.IntegerField(source='movimiento_almacen.almacen_id')
    tipo_movimiento_id = serializers.IntegerField(
        source='movimiento_almacen.tipo_movimiento_id'
    )
    estado_movimiento_id = serializers.IntegerField(
        source='movimiento_almacen.estado_movimiento_id'
    )
    movimiento_origen_id = serializers.IntegerField(
        source='movimiento_almacen.movimiento_origen_id',
        allow_null=True,
    )
    fecha_movimiento = serializers.DateTimeField(
        source='movimiento_almacen.fecha_movimiento'
    )
    documento_referencia = serializers.CharField(
        source='movimiento_almacen.documento_referencia',
        allow_null=True,
    )
    fecha_documento = serializers.DateField(
        source='movimiento_almacen.fecha_documento',
        allow_null=True,
    )
    destinatario = serializers.CharField(
        source='movimiento_almacen.destinatario',
        allow_null=True,
    )
    observacion = serializers.CharField(
        source='movimiento_almacen.observacion',
        allow_null=True,
    )
    fecha_confirmacion = serializers.DateTimeField(
        source='movimiento_almacen.fecha_confirmacion',
        allow_null=True,
    )
    encargado_almacen_id = serializers.IntegerField(
        source='movimiento_almacen.encargado_almacen_id'
    )
    c_usuari_login = serializers.CharField(source='movimiento_almacen.c_usuari_login')
    fecha_creacion = serializers.DateTimeField(
        source='movimiento_almacen.fecha_creacion'
    )
    fecha_modificacion = serializers.DateTimeField(
        source='movimiento_almacen.fecha_modificacion',
        allow_null=True,
    )
    almacen_codigo = serializers.CharField(source='movimiento_almacen.almacen.codigo')
    almacen_nombre = serializers.CharField(source='movimiento_almacen.almacen.nombre')
    tipo_movimiento_codigo = serializers.CharField(
        source='movimiento_almacen.tipo_movimiento.codigo'
    )
    tipo_movimiento_nombre = serializers.CharField(
        source='movimiento_almacen.tipo_movimiento.nombre'
    )
    tipo_movimiento_naturaleza = serializers.CharField(
        source='movimiento_almacen.tipo_movimiento.naturaleza'
    )
    tipo_movimiento_origen = serializers.BooleanField(
        source='movimiento_almacen.tipo_movimiento.requiere_movimiento_origen'
    )
    estado_movimiento_codigo = serializers.CharField(
        source='movimiento_almacen.estado_movimiento.codigo'
    )
    estado_movimiento_nombre = serializers.CharField(
        source='movimiento_almacen.estado_movimiento.nombre'
    )
    encargado_almacen_nombre = serializers.SerializerMethodField()
    planilla_entrega_id = serializers.IntegerField()
    numero_planilla = serializers.IntegerField()
    anio_planilla = serializers.IntegerField()
    integrante_receptor_id = serializers.IntegerField()
    planilla_fecha_entrega = serializers.DateField(source='fecha_entrega')
    estado_planilla_id = serializers.IntegerField()
    planilla_entrega_observacion = serializers.CharField(
        source='observacion',
        allow_null=True,
    )
    planilla_entrega_fecha_emision = serializers.DateTimeField(
        source='fecha_emision',
        allow_null=True,
    )
    planilla_entrega_fecha_anulacion = serializers.DateTimeField(
        source='fecha_anulacion',
        allow_null=True,
    )
    planilla_entrega_motivo_anulacion = serializers.CharField(
        source='motivo_anulacion',
        allow_null=True,
    )
    movimiento_almacen_id = serializers.IntegerField()
    codigo_sinpad = serializers.CharField(
        source=(
            'integrante_receptor.familia.vivienda.formulario_2a'
            '.emergencia.codigo_sinpad'
        ),
        allow_null=True,
    )
    distrito_nombre = serializers.CharField(allow_null=True)
    barrio_sector_urbanizacion = serializers.CharField(
        source=(
            'integrante_receptor.familia.vivienda.formulario_2a'
            '.barrio_sector_urbanizacion'
        ),
        allow_null=True,
    )
    numero_lote = serializers.CharField(
        source='integrante_receptor.familia.vivienda.numero_lote',
        allow_null=True,
    )
    integrante_receptor_nombre = serializers.SerializerMethodField()
    detalles = MovimientoDetalleBusquedaSerializer(
        source='movimiento_almacen.detalles',
        many=True,
    )

    def get_encargado_almacen_nombre(self, obj):
        personal = obj.movimiento_almacen.encargado_almacen
        return (
            f'{personal.apellido_paterno} {personal.apellido_materno} {personal.nombres}'
        )

    def get_integrante_receptor_nombre(self, obj):
        persona = obj.integrante_receptor.persona
        return f'{persona.apellido_paterno} {persona.apellido_materno} {persona.nombres}'
