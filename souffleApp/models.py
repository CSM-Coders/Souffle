from django.db import models

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

    @property
    def ventas_totales(self):
        """Retorna el número total de ventas reales de este curso"""
        return self.compras.filter(estado='confirmada').count()
    
    @property
    def ingresos_totales(self):
        """Retorna los ingresos totales de este curso"""
        import re
        try:
            # Extraer el número del precio (buscar patrón COP $XXX.XXX)
            precio_texto = self.price
            # Buscar números con formato COP $240.000 o similar
            match = re.search(r'COP \$?(\d+(?:\.\d+)*)', precio_texto)
            if match:
                # Remover puntos de separación de miles y convertir a número
                precio_num = float(match.group(1).replace('.', ''))
                return precio_num * self.ventas_totales
            return 0
        except:
            return 0
    
    def compras_por_mes(self, year=None, month=None):
        """Retorna las compras de este curso filtradas por año y mes"""
        compras = self.compras.filter(estado='confirmada')
        if year:
            compras = compras.filter(fecha_compra__year=year)
        if month:
            compras = compras.filter(fecha_compra__month=month)
        return compras.count()

    def __str__(self):
        return self.title

class Horario(models.Model):
    curso = models.ForeignKey(SouffleApp, on_delete=models.CASCADE, related_name='horarios')
    fecha = models.DateField()
    hora = models.TimeField()
    cupos = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"{self.curso.title} - {self.fecha} {self.hora} (Cupos: {self.cupos})"
    
    @property
    def cupos_disponibles(self):
        """Retorna el número de cupos disponibles para este horario"""
        return self.cupos
    
    @property
    def tiene_cupos(self):
        """Verifica si el horario tiene cupos disponibles"""
        return self.cupos > 0
    
    def reducir_cupo(self):
        """Reduce en 1 el número de cupos disponibles"""
        if self.cupos > 0:
            self.cupos -= 1
            self.save()
            return True
        return False
    
    class Meta:
        ordering = ['fecha', 'hora']

from django.contrib.auth.models import User


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    curso = models.ForeignKey(SouffleApp, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'curso')

    def __str__(self):
        return f"{self.user.username} ❤ {self.curso.title}"


class Compra(models.Model):
    # Información del usuario
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='compras')
    email_usuario = models.EmailField(default='')  # Guardamos el email en el momento de la compra
    nombre_usuario = models.CharField(max_length=150, default='')  # Nombre completo del usuario
    
    # Información del curso
    curso = models.ForeignKey(SouffleApp, on_delete=models.CASCADE, related_name='compras')
    nombre_curso = models.CharField(max_length=100, default='')  # Nombre del curso al momento de la compra
    precio_pagado = models.CharField(max_length=150, default='')  # Precio que pagó
    
    # Información del horario
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE, related_name='compras')
    fecha_curso = models.DateField(null=True, blank=True)  # Fecha del curso
    hora_curso = models.TimeField(null=True, blank=True)   # Hora del curso
    
    # Información de la compra
    fecha_compra = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=[
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada')
    ], default='confirmada')

    def save(self, *args, **kwargs):
        # Autocompletar campos al crear la compra
        if not self.pk:  # Solo en creación
            self.email_usuario = self.usuario.email
            self.nombre_usuario = f"{self.usuario.first_name} {self.usuario.last_name}".strip() or self.usuario.username
            self.nombre_curso = self.curso.title
            self.precio_pagado = self.curso.price
            self.fecha_curso = self.horario.fecha
            self.hora_curso = self.horario.hora
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre_usuario} ({self.email_usuario}) - {self.nombre_curso} - {self.fecha_curso}"
    
    class Meta:
        ordering = ['-fecha_compra']
        verbose_name = "Compra"
        verbose_name_plural = "Compras"

# Nueva clase: Review
class Review(models.Model):
    curso = models.ForeignKey(SouffleApp, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    content = models.TextField(max_length=2000)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)  # opcional 1-5
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} on {self.curso.title}"
