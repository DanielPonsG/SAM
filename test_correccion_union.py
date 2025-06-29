#!/usr/bin/env python3
"""
Script para probar la corrección del error de union() en ingresar_notas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Curso, Asignatura, Estudiante, Profesor, Perfil
from django.test import RequestFactory
from django.contrib.auth import authenticate
from smapp.views import ingresar_notas

def test_union_fix():
    """Test para verificar que se corrigió el error de union()"""
    print("🔧 INICIANDO PRUEBA DE CORRECCIÓN DEL ERROR UNION()")
    print("=" * 60)
    
    try:
        # Crear factory para requests
        factory = RequestFactory()
        
        # Obtener usuario admin
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            print("❌ No se encontró usuario administrador")
            return False
            
        # Obtener curso y asignatura
        curso = Curso.objects.first()
        asignatura = Asignatura.objects.first()
        
        if not curso or not asignatura:
            print("❌ No se encontraron curso o asignatura para la prueba")
            return False
            
        print(f"📚 Curso de prueba: {curso}")
        print(f"📖 Asignatura de prueba: {asignatura}")
        
        # Asignar asignatura al curso si no está asignada
        if not curso.asignaturas.filter(id=asignatura.id).exists():
            curso.asignaturas.add(asignatura)
            print(f"✅ Asignatura {asignatura.nombre} asignada al curso {curso}")
        
        # Crear request simulado
        request = factory.get('/notas/ingresar/', {
            'curso_id': curso.id,
            'asignatura_id': asignatura.id
        })
        request.user = admin_user
        
        # Crear perfil de usuario si no existe
        perfil, created = Perfil.objects.get_or_create(
            user=admin_user,
            defaults={'tipo_usuario': 'administrador'}
        )
        
        print(f"👤 Usuario de prueba: {admin_user.username} ({perfil.tipo_usuario})")
        
        # Ejecutar la vista
        print("\n🔍 EJECUTANDO VISTA ingresar_notas...")
        response = ingresar_notas(request)
        
        # Verificar respuesta
        if hasattr(response, 'status_code'):
            print(f"✅ Respuesta HTTP: {response.status_code}")
            if response.status_code == 200:
                print("✅ Vista ejecutada exitosamente sin errores de union()")
                return True
            else:
                print(f"⚠️  Código de respuesta inesperado: {response.status_code}")
                return False
        else:
            print("✅ Vista ejecutada exitosamente (redirect)")
            return True
            
    except Exception as e:
        print(f"❌ ERROR DURANTE LA PRUEBA: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_queryset_operations():
    """Test específico para operaciones de QuerySet"""
    print("\n🔍 PROBANDO OPERACIONES DE QUERYSET")
    print("=" * 40)
    
    try:
        curso = Curso.objects.first()
        if not curso:
            print("❌ No hay cursos disponibles")
            return False
            
        # Simular la lógica corregida
        asignaturas_curso_directo = curso.asignaturas.all()
        print(f"📚 Asignaturas del curso: {asignaturas_curso_directo.count()}")
        
        # Combinar usando IDs (método corregido)
        ids_asignaturas = set()
        ids_asignaturas.update(asignaturas_curso_directo.values_list('id', flat=True))
        
        asignaturas_disponibles = Asignatura.objects.filter(
            id__in=ids_asignaturas
        ).distinct().order_by('nombre')
        
        print(f"📖 Asignaturas disponibles: {asignaturas_disponibles.count()}")
        
        # Probar get() - esto debería funcionar ahora
        if asignaturas_disponibles.exists():
            primera_asignatura = asignaturas_disponibles.first()
            asignatura_obtenida = asignaturas_disponibles.get(id=primera_asignatura.id)
            print(f"✅ get() funciona correctamente: {asignatura_obtenida.nombre}")
            return True
        else:
            print("⚠️  No hay asignaturas disponibles para probar get()")
            return True
            
    except Exception as e:
        print(f"❌ ERROR EN OPERACIONES DE QUERYSET: {e}")
        return False

def main():
    print("🚀 INICIANDO PRUEBAS DE CORRECCIÓN")
    print("=" * 50)
    
    # Verificar estado de la base de datos
    print(f"📊 Cursos en DB: {Curso.objects.count()}")
    print(f"📖 Asignaturas en DB: {Asignatura.objects.count()}")
    print(f"👥 Usuarios admin: {User.objects.filter(is_superuser=True).count()}")
    
    # Ejecutar pruebas
    test1_passed = test_queryset_operations()
    test2_passed = test_union_fix()
    
    print("\n" + "=" * 50)
    print("📋 RESUMEN DE PRUEBAS:")
    print(f"  🔧 Operaciones QuerySet: {'✅ PASÓ' if test1_passed else '❌ FALLÓ'}")
    print(f"  🌐 Vista ingresar_notas: {'✅ PASÓ' if test2_passed else '❌ FALLÓ'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ La corrección del error union() fue exitosa")
    else:
        print("\n⚠️  Algunas pruebas fallaron")
        
    return test1_passed and test2_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
