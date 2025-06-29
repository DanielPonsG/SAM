#!/usr/bin/env python
"""
Script para crear datos de prueba completos para el sistema de gestión de notas
Incluye: usuarios, profesores, estudiantes, cursos, asignaturas, grupos, inscripciones y calificaciones
"""

import os
import django
import sys
from datetime import date, datetime, timedelta
import random

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import (
    Estudiante, Profesor, Curso, Asignatura, Grupo, 
    Inscripcion, Calificacion, Perfil, PeriodoAcademico
)

def crear_periodo_academico():
    """Crear periodo académico actual"""
    periodo, created = PeriodoAcademico.objects.get_or_create(
        nombre="Primer Semestre 2025",
        defaults={
            'fecha_inicio': date(2025, 3, 1),
            'fecha_fin': date(2025, 7, 31),
            'activo': True
        }
    )
    if created:
        print(f"✓ Periodo académico creado: {periodo.nombre}")
    else:
        print(f"✓ Periodo académico existente: {periodo.nombre}")
    return periodo

def crear_grupos_y_inscripciones():
    """Crear grupos e inscripciones de estudiantes"""
    print("\n--- CREANDO GRUPOS E INSCRIPCIONES ---")
    
    periodo = PeriodoAcademico.objects.first()
    if not periodo:
        periodo = crear_periodo_academico()
    
    # Obtener cursos y asignaturas del año actual
    cursos_actuales = Curso.objects.filter(anio=2025)
    asignaturas = Asignatura.objects.all()
    profesores = Profesor.objects.all()
    estudiantes = Estudiante.objects.all()
    
    grupos_creados = 0
    inscripciones_creadas = 0
    
    # Crear grupos para cada curso y asignatura
    for curso in cursos_actuales:
        # Asignar asignaturas básicas a cada curso
        asignaturas_curso = asignaturas[:6]  # Primeras 6 asignaturas para cada curso
        
        for asignatura in asignaturas_curso:
            # Asignar profesor aleatoriamente
            profesor = random.choice(profesores) if profesores else None
            
            # Crear o obtener grupo
            grupo, created = Grupo.objects.get_or_create(
                asignatura=asignatura,
                profesor=profesor,
                periodo_academico=periodo,
                defaults={
                    'capacidad_maxima': 35
                }
            )
            
            if created:
                grupos_creados += 1
                print(f"  ✓ Grupo creado: {grupo}")
                
                # Inscribir estudiantes del curso en el grupo
                estudiantes_curso = curso.estudiantes.all()
                for estudiante in estudiantes_curso:
                    inscripcion, inscripcion_created = Inscripcion.objects.get_or_create(
                        estudiante=estudiante,
                        grupo=grupo,
                        defaults={
                            'fecha_inscripcion': date.today()
                        }
                    )
                    
                    if inscripcion_created:
                        inscripciones_creadas += 1
    
    print(f"✓ Total grupos creados: {grupos_creados}")
    print(f"✓ Total inscripciones creadas: {inscripciones_creadas}")

def crear_calificaciones_demo():
    """Crear calificaciones de demostración"""
    print("\n--- CREANDO CALIFICACIONES DE DEMOSTRACIÓN ---")
    
    inscripciones = Inscripcion.objects.all()
    if not inscripciones:
        print("❌ No hay inscripciones para crear calificaciones")
        return
    
    tipos_evaluacion = [
        "Prueba Unidad 1", "Prueba Unidad 2", "Prueba Unidad 3",
        "Tarea 1", "Tarea 2", "Tarea 3",
        "Control de Lectura", "Examen Parcial", "Examen Final",
        "Proyecto", "Presentación Oral", "Laboratorio"
    ]
    
    detalles = [
        "Evaluación escrita", "Evaluación práctica", "Trabajo en grupo",
        "Trabajo individual", "Presentación", "Investigación"
    ]
    
    descripciones = [
        "Evaluación correspondiente a los contenidos revisados en clase durante la unidad.",
        "Actividad práctica que evalúa la aplicación de conceptos teóricos.",
        "Trabajo colaborativo que fomenta el aprendizaje entre pares.",
        "Evaluación individual que mide el dominio personal de la materia.",
        "Presentación oral que desarrolla habilidades comunicativas.",
        "Proyecto de investigación que profundiza en temas específicos."
    ]
    
    calificaciones_creadas = 0
    
    # Crear 3-5 calificaciones por inscripción
    for inscripcion in inscripciones:
        num_calificaciones = random.randint(3, 5)
        
        for i in range(num_calificaciones):
            # Generar datos aleatorios realistas
            puntaje = round(random.uniform(4.0, 7.0), 1)  # Notas chilenas
            porcentaje = random.choice([10, 15, 20, 25, 30])
            
            calificacion = Calificacion.objects.create(
                inscripcion=inscripcion,
                nombre_evaluacion=random.choice(tipos_evaluacion),
                puntaje=puntaje,
                porcentaje=porcentaje,
                detalle=random.choice(detalles),
                descripcion=random.choice(descripciones),
                fecha_evaluacion=date.today() - timedelta(days=random.randint(1, 60))
            )
            
            calificaciones_creadas += 1
    
    print(f"✓ Total calificaciones creadas: {calificaciones_creadas}")

