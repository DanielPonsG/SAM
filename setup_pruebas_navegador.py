#!/usr/bin/env python
"""
Script para crear datos de prueba y probar las mejoras del libro de anotaciones
en el navegador
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Curso, Estudiante, Anotacion, Profesor, Perfil
from django.utils import timezone
import random

def crear_usuario_test():
    """Crear un usuario de prueba para probar las funcionalidades"""
    print("="*60)
    print("CREANDO USUARIO DE PRUEBA")
    print("="*60)
    
    # Buscar si ya existe un usuario test
    username = "test_profesor"
    try:
        user = User.objects.get(username=username)
        print(f"✅ Usuario {username} ya existe")
    except User.DoesNotExist:
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            password="test123",
            email="test@escuela.edu",
            first_name="Profesor",
            last_name="de Prueba"
        )
        
        # Crear perfil
        try:
            perfil = Perfil.objects.create(
                user=user,
                tipo_usuario='profesor'
            )
            print(f"✅ Usuario {username} creado exitosamente")
        except Exception as e:
            print(f"⚠️ Error creando perfil: {e}")
            print(f"✅ Usuario {username} creado (sin perfil de profesor)")
    
    print(f"📋 Credenciales:")
    print(f"   Usuario: {username}")
    print(f"   Contraseña: test123")
    print(f"   Tipo: {'Profesor' if hasattr(user, 'perfil') else 'Usuario básico'}")
    
    return user

def mostrar_urls_importantes():
    """Mostrar las URLs importantes para probar"""
    print("\n" + "="*60)
    print("URLS IMPORTANTES PARA PROBAR")
    print("="*60)
    
    urls = [
        ("Login", "http://127.0.0.1:8000/login/"),
        ("Libro de Anotaciones", "http://127.0.0.1:8000/anotaciones/"),
        ("Crear Anotación", "http://127.0.0.1:8000/anotaciones/crear/"),
        ("AJAX Estudiantes por Curso", "http://127.0.0.1:8000/ajax/obtener-estudiantes-curso/"),
        ("AJAX Filtro Estudiantes", "http://127.0.0.1:8000/ajax/obtener-estudiantes-filtro/"),
    ]
    
    for nombre, url in urls:
        print(f"🔗 {nombre:.<30} {url}")
    
    # Mostrar algunas anotaciones para editar
    print(f"\n📝 Anotaciones disponibles para editar:")
    anotaciones = Anotacion.objects.all()[:3]
    for anotacion in anotaciones:
        url_editar = f"http://127.0.0.1:8000/anotaciones/editar/{anotacion.id}/"
        print(f"   - ID {anotacion.id}: {anotacion.titulo} -> {url_editar}")

def crear_anotacion_test():
    """Crear una anotación de prueba"""
    print("\n" + "="*60)
    print("CREANDO ANOTACIÓN DE PRUEBA")
    print("="*60)
    
    # Obtener un curso y estudiante
    curso = Curso.objects.filter(estudiantes__isnull=False).first()
    if not curso:
        print("❌ No hay cursos con estudiantes")
        return
    
    estudiante = curso.estudiantes.first()
    profesor = Profesor.objects.first()
    
    if not profesor:
        print("❌ No hay profesores disponibles")
        return
    
    # Crear anotación
    anotacion = Anotacion.objects.create(
        estudiante=estudiante,
        curso=curso,
        profesor_autor=profesor,
        tipo='positiva',
        categoria='comportamiento',
        titulo='Prueba de funcionalidad - Excelente comportamiento',
        descripcion='Esta es una anotación de prueba creada para verificar que el sistema funciona correctamente. El estudiante demostró un comportamiento ejemplar durante la clase.',
        puntos=5,
        es_grave=False,
        requiere_atencion_apoderado=False
    )
    
    print(f"✅ Anotación creada:")
    print(f"   ID: {anotacion.id}")
    print(f"   Estudiante: {anotacion.estudiante.get_nombre_completo()}")
    print(f"   Curso: {anotacion.curso}")
    print(f"   URL para editar: http://127.0.0.1:8000/anotaciones/editar/{anotacion.id}/")

def generar_instrucciones():
    """Generar instrucciones paso a paso"""
    print("\n" + "="*60)
    print("INSTRUCCIONES PARA PROBAR LAS MEJORAS")
    print("="*60)
    
    print("🚀 PASOS PARA PROBAR:")
    print()
    
    print("1. INICIAR SESIÓN:")
    print("   - Ve a: http://127.0.0.1:8000/login/")
    print("   - Usuario: test_profesor")
    print("   - Contraseña: test123")
    print()
    
    print("2. PROBAR FILTRO DINÁMICO:")
    print("   - Ve a: http://127.0.0.1:8000/anotaciones/")
    print("   - En la sección 'Filtros', selecciona un curso")
    print("   - ✅ El campo 'Estudiante' debería cargarse automáticamente")
    print("   - ✅ Solo debería mostrar estudiantes de ese curso")
    print()
    
    print("3. PROBAR EDICIÓN DE ANOTACIONES:")
    print("   - En la lista de anotaciones, haz clic en el botón 'Editar' (ícono lápiz)")
    print("   - ✅ Los campos 'Curso' y 'Estudiante' deben estar deshabilitados")
    print("   - ✅ Debe mostrar un aviso que no se pueden cambiar")
    print("   - ✅ Solo debe permitir modificar el contenido de la anotación")
    print("   - Prueba cambiar el título y guardar")
    print()
    
    print("4. PROBAR CREACIÓN DE ANOTACIONES:")
    print("   - Ve a: http://127.0.0.1:8000/anotaciones/crear/")
    print("   - Selecciona un curso")
    print("   - ✅ El campo 'Estudiante' debe cargarse automáticamente")
    print("   - Completa el formulario y crea una anotación")
    print()
    
    print("5. VERIFICAR TEMPLATE DE EDICIÓN:")
    print("   - El template de edición debe ser diferente al de creación")
    print("   - Debe mostrar información clara sobre las restricciones")
    print("   - Debe tener un botón para eliminar la anotación")
    print()

def main():
    """Función principal"""
    print("🔧 CONFIGURANDO ENTORNO DE PRUEBAS")
    print("="*60)
    
    # Crear usuario de prueba
    crear_usuario_test()
    
    # Crear anotación de prueba
    crear_anotacion_test()
    
    # Mostrar URLs importantes
    mostrar_urls_importantes()
    
    # Generar instrucciones
    generar_instrucciones()
    
    print("\n" + "="*60)
    print("SERVIDOR DJANGO")
    print("="*60)
    print("Asegúrate de que el servidor Django esté corriendo:")
    print("python manage.py runserver")
    print()
    print("Luego sigue las instrucciones anteriores para probar las mejoras.")
    print()
    print("🎯 OBJETIVOS DE LA PRUEBA:")
    print("✅ Filtro dinámico de estudiantes por curso funciona")
    print("✅ Edición de anotaciones bloquea cambios de curso/estudiante")
    print("✅ Template de edición es diferente y más claro")
    print("✅ AJAX funciona correctamente")
    print("✅ No hay errores de formulario falsos")

if __name__ == "__main__":
    main()
