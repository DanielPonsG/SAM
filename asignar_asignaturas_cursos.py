#!/usr/bin/env python
"""
Script para asignar asignaturas apropiadas a todos los cursos según su nivel
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Curso, Asignatura

def asignar_asignaturas_por_nivel():
    """Asigna asignaturas apropiadas a cada curso según su nivel"""
    
    # Definir asignaturas por niveles
    asignaturas_basica = [
        'Matemáticas', 'Lenguaje', 'Ciencias', 'Historia', 'Educación Física', 'Arte', 'Música'
    ]
    
    asignaturas_media = [
        'Matemáticas', 'Lenguaje', 'Biología', 'Química', 'Física', 'Historia', 
        'Geografía', 'Educación Física', 'Arte', 'Inglés', 'Filosofía'
    ]
    
    # Obtener todas las asignaturas disponibles
    todas_asignaturas = list(Asignatura.objects.all())
    
    # Procesar todos los cursos
    cursos = Curso.objects.all()
    
    for curso in cursos:
        print(f"\n📚 Procesando: {curso.nombre_completo}")
        
        # Determinar si es básica o media
        es_basica = curso.nivel.endswith('B')  # 1B, 2B, etc.
        es_media = curso.nivel.endswith('M')   # 1M, 2M, etc.
        
        # Seleccionar asignaturas apropiadas
        if es_basica:
            asignaturas_objetivo = asignaturas_basica
            print(f"   Nivel: Educación Básica")
        elif es_media:
            asignaturas_objetivo = asignaturas_media
            print(f"   Nivel: Educación Media")
        else:
            asignaturas_objetivo = asignaturas_basica  # Por defecto
            print(f"   Nivel: No determinado (usando básica)")
        
        # Buscar asignaturas que coincidan con los nombres objetivo
        asignaturas_encontradas = []
        for asignatura in todas_asignaturas:
            for objetivo in asignaturas_objetivo:
                if objetivo.lower() in asignatura.nombre.lower():
                    asignaturas_encontradas.append(asignatura)
                    break
        
        # Si no se encontraron suficientes, agregar más asignaturas
        if len(asignaturas_encontradas) < 5:
            for asignatura in todas_asignaturas:
                if asignatura not in asignaturas_encontradas:
                    asignaturas_encontradas.append(asignatura)
                    if len(asignaturas_encontradas) >= 6:  # Máximo 6 asignaturas
                        break
        
        # Limpiar asignaturas actuales del curso
        curso.asignaturas.clear()
        
        # Asignar nuevas asignaturas
        asignaturas_asignadas = 0
        for asignatura in asignaturas_encontradas[:6]:  # Máximo 6
            curso.asignaturas.add(asignatura)
            asignaturas_asignadas += 1
            print(f"   ✅ {asignatura.nombre}")
        
        print(f"   📊 Total asignadas: {asignaturas_asignadas}")

if __name__ == "__main__":
    print("🚀 Iniciando asignación de asignaturas por nivel...")
    asignar_asignaturas_por_nivel()
    print("\n✅ ¡Proceso completado!")
