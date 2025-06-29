#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar datos completos de demostración para el sistema de notas
Incluye usuarios, cursos, estudiantes, profesores, asignaturas y calificaciones
"""

import os
import django
import sys
from datetime import date, datetime, timedelta
import random

# Configuración Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import *
from django.db import transaction

def limpiar_datos():
    """Limpiar datos existentes para empezar limpio"""
    print("🗑️  Limpiando datos existentes...")
    
    # Orden de eliminación para respetar relaciones FK
    modelos_orden = [
        Calificacion,
        Inscripcion,
        Grupo,
        HorarioCurso,
        Estudiante,
        Profesor,
        Perfil,
        Curso,
        Asignatura,
        PeriodoAcademico,
    ]
    
    for modelo in modelos_orden:
        count = modelo.objects.count()
        if count > 0:
            modelo.objects.all().delete()
            print(f"   • Eliminados {count} registros de {modelo.__name__}")
    
    # También limpiar usuarios que no sean superuser
    User.objects.filter(is_superuser=False).delete()
    print("   • Usuarios no-admin eliminados")

def crear_usuarios_base():
    """Crear usuarios base del sistema"""
    print("👥 Creando usuarios base...")
    
    usuarios = [
        {
            'username': 'admin_director',
            'password': 'admin123',
            'email': 'director@colegio.cl',
            'first_name': 'María',
            'last_name': 'González',
            'tipo': 'administrador'
        },
        {
            'username': 'prof_matematicas',
            'password': 'prof123',
            'email': 'mate@colegio.cl',
            'first_name': 'Carlos',
            'last_name': 'Rodriguez',
            'tipo': 'profesor'
        },
        {
            'username': 'prof_lenguaje',
            'password': 'prof123',
            'email': 'lenguaje@colegio.cl',
            'first_name': 'Ana',
            'last_name': 'Martínez',
            'tipo': 'profesor'
        },
        {
            'username': 'alumno_juan',
            'password': 'alumno123',
            'email': 'juan@estudiante.cl',
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'tipo': 'alumno'
        },
        {
            'username': 'alumno_maria',
            'password': 'alumno123',
            'email': 'maria@estudiante.cl',
            'first_name': 'María',
            'last_name': 'Silva',
            'tipo': 'alumno'
        },
    ]
    
    for user_data in usuarios:
        # Crear usuario
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
            }
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
        
        # Crear perfil
        perfil, created = Perfil.objects.get_or_create(
            user=user,
            defaults={'tipo_usuario': user_data['tipo']}
        )
        
        print(f"   • Usuario: {user_data['username']} ({user_data['tipo']})")
    
    return User.objects.filter(username__in=[u['username'] for u in usuarios])

def crear_asignaturas():
    """Crear asignaturas básicas"""
    print("📚 Creando asignaturas...")
    
    asignaturas = [
        'Matemática',
        'Lenguaje y Comunicación',
        'Historia y Geografía',
        'Ciencias Naturales',
        'Educación Física',
        'Inglés',
        'Artes Visuales',
        'Música',
    ]
    
    objetos_asignaturas = []
    for i, nombre in enumerate(asignaturas, 1):
        asignatura, created = Asignatura.objects.get_or_create(
            nombre=nombre,
            defaults={
                'codigo_asignatura': f'ASIG{i:02d}',
                'descripcion': f'Asignatura de {nombre}',
            }
        )
        objetos_asignaturas.append(asignatura)
        if created:
            print(f"   • {nombre}")
    
    return objetos_asignaturas

def crear_periodo_academico():
    """Crear período académico actual"""
    print("📅 Creando período académico...")
    
    periodo, created = PeriodoAcademico.objects.get_or_create(
        nombre="Año Lectivo 2025",
        defaults={
            'fecha_inicio': date(2025, 3, 1),
            'fecha_fin': date(2025, 12, 15),
            'activo': True
        }
    )
    
    if created:
        print(f"   • {periodo.nombre}")
    
    return periodo

def crear_profesores():
    """Crear profesores con sus asignaturas"""
    print("👨‍🏫 Creando profesores...")
    
    # Obtener usuarios profesor
    user_mate = User.objects.get(username='prof_matematicas')
    user_lenguaje = User.objects.get(username='prof_lenguaje')
    
    asignaturas = {
        'Matemática': Asignatura.objects.get(nombre='Matemática'),
        'Lenguaje y Comunicación': Asignatura.objects.get(nombre='Lenguaje y Comunicación'),
        'Historia y Geografía': Asignatura.objects.get(nombre='Historia y Geografía'),
        'Ciencias Naturales': Asignatura.objects.get(nombre='Ciencias Naturales'),
    }
    
    # Profesor de Matemáticas
    prof_mate, created = Profesor.objects.get_or_create(
        user=user_mate,
        defaults={
            'numero_documento': '12345678-9',
            'codigo_profesor': 'PROF001',
            'primer_nombre': user_mate.first_name,
            'apellido_paterno': user_mate.last_name,
            'apellido_materno': 'González',
            'fecha_nacimiento': date(1980, 5, 15),
            'genero': 'M',
            'telefono': '+56912345678',
            'email': user_mate.email,
            'direccion': 'Av. Providencia 123',
            'especialidad': 'Matemáticas',
        }
    )
    prof_mate.asignaturas.set([asignaturas['Matemática'], asignaturas['Ciencias Naturales']])
    
    # Profesor de Lenguaje
    prof_len, created = Profesor.objects.get_or_create(
        user=user_lenguaje,
        defaults={
            'numero_documento': '11111111-1',
            'codigo_profesor': 'PROF002',
            'primer_nombre': user_lenguaje.first_name,
            'apellido_paterno': user_lenguaje.last_name,
            'apellido_materno': 'López',
            'fecha_nacimiento': date(1985, 8, 22),
            'genero': 'F',
            'telefono': '+56987654321',
            'email': user_lenguaje.email,
            'direccion': 'Av. Las Condes 456',
            'especialidad': 'Lenguaje',
        }
    )
    prof_len.asignaturas.set([asignaturas['Lenguaje y Comunicación'], asignaturas['Historia y Geografía']])
    
    print(f"   • {prof_mate.primer_nombre} {prof_mate.apellido_paterno} - Matemática")
    print(f"   • {prof_len.primer_nombre} {prof_len.apellido_paterno} - Lenguaje")
    
    return [prof_mate, prof_len]

def crear_cursos():
    """Crear cursos con profesores jefe"""
    print("🏫 Creando cursos...")
    
    profesores = Profesor.objects.all()
    prof_mate = profesores.get(especialidad='Matemáticas')
    
    cursos_data = [
        {
            'nivel': '1B',  # 1° Básico
            'paralelo': 'A',
            'profesor_jefe': prof_mate,
        },
        {
            'nivel': '1B',  # 1° Básico
            'paralelo': 'B', 
            'profesor_jefe': prof_mate,
        },
    ]
    
    cursos = []
    for data in cursos_data:
        curso, created = Curso.objects.get_or_create(
            nivel=data['nivel'],
            paralelo=data['paralelo'],
            anio=2025,
            defaults={
                'profesor_jefe': data['profesor_jefe'],
            }
        )
        cursos.append(curso)
        if created:
            print(f"   • {curso.get_nivel_display()}{curso.paralelo} - Prof. Jefe: {curso.profesor_jefe}")
    
    return cursos

def crear_estudiantes():
    """Crear estudiantes y asignarlos a cursos"""
    print("🎓 Creando estudiantes...")
    
    # Usuarios estudiantes
    user_juan = User.objects.get(username='alumno_juan')
    user_maria = User.objects.get(username='alumno_maria')
    
    cursos = Curso.objects.all()
    curso_1a = cursos.get(paralelo='A')
    curso_1b = cursos.get(paralelo='B')
    
    estudiantes_data = [
        {
            'user': user_juan,
            'numero_documento': '20123456-7',
            'primer_nombre': 'Juan',
            'apellido_paterno': 'Pérez',
            'apellido_materno': 'Gonzalez',
            'codigo_estudiante': 'EST001',
            'fecha_nacimiento': date(2010, 3, 15),
            'genero': 'M',
            'curso': curso_1a,
        },
        {
            'user': user_maria,
            'numero_documento': '20234567-8',
            'primer_nombre': 'María',
            'apellido_paterno': 'Silva',
            'apellido_materno': 'Martínez',
            'codigo_estudiante': 'EST002',
            'fecha_nacimiento': date(2010, 7, 22),
            'genero': 'F',
            'curso': curso_1b,
        },
    ]
    
    # Crear más estudiantes sin usuarios (solo datos)
    for i in range(3, 11):
        estudiantes_data.append({
            'user': None,
            'numero_documento': f'20{100000 + i:06d}-{random.randint(0, 9)}',
            'primer_nombre': random.choice(['Pedro', 'Ana', 'Luis', 'Carmen', 'Diego', 'Sofia']),
            'apellido_paterno': random.choice(['González', 'Rodríguez', 'López', 'Martínez', 'García']),
            'apellido_materno': random.choice(['Silva', 'Pérez', 'Muñoz', 'Torres', 'Vargas']),
            'codigo_estudiante': f'EST{i:03d}',
            'fecha_nacimiento': date(2010, random.randint(1, 12), random.randint(1, 28)),
            'genero': random.choice(['M', 'F']),
            'curso': random.choice([curso_1a, curso_1b]),
        })
    
    estudiantes = []
    for data in estudiantes_data:
        estudiante, created = Estudiante.objects.get_or_create(
            codigo_estudiante=data['codigo_estudiante'],
            defaults={
                'user': data['user'],
                'numero_documento': data['numero_documento'],
                'primer_nombre': data['primer_nombre'],
                'apellido_paterno': data['apellido_paterno'],
                'apellido_materno': data['apellido_materno'],
                'fecha_nacimiento': data['fecha_nacimiento'],
                'genero': data['genero'],
                'telefono': '+56912345678',
                'email': f"{data['codigo_estudiante'].lower()}@estudiante.cl",
                'direccion': 'Dir. Estudiante 123',
            }
        )
        
        # Asignar al curso
        data['curso'].estudiantes.add(estudiante)
        estudiantes.append(estudiante)
        
        if created:
            print(f"   • {estudiante.primer_nombre} {estudiante.apellido_paterno} - {data['curso']}")
    
    return estudiantes

def crear_grupos_e_inscripciones():
    """Crear grupos de asignaturas e inscribir estudiantes"""
    print("📝 Creando grupos e inscripciones...")
    
    periodo = PeriodoAcademico.objects.get(nombre="Año Lectivo 2025")
    asignaturas = Asignatura.objects.all()[:4]  # Solo las principales
    profesores = Profesor.objects.all()
    cursos = Curso.objects.all()
    
    grupos_creados = []
    
    for curso in cursos:
        for asignatura in asignaturas:
            # Asignar profesor según especialidad
            if 'Matemática' in asignatura.nombre or 'Ciencias' in asignatura.nombre:
                profesor = profesores.get(especialidad='Matemáticas')
            else:
                profesor = profesores.get(especialidad='Lenguaje')
            
            # Crear grupo
            grupo, created = Grupo.objects.get_or_create(
                asignatura=asignatura,
                profesor=profesor,
                periodo_academico=periodo,
                defaults={
                    'capacidad_maxima': 30,
                }
            )
            grupos_creados.append(grupo)
            
            # Inscribir todos los estudiantes del curso
            for estudiante in curso.estudiantes.all():
                inscripcion, created = Inscripcion.objects.get_or_create(
                    estudiante=estudiante,
                    grupo=grupo,
                    defaults={
                        'fecha_inscripcion': date(2025, 3, 1),
                    }
                )
                
                if created:
                    print(f"   • {estudiante.primer_nombre} inscrito en {grupo.asignatura.nombre} - {curso}")
    
    return grupos_creados

def crear_calificaciones():
    """Crear calificaciones de ejemplo con sistema chileno"""
    print("📊 Creando calificaciones...")
    
    inscripciones = Inscripcion.objects.all()
    
    # Tipos de evaluaciones
    evaluaciones = [
        'Prueba Parcial 1',
        'Prueba Parcial 2',
        'Trabajo Grupal',
        'Presentación Oral',
        'Examen Final',
        'Quiz Semanal',
        'Tarea de Investigación',
    ]
    
    calificaciones_creadas = []
    
    for inscripcion in inscripciones:
        num_notas = random.randint(3, 6)  # Entre 3 y 6 notas por inscripción
        
        for i in range(num_notas):
            evaluacion = random.choice(evaluaciones)
            
            # Generar puntaje realista (sistema chileno 1.0 - 7.0)
            # Distribución: más notas en rango 4-6
            rand_val = random.random()
            if rand_val < 0.1:  # 10% notas muy bajas
                puntaje = round(random.uniform(1.0, 3.9), 1)
            elif rand_val < 0.7:  # 60% notas en rango aprobatorio
                puntaje = round(random.uniform(4.0, 5.9), 1)
            else:  # 30% notas altas
                puntaje = round(random.uniform(6.0, 7.0), 1)
            
            calificacion, created = Calificacion.objects.get_or_create(
                inscripcion=inscripcion,
                nombre_evaluacion=evaluacion,
                puntaje=puntaje,
                defaults={
                    'porcentaje': random.randint(70, 100),
                    'detalle': f"Evaluación de {inscripcion.grupo.asignatura.nombre}",
                    'descripcion': f"Evaluación {evaluacion} para estudiante {inscripcion.estudiante.primer_nombre}",
                    'fecha_evaluacion': date(2025, random.randint(3, 6), random.randint(1, 28)),
                }
            )
            
            if created:
                calificaciones_creadas.append(calificacion)
                estado = "✅" if puntaje >= 4.0 else "❌"
                print(f"   • {inscripcion.estudiante.primer_nombre} - {evaluacion}: {puntaje} {estado}")
    
    return calificaciones_creadas

def generar_estadisticas():
    """Mostrar estadísticas de los datos generados"""
    print("\n📈 Estadísticas finales:")
    print(f"   • Usuarios: {User.objects.count()}")
    print(f"   • Profesores: {Profesor.objects.count()}")
    print(f"   • Estudiantes: {Estudiante.objects.count()}")
    print(f"   • Cursos: {Curso.objects.count()}")
    print(f"   • Asignaturas: {Asignatura.objects.count()}")
    print(f"   • Grupos: {Grupo.objects.count()}")
    print(f"   • Inscripciones: {Inscripcion.objects.count()}")
    print(f"   • Calificaciones: {Calificacion.objects.count()}")
    
    # Estadísticas de notas
    calificaciones = Calificacion.objects.all()
    if calificaciones.exists():
        aprobadas = calificaciones.filter(puntaje__gte=4.0).count()
        reprobadas = calificaciones.filter(puntaje__lt=4.0).count()
        promedio_general = sum(c.puntaje for c in calificaciones) / calificaciones.count()
        
        print(f"\n📊 Estadísticas de calificaciones:")
        print(f"   • Notas aprobadas (≥4.0): {aprobadas}")
        print(f"   • Notas reprobadas (<4.0): {reprobadas}")
        print(f"   • Promedio general: {promedio_general:.1f}")

@transaction.atomic
def main():
    """Función principal"""
    print("=" * 60)
    print("🎓 CONFIGURACIÓN COMPLETA DE DATOS DE DEMOSTRACIÓN")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    try:
        # Ejecutar en orden
        limpiar_datos()
        crear_usuarios_base()
        crear_asignaturas()
        crear_periodo_academico()
        crear_profesores()
        crear_cursos()
        crear_estudiantes()
        crear_grupos_e_inscripciones()
        crear_calificaciones()
        generar_estadisticas()
        
        print("\n" + "=" * 60)
        print("🎉 ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
        print("=" * 60)
        print("\n📋 Usuarios de prueba:")
        print("   👨‍💼 Director: admin_director / admin123")
        print("   👨‍🏫 Profesor Matemática: prof_matematicas / prof123")
        print("   👩‍🏫 Profesora Lenguaje: prof_lenguaje / prof123")
        print("   🎓 Estudiante Juan: alumno_juan / alumno123")
        print("   🎓 Estudiante María: alumno_maria / alumno123")
        
        print("\n✨ El sistema está listo para probar todas las funcionalidades avanzadas!")
        
    except Exception as e:
        print(f"\n❌ Error durante la configuración: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
