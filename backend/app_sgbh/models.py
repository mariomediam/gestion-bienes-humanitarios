from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class TipoSeguro(models.Model):
    tipseguro_id = models.AutoField(primary_key=True)
    tipseguro_desc = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'Tipo_seguro'
        verbose_name = 'Tipo de Seguro'
        verbose_name_plural = 'Tipos de Seguro'

    def __str__(self):
        return f"{self.tipseguro_id} - {self.tipseguro_desc}"


# Unmanaged models for the existing SIAC tables prefixed with S43.
# Column names, nullability, defaults, unique keys and check constraints
# follow database/schema-SIAC-S43.sql. Foreign keys use PROTECT because
# the DDL does not declare ON DELETE CASCADE.


class Almacen(models.Model):
    almacen_id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=150)
    ubicacion = models.CharField(max_length=300, null=True, blank=True)
    esta_activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'S43alm_almacenes'
        verbose_name = 'Almacén'
        verbose_name_plural = 'Almacenes'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo'],
                name='UQ_alm_almacenes_codigo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class MovimientoDetalle(models.Model):
    movimiento_detalle_id = models.AutoField(primary_key=True)
    movimiento = models.ForeignKey(
        'Movimiento',
        on_delete=models.PROTECT,
        db_column='movimiento_id',
        db_index=False,
        related_name='detalles',
    )
    bien = models.ForeignKey(
        'Bien',
        on_delete=models.PROTECT,
        db_column='bien_id',
        db_index=False,
        related_name='movimientos_detalle',
    )
    cantidad = models.DecimalField(max_digits=18, decimal_places=6)
    cantidad_texto = models.CharField(max_length=30, null=True, blank=True)
    es_devolvible = models.BooleanField(default=False)
    observacion = models.CharField(max_length=500, null=True, blank=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'S43alm_movimiento_detalle'
        verbose_name = 'Detalle de movimiento'
        verbose_name_plural = 'Detalles de movimiento'
        constraints = [
            models.UniqueConstraint(
                fields=['movimiento', 'bien', 'es_devolvible'],
                name='UQ_alm_mov_det_bien_modalidad',
            ),
            models.CheckConstraint(
                condition=~Q(cantidad=0),
                name='CK_alm_mov_det_cantidad',
            ),
            models.CheckConstraint(
                condition=Q(cantidad__lt=0) | Q(es_devolvible=False),
                name='CK_alm_mov_det_devolvible',
            ),
            # CK_alm_mov_det_cantidad_texto stays in SQL Server:
            # cantidad_texto IS NULL OR LTRIM(RTRIM(cantidad_texto)) <> ''
        ]

    def __str__(self):
        return str(self.movimiento_detalle_id)


class Movimiento(models.Model):
    movimiento_id = models.AutoField(primary_key=True)
    almacen = models.ForeignKey(
        Almacen,
        on_delete=models.PROTECT,
        db_column='almacen_id',
        db_index=False,
        related_name='movimientos',
    )
    tipo_movimiento = models.ForeignKey(
        'TipoMovimiento',
        on_delete=models.PROTECT,
        db_column='tipo_movimiento_id',
        db_index=False,
        related_name='movimientos',
    )
    # DDL default: estado_movimiento_id = 1
    estado_movimiento = models.ForeignKey(
        'EstadoMovimiento',
        on_delete=models.PROTECT,
        db_column='estado_movimiento_id',
        db_index=False,
        related_name='movimientos',
        default=1,
    )
    movimiento_origen = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        db_column='movimiento_origen_id',
        db_index=False,
        related_name='movimientos_derivados',
        null=True,
        blank=True,
    )
    fecha_movimiento = models.DateTimeField(default=timezone.now)
    documento_referencia = models.CharField(max_length=100, null=True, blank=True)
    fecha_documento = models.DateField(null=True, blank=True)
    destinatario = models.CharField(max_length=250, null=True, blank=True)
    observacion = models.CharField(max_length=1000, null=True, blank=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)
    encargado_almacen = models.ForeignKey(
        'Personal',
        on_delete=models.PROTECT,
        db_column='encargado_almacen_id',
        db_index=False,
        related_name='movimientos_encargado',
    )
    # No foreign key in the schema.
    c_usuari_login = models.CharField(max_length=20)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_modificacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'S43alm_movimientos'
        verbose_name = 'Movimiento de almacén'
        verbose_name_plural = 'Movimientos de almacén'
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(movimiento_origen__isnull=True)
                    | ~Q(movimiento_origen=F('movimiento_id'))
                ),
                name='CK_alm_movimiento_origen_distinto',
            ),
        ]

    def __str__(self):
        return str(self.movimiento_id)


