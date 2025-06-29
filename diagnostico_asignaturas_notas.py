#!/usr/bin/env python3
"""
Script para diagnosticar el problema de asignaturas no visibles en ingresar_notas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Asignatura, Curso, Grupo, Inscripcion, Estudiante, Profesor, PeriodoAcademico
from django.utils import timezone

def diagnosticar_asignaturas():
    """Diagnosticar el estado de asignaturas, cursos y grupos"""
    print("=== DIAGNÓSTICO DE ASIGNATURAS Y CURSOS ===")
    
    # Ver asignaturas
    asignaturas = Asignatura.objects.all()
    print(f"\nASIGNATURAS EN EL SISTEMA ({asignaturas.count()}):")
    for asig in asignaturas:
        print(f"  - {asig.nombre} ({asig.codigo_asignatura})")
        profesores = asig.get_profesores_display()
        if profesores:
            print(f"    Profesores: {[p.get_nombre_completo() for p in profesores]}")
        else:
            print(f"    Sin profesores asignados")
    
    # Ver cursos
    cursos = Curso.objects.all()
    print(f"\nCURSOS EN EL SISTEMA ({cursos.count()}):")
    for curso in cursos:
        print(f"  - {curso} ({curso.estudiantes.count()} estudiantes)")
        asignaturas_curso = curso.asignaturas.all()
        if asignaturas_curso.exists():
            print(f"    Asignaturas asignadas: {[a.nombre for a in asignaturas_curso]}")
        else:
            print(f"    Sin asignaturas asignadas")
    
    # Ver grupos
    grupos = Grupo.objects.all()
    print(f"\nGRUPOS EN EL SISTEMA ({grupos.count()}):")
    for grupo in grupos:
        inscripciones = grupo.inscripcion_set.count()
        print(f"  - {grupo} ({inscripciones} estudiantes inscritos)")
    
    # Ver periodos académicos
    periodos = PeriodoAcademico.objects.all()
    print(f"\nPERIODOS ACADÉMICOS ({periodos.count()}):")
    for periodo in periodos:
        print(f"  - {periodo} (Activo: {periodo.activo})")
    
    # Ver inscripciones
    inscripciones = Inscripcion.objects.all()
    print(f"\nINSCRIPCIONES ({inscripciones.count()}):")
    for inscripcion in inscripciones[:10]:  # Solo mostrar las primeras 10
        print(f"  - {inscripcion}")
    
    return asignaturas, cursos, grupos

def analizar_problema():
    """Analizar por qué las asignaturas no aparecen en ingresar_notas"""
    print("\n=== ANÁLISIS DEL PROBLEMA ===")
    
    # La lógica actual busca asignaturas a través de:
    # Inscripcion.objects.filter(estudiante__in=curso_seleccionado.estudiantes.all())
    # .select_related('grupo__asignatura')
    
    # Esto significa que solo se muestran asignaturas que YA TIENEN estudiantes inscritos
    # a través de un GRUPO, pero las asignaturas recién creadas no tienen grupos
    
    print("PROBLEMA IDENTIFICADO:")
    print("1. Las asignaturas se crean en 'Listar Asignaturas'")
    print("2. Pero para aparecer en 'Ingresar Notas', necesitan tener:")
    print("   - Un Grupo asociado (asignatura + profesor + periodo)")
    print("   - Estudiantes inscritos en ese grupo")
    print("3. Actualmente no hay mecanismo para crear grupos automáticamente")
    
    print("\nSOLUCIONES POSIBLES:")
    print("A. Crear grupos automáticamente cuando se asigna una asignatura a un curso")
    print("B. Modificar la lógica para mostrar asignaturas del curso directamente")
    print("C. Crear una vista para gestionar grupos/inscripciones")

def verificar_datos_ejemplo():
    """Verificar si hay datos de ejemplo que funcionen"""
    print("\n=== VERIFICANDO DATOS DE EJEMPLO ===")
    
    # Buscar un curso con estudiantes
    curso_con_estudiantes = Curso.objects.filter(estudiantes__isnull=False).first()
    if curso_con_estudiantes:
        print(f"Curso encontrado: {curso_con_estudiantes}")
        print(f"Estudiantes: {curso_con_estudiantes.estudiantes.count()}")
        
        # Ver si tiene asignaturas
        asignaturas_curso = curso_con_estudiantes.asignaturas.all()
        print(f"Asignaturas del curso: {asignaturas_curso.count()}")
        
        # Ver si hay grupos para este curso
        estudiantes_curso = curso_con_estudiantes.estudiantes.all()
        inscripciones = Inscripcion.objects.filter(estudiante__in=estudiantes_curso)
        print(f"Inscripciones encontradas: {inscripciones.count()}")
        
        if inscripciones.exists():
            asignaturas_con_grupos = Asignatura.objects.filter(
                grupo__inscripcion__in=inscripciones
            ).distinct()
            print(f"Asignaturas con grupos: {asignaturas_con_grupos.count()}")
            for asig in asignaturas_con_grupos:
                print(f"  - {asig.nombre}")
        else:
            print("No hay inscripciones para este curso")
    else:
        print("No se encontró ningún curso con estudiantes")

def proponer_solucion():
    """Proponer una solución para el problema"""
    print("\n=== SOLUCIÓN PROPUESTA ===")
    
    print("OPCIÓN A: Modificar vista ingresar_notas para usar asignaturas del curso")
    print("  - Cambiar la lógica para usar curso.asignaturas.all()")
    print("  - Crear grupos automáticamente cuando sea necesario")
    print("  - Ventaja: Más directo y simple")
    
    print("\nOPCIÓN B: Crear sistema de gestión de grupos")
    print("  - Agregar vista para asignar asignaturas a cursos")
    print("  - Crear grupos automáticamente")
    print("  - Inscribir estudiantes automáticamente")
    print("  - Ventaja: Más completo y estructurado")
    
    print("\nRECOMENDACIÓN: Implementar OPCIÓN A primero (más rápido)")

def main():
    print("DIAGNÓSTICO: Por qué las asignaturas no aparecen en Ingresar Notas")
    print("=" * 60)
    
    asignaturas, cursos, grupos = diagnosticar_asignaturas()
    analizar_problema()
    verificar_datos_ejemplo()
    proponer_solucion()
    
    print("\n" + "=" * 60)
    print("RESUMEN:")
    print(f"- {asignaturas.count()} asignaturas creadas")
    print(f"- {cursos.count()} cursos disponibles") 
    print(f"- {grupos.count()} grupos configurados")
    print("- PROBLEMA: Falta conexión entre asignaturas y cursos para notas")

if __name__ == "__main__":
    main()
