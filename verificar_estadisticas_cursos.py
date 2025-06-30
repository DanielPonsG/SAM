#!/usr/bin/env python
"""
Script para verificar las mejoras en el listado de cursos con estadísticas
"""

import os
import sys
import django

# Configurar el entorno Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Curso, Asignatura, Estudiante, Usuario
from django.utils import timezone

def mostrar_estadisticas_actuales():
    """Mostrar las estadísticas actuales del sistema"""
    print("=== ESTADÍSTICAS ACTUALES DEL SISTEMA ===\n")
    
    anio_actual = timezone.now().year
    print(f"📅 Año académico actual: {anio_actual}")
    
    # Estadísticas de cursos
    cursos_queryset = Curso.objects.filter(anio=anio_actual)
    total_cursos = cursos_queryset.count()
    print(f"🎓 Total de cursos: {total_cursos}")
    
    # Estadísticas de estudiantes
    total_estudiantes = Estudiante.objects.count()
    
    # Estudiantes asignados
    estudiantes_asignados_ids = set()
    for curso in cursos_queryset:
        estudiantes_curso = list(curso.estudiantes.values_list('id', flat=True))
        estudiantes_asignados_ids.update(estudiantes_curso)
    
    total_estudiantes_asignados = len(estudiantes_asignados_ids)
    total_estudiantes_pendientes = total_estudiantes - total_estudiantes_asignados
    
    print(f"👥 Total de estudiantes en el sistema: {total_estudiantes}")
    print(f"✅ Estudiantes asignados a cursos: {total_estudiantes_asignados}")
    print(f"⏳ Estudiantes sin asignar: {total_estudiantes_pendientes}")
    
    # Estadísticas de asignaturas
    total_asignaturas = Asignatura.objects.count()
    print(f"📚 Total de asignaturas disponibles: {total_asignaturas}")
    
    print(f"\n📊 DETALLES POR CURSO:")
    if total_cursos > 0:
        for curso in cursos_queryset.order_by('nivel', 'paralelo'):
            num_estudiantes = curso.estudiantes.count()
            num_asignaturas = curso.asignaturas.count()
            profesor_jefe = curso.profesor_jefe.get_nombre_completo() if curso.profesor_jefe else "Sin asignar"
            
            print(f"   • {curso.get_nivel_display()}{curso.paralelo}: "
                  f"{num_estudiantes} estudiantes, {num_asignaturas} asignaturas, "
                  f"Profesor jefe: {profesor_jefe}")
    else:
        print("   No hay cursos registrados para este año")
    
    print(f"\n✨ Las estadísticas se mostrarán en el listado de cursos con:")
    print(f"   - Tarjetas visuales con iconos")
    print(f"   - Colores diferenciados por tipo de estadística")
    print(f"   - Layout responsive para dispositivos móviles")
    print(f"   - Animaciones hover para mejor interacción")

if __name__ == "__main__":
    mostrar_estadisticas_actuales()
