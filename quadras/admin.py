from django.contrib import admin, messages
from django.utils.timezone import now, localtime
from .models import Quadra

@admin.register(Quadra)
class QuadraAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativa')
    list_filter = ('ativa',)
    search_fields = ('nome',)

    def save_model(self, request, obj, form, change):
        if change and not obj.ativa:
            from reservas.models import Reserva
            hoje = localtime(now()).date()
            reservas_futuras = Reserva.objects.filter(
                quadra=obj, data__gte=hoje
            ).count()
            
            if reservas_futuras > 0:
                self.message_user(
                    request,
                    f'⚠️ Atenção: A quadra "{obj.nome}" foi desativada, mas existem {reservas_futuras} reserva(s) futuras para ela.',
                    level=messages.WARNING
                )
        super().save_model(request, obj, form, change)