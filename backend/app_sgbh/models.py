from django.db import models


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

