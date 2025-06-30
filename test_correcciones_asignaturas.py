#!/usr/bin/env python
"""
Script para probar las correcciones en listar_asignaturas y editar_anotacion
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Asignatura, Profesor, Curso, Anotacion
from django.test import Client
from django.urls import reverse

def test_listar_asignaturas():
    """Probar que la vista listar_asignaturas funciona sin errores"""
    print("="*60)
    print("PROBANDO VISTA LISTAR_ASIGNATURAS")
    print("="*60)
    
    # Obtener estadísticas
    total_asignaturas = Asignatura.objects.count()
    con_profesor = Asignatura.objects.filter(profesor_responsable__isnull=False).count()
    sin_profesor = total_asignaturas - con_profesor
    
    print(f"📊 Estadísticas del sistema:")
    print(f"   Total asignaturas: {total_asignaturas}")
    print(f"   Con profesor: {con_profesor}")
    print(f"   Sin profesor: {sin_profesor}")
    
    # Crear cliente de prueba
    client = Client()
    
    # Buscar un usuario admin o crear uno de prueba
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            print("❌ No hay usuario administrador")
            return False
        
        client.force_login(admin_user)
        print(f"✅ Logueado como: {admin_user.username}")
        
        # Hacer petición a la vista
        url = reverse('listar_asignaturas')
        response = client.get(url)
        
        print(f"🌐 URL: {url}")
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Vista listar_asignaturas funciona correctamente")
            return True
        else:
            print(f"❌ Error en la vista: {response.status_code}")
            print(f"   Contenido: {response.content.decode('utf-8')[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error al probar vista: {e}")
        return False

def test_asignaturas_en_anotacion():
    """Probar que las asignaturas se muestran correctamente en el formulario de anotación"""
    print("\n" + "="*60)
    print("PROBANDO ASIGNATURAS EN FORMULARIO DE ANOTACIÓN")
    print("="*60)
    
    from smapp.forms import AnotacionForm
    
    # Buscar un profesor
    profesor = Profesor.objects.first()
    if not profesor:
        print("❌ No hay profesores en el sistema")
        return False
    
    print(f"👨‍🏫 Profesor: {profesor.get_nombre_completo()}")
    
    # Buscar asignaturas del profesor
    asignaturas_profesor = Asignatura.objects.filter(profesor_responsable=profesor)
    print(f"📚 Asignaturas del profesor: {asignaturas_profesor.count()}")
    
    for asig in asignaturas_profesor:
        print(f"   - {asig.nombre} ({asig.codigo_asignatura})")
    
    # Crear formulario para nueva anotación
    form_nuevo = AnotacionForm(profesor=profesor)
    asignaturas_disponibles = form_nuevo.fields['asignatura'].queryset
    
    print(f"📝 Asignaturas disponibles en formulario nuevo: {asignaturas_disponibles.count()}")
    
    # Buscar una anotación existente
    anotacion = Anotacion.objects.first()
    if anotacion:
        print(f"\n📋 Probando formulario de edición:")
        print(f"   Anotación ID: {anotacion.id}")
        print(f"   Estudiante: {anotacion.estudiante.get_nombre_completo()}")
        print(f"   Curso: {anotacion.curso}")
        
        form_editar = AnotacionForm(instance=anotacion, profesor=profesor)
        
        print(f"   Campo curso deshabilitado: {'disabled' in form_editar.fields['curso'].widget.attrs}")
        print(f"   Campo estudiante deshabilitado: {'disabled' in form_editar.fields['estudiante'].widget.attrs}")
        print(f"   Asignaturas disponibles: {form_editar.fields['asignatura'].queryset.count()}")
        
        return True
    else:
        print("⚠️ No hay anotaciones para probar el formulario de edición")
        return True

def test_acceso_urls():
    """Probar el acceso a las URLs importantes"""
    print("\n" + "="*60)
    print("PROBANDO ACCESO A URLS")
    print("="*60)
    
    client = Client()
    
    # Buscar usuario admin
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No hay usuario administrador")
        return False
    
    client.force_login(admin_user)
    
    urls_importantes = [
        ('Listar Asignaturas', '/asignaturas/'),
        ('Libro de Anotaciones', '/anotaciones/'),
        ('Crear Anotación', '/anotaciones/crear/'),
    ]
    
    resultados = []
    for nombre, url in urls_importantes:
        try:
            response = client.get(url)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {nombre:.<30} {url} ({response.status_code})")
            resultados.append(response.status_code == 200)
        except Exception as e:
            print(f"❌ {nombre:.<30} {url} (Error: {e})")
            resultados.append(False)
    
    return all(resultados)

def mostrar_info_modelo():
    """Mostrar información sobre los modelos"""
    print("\n" + "="*60)
    print("INFORMACIÓN DE MODELOS")
    print("="*60)
    
    # Campos del modelo Asignatura
    from django.apps import apps
    Asignatura = apps.get_model('smapp', 'Asignatura')
    
    print("📋 Campos del modelo Asignatura:")
    for field in Asignatura._meta.fields:
        print(f"   - {field.name}: {field.__class__.__name__}")
    
    print("\n📋 Relaciones del modelo Asignatura:")
    for rel in Asignatura._meta.related_objects:
        print(f"   - {rel.name}: {rel.related_model.__name__}")
    
    # Verificar si existe relación many-to-many con profesores
    many_to_many = [f for f in Asignatura._meta.many_to_many]
    print(f"\n📋 Relaciones Many-to-Many: {len(many_to_many)}")
    for field in many_to_many:
        print(f"   - {field.name}: {field.related_model.__name__}")

def main():
    """Función principal"""
    print("🧪 PROBANDO CORRECCIONES DE ASIGNATURAS Y ANOTACIONES")
    print("="*60)
    
    # Mostrar info del modelo
    mostrar_info_modelo()
    
    # Ejecutar pruebas
    tests = [
        ("Listar Asignaturas", test_listar_asignaturas),
        ("Asignaturas en Anotación", test_asignaturas_en_anotacion),
        ("Acceso a URLs", test_acceso_urls),
    ]
    
    resultados = []
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")
            resultados.append((nombre, False))
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE PRUEBAS")
    print("="*60)
    
    exitosos = 0
    for nombre, resultado in resultados:
        status = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"{status} - {nombre}")
        if resultado:
            exitosos += 1
    
    print(f"\n🏆 Resultado: {exitosos}/{len(resultados)} pruebas exitosas")
    
    if exitosos == len(resultados):
        print("🎉 ¡Todas las correcciones funcionan correctamente!")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar la implementación.")

if __name__ == "__main__":
    main()
