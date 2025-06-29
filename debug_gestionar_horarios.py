#!/usr/bin/env python
"""
Script para debuggear la vista gestionar_horarios y ver qué datos se están pasando
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Curso, Asignatura, HorarioCurso, Profesor

def debug_gestionar_horarios():
    print("=== DEBUG GESTIONAR HORARIOS ===\n")
    
    # Simular lo que hace la vista
    curso_id = 1
    curso = Curso.objects.get(id=curso_id)
    
    print(f"Curso: {curso.nombre_completo}")
    print(f"ID del curso: {curso.id}")
    
    # Obtener horarios del curso
    horarios = HorarioCurso.objects.filter(curso=curso, activo=True).select_related('asignatura', 'profesor')
    print(f"Horarios encontrados: {horarios.count()}")
    for h in horarios:
        print(f"  - {h}")
    
    print()
    
    # Obtener asignaturas disponibles para el curso
    asignaturas_curso = curso.asignaturas.all()
    print(f"Asignaturas del curso: {asignaturas_curso.count()}")
    for a in asignaturas_curso:
        print(f"  - {a.nombre} (ID: {a.id})")
    
    if asignaturas_curso.exists():
        asignaturas = asignaturas_curso
        print("Usando asignaturas del curso")
    else:
        asignaturas = Asignatura.objects.all()
        print("Usando todas las asignaturas (fallback)")
    
    print(f"\nAsignaturas finales a mostrar: {asignaturas.count()}")
    for a in asignaturas:
        print(f"  - {a.nombre} (ID: {a.id})")
    
    # Obtener profesores disponibles
    profesores = Profesor.objects.all()
    print(f"\nProfesores disponibles: {profesores.count()}")
    for p in profesores[:3]:  # Solo mostrar los primeros 3
        print(f"  - {p.get_nombre_completo()}")
    
    print()
    print("=== CONTEXTO FINAL PARA TEMPLATE ===")
    context = {
        'curso': curso,
        'horarios': horarios,
        'asignaturas': asignaturas,
        'profesores': profesores,
    }
    
    for key, value in context.items():
        if hasattr(value, 'count'):
            print(f"{key}: {value.count()} elementos")
        else:
            print(f"{key}: {value}")

if __name__ == "__main__":
    debug_gestionar_horarios()
