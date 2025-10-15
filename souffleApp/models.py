from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class SouffleApp(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    long_description = models.TextField(blank=True)
    duration = models.CharField(max_length=50, blank=True)
    learning_outcomes = models.TextField(blank=True)
    materials = models.TextField(blank=True)
    ingredients = models.TextField(blank=True)
    price = models.CharField(max_length=150, blank=True)
    image = models.ImageField(upload_to='souffleApp/images/')
    embedding = models.BinaryField(null=True, blank=True)

class Horario(models.Model):
    curso = models.ForeignKey(SouffleApp, on_delete=models.CASCADE, related_name='horarios')
    fecha = models.DateField()
    hora = models.TimeField()
    cupos = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"{self.curso.title} - {self.fecha} {self.hora} (Cupos: {self.cupos})"

class Compra(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    curso = models.ForeignKey(SouffleApp, on_delete=models.CASCADE)
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE)
    fecha_compra = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} compró {self.curso.title} ({self.horario})"


class Favorite(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    curso = models.ForeignKey(SouffleApp, on_delete=models.CASCADE, related_name='favorited_by')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['usuario', 'curso'], name='unique_favorite_curso_usuario')
        ]

    def __str__(self):
        return f"{self.usuario.username} marcó como favorito {self.curso.title}"
