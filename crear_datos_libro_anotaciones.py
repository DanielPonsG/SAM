#!/usr/bin/env python
"""
Script para generar datos de prueba para el sistema de libro de anotaciones
"""
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Estudiante, Profesor, Curso, Asignatura, Anotacion, Perfil
from django.utils import timezone
from datetime import datetime, timedelta
import random

def crear_datos_prueba():
    print("🚀 Creando datos de prueba para el libro de anotaciones...")
    
    # 1. Crear algunos profesores
    print("📚 Creando profesores...")
    profesores_data = [
        {
            'codigo_profesor': 'PROF001',
            'primer_nombre': 'María',
            'apellido_paterno': 'González',
            'apellido_materno': 'López',
            'tipo_documento': 'CC',
            'numero_documento': '12345678',
            'fecha_nacimiento': '1985-03-15',
            'genero': 'F',
            'email': 'maria.gonzalez@sma.cl',
            'especialidad': 'Matemáticas',
            'username': 'prof_maria'
        },
        {
            'codigo_profesor': 'PROF002',
            'primer_nombre': 'Carlos',
            'apellido_paterno': 'Rodríguez',
            'apellido_materno': 'Martínez',
            'tipo_documento': 'CC',
            'numero_documento': '87654321',
            'fecha_nacimiento': '1980-07-22',
            'genero': 'M',
            'email': 'carlos.rodriguez@sma.cl',
            'especialidad': 'Lenguaje',
            'username': 'prof_carlos'
        },
        {
            'codigo_profesor': 'PROF003',
            'primer_nombre': 'Ana',
            'apellido_paterno': 'Silva',
            'apellido_materno': 'Morales',
            'tipo_documento': 'CC',
            'numero_documento': '11223344',
            'fecha_nacimiento': '1988-11-10',
            'genero': 'F',
            'email': 'ana.silva@sma.cl',
            'especialidad': 'Ciencias',
            'username': 'prof_ana'
        }
    ]
    
    profesores = []
    for prof_data in profesores_data:
        # Crear usuario
        user, created = User.objects.get_or_create(
            username=prof_data['username'],
            defaults={
                'email': prof_data['email'],
                'first_name': prof_data['primer_nombre'],
                'last_name': prof_data['apellido_paterno'],
                'is_staff': True
            }
        )
        if created:
            user.set_password('123456')
            user.save()
            
            # Crear perfil de profesor
            Perfil.objects.get_or_create(
                user=user,
                defaults={'tipo_usuario': 'profesor'}
            )
        
        # Crear profesor
        profesor, created = Profesor.objects.get_or_create(
            codigo_profesor=prof_data['codigo_profesor'],
            defaults={
                'primer_nombre': prof_data['primer_nombre'],
                'apellido_paterno': prof_data['apellido_paterno'],
                'apellido_materno': prof_data['apellido_materno'],
                'tipo_documento': prof_data['tipo_documento'],
                'numero_documento': prof_data['numero_documento'],
                'fecha_nacimiento': prof_data['fecha_nacimiento'],
                'genero': prof_data['genero'],
                'email': prof_data['email'],
                'especialidad': prof_data['especialidad'],
                'user': user
            }
        )
        profesores.append(profesor)
        if created:
            print(f"  ✅ Profesor creado: {profesor.get_nombre_completo()}")
    
    # 2. Crear asignaturas
    print("📖 Creando asignaturas...")
    asignaturas_data = [
        {'nombre': 'Matemáticas', 'codigo': 'MAT001'},
        {'nombre': 'Lenguaje y Comunicación', 'codigo': 'LEN001'},
        {'nombre': 'Ciencias Naturales', 'codigo': 'CIE001'},
        {'nombre': 'Historia y Geografía', 'codigo': 'HIS001'},
        {'nombre': 'Educación Física', 'codigo': 'EDF001'},
        {'nombre': 'Inglés', 'codigo': 'ING001'},
        {'nombre': 'Artes Visuales', 'codigo': 'ART001'},
    ]
    
    asignaturas = []
    for asig_data in asignaturas_data:
        asignatura, created = Asignatura.objects.get_or_create(
            codigo_asignatura=asig_data['codigo'],
            defaults={
                'nombre': asig_data['nombre'],
                'descripcion': f'Asignatura de {asig_data["nombre"]}',
                'profesor_responsable': random.choice(profesores)
            }
        )
        asignaturas.append(asignatura)
        if created:
            print(f"  ✅ Asignatura creada: {asignatura.nombre}")
    
    # 3. Crear cursos
    print("🏫 Creando cursos...")
    cursos_data = [
        {'nivel': '1M', 'paralelo': 'A'},
        {'nivel': '1M', 'paralelo': 'B'},
        {'nivel': '2M', 'paralelo': 'A'},
        {'nivel': '3M', 'paralelo': 'A'},
    ]
    
    cursos = []
    for curso_data in cursos_data:
        curso, created = Curso.objects.get_or_create(
            nivel=curso_data['nivel'],
            paralelo=curso_data['paralelo'],
            anio=timezone.now().year,
            defaults={
                'profesor_jefe': random.choice(profesores)
            }
        )
        
        # Asignar asignaturas al curso
        if created:
            curso.asignaturas.set(asignaturas[:5])  # Asignar las primeras 5 asignaturas
        
        cursos.append(curso)
        if created:
            print(f"  ✅ Curso creado: {curso}")
    
    # 4. Crear estudiantes
    print("👨‍🎓 Creando estudiantes...")
    estudiantes_data = [
        # Estudiantes para 1M A
        {'nombre': 'Juan', 'apellido': 'Pérez', 'codigo': 'EST001', 'curso': cursos[0]},
        {'nombre': 'María', 'apellido': 'García', 'codigo': 'EST002', 'curso': cursos[0]},
        {'nombre': 'Pedro', 'apellido': 'López', 'codigo': 'EST003', 'curso': cursos[0]},
        {'nombre': 'Ana', 'apellido': 'Martínez', 'codigo': 'EST004', 'curso': cursos[0]},
        {'nombre': 'Luis', 'apellido': 'Fernández', 'codigo': 'EST005', 'curso': cursos[0]},
        
        # Estudiantes para 1M B
        {'nombre': 'Carmen', 'apellido': 'Ruiz', 'codigo': 'EST006', 'curso': cursos[1]},
        {'nombre': 'Diego', 'apellido': 'Morales', 'codigo': 'EST007', 'curso': cursos[1]},
        {'nombre': 'Sofía', 'apellido': 'Vega', 'codigo': 'EST008', 'curso': cursos[1]},
        {'nombre': 'Gabriel', 'apellido': 'Torres', 'codigo': 'EST009', 'curso': cursos[1]},
        
        # Estudiantes para 2M A
        {'nombre': 'Valentina', 'apellido': 'Herrera', 'codigo': 'EST010', 'curso': cursos[2]},
        {'nombre': 'Matías', 'apellido': 'Castillo', 'codigo': 'EST011', 'curso': cursos[2]},
        {'nombre': 'Javiera', 'apellido': 'Flores', 'codigo': 'EST012', 'curso': cursos[2]},
        
        # Estudiantes para 3M A
        {'nombre': 'Benjamín', 'apellido': 'Soto', 'codigo': 'EST013', 'curso': cursos[3]},
        {'nombre': 'Isidora', 'apellido': 'Muñoz', 'codigo': 'EST014', 'curso': cursos[3]},
        {'nombre': 'Cristóbal', 'apellido': 'Bravo', 'codigo': 'EST015', 'curso': cursos[3]},
    ]
    
    estudiantes = []
    for est_data in estudiantes_data:
        # Crear usuario para el estudiante
        username = f"est_{est_data['codigo'].lower()}"
        user, user_created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f"{username}@estudiante.sma.cl",
                'first_name': est_data['nombre'],
                'last_name': est_data['apellido']
            }
        )
        if user_created:
            user.set_password('123456')
            user.save()
            
            # Crear perfil de alumno
            Perfil.objects.get_or_create(
                user=user,
                defaults={'tipo_usuario': 'alumno'}
            )
        
        # Crear estudiante
        estudiante, created = Estudiante.objects.get_or_create(
            codigo_estudiante=est_data['codigo'],
            defaults={
                'primer_nombre': est_data['nombre'],
                'apellido_paterno': est_data['apellido'],
                'apellido_materno': 'Apellido2',
                'tipo_documento': 'TI',
                'numero_documento': f"9876543{len(estudiantes):02d}",
                'fecha_nacimiento': '2008-01-01',
                'genero': 'M' if est_data['nombre'] in ['Juan', 'Pedro', 'Luis', 'Diego', 'Gabriel', 'Matías', 'Benjamín', 'Cristóbal'] else 'F',
                'email': f"{username}@estudiante.sma.cl",
                'user': user
            }
        )
        
        # Agregar estudiante al curso
        est_data['curso'].estudiantes.add(estudiante)
        
        estudiantes.append(estudiante)
        if created:
            print(f"  ✅ Estudiante creado: {estudiante.get_nombre_completo()} - {est_data['curso']}")
    
    # 5. Crear anotaciones de prueba
    print("📝 Creando anotaciones de prueba...")
    
    # Tipos de anotaciones de ejemplo
    anotaciones_ejemplos = [
        # Anotaciones positivas
        {
            'tipo': 'positiva',
            'categoria': 'comportamiento',
            'titulo': 'Excelente comportamiento en clase',
            'descripcion': 'El estudiante demostró un comportamiento ejemplar durante toda la clase, ayudando a sus compañeros y manteniendo el orden.',
            'puntos': 5
        },
        {
            'tipo': 'positiva',
            'categoria': 'participacion',
            'titulo': 'Participación destacada',
            'descripcion': 'Participó activamente en la discusión de clase con aportes muy valiosos y demostró gran interés en la materia.',
            'puntos': 4
        },
        {
            'tipo': 'positiva',
            'categoria': 'responsabilidad',
            'titulo': 'Entrega puntual de trabajos',
            'descripcion': 'Entregó todos los trabajos en tiempo y forma, demostrando gran responsabilidad académica.',
            'puntos': 3
        },
        {
            'tipo': 'positiva',
            'categoria': 'colaboracion',
            'titulo': 'Liderazgo en trabajo grupal',
            'descripcion': 'Demostró excelentes habilidades de liderazgo y colaboración durante el trabajo en equipo.',
            'puntos': 5
        },
        
        # Anotaciones negativas
        {
            'tipo': 'negativa',
            'categoria': 'disciplina',
            'titulo': 'Interrupción constante de la clase',
            'descripcion': 'El estudiante interrumpió repetidamente la clase hablando con sus compañeros sin permiso.',
            'puntos': -3,
            'es_grave': False
        },
        {
            'tipo': 'negativa',
            'categoria': 'puntualidad',
            'titulo': 'Llegada tardía reiterada',
            'descripcion': 'Ha llegado tarde a clases en múltiples ocasiones durante la semana.',
            'puntos': -2,
            'es_grave': False
        },
        {
            'tipo': 'negativa',
            'categoria': 'disciplina',
            'titulo': 'Falta de respeto al profesor',
            'descripcion': 'Mostró una actitud irrespetuosa hacia el profesor y no siguió las instrucciones dadas.',
            'puntos': -5,
            'es_grave': True,
            'requiere_atencion_apoderado': True
        },
        {
            'tipo': 'negativa',
            'categoria': 'responsabilidad',
            'titulo': 'No entrega de tareas',
            'descripcion': 'No ha entregado las tareas asignadas en los últimos días.',
            'puntos': -3,
            'es_grave': False
        },
        
        # Anotaciones neutras
        {
            'tipo': 'neutra',
            'categoria': 'otro',
            'titulo': 'Observación general',
            'descripcion': 'Observación sobre el progreso del estudiante en la asignatura.',
            'puntos': 0
        }
    ]
    
    # Crear anotaciones para varios estudiantes
    for i, estudiante in enumerate(estudiantes[:10]):  # Solo para los primeros 10 estudiantes
        curso = estudiante.get_curso_actual()
        if not curso:
            continue
            
        # Cada estudiante tendrá entre 2 y 5 anotaciones
        num_anotaciones = random.randint(2, 5)
        
        for j in range(num_anotaciones):
            # Seleccionar una anotación de ejemplo aleatoria
            anotacion_ejemplo = random.choice(anotaciones_ejemplos)
            
            # Crear la anotación
            anotacion = Anotacion.objects.create(
                estudiante=estudiante,
                curso=curso,
                asignatura=random.choice(list(curso.asignaturas.all())),
                profesor_autor=random.choice(profesores),
                tipo=anotacion_ejemplo['tipo'],
                categoria=anotacion_ejemplo['categoria'],
                titulo=anotacion_ejemplo['titulo'],
                descripcion=anotacion_ejemplo['descripcion'],
                puntos=anotacion_ejemplo['puntos'],
                es_grave=anotacion_ejemplo.get('es_grave', False),
                requiere_atencion_apoderado=anotacion_ejemplo.get('requiere_atencion_apoderado', False),
                fecha_creacion=timezone.now() - timedelta(days=random.randint(1, 30))
            )
            
            print(f"  ✅ Anotación creada: {estudiante.get_nombre_completo()} - {anotacion.get_tipo_display()}: {anotacion.titulo}")
    
    print("\n🎉 ¡Datos de prueba creados exitosamente!")
    print("\n📊 Resumen:")
    print(f"  • Profesores: {Profesor.objects.count()}")
    print(f"  • Estudiantes: {Estudiante.objects.count()}")
    print(f"  • Cursos: {Curso.objects.count()}")
    print(f"  • Asignaturas: {Asignatura.objects.count()}")
    print(f"  • Anotaciones: {Anotacion.objects.count()}")
    
    print("\n🔑 Usuarios creados:")
    print("  • Administrador: danie / [tu contraseña]")
    print("  • Profesores: prof_maria, prof_carlos, prof_ana / 123456")
    print("  • Estudiantes: est_est001, est_est002, etc. / 123456")
    
    print("\n🌐 Accede al sistema en: http://127.0.0.1:8000/")
    print("📚 Libro de anotaciones en: http://127.0.0.1:8000/anotaciones/")

if __name__ == '__main__':
    crear_datos_prueba()