class Personal(models.Model):
    personal_id = models.SmallAutoField(primary_key=True)
    apellido_paterno = models.CharField(max_length=50)
    apellido_materno = models.CharField(max_length=50)
    nombres = models.CharField(max_length=150)
    es_evaluador_edan = models.BooleanField(default=False)
    es_encargado_almacen = models.BooleanField(default=False)
    esta_activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_modificacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'S43bah_personal'
        verbose_name = 'Personal'
        verbose_name_plural = 'Personal'
        constraints = [
            models.CheckConstraint(
                condition=Q(es_evaluador_edan=True) | Q(es_encargado_almacen=True),
                name='CK_bah_personal_tipo',
            ),
        ]

    def __str__(self):
        return f'{self.apellido_paterno} {self.apellido_materno}, {self.nombres}'


class PlanillaEntrega(models.Model):
    planilla_entrega_id = models.AutoField(primary_key=True)
    numero_planilla = models.IntegerField()
    anio_planilla = models.IntegerField()
    integrante_receptor = models.ForeignKey(
        'Formulario2AIntegrante',
        on_delete=models.PROTECT,
        db_column='integrante_receptor_id',
        db_index=False,
        related_name='planillas_entrega',
    )
    fecha_entrega = models.DateField()
    # DDL default: estado_planilla_id = 1
    estado_planilla = models.ForeignKey(
        'EstadoPlanilla',
        on_delete=models.PROTECT,
        db_column='estado_planilla_id',
        db_index=False,
        related_name='planillas',
        default=1,
    )
    observacion = models.CharField(max_length=1000, null=True, blank=True)
    fecha_emision = models.DateTimeField(null=True, blank=True)
    fecha_anulacion = models.DateTimeField(null=True, blank=True)
    motivo_anulacion = models.CharField(max_length=500, null=True, blank=True)
    # No foreign key in the schema.
    c_usuari_login = models.CharField(max_length=20)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_modificacion = models.DateTimeField(null=True, blank=True)
    movimiento_almacen = models.ForeignKey(
        Movimiento,
        on_delete=models.PROTECT,
        db_column='movimiento_almacen_id',
        db_index=False,
        related_name='planillas_entrega',
        null=True,
        blank=True,
    )

    class Meta:
        managed = False
        db_table = 'S43bah_planilla_entrega'
        verbose_name = 'Planilla de entrega'
        verbose_name_plural = 'Planillas de entrega'

    def __str__(self):
        return f'{self.numero_planilla}-{self.anio_planilla}'


