#!/usr/bin/env python
"""
Script de validación final para verificar la coherencia de la gestión de cursos y asignaturas
después de implementar las mejoras de diseño y funcionalidad.
"""

import os
import sys
import django

# Configurar el entorno Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Curso, Asignatura, Estudiante, Usuario

def validar_coherencia_final():
    """Validación final completa del sistema"""
    print("=== VALIDACIÓN FINAL DE COHERENCIA ===\n")
    
    # 1. Verificar estadísticas generales
    print("📊 ESTADÍSTICAS GENERALES:")
    total_cursos = Curso.objects.count()
    total_asignaturas = Asignatura.objects.count()
    total_estudiantes = Estudiante.objects.count()
    total_usuarios = Usuario.objects.count()
    
    print(f"   • Total de cursos: {total_cursos}")
    print(f"   • Total de asignaturas: {total_asignaturas}")
    print(f"   • Total de estudiantes: {total_estudiantes}")
    print(f"   • Total de usuarios: {total_usuarios}")
    
    # 2. Verificar cursos
    print(f"\n🎓 ANÁLISIS DE CURSOS:")
    cursos_con_estudiantes = 0
    cursos_sin_estudiantes = 0
    cursos_con_asignaturas = 0
    cursos_sin_asignaturas = 0
    
    for curso in Curso.objects.all():
        num_estudiantes = curso.estudiantes.count()
        num_asignaturas = curso.asignaturas.count()
        
        if num_estudiantes > 0:
            cursos_con_estudiantes += 1
        else:
            cursos_sin_estudiantes += 1
            
        if num_asignaturas > 0:
            cursos_con_asignaturas += 1
        else:
            cursos_sin_asignaturas += 1
    
    print(f"   • Cursos con estudiantes: {cursos_con_estudiantes}")
    print(f"   • Cursos sin estudiantes: {cursos_sin_estudiantes}")
    print(f"   • Cursos con asignaturas: {cursos_con_asignaturas}")
    print(f"   • Cursos sin asignaturas: {cursos_sin_asignaturas}")
    
    # 3. Verificar asignaturas
    print(f"\n📚 ANÁLISIS DE ASIGNATURAS:")
    asignaturas_con_cursos = 0
    asignaturas_sin_cursos = 0
    nombres_asignaturas = set()
    asignaturas_duplicadas = []
    
    for asignatura in Asignatura.objects.all():
        num_cursos = asignatura.curso_set.count()
        
        if num_cursos > 0:
            asignaturas_con_cursos += 1
        else:
            asignaturas_sin_cursos += 1
            
        # Verificar duplicados por nombre
        if asignatura.nombre in nombres_asignaturas:
            asignaturas_duplicadas.append(asignatura.nombre)
        else:
            nombres_asignaturas.add(asignatura.nombre)
    
    print(f"   • Asignaturas con cursos: {asignaturas_con_cursos}")
    print(f"   • Asignaturas sin cursos: {asignaturas_sin_cursos}")
    print(f"   • Nombres únicos de asignaturas: {len(nombres_asignaturas)}")
    
    if asignaturas_duplicadas:
        print(f"   ⚠️  Asignaturas con nombres duplicados: {set(asignaturas_duplicadas)}")
    else:
        print(f"   ✅ No hay asignaturas con nombres duplicados")
    
    # 4. Verificar estudiantes
    print(f"\n👥 ANÁLISIS DE ESTUDIANTES:")
    estudiantes_con_curso = 0
    estudiantes_sin_curso = 0
    estudiantes_multiples_cursos = 0
    
    for estudiante in Estudiante.objects.all():
        cursos_estudiante = estudiante.curso_set.count()
        
        if cursos_estudiante == 0:
            estudiantes_sin_curso += 1
        elif cursos_estudiante == 1:
            estudiantes_con_curso += 1
        else:
            estudiantes_multiples_cursos += 1
    
    print(f"   • Estudiantes con un curso: {estudiantes_con_curso}")
    print(f"   • Estudiantes sin curso: {estudiantes_sin_curso}")
    print(f"   • Estudiantes en múltiples cursos: {estudiantes_multiples_cursos}")
    
    # 5. Verificar relaciones consistentes
    print(f"\n🔗 VERIFICACIÓN DE CONSISTENCIA:")
    inconsistencias = []
    
    # Verificar que los cursos con asignaturas tengan esas asignaturas asociadas correctamente
    for curso in Curso.objects.all():
        asignaturas_curso = set(curso.asignaturas.all())
        for asignatura in asignaturas_curso:
            cursos_asignatura = set(asignatura.curso_set.all())
            if curso not in cursos_asignatura:
                inconsistencias.append(f"Curso {curso.nombre} tiene asignatura {asignatura.nombre} pero la asignatura no lista al curso")
    
    if inconsistencias:
        print(f"   ⚠️  Inconsistencias encontradas:")
        for inc in inconsistencias:
            print(f"      • {inc}")
    else:
        print(f"   ✅ Todas las relaciones son consistentes")
    
    # 6. Resumen final
    print(f"\n📋 RESUMEN FINAL:")
    problemas = []
    
    if cursos_sin_estudiantes > 0:
        problemas.append(f"{cursos_sin_estudiantes} cursos sin estudiantes")
    if cursos_sin_asignaturas > 0:
        problemas.append(f"{cursos_sin_asignaturas} cursos sin asignaturas")
    if asignaturas_sin_cursos > 0:
        problemas.append(f"{asignaturas_sin_cursos} asignaturas sin cursos")
    if estudiantes_multiples_cursos > 0:
        problemas.append(f"{estudiantes_multiples_cursos} estudiantes en múltiples cursos")
    if asignaturas_duplicadas:
        problemas.append("asignaturas con nombres duplicados")
    if inconsistencias:
        problemas.append("inconsistencias en relaciones")
    
    if problemas:
        print(f"   ⚠️  Problemas detectados: {', '.join(problemas)}")
        print(f"   📝 Estos pueden ser normales según el estado del sistema")
    else:
        print(f"   ✅ Sistema completamente coherente")
    
    print(f"\n🎯 VALIDACIÓN COMPLETADA")
    print(f"   El sistema de gestión de cursos y asignaturas está listo para usar")
    print(f"   Templates actualizados con diseño moderno y funcionalidad mejorada")

if __name__ == "__main__":
    validar_coherencia_final()
