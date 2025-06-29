#!/usr/bin/env python
"""
Script para verificar las asignaturas y cursos en el sistema
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Curso, Asignatura

def verificar_datos():
    print("=== VERIFICACIÓN DE DATOS ===\n")
    
    # Verificar cursos
    cursos = Curso.objects.all()[:5]
    print(f"Total cursos en sistema: {Curso.objects.count()}")
    print(f"Primeros 5 cursos:")
    for curso in cursos:
        print(f"  - {curso.nombre_completo}: {curso.asignaturas.count()} asignaturas")
    
    print()
    
    # Verificar asignaturas
    asignaturas = Asignatura.objects.all()
    print(f"Total asignaturas en sistema: {asignaturas.count()}")
    print("Asignaturas:")
    for asig in asignaturas:
        print(f"  - {asig.nombre} (Código: {asig.codigo_asignatura})")
    
    print()
    
    # Verificar primer curso específicamente
    primer_curso = Curso.objects.first()
    if primer_curso:
        print(f"Asignaturas del curso {primer_curso.nombre_completo}:")
        if primer_curso.asignaturas.exists():
            for asig in primer_curso.asignaturas.all():
                print(f"  - {asig.nombre}")
        else:
            print("  ¡No tiene asignaturas asignadas!")
            print("  Esto explica por qué no aparecen en gestionar_horarios.html")

if __name__ == "__main__":
    verificar_datos()