class EstadoMovimiento(models.Model):
    estado_movimiento_id = models.SmallIntegerField(primary_key=True)
    codigo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=100)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_alm_estados_movimiento'
        verbose_name = 'Estado de movimiento'
        verbose_name_plural = 'Estados de movimiento'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo'],
                name='UQ_cat_alm_estados_movimiento_codigo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class TipoMovimiento(models.Model):
    tipo_movimiento_id = models.SmallIntegerField(primary_key=True)
    codigo = models.CharField(max_length=50)
    nombre = models.CharField(max_length=150)
    naturaleza = models.CharField(max_length=1)
    requiere_movimiento_origen = models.BooleanField(default=False)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_alm_tipos_movimiento'
        verbose_name = 'Tipo de movimiento'
        verbose_name_plural = 'Tipos de movimiento'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo'],
                name='UQ_cat_alm_tipos_movimiento_codigo',
            ),
            models.CheckConstraint(
                condition=Q(naturaleza__in=['E', 'S', 'M']),
                name='CK_cat_alm_tipos_movimiento_naturaleza',
            ),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class Bien(models.Model):
    bien_id = models.AutoField(primary_key=True)
    categoria_bien = models.ForeignKey(
        'CategoriaBien',
        on_delete=models.PROTECT,
        db_column='categoria_bien_id',
        db_index=False,
        related_name='bienes',
    )
    unidad_medida = models.ForeignKey(
        'UnidadMedida',
        on_delete=models.PROTECT,
        db_column='unidad_medida_id',
        db_index=False,
        related_name='bienes',
    )
    codigo = models.CharField(max_length=50)
    nombre = models.CharField(max_length=250)
    descripcion = models.CharField(max_length=500, null=True, blank=True)
    orden_impresion = models.SmallIntegerField(null=True, blank=True)
    esta_activo = models.BooleanField(default=True)
    visible_planilla = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_bah_bienes'
        verbose_name = 'Bien'
        verbose_name_plural = 'Bienes'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo'],
                name='UQ_cat_bah_bienes_codigo',
            ),
            models.CheckConstraint(
                condition=Q(orden_impresion__isnull=True) | Q(orden_impresion__gt=0),
                name='CK_cat_bah_bien_orden',
            ),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class CategoriaBien(models.Model):
    categoria_bien_id = models.SmallIntegerField(primary_key=True)
    codigo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=100)
    orden = models.SmallIntegerField()
    esta_activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_bah_categorias_bienes'
        verbose_name = 'Categoría de bien'
        verbose_name_plural = 'Categorías de bienes'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo'],
                name='UQ_cat_bah_categorias_bienes_codigo',
            ),
            models.CheckConstraint(
                condition=Q(orden__gt=0),
                name='CK_cat_bah_categorias_orden',
            ),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class EstadoPlanilla(models.Model):
    estado_planilla_id = models.SmallIntegerField(primary_key=True)
    codigo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=100)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_bah_estados_planilla'
        verbose_name = 'Estado de planilla'
        verbose_name_plural = 'Estados de planilla'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo'],
                name='UQ_cat_bah_estados_planilla_codigo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class ReglaEntrega(models.Model):
    regla_entrega_id = models.AutoField(primary_key=True)
    bien = models.ForeignKey(
        Bien,
        on_delete=models.PROTECT,
        db_column='bien_id',
        db_index=False,
        related_name='reglas_entrega',
    )
    tipo_calculo = models.ForeignKey(
        'TipoCalculo',
        on_delete=models.PROTECT,
        db_column='tipo_calculo_id',
        db_index=False,
        related_name='reglas_entrega',
    )
    cantidad_base = models.DecimalField(max_digits=18, decimal_places=6)
    cantidad_base_texto = models.CharField(max_length=30, null=True, blank=True)
    aplica_damnificado = models.BooleanField(default=False)
    aplica_afectado = models.BooleanField(default=False)
    cantidad_maxima = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        null=True,
        blank=True,
    )
    cantidad_maxima_texto = models.CharField(max_length=30, null=True, blank=True)
    observacion = models.CharField(max_length=500, null=True, blank=True)
    esta_activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_modificacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'S43cat_bah_reglas_entrega'
        verbose_name = 'Regla de entrega'
        verbose_name_plural = 'Reglas de entrega'
        constraints = [
            models.CheckConstraint(
                condition=Q(aplica_damnificado=True) | Q(aplica_afectado=True),
                name='CK_cat_bah_regla_aplicacion',
            ),
            models.CheckConstraint(
                condition=Q(cantidad_base__gt=0),
                name='CK_cat_bah_regla_cantidad_base',
            ),
            models.CheckConstraint(
                condition=Q(cantidad_maxima__isnull=True) | Q(cantidad_maxima__gt=0),
                name='CK_cat_bah_regla_cantidad_maxima',
            ),
            # CK_cat_bah_regla_base_texto and CK_cat_bah_regla_maximo_texto
            # stay in SQL Server: LTRIM(RTRIM(texto)) <> '' when the value is not null.
        ]

    def __str__(self):
        return str(self.regla_entrega_id)


