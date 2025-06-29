#!/usr/bin/env python3
"""
Script de prueba completa para verificar la creación de usuarios con RUT válido.
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Estudiante, Profesor
from smapp.forms import EstudianteForm, ProfesorForm
from django.contrib.auth.models import User

def limpiar_datos_prueba():
    """Limpiar datos de prueba existentes"""
    try:
        # Eliminar usuarios de prueba si existen
        usuarios_prueba = ['test.estudiante', 'test.profesor']
        for username in usuarios_prueba:
            try:
                user = User.objects.get(username=username)
                user.delete()
                print(f"✓ Usuario {username} eliminado")
            except User.DoesNotExist:
                print(f"- Usuario {username} no existe (OK)")
        
        # Eliminar estudiantes y profesores de prueba
        try:
            estudiante = Estudiante.objects.get(codigo_estudiante='TEST001')
            estudiante.delete()
            print("✓ Estudiante de prueba eliminado")
        except Estudiante.DoesNotExist:
            print("- Estudiante de prueba no existe (OK)")
            
        try:
            profesor = Profesor.objects.get(codigo_profesor='TEST001')
            profesor.delete()
            print("✓ Profesor de prueba eliminado")
        except Profesor.DoesNotExist:
            print("- Profesor de prueba no existe (OK)")
            
    except Exception as e:
        print(f"Error limpiando datos: {e}")

def test_crear_estudiante():
    """Probar creación completa de estudiante"""
    print("\n=== PRUEBA CREAR ESTUDIANTE ===")
    
    datos = {
        'primer_nombre': 'Test',
        'segundo_nombre': 'Usuario',
        'apellido_paterno': 'Estudiante',
        'apellido_materno': 'Prueba',
        'tipo_documento': 'RUT',
        'numero_documento': '20.589.644-9',
        'fecha_nacimiento': '2005-01-15',
        'genero': 'M',
        'direccion': 'Calle Falsa 123',
        'telefono': '+56987654321',
        'email': 'test.estudiante@ejemplo.com',
        'codigo_estudiante': 'TEST001',
        'username': 'test.estudiante',
        'password': 'password123'
    }
    
    form = EstudianteForm(data=datos)
    
    if form.is_valid():
        print("✓ Formulario válido")
        
        # Crear usuario Django
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
            email=form.cleaned_data['email']
        )
        
        # Crear estudiante
        estudiante = form.save(commit=False)
        estudiante.user = user
        estudiante.save()
        
        print(f"✓ Estudiante creado exitosamente")
        print(f"  - ID: {estudiante.id}")
        print(f"  - Nombre: {estudiante.get_nombre_completo()}")
        print(f"  - RUT: {estudiante.numero_documento}")
        print(f"  - Email: {estudiante.email}")
        print(f"  - Código: {estudiante.codigo_estudiante}")
        print(f"  - Usuario: {estudiante.user.username}")
        
        return True
    else:
        print("✗ Formulario inválido")
        print(f"Errores: {form.errors}")
        return False

def test_crear_profesor():
    """Probar creación completa de profesor"""
    print("\n=== PRUEBA CREAR PROFESOR ===")
    
    datos = {
        'primer_nombre': 'Test',
        'segundo_nombre': 'Usuario',
        'apellido_paterno': 'Profesor',
        'apellido_materno': 'Prueba',
        'tipo_documento': 'RUT',
        'numero_documento': '15.123.456-7',  # RUT diferente
        'fecha_nacimiento': '1980-05-20',
        'genero': 'F',
        'direccion': 'Avenida Siempre Viva 742',
        'telefono': '+56912345678',
        'email': 'test.profesor@ejemplo.com',
        'codigo_profesor': 'TEST001',
        'especialidad': 'Matemáticas',
        'username': 'test.profesor',
        'password': 'password123'
    }
    
    form = ProfesorForm(data=datos)
    
    if form.is_valid():
        print("✓ Formulario válido")
        
        # Crear usuario Django
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
            email=form.cleaned_data['email']
        )
        
        # Crear profesor
        profesor = form.save(commit=False)
        profesor.user = user
        profesor.save()
        
        print(f"✓ Profesor creado exitosamente")
        print(f"  - ID: {profesor.id}")
        print(f"  - Nombre: {profesor.get_nombre_completo()}")
        print(f"  - RUT: {profesor.numero_documento}")
        print(f"  - Email: {profesor.email}")
        print(f"  - Código: {profesor.codigo_profesor}")
        print(f"  - Especialidad: {profesor.especialidad}")
        print(f"  - Usuario: {profesor.user.username}")
        
        return True
    else:
        print("✗ Formulario inválido")
        print(f"Errores: {form.errors}")
        return False

def verificar_datos_creados():
    """Verificar que los datos se crearon correctamente en la base de datos"""
    print("\n=== VERIFICACIÓN DE DATOS ===")
    
    try:
        estudiante = Estudiante.objects.get(codigo_estudiante='TEST001')
        print(f"✓ Estudiante encontrado: {estudiante.get_nombre_completo()}")
        print(f"  - RUT: {estudiante.numero_documento}")
        print(f"  - Tipo documento: {estudiante.get_tipo_documento_display()}")
    except Estudiante.DoesNotExist:
        print("✗ Estudiante no encontrado")
    
    try:
        profesor = Profesor.objects.get(codigo_profesor='TEST001')
        print(f"✓ Profesor encontrado: {profesor.get_nombre_completo()}")
        print(f"  - RUT: {profesor.numero_documento}")
        print(f"  - Tipo documento: {profesor.get_tipo_documento_display()}")
    except Profesor.DoesNotExist:
        print("✗ Profesor no encontrado")

if __name__ == "__main__":
    print("=== PRUEBA COMPLETA DE CREACIÓN DE USUARIOS ===")
    
    # Limpiar datos previos
    limpiar_datos_prueba()
    
    # Probar creación de estudiante
    estudiante_ok = test_crear_estudiante()
    
    # Probar creación de profesor
    profesor_ok = test_crear_profesor()
    
    # Verificar datos
    verificar_datos_creados()
    
    # Resumen
    print("\n=== RESUMEN ===")
    print(f"Estudiante creado: {'✓' if estudiante_ok else '✗'}")
    print(f"Profesor creado: {'✓' if profesor_ok else '✗'}")
    
    if estudiante_ok and profesor_ok:
        print("\n🎉 ¡Todas las pruebas pasaron! El sistema funciona correctamente.")
    else:
        print("\n❌ Algunas pruebas fallaron. Revisar los errores.")
    
    print("\nDatos de prueba creados:")
    print("- Estudiante: test.estudiante / password123")
    print("- Profesor: test.profesor / password123")
