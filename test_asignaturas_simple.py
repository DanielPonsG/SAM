#!/usr/bin/env python3
"""
Script para diagnosticar el problema con la vista de asignaturas
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from smapp.models import Asignatura, Profesor, Perfil

def test_asignaturas_view():
    """Test de la vista de asignaturas"""
    print("=" * 60)
    print("DIAGNÓSTICO DE LA VISTA DE ASIGNATURAS")
    print("=" * 60)
    
    try:
        # 1. Verificar datos en la base de datos
        total_asignaturas = Asignatura.objects.count()
        total_profesores = Profesor.objects.count()
        
        print(f"📊 Datos en base de datos:")
        print(f"   Total asignaturas: {total_asignaturas}")
        print(f"   Total profesores: {total_profesores}")
        
        # 2. Listar asignaturas existentes
        asignaturas = Asignatura.objects.all()
        print(f"\n📋 Asignaturas encontradas:")
        for i, asignatura in enumerate(asignaturas, 1):
            profesor = asignatura.profesor_responsable
            profesor_info = f"{profesor.primer_nombre} {profesor.apellido_paterno}" if profesor else "Sin profesor"
            print(f"   {i}. {asignatura.codigo_asignatura} - {asignatura.nombre} ({profesor_info})")
        
        # 3. Probar la vista con usuario admin
        client = Client()
        admin_user = User.objects.filter(username='admin').first()
        
        if not admin_user:
            print("❌ No existe usuario admin")
            return False
        
        # Hacer login
        login_success = client.login(username='admin', password='admin123')
        if not login_success:
            print("❌ No se pudo hacer login")
            return False
        
        print("✅ Login exitoso como admin")
        
        # 4. Acceder a la vista de asignaturas
        response = client.get('/asignaturas/')
        print(f"📄 Respuesta de /asignaturas/: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Verificar elementos del template
            if 'Gestión de Asignaturas' in content:
                print("✅ Título encontrado")
            else:
                print("❌ Título no encontrado")
            
            if 'table' in content:
                print("✅ Tabla encontrada en HTML")
            else:
                print("❌ No se encontró tabla en HTML")
            
            if 'Nueva Asignatura' in content:
                print("✅ Botón 'Nueva Asignatura' encontrado")
            else:
                print("❌ Botón 'Nueva Asignatura' no encontrado")
            
            # Contar filas de la tabla
            table_rows = content.count('<tr>')
            print(f"📊 Filas en tabla HTML: {table_rows}")
            
            # Verificar si hay mensaje de "no hay asignaturas"
            if 'No hay asignaturas registradas' in content:
                print("⚠️  Mensaje de 'No hay asignaturas' encontrado")
            
            # Verificar botones de acción
            if 'fas fa-edit' in content:
                print("✅ Botones de editar encontrados")
            else:
                print("❌ Botones de editar no encontrados")
            
        else:
            print(f"❌ Error al acceder a la vista: {response.status_code}")
            if hasattr(response, 'content'):
                print(f"   Contenido: {response.content.decode('utf-8')[:500]}")
        
        print("\n" + "=" * 60)
        print("DIAGNÓSTICO COMPLETADO")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_asignaturas_view()
    sys.exit(0 if success else 1)
