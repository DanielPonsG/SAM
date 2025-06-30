#!/usr/bin/env python
"""
Script para verificar que el filtrado de estudiantes por curso funciona correctamente
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Curso, Estudiante
from django.http import JsonResponse
import json

def probar_ajax_estudiantes_curso():
    """Simular la vista AJAX para verificar que funciona"""
    print("=== PROBANDO FILTRADO DE ESTUDIANTES POR CURSO ===")
    
    cursos = Curso.objects.filter(estudiantes__isnull=False).distinct()
    
    for curso in cursos[:3]:  # Solo los primeros 3 cursos
        print(f"\n--- CURSO: {curso} ---")
        print(f"ID del curso: {curso.id}")
        
        # Simular la vista AJAX
        estudiantes = curso.estudiantes.all().order_by('primer_nombre', 'apellido_paterno')
        
        data = {
            'estudiantes': [
                {
                    'id': est.id,
                    'nombre': est.get_nombre_completo(),
                    'rut': est.numero_documento
                }
                for est in estudiantes
            ]
        }
        
        print(f"Estudiantes encontrados: {len(data['estudiantes'])}")
        for est in data['estudiantes']:
            print(f"  - ID: {est['id']}, Nombre: {est['nombre']}, RUT: {est['rut']}")
        
        # Verificar que los estudiantes realmente pertenecen al curso
        print("\nVerificación de pertenencia al curso:")
        for est in estudiantes:
            cursos_estudiante = est.cursos.all()
            if curso in cursos_estudiante:
                print(f"  ✓ {est.get_nombre_completo()} SÍ pertenece al curso")
            else:
                print(f"  ✗ {est.get_nombre_completo()} NO pertenece al curso")

def verificar_formulario_anotaciones():
    """Verificar que el formulario de anotaciones filtra cursos correctamente"""
    print("\n=== VERIFICANDO FORMULARIO DE ANOTACIONES ===")
    
    from smapp.forms import AnotacionForm
    from django.utils import timezone
    
    # Probar para administrador (sin profesor)
    print("\n--- Para Administrador ---")
    form_admin = AnotacionForm()
    cursos_admin = form_admin.fields['curso'].queryset
    print(f"Cursos disponibles para admin: {cursos_admin.count()}")
    
    for curso in cursos_admin:
        num_estudiantes = curso.estudiantes.count()
        print(f"  - {curso}: {num_estudiantes} estudiantes")
    
    # Probar para profesor (si existe alguno)
    from smapp.models import Profesor
    profesores = Profesor.objects.all()
    
    if profesores.exists():
        profesor = profesores.first()
        print(f"\n--- Para Profesor: {profesor.get_nombre_completo()} ---")
        
        form_profesor = AnotacionForm(profesor=profesor)
        cursos_profesor = form_profesor.fields['curso'].queryset
        print(f"Cursos disponibles para profesor: {cursos_profesor.count()}")
        
        for curso in cursos_profesor:
            num_estudiantes = curso.estudiantes.count()
            print(f"  - {curso}: {num_estudiantes} estudiantes")

def verificar_consistencia_datos():
    """Verificar la consistencia de los datos"""
    print("\n=== VERIFICANDO CONSISTENCIA DE DATOS ===")
    
    # Verificar que no hay estudiantes en múltiples cursos del mismo año
    from django.utils import timezone
    anio_actual = timezone.now().year
    
    estudiantes_problema = []
    
    for estudiante in Estudiante.objects.all():
        cursos_estudiante = estudiante.cursos.filter(anio=anio_actual)
        if cursos_estudiante.count() > 1:
            estudiantes_problema.append({
                'estudiante': estudiante,
                'cursos': list(cursos_estudiante)
            })
    
    if estudiantes_problema:
        print(f"⚠️  Encontrados {len(estudiantes_problema)} estudiantes en múltiples cursos del año {anio_actual}:")
        for problema in estudiantes_problema:
            est = problema['estudiante']
            cursos = ', '.join([str(c) for c in problema['cursos']])
            print(f"  - {est.get_nombre_completo()}: {cursos}")
    else:
        print(f"✓ No hay estudiantes en múltiples cursos del año {anio_actual}")
    
    # Verificar cursos sin estudiantes
    cursos_sin_estudiantes = Curso.objects.filter(
        anio=anio_actual,
        estudiantes__isnull=True
    )
    
    if cursos_sin_estudiantes.exists():
        print(f"\n📝 Cursos sin estudiantes del año {anio_actual}:")
        for curso in cursos_sin_estudiantes:
            print(f"  - {curso}")
    else:
        print(f"\n✓ Todos los cursos del año {anio_actual} tienen estudiantes")

def main():
    print("VERIFICACIÓN DEL SISTEMA DE FILTRADO DE ESTUDIANTES")
    print("=" * 60)
    
    probar_ajax_estudiantes_curso()
    verificar_formulario_anotaciones()
    verificar_consistencia_datos()
    
    print("\n" + "=" * 60)
    print("RECOMENDACIONES:")
    print("1. Verificar que la URL AJAX esté funcionando en el navegador")
    print("2. Revisar la consola del navegador para errores JavaScript")
    print("3. Confirmar que el curso seleccionado tiene estudiantes")
    print("4. Probar con diferentes navegadores")
    print("\nURL para probar manualmente:")
    print("http://127.0.0.1:8000/ajax/obtener-estudiantes-curso/?curso_id=1")

if __name__ == '__main__':
    main()
