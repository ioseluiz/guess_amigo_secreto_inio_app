from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .utils import encrypt_data, decrypt_data

class GameSettings(models.Model):
    reveal_date = models.DateTimeField(help_text="Fecha y hora para revelar los resultados del juego.")

    def __str__(self):
        return f"Revelación: {self.reveal_date}"
    
    class Meta:
        verbose_name_plural = "Configuraciones del Juego"

class Assignment(models.Model):
    """Quien le regala a quien (Realidad)"""
    giver = models.OneToOneField(User, on_delete=models.CASCADE, related_name='my_assignment')
    # Guardamos el ID o Username del receptor encriptado
    encrypted_receiver = models.TextField()

    def set_receiver(self, receiver_username):
        self.encrypted_receiver = encrypt_data(receiver_username)
        self.save()

    def get_receiver(self):
        # Solo debe llamarse si la fecha de revalacion ha pasado o es el propio usuario
        return decrypt_data(self.encrypted_receiver)
    
class Vote(models.Model):
    """La prediccion de un usuario sobre otro"""
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes_made')
    target_giver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes_on_me')
    # Guardamos el ID o Username del receptor que el votante cree que es, encriptado
    encrypted_guess = models.TextField()

    class Meta:
        unique_together = ('voter', 'target_giver')

    def set_guess(self, guess_username):
        self.encrypted_guess = encrypt_data(guess_username)
        self.save()

    def get_guess(self):
        return decrypt_data(self.encrypted_guess)
    