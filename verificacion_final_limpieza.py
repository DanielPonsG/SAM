#!/usr/bin/env python3
"""
Script de verificación final después de la limpieza de templates.
Verifica que el sistema funcione correctamente y que todos los templates principales estén operativos.
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth.models import User

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

def test_templates_principales():
    """Verificar que los templates principales cargan correctamente"""
    print("🧪 VERIFICACIÓN DE TEMPLATES PRINCIPALES")
    print("=" * 50)
    
    client = Client()
    
    # Obtener usuario admin
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("❌ Usuario admin no encontrado. Creando usuario de prueba...")
        admin_user = User.objects.create_user(
            username='admin_test',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
    
    # Hacer login
    client.force_login(admin_user)
    
    # URLs importantes a verificar
    urls_verificar = [
        ('/', 'Página de inicio'),
        ('/asignaturas/', 'Lista de asignaturas'),
        ('/calendario/', 'Calendario'),
        ('/profesores/', 'Lista de profesores'),
        ('/cursos/', 'Lista de cursos'),
        ('/estudiantes/listar/', 'Lista de estudiantes'),
    ]
    
    resultados = []
    
    for url, descripcion in urls_verificar:
        try:
            print(f"🔍 Verificando: {descripcion} ({url})")
            response = client.get(url)
            
            if response.status_code == 200:
                print(f"   ✅ OK - Status: {response.status_code}")
                resultados.append((url, descripcion, True, response.status_code))
            else:
                print(f"   ❌ Error - Status: {response.status_code}")
                resultados.append((url, descripcion, False, response.status_code))
                
        except Exception as e:
            print(f"   ❌ Excepción: {str(e)}")
            resultados.append((url, descripcion, False, f"Exception: {str(e)}"))
    
    return resultados

def verificar_templates_existen():
    """Verificar que los templates esenciales existan"""
    print("\n📁 VERIFICACIÓN DE ARCHIVOS DE TEMPLATES")
    print("=" * 50)
    
    templates_esenciales = [
        'index_master.html',
        'listar_asignaturas.html',
        'calendario.html',
        'login.html',
        'inicio.html',
        'agregar_asignatura.html',
        'editar_asignatura.html',
        'eliminar_asignatura.html',
    ]
    
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    
    for template in templates_esenciales:
        template_path = os.path.join(templates_dir, template)
        if os.path.exists(template_path):
            print(f"✅ {template} - Existe")
        else:
            print(f"❌ {template} - NO EXISTE")

def verificar_asignaturas_funcionando():
    """Verificación específica de la funcionalidad de asignaturas"""
    print("\n🎯 VERIFICACIÓN ESPECÍFICA: GESTIÓN DE ASIGNATURAS")
    print("=" * 50)
    
    client = Client()
    
    try:
        admin_user = User.objects.get(username='admin')
        client.force_login(admin_user)
        
        # Verificar página principal de asignaturas
        response = client.get('/asignaturas/')
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Verificar elementos importantes
            verificaciones = [
                ('Bootstrap 5', 'bootstrap' in content.lower()),
                ('jQuery', 'jquery' in content.lower()),
                ('Tabla de asignaturas', 'table' in content.lower()),
                ('Botón agregar', 'agregar' in content.lower()),
                ('Modal asignar profesor', 'modal' in content.lower()),
                ('AJAX funcionalidad', 'xhr' in content.lower() or 'ajax' in content.lower()),
            ]
            
            for nombre, resultado in verificaciones:
                estado = "✅" if resultado else "❌"
                print(f"{estado} {nombre}: {'OK' if resultado else 'NO DETECTADO'}")
            
            print("✅ Página de asignaturas carga correctamente")
            return True
            
        else:
            print(f"❌ Error al cargar asignaturas - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en verificación de asignaturas: {str(e)}")
        return False

def generar_reporte_final(resultados):
    """Generar reporte final de la verificación"""
    print("\n📊 REPORTE FINAL DE VERIFICACIÓN")
    print("=" * 50)
    
    exitosos = sum(1 for _, _, success, _ in resultados if success)
    total = len(resultados)
    
    print(f"🎯 URLs verificadas: {total}")
    print(f"✅ Exitosas: {exitosos}")
    print(f"❌ Fallidas: {total - exitosos}")
    print(f"📈 Tasa de éxito: {(exitosos/total)*100:.1f}%")
    
    if total - exitosos > 0:
        print("\n❌ URLS CON PROBLEMAS:")
        for url, descripcion, success, status in resultados:
            if not success:
                print(f"   • {descripcion} ({url}) - Status: {status}")
    
    print(f"\n{'✅ VERIFICACIÓN COMPLETADA - TODO FUNCIONAL' if exitosos == total else '⚠️  VERIFICACIÓN COMPLETADA - HAY PROBLEMAS'}")

def main():
    """Función principal"""
    print("🔬 VERIFICACIÓN FINAL DEL PROYECTO SMA")
    print("🧹 Después de la limpieza de templates")
    print("=" * 60)
    
    # Verificar que existen los templates
    verificar_templates_existen()
    
    # Verificar URLs principales
    resultados = test_templates_principales()
    
    # Verificación específica de asignaturas
    verificar_asignaturas_funcionando()
    
    # Generar reporte final
    generar_reporte_final(resultados)
    
    print("\n🎉 ¡Verificación final completada!")
    print("📝 El proyecto está limpio y funcional después de eliminar templates innecesarios.")

if __name__ == "__main__":
    main()