def asignar_estudiantes_a_cursos():
    """Asignar estudiantes existentes a cursos"""
    print("\n--- ASIGNANDO ESTUDIANTES A CURSOS ---")
    
    estudiantes = Estudiante.objects.all()
    cursos_actuales = Curso.objects.filter(anio=2025)
    
    asignaciones = 0
    
    for estudiante in estudiantes:
        # Asignar cada estudiante a un curso aleatorio
        if cursos_actuales:
            curso = random.choice(cursos_actuales)
            curso.estudiantes.add(estudiante)
            asignaciones += 1
            print(f"  ✓ {estudiante.get_nombre_completo()} → {curso.nombre}")
    
    print(f"✓ Total asignaciones: {asignaciones}")

def configurar_profesores_jefe():
    """Configurar profesores jefe para los cursos"""
    print("\n--- CONFIGURANDO PROFESORES JEFE ---")
    
    cursos = Curso.objects.filter(anio=2025)
    profesores = Profesor.objects.all()
    
    if not profesores:
        print("❌ No hay profesores disponibles")
        return
    
    configurados = 0
    
    for curso in cursos:
        if not curso.profesor_jefe:
            profesor = random.choice(profesores)
            curso.profesor_jefe = profesor
            curso.save()
            configurados += 1
            print(f"  ✓ {curso.nombre} → Prof. Jefe: {profesor.get_nombre_completo()}")
    
    print(f"✓ Total profesores jefe configurados: {configurados}")

def asignar_asignaturas_profesores():
    """Asignar asignaturas a profesores"""
    print("\n--- ASIGNANDO ASIGNATURAS A PROFESORES ---")
    
    profesores = Profesor.objects.all()
    asignaturas = Asignatura.objects.all()
    
    asignaciones = 0
    
    for profesor in profesores:
        # Asignar 2-4 asignaturas por profesor
        num_asignaturas = random.randint(2, 4)
        asignaturas_profesor = random.sample(list(asignaturas), min(num_asignaturas, len(asignaturas)))
        
        for asignatura in asignaturas_profesor:
            profesor.asignaturas.add(asignatura)
            asignaciones += 1
        
        print(f"  ✓ {profesor.get_nombre_completo()}: {len(asignaturas_profesor)} asignaturas")
    
    print(f"✓ Total asignaciones: {asignaciones}")

def verificar_datos_sistema():
    """Verificar que todos los datos estén correctamente creados"""
    print("\n--- VERIFICACIÓN FINAL ---")
    
    print(f"✓ Usuarios: {User.objects.count()}")
    print(f"✓ Perfiles: {Perfil.objects.count()}")
    print(f"✓ Profesores: {Profesor.objects.count()}")
    print(f"✓ Estudiantes: {Estudiante.objects.count()}")
    print(f"✓ Cursos: {Curso.objects.count()}")
    print(f"✓ Asignaturas: {Asignatura.objects.count()}")
    print(f"✓ Grupos: {Grupo.objects.count()}")
    print(f"✓ Inscripciones: {Inscripcion.objects.count()}")
    print(f"✓ Calificaciones: {Calificacion.objects.count()}")
    print(f"✓ Periodos Académicos: {PeriodoAcademico.objects.count()}")
    
    # Verificar que hay datos para probar cada tipo de usuario
    directores = User.objects.filter(perfil__tipo_usuario='director').count()
    profesores = User.objects.filter(perfil__tipo_usuario='profesor').count()
    alumnos = User.objects.filter(perfil__tipo_usuario='alumno').count()
    
    print(f"\n📊 USUARIOS POR TIPO:")
    print(f"   - Directores: {directores}")
    print(f"   - Profesores: {profesores}")
    print(f"   - Alumnos: {alumnos}")
    
    # Estadísticas adicionales
    from django.db.models import Avg
    promedio_notas = Calificacion.objects.aggregate(Avg('puntaje'))['puntaje__avg']
    if promedio_notas:
        print(f"\n📈 ESTADÍSTICAS:")
        print(f"   - Promedio general de notas: {promedio_notas:.2f}")

def main():
    """Función principal"""
    print("🏗️  CONFIGURANDO SISTEMA DE GESTIÓN DE NOTAS")
    print("=" * 60)
    
    # Crear periodo académico
    crear_periodo_academico()
    
    # Asignar estudiantes a cursos
    asignar_estudiantes_a_cursos()
    
    # Configurar profesores jefe
    configurar_profesores_jefe()
    
    # Asignar asignaturas a profesores
    asignar_asignaturas_profesores()
    
    # Crear grupos e inscripciones
    crear_grupos_y_inscripciones()
    
    # Crear calificaciones de demostración
    crear_calificaciones_demo()
    
    # Verificar datos
    verificar_datos_sistema()
    
    print("\n" + "=" * 60)
    print("🎉 ¡SISTEMA CONFIGURADO EXITOSAMENTE!")
    print("📋 El sistema de gestión de notas está listo para usar")
    print("🚀 Puedes probar todas las funcionalidades ahora")

if __name__ == '__main__':
    main()
