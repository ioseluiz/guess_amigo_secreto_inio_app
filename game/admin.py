from django.contrib import admin
from .models import GameSettings, Assignment, Vote

@admin.register(GameSettings)
class GameSettingsAdmin(admin.ModelAdmin):
    list_display = ('reveal_date',)

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('giver', 'encrypted_receiver')
    # Nota: No mostramos el receptor desencriptado aquí para mantener la seguridad
    # incluso ante los ojos del administrador.

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('voter', 'target_giver', 'encrypted_guess')