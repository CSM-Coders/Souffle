from django.db import models

# Create your models here.
class SouffleApp(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    long_description = models.TextField(blank=True)
    image = models.ImageField(upload_to='souffleApp/images/')
    url = models.URLField(blank=True)

class Horario(models.Model):
    curso = models.ForeignKey(SouffleApp, on_delete=models.CASCADE, related_name='horarios')
    fecha = models.DateField()
    hora = models.TimeField()
    cupos = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"{self.curso.title} - {self.fecha} {self.hora} (Cupos: {self.cupos})"

from django.contrib.auth.models import User
class Compra(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    curso = models.ForeignKey(SouffleApp, on_delete=models.CASCADE)
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE)
    fecha_compra = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} compró {self.curso.title} ({self.horario})"
