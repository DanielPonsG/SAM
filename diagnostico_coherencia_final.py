#!/usr/bin/env python
"""
Script para diagnosticar y verificar la coherencia entre datos de cursos y asignaturas
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Curso, Asignatura, Profesor, Estudiante
from django.utils import timezone

def main():
    print("=== DIAGNÓSTICO DE COHERENCIA CURSOS-ASIGNATURAS ===")
    print()
    
    anio_actual = timezone.now().year
    
    # === ESTADÍSTICAS DE CURSOS ===
    print("📚 ESTADÍSTICAS DE CURSOS:")
    print("-" * 40)
    
    cursos = Curso.objects.filter(anio=anio_actual)
    total_cursos = cursos.count()
    total_estudiantes_asignados = sum(curso.estudiantes.count() for curso in cursos)
    profesores_jefe_asignados = len([curso for curso in cursos if curso.profesor_jefe])
    total_asignaturas_asignadas_cursos = sum(curso.asignaturas.count() for curso in cursos)
    
    print(f"Total cursos ({anio_actual}): {total_cursos}")
    print(f"Total estudiantes asignados: {total_estudiantes_asignados}")
    print(f"Profesores jefe asignados: {profesores_jefe_asignados}")
    print(f"Total asignaturas asignadas a cursos: {total_asignaturas_asignadas_cursos}")
    print()
    
    # === ESTADÍSTICAS DE ASIGNATURAS ===
    print("📖 ESTADÍSTICAS DE ASIGNATURAS:")
    print("-" * 40)
    
    asignaturas = Asignatura.objects.all()
    total_asignaturas = asignaturas.count()
    asignaturas_con_profesor = asignaturas.filter(profesor_responsable__isnull=False).count()
    asignaturas_con_cursos = asignaturas.filter(cursos__anio=anio_actual).distinct().count()
    asignaturas_sin_cursos = total_asignaturas - asignaturas_con_cursos
    
    print(f"Total asignaturas: {total_asignaturas}")
    print(f"Asignaturas con profesor: {asignaturas_con_profesor}")
    print(f"Asignaturas asignadas a cursos ({anio_actual}): {asignaturas_con_cursos}")
    print(f"Asignaturas sin cursos: {asignaturas_sin_cursos}")
    print()
    
    # === VERIFICACIÓN DE COHERENCIA ===
    print("🔍 VERIFICACIÓN DE COHERENCIA:")
    print("-" * 40)
    
    print(f"¿Coinciden las estadísticas?")
    print(f"  - Total asignaturas en cursos (vista cursos): {total_asignaturas_asignadas_cursos}")
    print(f"  - Total asignaciones curso-asignatura (vista asignaturas): ", end="")
    
    # Contar asignaciones reales (cada asignatura puede estar en múltiples cursos)
    total_asignaciones = 0
    for asignatura in asignaturas:
        total_asignaciones += asignatura.cursos.filter(anio=anio_actual).count()
    
    print(f"{total_asignaciones}")
    
    if total_asignaturas_asignadas_cursos == total_asignaciones:
        print("  ✅ Las estadísticas coinciden perfectamente")
    else:
        print("  ❌ Las estadísticas NO coinciden")
        print(f"     Diferencia: {abs(total_asignaturas_asignadas_cursos - total_asignaciones)}")
    
    print()
    
    # === DETALLE POR CURSO ===
    print("📋 DETALLE POR CURSO:")
    print("-" * 40)
    
    for curso in cursos.order_by('nivel', 'paralelo'):
        num_estudiantes = curso.estudiantes.count()
        num_asignaturas = curso.asignaturas.count()
        profesor_jefe = curso.profesor_jefe.get_nombre_completo() if curso.profesor_jefe else "Sin asignar"
        
        print(f"📚 {curso.get_nivel_display()}{curso.paralelo}")
        print(f"   👨‍🏫 Profesor Jefe: {profesor_jefe}")
        print(f"   👥 Estudiantes: {num_estudiantes}")
        print(f"   📖 Asignaturas: {num_asignaturas}")
        
        if num_asignaturas > 0:
            print("   📖 Lista de asignaturas:")
            for asignatura in curso.asignaturas.all():
                profesor = asignatura.profesor_responsable.get_nombre_completo() if asignatura.profesor_responsable else "Sin profesor"
                print(f"      - {asignatura.nombre} ({asignatura.codigo_asignatura}) - {profesor}")
        print()
    
    # === DETALLE POR ASIGNATURA ===
    print("📖 DETALLE POR ASIGNATURA:")
    print("-" * 40)
    
    for asignatura in asignaturas.order_by('nombre'):
        cursos_asignados = asignatura.cursos.filter(anio=anio_actual)
        num_cursos = cursos_asignados.count()
        profesor = asignatura.profesor_responsable.get_nombre_completo() if asignatura.profesor_responsable else "Sin profesor"
        
        print(f"📖 {asignatura.nombre} ({asignatura.codigo_asignatura})")
        print(f"   👨‍🏫 Profesor responsable: {profesor}")
        print(f"   📚 Cursos asignados ({anio_actual}): {num_cursos}")
        
        if num_cursos > 0:
            print("   📚 Lista de cursos:")
            for curso in cursos_asignados.order_by('nivel', 'paralelo'):
                print(f"      - {curso.get_nivel_display()}{curso.paralelo}")
        print()
    
    # === PROBLEMAS DETECTADOS ===
    print("⚠️  PROBLEMAS DETECTADOS:")
    print("-" * 40)
    
    problemas = []
    
    # Cursos sin profesor jefe
    cursos_sin_jefe = cursos.filter(profesor_jefe__isnull=True)
    if cursos_sin_jefe.exists():
        problemas.append(f"Cursos sin profesor jefe: {cursos_sin_jefe.count()}")
        for curso in cursos_sin_jefe:
            print(f"  - {curso.get_nivel_display()}{curso.paralelo}: Sin profesor jefe")
    
    # Cursos sin asignaturas
    cursos_sin_asignaturas = [curso for curso in cursos if curso.asignaturas.count() == 0]
    if cursos_sin_asignaturas:
        problemas.append(f"Cursos sin asignaturas: {len(cursos_sin_asignaturas)}")
        for curso in cursos_sin_asignaturas:
            print(f"  - {curso.get_nivel_display()}{curso.paralelo}: Sin asignaturas")
    
    # Asignaturas sin profesor
    asignaturas_sin_profesor = asignaturas.filter(profesor_responsable__isnull=True)
    if asignaturas_sin_profesor.exists():
        problemas.append(f"Asignaturas sin profesor: {asignaturas_sin_profesor.count()}")
        for asignatura in asignaturas_sin_profesor:
            print(f"  - {asignatura.nombre}: Sin profesor responsable")
    
    # Asignaturas sin cursos
    asignaturas_sin_cursos_obj = asignaturas.filter(cursos__isnull=True)
    if asignaturas_sin_cursos_obj.exists():
        problemas.append(f"Asignaturas sin cursos: {asignaturas_sin_cursos_obj.count()}")
        for asignatura in asignaturas_sin_cursos_obj:
            print(f"  - {asignatura.nombre}: No asignada a ningún curso")
    
    if not problemas:
        print("✅ No se detectaron problemas importantes")
    
    print()
    print("=== FIN DEL DIAGNÓSTICO ===")

if __name__ == '__main__':
    main()
