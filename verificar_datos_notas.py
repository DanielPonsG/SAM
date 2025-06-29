#!/usr/bin/env python
"""
Script para verificar los datos en la base de datos y depurar la vista
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Estudiante, Asignatura, Calificacion, Curso, Inscripcion, Grupo, PeriodoAcademico

def verificar_datos():
    """Verificar que los datos están en la base de datos"""
    
    print("=== VERIFICACIÓN DE DATOS ===")
    
    # Verificar curso
    curso = Curso.objects.filter(nivel='1B', paralelo='A', anio=2025).first()
    if curso:
        print(f"✓ Curso encontrado: {curso}")
        print(f"  - Estudiantes: {curso.estudiantes.count()}")
        print(f"  - Asignaturas: {curso.asignaturas.count()}")
        
        # Listar estudiantes
        for estudiante in curso.estudiantes.all():
            print(f"    - {estudiante.get_nombre_completo()}")
            
        # Listar asignaturas
        for asignatura in curso.asignaturas.all():
            print(f"    - {asignatura.nombre}")
    else:
        print("✗ Curso no encontrado")
        return
    
    # Verificar asignatura específica
    asignatura = Asignatura.objects.filter(codigo_asignatura='MAT001').first()
    if asignatura:
        print(f"✓ Asignatura encontrada: {asignatura.nombre}")
    else:
        print("✗ Asignatura no encontrada")
        return
    
    # Verificar grupos e inscripciones
    grupo = Grupo.objects.filter(asignatura=asignatura).first()
    if grupo:
        print(f"✓ Grupo encontrado: {grupo}")
        print(f"  - Inscripciones: {grupo.inscripcion_set.count()}")
        
        for inscripcion in grupo.inscripcion_set.all():
            print(f"    - {inscripcion.estudiante.get_nombre_completo()}")
    else:
        print("✗ Grupo no encontrado")
        return
    
    # Verificar calificaciones
    calificaciones = Calificacion.objects.filter(inscripcion__grupo=grupo)
    print(f"✓ Calificaciones encontradas: {calificaciones.count()}")
    
    for cal in calificaciones:
        print(f"  - {cal.inscripcion.estudiante.get_nombre_completo()}: {cal.nombre_evaluacion} = {cal.puntaje}")
    
    # Probar la lógica de la vista manualmente
    print("\n=== SIMULANDO LÓGICA DE VISTA ===")
    
    # Obtener estudiantes del curso
    estudiantes_curso = curso.estudiantes.all()
    print(f"Estudiantes del curso: {estudiantes_curso.count()}")
    
    # Obtener inscripciones para esta asignatura
    inscripciones = Inscripcion.objects.filter(
        estudiante__in=estudiantes_curso,
        grupo__asignatura=asignatura
    )
    print(f"Inscripciones relevantes: {inscripciones.count()}")
    
    # Obtener notas
    notas = Calificacion.objects.filter(inscripcion__in=inscripciones)
    print(f"Notas encontradas: {notas.count()}")
    
    # Obtener evaluaciones únicas
    evaluaciones_nombres = set()
    for nota in notas:
        evaluaciones_nombres.add(nota.nombre_evaluacion)
    
    evaluaciones = [{'nombre': nombre} for nombre in sorted(evaluaciones_nombres)]
    print(f"Evaluaciones únicas: {[ev['nombre'] for ev in evaluaciones]}")
    
    # Simular estructura notas_por_estudiante
    from collections import defaultdict
    notas_por_estudiante = defaultdict(dict)
    
    for estudiante in estudiantes_curso:
        notas_est = [None] * len(evaluaciones)
        # Obtener todas las notas del estudiante para esta asignatura
        notas_estudiante = notas.filter(inscripcion__estudiante=estudiante)
        
        for idx, ev in enumerate(evaluaciones):
            # Obtener la nota más reciente para esta evaluación
            nota = notas_estudiante.filter(nombre_evaluacion=ev['nombre']).order_by('-fecha_evaluacion').first()
            notas_est[idx] = nota
        notas_por_estudiante[estudiante] = notas_est
        
        print(f"Estudiante {estudiante.get_nombre_completo()}:")
        for idx, nota in enumerate(notas_est):
            ev_nombre = evaluaciones[idx]['nombre'] if idx < len(evaluaciones) else 'N/A'
            nota_valor = nota.puntaje if nota else 'VACÍO'
            print(f"  - {ev_nombre}: {nota_valor}")

if __name__ == "__main__":
    verificar_datos()
