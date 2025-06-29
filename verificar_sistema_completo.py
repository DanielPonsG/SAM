#!/usr/bin/env python
"""
Script para verificar y asegurar que las asignaturas se vean reflejadas en todos los templates
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Curso, Asignatura, HorarioCurso, Profesor

def verificar_todo():
    print("=== VERIFICACIÓN COMPLETA DEL SISTEMA ===\n")
    
    # 1. Verificar asignaturas totales
    asignaturas = Asignatura.objects.all()
    print(f"📚 Total de asignaturas en el sistema: {asignaturas.count()}")
    
    # Mostrar las últimas 5 asignaturas creadas
    print("Últimas 5 asignaturas creadas:")
    for asig in asignaturas.order_by('-id')[:5]:
        print(f"  - {asig.nombre} (Código: {asig.codigo_asignatura}) - ID: {asig.id}")
    
    print()
    
    # 2. Verificar cursos y sus asignaturas
    print("🏫 CURSOS Y SUS ASIGNATURAS ASIGNADAS:")
    cursos = Curso.objects.all()[:5]  # Primeros 5 cursos
    
    for curso in cursos:
        print(f"\n{curso.nombre_completo} (ID: {curso.id}):")
        print(f"  - Asignaturas asignadas: {curso.asignaturas.count()}")
        if curso.asignaturas.exists():
            for asig in curso.asignaturas.all():
                print(f"    • {asig.nombre}")
        else:
            print("    ⚠️  No tiene asignaturas asignadas")
    
    print()
    
    # 3. Verificar horarios existentes
    print("⏰ HORARIOS EXISTENTES:")
    horarios = HorarioCurso.objects.filter(activo=True)
    print(f"Total horarios activos: {horarios.count()}")
    
    if horarios.exists():
        print("Horarios por curso:")
        for curso in Curso.objects.filter(horarios__activo=True).distinct():
            horarios_curso = HorarioCurso.objects.filter(curso=curso, activo=True)
            print(f"  {curso.nombre_completo}: {horarios_curso.count()} horarios")
    else:
        print("  ⚠️  No hay horarios configurados")
    
    print()
    
    # 4. Verificar URL de gestionar horarios para curso específico
    curso_ejemplo = Curso.objects.filter(nivel='1B', paralelo='A').first()
    if curso_ejemplo:
        print(f"🔗 URLs DE PRUEBA:")
        print(f"  - Gestionar horarios para {curso_ejemplo.nombre_completo}:")
        print(f"    http://127.0.0.1:8000/cursos/{curso_ejemplo.id}/gestionar-horarios/")
        print(f"  - Listar cursos:")
        print(f"    http://127.0.0.1:8000/cursos/")
        print(f"  - Seleccionar curso para horarios:")
        print(f"    http://127.0.0.1:8000/seleccionar-curso-horarios/")
    
    print()
    
    # 5. Verificar profesores disponibles
    profesores = Profesor.objects.all()
    print(f"👨‍🏫 Total profesores: {profesores.count()}")
    
    print("\n=== RECOMENDACIONES ===")
    
    # Buscar cursos sin asignaturas
    cursos_sin_asignaturas = Curso.objects.filter(asignaturas__isnull=True)
    if cursos_sin_asignaturas.exists():
        print("⚠️  CURSOS SIN ASIGNATURAS ASIGNADAS:")
        for curso in cursos_sin_asignaturas:
            print(f"  - {curso.nombre_completo} (ID: {curso.id})")
        print("  💡 Considera asignar asignaturas a estos cursos desde el admin de Django.")
    
    # Verificar asignaturas no asignadas a ningún curso
    asignaturas_no_asignadas = Asignatura.objects.filter(cursos__isnull=True)
    if asignaturas_no_asignadas.exists():
        print("\n📚 ASIGNATURAS NO ASIGNADAS A NINGÚN CURSO:")
        for asig in asignaturas_no_asignadas:
            print(f"  - {asig.nombre}")
        print("  💡 Estas asignaturas aparecerán como fallback en gestionar_horarios si un curso no tiene asignaturas.")

if __name__ == "__main__":
    verificar_todo()