class TipoCalculo(models.Model):
    tipo_calculo_id = models.SmallIntegerField(primary_key=True)
    codigo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=150)
    descripcion = models.CharField(max_length=500, null=True, blank=True)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_bah_tipos_calculo'
        verbose_name = 'Tipo de cálculo'
        verbose_name_plural = 'Tipos de cálculo'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo'],
                name='UQ_cat_bah_tipos_calculo_codigo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class UnidadMedida(models.Model):
    unidad_medida_id = models.SmallIntegerField(primary_key=True)
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=100)
    abreviatura = models.CharField(max_length=20, null=True, blank=True)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_bah_unidades_medida'
        verbose_name = 'Unidad de medida'
        verbose_name_plural = 'Unidades de medida'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo'],
                name='UQ_cat_bah_unidades_medida_codigo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class CategoriaMedioVida(models.Model):
    categoria_medio_vida_id = models.SmallIntegerField(primary_key=True)
    codigo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=100)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_categorias_medios_vida'
        verbose_name = 'Categoría de medio de vida'
        verbose_name_plural = 'Categorías de medios de vida'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo'],
                name='UQ_cat_categorias_medios_vida_codigo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class CondicionPersona(models.Model):
    condicion_persona_id = models.SmallIntegerField(primary_key=True)
    codigo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=100)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_condiciones_persona'
        verbose_name = 'Condición de persona'
        verbose_name_plural = 'Condiciones de persona'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo'],
                name='UQ_cat_condiciones_persona_codigo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class CondicionVivienda(models.Model):
    condicion_vivienda_id = models.SmallIntegerField(primary_key=True)
    codigo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=100)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_condiciones_vivienda'
        verbose_name = 'Condición de vivienda'
        verbose_name_plural = 'Condiciones de vivienda'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo'],
                name='UQ_cat_condiciones_vivienda_codigo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class EnfermedadCronica(models.Model):
    enfermedad_cronica_id = models.SmallIntegerField(primary_key=True)
    codigo_formulario = models.SmallIntegerField()
    nombre = models.CharField(max_length=200)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_enfermedades_cronicas'
        verbose_name = 'Enfermedad crónica'
        verbose_name_plural = 'Enfermedades crónicas'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo_formulario'],
                name='UQ_cat_enfermedades_cronicas_codigo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo_formulario} - {self.nombre}'


class EstadoRegistro(models.Model):
    estado_registro_id = models.SmallIntegerField(primary_key=True)
    codigo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=100)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_estados_registro'
        verbose_name = 'Estado de registro'
        verbose_name_plural = 'Estados de registro'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo'],
                name='UQ_cat_estados_registro_codigo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class GradoLesion(models.Model):
    grado_lesion_id = models.SmallIntegerField(primary_key=True)
    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=100)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_grados_lesion'
        verbose_name = 'Grado de lesión'
        verbose_name_plural = 'Grados de lesión'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo'],
                name='UQ_cat_grados_lesion_codigo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class MaterialPared(models.Model):
    material_pared_id = models.SmallIntegerField(primary_key=True)
    codigo_formulario = models.SmallIntegerField()
    nombre = models.CharField(max_length=200)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_materiales_pared'
        verbose_name = 'Material de pared'
        verbose_name_plural = 'Materiales de pared'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo_formulario'],
                name='UQ_cat_materiales_pared_codigo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo_formulario} - {self.nombre}'


