from ..models import TipoSeguro


class TipoSeguroService:
    @staticmethod
    def get_all():
        return TipoSeguro.objects.all()

    @staticmethod
    def get_by_id(self, id: int):
        return TipoSeguro.objects.get(pk=id)
