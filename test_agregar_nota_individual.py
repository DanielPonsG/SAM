#!/usr/bin/env python
"""
Script para probar la funcionalidad de agregar notas individuales desde celdas vacías.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Estudiante, Asignatura, Calificacion, Curso, Inscripcion, Grupo, PeriodoAcademico
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from smapp.views import agregar_nota_individual

def test_agregar_nota_individual():
    """Prueba la vista agregar_nota_individual"""
    
    print("=== PRUEBA: Agregar Nota Individual ===")
    
    # Crear datos de prueba
    try:
        # Obtener o crear usuario administrador
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@test.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            print(f"✓ Usuario administrador creado: {admin_user.username}")
        else:
            print(f"✓ Usuario administrador encontrado: {admin_user.username}")
        
        # Obtener o crear estudiante
        estudiante, created = Estudiante.objects.get_or_create(
            primer_nombre='Juan',
            apellido_paterno='Pérez',
            defaults={
                'rut': '12345678-9',
                'email': 'juan@test.com'
            }
        )
        if created:
            print(f"✓ Estudiante creado: {estudiante.get_nombre_completo()}")
        else:
            print(f"✓ Estudiante encontrado: {estudiante.get_nombre_completo()}")
        
        # Obtener o crear asignatura
        asignatura, created = Asignatura.objects.get_or_create(
            nombre='Matemáticas',
            defaults={'codigo_asignatura': 'MAT001'}
        )
        if created:
            print(f"✓ Asignatura creada: {asignatura.nombre}")
        else:
            print(f"✓ Asignatura encontrada: {asignatura.nombre}")
        
        # Crear perfil para el usuario admin
        from smapp.models import Perfil
        perfil, created = Perfil.objects.get_or_create(
            user=admin_user,
            defaults={'tipo_usuario': 'director'}
        )
        if created:
            print(f"✓ Perfil creado: {perfil.tipo_usuario}")
        else:
            print(f"✓ Perfil encontrado: {perfil.tipo_usuario}")
        
        # Crear factory para request
        factory = RequestFactory()
        
        # Crear request GET (mostrar formulario)
        request = factory.get(f'/notas/agregar/{estudiante.id}/{asignatura.id}/Examen Final/')
        request.user = admin_user
        
        print("\n--- Probando vista GET (mostrar formulario) ---")
        response = agregar_nota_individual(request, estudiante.id, asignatura.id, 'Examen Final')
        print(f"✓ Respuesta GET: Status OK")
        
        # Crear request POST (agregar nota)
        request = factory.post(f'/notas/agregar/{estudiante.id}/{asignatura.id}/Examen Final/', {
            'nombre_evaluacion': 'Examen Final',
            'puntaje': 6.5,
            'porcentaje': 40,
            'detalle': 'Examen final de matemáticas',
            'descripcion': 'Evaluación completa de la materia'
        })
        request.user = admin_user
        
        print("\n--- Probando vista POST (crear nota) ---")
        response = agregar_nota_individual(request, estudiante.id, asignatura.id, 'Examen Final')
        print(f"✓ Respuesta POST: Status OK")
        
        # Verificar que la nota se creó
        calificacion = Calificacion.objects.filter(
            inscripcion__estudiante=estudiante,
            nombre_evaluacion='Examen Final'
        ).first()
        
        if calificacion:
            print(f"✓ Nota creada exitosamente:")
            print(f"  - Estudiante: {calificacion.inscripcion.estudiante.get_nombre_completo()}")
            print(f"  - Evaluación: {calificacion.nombre_evaluacion}")
            print(f"  - Puntaje: {calificacion.puntaje}")
            print(f"  - Porcentaje: {calificacion.porcentaje}%")
        else:
            print("✗ La nota no se creó correctamente")
        
        print("\n=== PRUEBA COMPLETADA ===")
        return True
        
    except Exception as e:
        print(f"✗ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_agregar_nota_individual()
    sys.exit(0 if success else 1)