class MaterialPiso(models.Model):
    material_piso_id = models.SmallIntegerField(primary_key=True)
    codigo_formulario = models.SmallIntegerField()
    nombre = models.CharField(max_length=200)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_materiales_piso'
        verbose_name = 'Material de piso'
        verbose_name_plural = 'Materiales de piso'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo_formulario'],
                name='UQ_cat_materiales_piso_codigo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo_formulario} - {self.nombre}'


class MaterialTecho(models.Model):
    material_techo_id = models.SmallIntegerField(primary_key=True)
    codigo_formulario = models.SmallIntegerField()
    nombre = models.CharField(max_length=200)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_materiales_techo'
        verbose_name = 'Material de techo'
        verbose_name_plural = 'Materiales de techo'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo_formulario'],
                name='UQ_cat_materiales_techo_codigo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo_formulario} - {self.nombre}'


class RolFamiliar(models.Model):
    rol_familiar_id = models.SmallIntegerField(primary_key=True)
    codigo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=100)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_roles_familiares'
        verbose_name = 'Rol familiar'
        verbose_name_plural = 'Roles familiares'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo'],
                name='UQ_cat_roles_familiares_codigo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class TipoDanioPersonal(models.Model):
    tipo_danio_personal_id = models.SmallIntegerField(primary_key=True)
    codigo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=100)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_tipos_danio_personal'
        verbose_name = 'Tipo de daño personal'
        verbose_name_plural = 'Tipos de daño personal'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo'],
                name='UQ_cat_tipos_danio_personal_codigo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class TipoDiscapacidad(models.Model):
    tipo_discapacidad_id = models.SmallIntegerField(primary_key=True)
    codigo_formulario = models.SmallIntegerField()
    nombre = models.CharField(max_length=150)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_tipos_discapacidad'
        verbose_name = 'Tipo de discapacidad'
        verbose_name_plural = 'Tipos de discapacidad'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo_formulario'],
                name='UQ_cat_tipos_discapacidad_codigo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo_formulario} - {self.nombre}'


class TipoDocumento(models.Model):
    tipo_documento_id = models.SmallIntegerField(primary_key=True)
    codigo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=100)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_tipos_documento'
        verbose_name = 'Tipo de documento'
        verbose_name_plural = 'Tipos de documento'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo'],
                name='UQ_cat_tipos_documento_codigo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class TipoMedioVida(models.Model):
    tipo_medio_vida_id = models.SmallIntegerField(primary_key=True)
    categoria_medio_vida = models.ForeignKey(
        CategoriaMedioVida,
        on_delete=models.PROTECT,
        db_column='categoria_medio_vida_id',
        db_index=False,
        related_name='tipos_medio_vida',
    )
    codigo_formulario = models.SmallIntegerField()
    nombre = models.CharField(max_length=200)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_tipos_medios_vida'
        verbose_name = 'Tipo de medio de vida'
        verbose_name_plural = 'Tipos de medio de vida'
        constraints = [
            models.UniqueConstraint(
                fields=['categoria_medio_vida', 'codigo_formulario'],
                name='UQ_cat_tipos_medios_vida_codigo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo_formulario} - {self.nombre}'


class TipoPeligro(models.Model):
    tipo_peligro_id = models.IntegerField(primary_key=True)
    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=200)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_tipos_peligro'
        verbose_name = 'Tipo de peligro'
        verbose_name_plural = 'Tipos de peligro'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo'],
                name='UQ_cat_tipos_peligro_codigo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class TipoUsoInstalacion(models.Model):
    tipo_uso_instalacion_id = models.SmallIntegerField(primary_key=True)
    codigo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=100)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'S43cat_tipos_uso_instalacion'
        verbose_name = 'Tipo de uso de instalación'
        verbose_name_plural = 'Tipos de uso de instalación'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo'],
                name='UQ_cat_tipos_uso_instalacion_codigo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class Emergencia(models.Model):
    emergencia_id = models.AutoField(primary_key=True)
    numero_evaluacion = models.CharField(max_length=50)
    codigo_sinpad = models.CharField(max_length=30, null=True, blank=True)
    tipo_peligro = models.ForeignKey(
        TipoPeligro,
        on_delete=models.PROTECT,
        db_column='tipo_peligro_id',
        db_index=False,
        related_name='emergencias',
    )
    fecha_emergencia = models.DateField()
    hora_ocurrencia_estimada = models.TimeField(null=True, blank=True)
    esta_activo = models.BooleanField(default=True)
    # No foreign key in the schema.
    c_usuari_login = models.CharField(max_length=20)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_modificacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'S43edan_emergencias'
        verbose_name = 'Emergencia'
        verbose_name_plural = 'Emergencias'

    def __str__(self):
        return self.numero_evaluacion


