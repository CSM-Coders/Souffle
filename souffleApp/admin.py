from django.contrib import admin
from .models import SouffleApp, Horario, Compra, Review

# Register your models here.

admin.site.register(SouffleApp)

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('get_info_usuario', 'nombre_curso', 'precio_pagado', 'fecha_curso', 'hora_curso', 'fecha_compra', 'estado')
    list_filter = ('estado', 'fecha_compra', 'fecha_curso', 'nombre_curso')
    search_fields = ('nombre_usuario', 'email_usuario', 'nombre_curso')
    readonly_fields = ('email_usuario', 'nombre_usuario', 'nombre_curso', 'precio_pagado', 'fecha_curso', 'hora_curso', 'fecha_compra')
    ordering = ('-fecha_compra',)
    
    def get_info_usuario(self, obj):
        return f"{obj.nombre_usuario} ({obj.email_usuario})"
    get_info_usuario.short_description = 'Usuario'
    
    # Configuración para mejor visualización
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('usuario', 'nombre_usuario', 'email_usuario')
        }),
        ('Información del Curso', {
            'fields': ('curso', 'nombre_curso', 'precio_pagado')
        }),
        ('Información del Horario', {
            'fields': ('horario', 'fecha_curso', 'hora_curso')
        }),
        ('Información de la Compra', {
            'fields': ('fecha_compra', 'estado')
        }),
    )

@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ('curso', 'fecha', 'hora', 'cupos', 'tiene_cupos', 'compras_realizadas')
    list_filter = ('fecha', 'curso')
    search_fields = ('curso__title',)
    ordering = ('fecha', 'hora')
    
    def tiene_cupos(self, obj):
        return obj.cupos > 0
    tiene_cupos.boolean = True
    tiene_cupos.short_description = 'Disponible'
    
    def compras_realizadas(self, obj):
        return obj.compras.filter(estado='confirmada').count()
    compras_realizadas.short_description = 'Compras'

# Registrar Review en admin

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('short_content', 'user', 'curso', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'curso')
    search_fields = ('content', 'user__username', 'curso__title')
    readonly_fields = ('created_at', 'updated_at')

    def short_content(self, obj):
        return (obj.content[:75] + '...') if len(obj.content) > 75 else obj.content
    short_content.short_description = 'Contenido'
