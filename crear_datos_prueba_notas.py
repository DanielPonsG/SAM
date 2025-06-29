#!/usr/bin/env python
"""
Script para crear datos de prueba y verificar la funcionalidad completa de agregar notas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Estudiante, Asignatura, Calificacion, Curso, Inscripcion, Grupo, PeriodoAcademico, Profesor, Perfil
from django.utils import timezone
import requests

def create_test_data():
    """Crear datos de prueba para demostrar la funcionalidad de agregar notas"""
    
    print("=== CREANDO DATOS DE PRUEBA ===")
    
    try:
        # 1. Crear usuario director
        admin_user, created = User.objects.get_or_create(
            username='director_test',
            defaults={
                'email': 'director@test.com',
                'first_name': 'Director',
                'last_name': 'Test',
                'is_staff': True
            }
        )
        if created:
            admin_user.set_password('director123')
            admin_user.save()
            print("✓ Usuario director creado")
        else:
            print("✓ Usuario director encontrado")
        
        # Crear perfil para el director
        perfil, created = Perfil.objects.get_or_create(
            user=admin_user,
            defaults={'tipo_usuario': 'director'}
        )
        if created:
            print("✓ Perfil de director creado")
        
        # 2. Crear profesor
        profesor_user, created = User.objects.get_or_create(
            username='prof_matematicas',
            defaults={
                'email': 'profesor@test.com',
                'first_name': 'Profesor',
                'last_name': 'Matemáticas'
            }
        )
        if created:
            profesor_user.set_password('prof123')
            profesor_user.save()
            print("✓ Usuario profesor creado")
        
        # Perfil de profesor
        perfil_prof, created = Perfil.objects.get_or_create(
            user=profesor_user,
            defaults={'tipo_usuario': 'profesor'}
        )
        
        # Crear objeto Profesor
        profesor, created = Profesor.objects.get_or_create(
            user=profesor_user,
            defaults={
                'numero_documento': '11111111-1',
                'primer_nombre': 'Profesor',
                'apellido_paterno': 'Matemáticas',
                'email': 'profesor@test.com',
                'codigo_profesor': 'PROF001',
                'especialidad': 'Matemáticas',
                'fecha_nacimiento': timezone.now().date().replace(year=1980),
                'genero': 'M'
            }
        )
        
        # 3. Crear curso
        curso, created = Curso.objects.get_or_create(
            nivel='1B',
            paralelo='A',
            anio=2025
        )
        if created:
            print("✓ Curso 1°A creado")
        
        # 4. Crear asignatura
        asignatura, created = Asignatura.objects.get_or_create(
            codigo_asignatura='MAT001',
            defaults={
                'nombre': 'Matemáticas Básicas',
                'descripcion': 'Matemáticas para primer año básico',
                'profesor_responsable': profesor
            }
        )
        if created:
            asignatura.profesores_responsables.add(profesor)
            print("✓ Asignatura Matemáticas Básicas creada")
        
        # Asignar asignatura al curso
        curso.asignaturas.add(asignatura)
        
        # 5. Crear estudiantes
        estudiantes_data = [
            ('12345678-9', 'Ana', 'García', 'López'),
            ('98765432-1', 'Carlos', 'Rodríguez', 'Pérez'),
            ('11122333-1', 'María', 'González', 'Silva'),
            ('22233444-2', 'Pedro', 'Martínez', 'Torres')
        ]
        
        estudiantes_creados = []
        for numero_doc, nombre, ap_pat, ap_mat in estudiantes_data:
            estudiante, created = Estudiante.objects.get_or_create(
                numero_documento=numero_doc,
                defaults={
                    'primer_nombre': nombre,
                    'apellido_paterno': ap_pat,
                    'apellido_materno': ap_mat,
                    'email': f'{nombre.lower()}@test.com',
                    'codigo_estudiante': f'EST{numero_doc[:3]}',
                    'fecha_nacimiento': timezone.now().date().replace(year=2010),
                    'genero': 'M' if nombre in ['Carlos', 'Pedro'] else 'F'
                }
            )
            if created:
                print(f"✓ Estudiante {nombre} {ap_pat} creado")
            
            # Asignar estudiante al curso
            curso.estudiantes.add(estudiante)
            estudiantes_creados.append(estudiante)
        
        # 6. Crear período académico
        periodo, created = PeriodoAcademico.objects.get_or_create(
            nombre="Año Lectivo 2025",
            defaults={
                'fecha_inicio': timezone.now().date(),
                'fecha_fin': timezone.now().date().replace(month=12, day=31),
                'activo': True
            }
        )
        
        # 7. Crear grupo
        grupo, created = Grupo.objects.get_or_create(
            asignatura=asignatura,
            periodo_academico=periodo,
            profesor=profesor,
            defaults={'capacidad_maxima': 30}
        )
        
        # 8. Crear inscripciones
        for estudiante in estudiantes_creados:
            inscripcion, created = Inscripcion.objects.get_or_create(
                estudiante=estudiante,
                grupo=grupo
            )
        
        # 9. Crear algunas notas para demostrar (dejando algunas evaluaciones sin notas)
        evaluaciones = ['Prueba 1', 'Prueba 2', 'Examen Final']
        
        # Solo crear notas para la primera prueba, dejando las otras vacías
        for i, estudiante in enumerate(estudiantes_creados):
            if i < 2:  # Solo los primeros 2 estudiantes tienen nota en Prueba 1
                inscripcion = Inscripcion.objects.get(estudiante=estudiante, grupo=grupo)
                calificacion, created = Calificacion.objects.get_or_create(
                    inscripcion=inscripcion,
                    nombre_evaluacion='Prueba 1',
                    defaults={
                        'puntaje': 6.0 + i,
                        'porcentaje': 25,
                        'fecha_evaluacion': timezone.now().date()
                    }
                )
        
        print("✓ Datos de prueba creados exitosamente")
        print(f"  - Curso: {curso}")
        print(f"  - Asignatura: {asignatura}")
        print(f"  - Estudiantes: {len(estudiantes_creados)}")
        print(f"  - Solo 2 estudiantes tienen nota en 'Prueba 1'")
        print(f"  - Las evaluaciones 'Prueba 2' y 'Examen Final' están vacías")
        
        return curso.id, asignatura.id
        
    except Exception as e:
        print(f"✗ Error creando datos de prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

def test_with_data(curso_id, asignatura_id):
    """Probar la funcionalidad con los datos creados"""
    
    print("\n=== PROBANDO CON DATOS DE PRUEBA ===")
    
    # URL con los datos específicos
    url = f"http://127.0.0.1:8000/notas/ver/?curso_id={curso_id}&asignatura_id={asignatura_id}"
    
    try:
        print(f"Probando URL: {url}")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✓ Página carga correctamente")
            
            # Buscar botones de agregar
            if 'agregar-btn' in response.text:
                print("✓ Botones de agregar nota encontrados")
            
            # Buscar botones de editar
            if 'nota-btn' in response.text:
                print("✓ Botones de editar nota encontrados")
            
            # Contar celdas con botones +
            import re
            agregar_count = len(re.findall(r'class="agregar-btn"', response.text))
            editar_count = len(re.findall(r'class="nota-btn"', response.text))
            
            print(f"✓ Celdas vacías (botón +): {agregar_count}")
            print(f"✓ Celdas con nota (editable): {editar_count}")
            
            if agregar_count > 0:
                print("✓ ¡La funcionalidad de agregar desde celdas vacías está funcionando!")
            
        else:
            print(f"✗ Error: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error probando: {str(e)}")

if __name__ == "__main__":
    curso_id, asignatura_id = create_test_data()
    if curso_id and asignatura_id:
        test_with_data(curso_id, asignatura_id)
        print(f"\n🔗 Visita: http://127.0.0.1:8000/notas/ver/?curso_id={curso_id}&asignatura_id={asignatura_id}")
    else:
        print("✗ No se pudieron crear los datos de prueba")
        sys.exit(1)