class Formulario2A(models.Model):
    formulario_2a_id = models.AutoField(primary_key=True)
    emergencia = models.ForeignKey(
        Emergencia,
        on_delete=models.PROTECT,
        db_column='emergencia_id',
        db_index=False,
        related_name='formularios_2a',
    )
    # Ubigeo codes stored as CHAR(2). The schema does not declare a foreign key.
    departamento_id = models.CharField(max_length=2)
    provincia_id = models.CharField(max_length=2)
    distrito_id = models.CharField(max_length=2)
    fecha_empadronamiento = models.DateField()
    hora_empadronamiento = models.TimeField(null=True, blank=True)
    localidad = models.CharField(max_length=200, null=True, blank=True)
    barrio_sector_urbanizacion = models.CharField(max_length=250, null=True, blank=True)
    centro_poblado = models.CharField(max_length=200, null=True, blank=True)
    caserio = models.CharField(max_length=200, null=True, blank=True)
    anexo = models.CharField(max_length=200, null=True, blank=True)
    calle_manzana = models.CharField(max_length=250, null=True, blank=True)
    edificio_piso_dpto = models.CharField(max_length=250, null=True, blank=True)
    otros_ubicacion = models.CharField(max_length=250, null=True, blank=True)
    numero_hoja = models.SmallIntegerField(default=1)
    total_hojas = models.SmallIntegerField(null=True, blank=True)
    institucion = models.CharField(max_length=250, null=True, blank=True)
    evaluador = models.ForeignKey(
        Personal,
        on_delete=models.PROTECT,
        db_column='evaluador_id',
        db_index=False,
        related_name='formularios_evaluados',
    )
    # DDL default: estado_registro_id = 1
    estado_registro = models.ForeignKey(
        EstadoRegistro,
        on_delete=models.PROTECT,
        db_column='estado_registro_id',
        db_index=False,
        related_name='formularios_2a',
        default=1,
    )
    # No foreign key in the schema.
    c_usuari_login = models.CharField(max_length=20)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_modificacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'S43edan_formulario_2a'
        verbose_name = 'Formulario EDAN 2A'
        verbose_name_plural = 'Formularios EDAN 2A'
        constraints = [
            models.CheckConstraint(
                condition=Q(numero_hoja__gt=0),
                name='CK_f2a_numero_hoja',
            ),
            models.CheckConstraint(
                condition=Q(total_hojas__isnull=True) | Q(total_hojas__gte=F('numero_hoja')),
                name='CK_f2a_total_hojas',
            ),
        ]

    def __str__(self):
        return str(self.formulario_2a_id)


class Formulario2AFamilia(models.Model):
    familia_id = models.AutoField(primary_key=True)
    vivienda = models.ForeignKey(
        'Formulario2AVivienda',
        on_delete=models.PROTECT,
        db_column='vivienda_id',
        db_index=False,
        related_name='familias',
    )
    numero_orden = models.SmallIntegerField()
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'S43edan_formulario_2a_familias'
        verbose_name = 'Familia del formulario 2A'
        verbose_name_plural = 'Familias del formulario 2A'
        constraints = [
            models.UniqueConstraint(
                fields=['vivienda', 'numero_orden'],
                name='UQ_f2a_familia_orden',
            ),
            models.CheckConstraint(
                condition=Q(numero_orden__gt=0),
                name='CK_f2a_familia_orden',
            ),
        ]

    def __str__(self):
        return str(self.familia_id)


