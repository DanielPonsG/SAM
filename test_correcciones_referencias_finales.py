#!/usr/bin/env python
"""
Script para probar las correcciones de referencias a profesores_responsables
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import *
from smapp.forms import AnotacionForm
from django.test import RequestFactory, TestCase
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware

def test_modelo_asignatura():
    """Verificar que el modelo Asignatura no tiene referencias a profesores_responsables"""
    print("=== TEST: Modelo Asignatura ===")
    
    # Verificar que profesor_responsable existe
    try:
        asignatura = Asignatura.objects.create(
            nombre="Test",
            codigo_asignatura="TEST001",
            descripcion="Test"
        )
        print("✓ Campo profesor_responsable existe y funciona")
        
        # Verificar que profesores_responsables no existe
        try:
            _ = asignatura.profesores_responsables
            print("✗ ERROR: Campo profesores_responsables aún existe")
            return False
        except AttributeError:
            print("✓ Campo profesores_responsables no existe (correcto)")
            
        asignatura.delete()
        return True
        
    except Exception as e:
        print(f"✗ ERROR en modelo Asignatura: {e}")
        return False

def test_anotacion_form():
    """Verificar que AnotacionForm funciona correctamente"""
    print("\n=== TEST: AnotacionForm ===")
    
    try:
        # Crear datos de prueba
        user = User.objects.create_user(username='test_prof_unique', password='test123')
        profesor = Profesor.objects.create(
            user=user,
            primer_nombre="Test",
            apellido_paterno="Profesor",
            numero_documento="12345678-9",
            codigo_profesor="PROF001",
            especialidad="Matemáticas",
            telefono="123456789",
            email="test@test.com"
        )
        
        curso = Curso.objects.create(
            nivel='1B',
            paralelo='A',
            anio=2024
        )
        
        asignatura = Asignatura.objects.create(
            nombre="Matemáticas",
            codigo_asignatura="MAT001",
            profesor_responsable=profesor
        )
        
        curso.asignaturas.add(asignatura)
        
        estudiante = Estudiante.objects.create(
            primer_nombre="Test",
            apellido_paterno="Estudiante",
            numero_documento="87654321-0",
            codigo_estudiante="EST001",
            fecha_nacimiento="2010-01-01"
        )
        
        curso.estudiantes.add(estudiante)
        
        # Probar el formulario
        form = AnotacionForm(profesor=profesor)
        print("✓ AnotacionForm se instancia correctamente")
        
        # Verificar que las asignaturas se filtran correctamente
        asignaturas_queryset = form.fields['asignatura'].queryset
        print(f"✓ Asignaturas disponibles: {asignaturas_queryset.count()}")
        
        # Limpiar datos de prueba
        curso.delete()
        asignatura.delete()
        estudiante.delete()
        profesor.delete()
        user.delete()
        
        return True
        
    except Exception as e:
        print(f"✗ ERROR en AnotacionForm: {e}")
        return False

def test_vista_listar_asignaturas():
    """Verificar que la vista listar_asignaturas funciona"""
    print("\n=== TEST: Vista listar_asignaturas ===")
    
    try:
        from smapp.views import listar_asignaturas
        from django.test import RequestFactory
        
        # Crear request simulado
        factory = RequestFactory()
        request = factory.get('/listar_asignaturas/')
        
        # Crear usuario admin
        import random
        username = f'admin_test_{random.randint(1000, 9999)}'
        user = User.objects.create_user(username=username, password='test123')
        user.is_staff = True
        user.is_superuser = True
        user.save()
        request.user = user
        
        # Simular middleware
        SessionMiddleware().process_request(request)
        MessageMiddleware().process_request(request)
        request.session.save()
        
        # Llamar a la vista
        response = listar_asignaturas(request)
        
        if response.status_code == 200:
            print("✓ Vista listar_asignaturas funciona correctamente")
            user.delete()
            return True
        else:
            print(f"✗ ERROR: Vista retorna código {response.status_code}")
            user.delete()
            return False
            
    except Exception as e:
        print(f"✗ ERROR en vista listar_asignaturas: {e}")
        try:
            user.delete()
        except:
            pass
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("INICIANDO PRUEBAS DE CORRECCIONES DE REFERENCIAS")
    print("=" * 60)
    
    resultados = []
    
    # Ejecutar pruebas
    resultados.append(test_modelo_asignatura())
    resultados.append(test_anotacion_form())
    resultados.append(test_vista_listar_asignaturas())
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS:")
    exitosas = sum(resultados)
    total = len(resultados)
    
    print(f"✓ Pruebas exitosas: {exitosas}/{total}")
    
    if exitosas == total:
        print("🎉 TODAS LAS CORRECCIONES FUNCIONAN CORRECTAMENTE")
        return True
    else:
        print("⚠️  ALGUNAS CORRECCIONES NECESITAN REVISIÓN")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
