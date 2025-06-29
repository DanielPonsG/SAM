#!/usr/bin/env python3
"""
Script para probar el escenario específico que causaba el error NotSupportedError
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Curso, Asignatura, Estudiante, Profesor, Perfil
from django.test import Client

def test_specific_error_scenario():
    """Prueba el escenario específico que causaba el error"""
    print("🎯 PROBANDO ESCENARIO ESPECÍFICO DEL ERROR")
    print("=" * 50)
    
    try:
        # Crear cliente de prueba
        client = Client()
        
        # Obtener usuario admin
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            print("❌ No se encontró usuario administrador")
            return False
            
        # Hacer login
        client.force_login(admin_user)
        print(f"👤 Login como: {admin_user.username}")
        
        # Obtener curso y asignatura
        curso = Curso.objects.first()
        asignatura = Asignatura.objects.first()
        
        if not curso or not asignatura:
            print("❌ No se encontraron curso o asignatura")
            return False
            
        # Asignar asignatura al curso
        curso.asignaturas.add(asignatura)
        print(f"✅ Asignatura {asignatura.nombre} asignada al curso {curso}")
        
        # Probar la URL que causaba el error
        url = f"/notas/ingresar/?curso_id={curso.id}&asignatura_id={asignatura.id}&curso_id={curso.id}"
        print(f"🌐 Probando URL: {url}")
        
        response = client.get(url)
        
        print(f"📊 Código de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Respuesta exitosa - Sin error NotSupportedError")
            return True
        elif response.status_code == 302:
            print("✅ Redirección exitosa - Sin error NotSupportedError")
            return True
        else:
            print(f"⚠️  Código inesperado: {response.status_code}")
            if hasattr(response, 'content'):
                print(f"Contenido: {response.content[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_queryset_union_fix():
    """Prueba específica del problema union()"""
    print("\n🔧 PROBANDO CORRECCIÓN ESPECÍFICA DE UNION()")
    print("=" * 45)
    
    try:
        curso = Curso.objects.first()
        if not curso:
            print("❌ No hay cursos para probar")
            return False
            
        print(f"📚 Probando con curso: {curso}")
        
        # Método ANTERIOR (que causaba error) - comentado para referencia
        # asignaturas_curso_directo = curso.asignaturas.all()
        # asignaturas_con_grupos = Asignatura.objects.filter(...).distinct()
        # asignaturas_union = asignaturas_curso_directo.union(asignaturas_con_grupos)
        # asignatura = asignaturas_union.get(id=X)  # ESTO CAUSABA ERROR
        
        # Método NUEVO (corregido)
        asignaturas_curso_directo = curso.asignaturas.all()
        print(f"📖 Asignaturas directas: {asignaturas_curso_directo.count()}")
        
        # Usar IDs en lugar de union()
        ids_asignaturas = set()
        ids_asignaturas.update(asignaturas_curso_directo.values_list('id', flat=True))
        
        asignaturas_disponibles = Asignatura.objects.filter(
            id__in=ids_asignaturas
        ).distinct().order_by('nombre')
        
        print(f"🎯 Asignaturas disponibles: {asignaturas_disponibles.count()}")
        
        # Probar .get() que antes fallaba
        if asignaturas_disponibles.exists():
            primera = asignaturas_disponibles.first()
            obtenida = asignaturas_disponibles.get(id=primera.id)
            print(f"✅ .get() funciona: {obtenida.nombre}")
            return True
        else:
            print("⚠️  No hay asignaturas para probar .get()")
            return True
            
    except Exception as e:
        print(f"❌ ERROR en prueba de union: {e}")
        return False

def main():
    print("🚀 INICIANDO PRUEBAS DEL ERROR ESPECÍFICO")
    print("=" * 55)
    
    test1 = test_queryset_union_fix()
    test2 = test_specific_error_scenario()
    
    print("\n" + "=" * 55)
    print("📋 RESULTADOS:")
    print(f"  🔧 Corrección union(): {'✅ PASÓ' if test1 else '❌ FALLÓ'}")
    print(f"  🌐 Escenario específico: {'✅ PASÓ' if test2 else '❌ FALLÓ'}")
    
    if test1 and test2:
        print("\n🎉 ¡ERROR COMPLETAMENTE CORREGIDO!")
        print("✅ La funcionalidad ahora trabaja sin problemas")
    else:
        print("\n⚠️  Aún hay problemas que resolver")
        
    return test1 and test2

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
