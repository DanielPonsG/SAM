#!/usr/bin/env python
"""
Script para diagnosticar inconsistencias entre listar_cursos y listar_asignaturas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import *
from django.utils import timezone

def diagnosticar_datos():
    """Diagnosticar la relación entre cursos y asignaturas"""
    print("=== DIAGNÓSTICO DE DATOS CURSO-ASIGNATURA ===")
    
    anio_actual = timezone.now().year
    
    # 1. Obtener todos los cursos del año actual
    cursos = Curso.objects.filter(anio=anio_actual)
    print(f"\n1. CURSOS DEL AÑO {anio_actual}: {cursos.count()}")
    
    for curso in cursos:
        asignaturas_curso = curso.asignaturas.all()
        print(f"   Curso {curso}: {asignaturas_curso.count()} asignaturas")
        for asig in asignaturas_curso:
            profesor = asig.profesor_responsable
            profesor_nombre = f"{profesor.primer_nombre} {profesor.apellido_paterno}" if profesor else "Sin profesor"
            print(f"     - {asig.nombre} (Profesor: {profesor_nombre})")
    
    # 2. Obtener todas las asignaturas
    asignaturas = Asignatura.objects.all()
    print(f"\n2. ASIGNATURAS TOTALES: {asignaturas.count()}")
    
    for asignatura in asignaturas:
        cursos_asignatura = asignatura.cursos.filter(anio=anio_actual)
        profesor = asignatura.profesor_responsable
        profesor_nombre = f"{profesor.primer_nombre} {profesor.apellido_paterno}" if profesor else "Sin profesor"
        print(f"   {asignatura.nombre} (Profesor: {profesor_nombre}): {cursos_asignatura.count()} cursos")
        for curso in cursos_asignatura:
            print(f"     - {curso}")
    
    # 3. Verificar inconsistencias
    print(f"\n3. VERIFICACIÓN DE CONSISTENCIA")
    
    inconsistencias = []
    
    for curso in cursos:
        for asignatura in curso.asignaturas.all():
            # Verificar si la asignatura también tiene al curso en su lista
            if not asignatura.cursos.filter(id=curso.id).exists():
                inconsistencias.append(f"Curso {curso} tiene asignatura {asignatura.nombre}, pero la asignatura no tiene el curso")
    
    for asignatura in asignaturas:
        for curso in asignatura.cursos.all():
            # Verificar si el curso también tiene a la asignatura en su lista
            if not curso.asignaturas.filter(id=asignatura.id).exists():
                inconsistencias.append(f"Asignatura {asignatura.nombre} tiene curso {curso}, pero el curso no tiene la asignatura")
    
    if inconsistencias:
        print("   ❌ INCONSISTENCIAS ENCONTRADAS:")
        for inc in inconsistencias:
            print(f"     - {inc}")
    else:
        print("   ✅ No se encontraron inconsistencias en la relación Many-to-Many")
    
    # 4. Resumen de estadísticas
    print(f"\n4. RESUMEN DE ESTADÍSTICAS")
    
    # Estadísticas desde perspectiva de cursos
    total_asignaturas_desde_cursos = sum(curso.asignaturas.count() for curso in cursos)
    print(f"   Total asignaciones desde cursos: {total_asignaturas_desde_cursos}")
    
    # Estadísticas desde perspectiva de asignaturas
    total_cursos_desde_asignaturas = sum(asignatura.cursos.filter(anio=anio_actual).count() for asignatura in asignaturas)
    print(f"   Total asignaciones desde asignaturas: {total_cursos_desde_asignaturas}")
    
    # Asignaturas con/sin profesor
    asignaturas_con_profesor = asignaturas.filter(profesor_responsable__isnull=False).count()
    asignaturas_sin_profesor = asignaturas.filter(profesor_responsable__isnull=True).count()
    print(f"   Asignaturas con profesor: {asignaturas_con_profesor}")
    print(f"   Asignaturas sin profesor: {asignaturas_sin_profesor}")
    
    # Asignaturas asignadas a cursos vs no asignadas
    asignaturas_asignadas = asignaturas.filter(cursos__anio=anio_actual).distinct().count()
    asignaturas_no_asignadas = asignaturas.exclude(cursos__anio=anio_actual).count()
    print(f"   Asignaturas asignadas a cursos: {asignaturas_asignadas}")
    print(f"   Asignaturas NO asignadas a cursos: {asignaturas_no_asignadas}")
    
    return {
        'cursos': cursos,
        'asignaturas': asignaturas,
        'inconsistencias': inconsistencias,
        'stats': {
            'total_asignaturas_desde_cursos': total_asignaturas_desde_cursos,
            'total_cursos_desde_asignaturas': total_cursos_desde_asignaturas,
            'asignaturas_con_profesor': asignaturas_con_profesor,
            'asignaturas_sin_profesor': asignaturas_sin_profesor,
            'asignaturas_asignadas': asignaturas_asignadas,
            'asignaturas_no_asignadas': asignaturas_no_asignadas
        }
    }

if __name__ == '__main__':
    diagnosticar_datos()
