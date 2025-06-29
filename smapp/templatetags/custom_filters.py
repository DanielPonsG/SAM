from django import template
from smapp.models import Asignatura

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter para obtener un elemento de un diccionario por clave
    Uso: {{ mi_diccionario|get_item:mi_clave }}
    """
    return dictionary.get(key, [])

@register.simple_tag
def get_asignaturas_no_asignadas_curso(curso):
    """
    Obtiene las asignaturas que no están asignadas a un curso específico
    """
    if not curso:
        return Asignatura.objects.none()
    
    # Obtener todas las asignaturas
    todas_asignaturas = Asignatura.objects.all()
    
    # Obtener asignaturas ya asignadas al curso
    asignaturas_del_curso = curso.asignaturas.all()
    
    # Retornar las que no están asignadas
    asignaturas_no_asignadas = todas_asignaturas.exclude(
        id__in=asignaturas_del_curso.values_list('id', flat=True)
    )
    
    return asignaturas_no_asignadas