class Formulario2AIntegrante(models.Model):
    integrante_id = models.AutoField(primary_key=True)
    familia = models.ForeignKey(
        Formulario2AFamilia,
        on_delete=models.PROTECT,
        db_column='familia_id',
        db_index=False,
        related_name='integrantes',
    )
    persona = models.ForeignKey(
        'Persona',
        on_delete=models.PROTECT,
        db_column='persona_id',
        db_index=False,
        related_name='integrantes',
    )
    rol_familiar = models.ForeignKey(
        RolFamiliar,
        on_delete=models.PROTECT,
        db_column='rol_familiar_id',
        db_index=False,
        related_name='integrantes',
    )
    numero_orden = models.SmallIntegerField()
    edad = models.SmallIntegerField()
    condicion_persona = models.ForeignKey(
        CondicionPersona,
        on_delete=models.PROTECT,
        db_column='condicion_persona_id',
        db_index=False,
        related_name='integrantes',
    )
    tipo_danio_personal = models.ForeignKey(
        TipoDanioPersonal,
        on_delete=models.PROTECT,
        db_column='tipo_danio_personal_id',
        db_index=False,
        related_name='integrantes',
        null=True,
        blank=True,
    )
    grado_lesion = models.ForeignKey(
        GradoLesion,
        on_delete=models.PROTECT,
        db_column='grado_lesion_id',
        db_index=False,
        related_name='integrantes',
        null=True,
        blank=True,
    )
    gestante_semanas = models.SmallIntegerField(null=True, blank=True)
    tipo_discapacidad = models.ForeignKey(
        TipoDiscapacidad,
        on_delete=models.PROTECT,
        db_column='tipo_discapacidad_id',
        db_index=False,
        related_name='integrantes',
        null=True,
        blank=True,
    )
    enfermedad_cronica = models.ForeignKey(
        EnfermedadCronica,
        on_delete=models.PROTECT,
        db_column='enfermedad_cronica_id',
        db_index=False,
        related_name='integrantes',
        null=True,
        blank=True,
    )
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'S43edan_formulario_2a_integrantes'
        verbose_name = 'Integrante del formulario 2A'
        verbose_name_plural = 'Integrantes del formulario 2A'
        constraints = [
            models.UniqueConstraint(
                fields=['familia', 'numero_orden'],
                name='UQ_f2a_integrante_orden',
            ),
            models.UniqueConstraint(
                fields=['familia', 'persona'],
                name='UQ_f2a_integrante_persona',
            ),
            models.CheckConstraint(
                condition=Q(edad__gte=0, edad__lte=130),
                name='CK_f2a_integrante_edad',
            ),
            # DDL check compares tipo_danio_personal_id to 1.
            models.CheckConstraint(
                condition=Q(grado_lesion__isnull=True) | Q(tipo_danio_personal_id=1),
                name='CK_f2a_integrante_grado',
            ),
            models.CheckConstraint(
                condition=(
                    Q(gestante_semanas__isnull=True)
                    | Q(gestante_semanas__gte=1, gestante_semanas__lte=45)
                ),
                name='CK_f2a_salud_gestante',
            ),
        ]

    def __str__(self):
        return str(self.integrante_id)


