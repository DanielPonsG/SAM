#!/usr/bin/env python
"""
Script para encontrar el ID del curso 1° BásicoA
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Curso

def encontrar_curso():
    # Buscar 1° BásicoA
    curso_basico = Curso.objects.filter(nivel='1B', paralelo='A').first()
    if curso_basico:
        print(f"1° BásicoA encontrado: ID {curso_basico.id}")
        return curso_basico.id
    else:
        print("1° BásicoA no encontrado")
        
    # Mostrar todos los cursos con sus IDs
    print("\nTodos los cursos:")
    for curso in Curso.objects.all():
        print(f"  ID {curso.id}: {curso.nombre_completo}")

if __name__ == "__main__":
    encontrar_curso()