class Formulario2AMedioVida(models.Model):
    medio_vida_id = models.AutoField(primary_key=True)
    familia = models.ForeignKey(
        Formulario2AFamilia,
        on_delete=models.PROTECT,
        db_column='familia_id',
        db_index=False,
        related_name='medios_vida',
    )
    tipo_medio_vida = models.ForeignKey(
        TipoMedioVida,
        on_delete=models.PROTECT,
        db_column='tipo_medio_vida_id',
        db_index=False,
        related_name='medios_vida',
    )
    cantidad = models.IntegerField()
    observacion = models.CharField(max_length=500, null=True, blank=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'S43edan_formulario_2a_medios_vida'
        verbose_name = 'Medio de vida del formulario 2A'
        verbose_name_plural = 'Medios de vida del formulario 2A'
        constraints = [
            models.UniqueConstraint(
                fields=['familia', 'tipo_medio_vida'],
                name='UQ_f2a_medio_vida_familia_tipo',
            ),
            models.CheckConstraint(
                condition=Q(cantidad__gt=0),
                name='CK_f2a_medio_vida_cantidad',
            ),
        ]

    def __str__(self):
        return str(self.medio_vida_id)


class Formulario2AVivienda(models.Model):
    vivienda_id = models.AutoField(primary_key=True)
    formulario_2a = models.ForeignKey(
        Formulario2A,
        on_delete=models.PROTECT,
        db_column='formulario_2a_id',
        db_index=False,
        related_name='viviendas',
    )
    numero_orden = models.SmallIntegerField()
    numero_lote = models.CharField(max_length=50, null=True, blank=True)
    tenencia_propia = models.BooleanField(null=True, blank=True)
    tipo_uso_instalacion = models.ForeignKey(
        TipoUsoInstalacion,
        on_delete=models.PROTECT,
        db_column='tipo_uso_instalacion_id',
        db_index=False,
        related_name='viviendas',
    )
    condicion_vivienda = models.ForeignKey(
        CondicionVivienda,
        on_delete=models.PROTECT,
        db_column='condicion_vivienda_id',
        db_index=False,
        related_name='viviendas',
        null=True,
        blank=True,
    )
    material_techo = models.ForeignKey(
        MaterialTecho,
        on_delete=models.PROTECT,
        db_column='material_techo_id',
        db_index=False,
        related_name='viviendas',
        null=True,
        blank=True,
    )
    material_pared = models.ForeignKey(
        MaterialPared,
        on_delete=models.PROTECT,
        db_column='material_pared_id',
        db_index=False,
        related_name='viviendas',
        null=True,
        blank=True,
    )
    material_piso = models.ForeignKey(
        MaterialPiso,
        on_delete=models.PROTECT,
        db_column='material_piso_id',
        db_index=False,
        related_name='viviendas',
        null=True,
        blank=True,
    )
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'S43edan_formulario_2a_viviendas'
        verbose_name = 'Vivienda del formulario 2A'
        verbose_name_plural = 'Viviendas del formulario 2A'
        constraints = [
            models.UniqueConstraint(
                fields=['formulario_2a', 'numero_orden'],
                name='UQ_f2a_instalacion_orden',
            ),
            models.CheckConstraint(
                condition=Q(numero_orden__gt=0),
                name='CK_f2a_instalacion_orden',
            ),
        ]

    def __str__(self):
        return str(self.vivienda_id)


class Persona(models.Model):
    persona_id = models.AutoField(primary_key=True)
    tipo_documento = models.ForeignKey(
        TipoDocumento,
        on_delete=models.PROTECT,
        db_column='tipo_documento_id',
        db_index=False,
        related_name='personas',
        null=True,
        blank=True,
    )
    numero_documento = models.CharField(max_length=20, null=True, blank=True)
    apellido_paterno = models.CharField(max_length=50)
    apellido_materno = models.CharField(max_length=50)
    nombres = models.CharField(max_length=150)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=1)
    telefono = models.CharField(max_length=50)
    correo = models.CharField(max_length=50)
    esta_activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    # No foreign key in the schema.
    c_usuari_login = models.CharField(max_length=20)
    fecha_modificacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'S43personas'
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'
        constraints = [
            models.CheckConstraint(
                condition=(
                    (Q(numero_documento__isnull=True) & Q(tipo_documento__isnull=True))
                    | (Q(numero_documento__isnull=False) & Q(tipo_documento__isnull=False))
                ),
                name='CK_personas_documento',
            ),
        ]

    def __str__(self):
        return f'{self.apellido_paterno} {self.apellido_materno}, {self.nombres}'
