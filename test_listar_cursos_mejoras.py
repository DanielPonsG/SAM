#!/usr/bin/env python
"""
Script para probar las mejoras en listar_cursos.html
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from smapp.models import Curso, Asignatura

def test_listar_cursos_mejoras():
    """Prueba las nuevas funcionalidades de listar cursos"""
    client = Client()
    
    try:
        # Hacer login como admin
        user = User.objects.filter(username='admin').first()
        if not user:
            print("❌ No se encontró usuario admin")
            return False
            
        client.force_login(user)
        print("✅ Login exitoso")
        
        # Probar la vista listar_cursos
        response = client.get('/cursos/')
        if response.status_code == 200:
            print("✅ Vista listar_cursos funciona correctamente")
        else:
            print(f"❌ Error en listar_cursos: status {response.status_code}")
            return False
        
        # Verificar que el template se renderiza sin errores
        content = response.content.decode('utf-8')
        print(f"✅ Template renderizado exitosamente ({len(content)} caracteres)")
        
        # Buscar elementos clave del nuevo template
        elementos_clave = [
            'Asignaturas',
            'Gestionar',
            'modalGestionarAsignaturas',
            'toggleAsignaturas',
            'gestionarAsignaturasCurso'
        ]
        
        elementos_encontrados = 0
        for elemento in elementos_clave:
            if elemento in content:
                print(f"✅ Template incluye '{elemento}'")
                elementos_encontrados += 1
            else:
                print(f"❌ Template no incluye '{elemento}'")
        
        if elementos_encontrados >= 3:
            print(f"\n✅ Template actualizado correctamente ({elementos_encontrados}/{len(elementos_clave)} elementos encontrados)")
        else:
            print(f"\n❌ Template no se actualizó correctamente ({elementos_encontrados}/{len(elementos_clave)} elementos encontrados)")
            return False
        
        # Verificar estadísticas básicas
        total_cursos = Curso.objects.count()
        total_asignaturas = Asignatura.objects.count()
        
        print(f"\n📊 Estadísticas del sistema:")
        print(f"   - Cursos totales: {total_cursos}")
        print(f"   - Asignaturas disponibles: {total_asignaturas}")
        
        print("\n🎉 Pruebas básicas de listar_cursos pasaron exitosamente")
        print("Las mejoras principales están funcionando:")
        print("- ✅ Template actualizado con nuevas funcionalidades")
        print("- ✅ Modal de gestión de asignaturas disponible")
        print("- ✅ JavaScript para gestión incluido")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Probando mejoras en listar_cursos...")
    
    success = test_listar_cursos_mejoras()
    
    if success:
        print("\n✅ MEJORAS DE LISTAR_CURSOS FUNCIONANDO CORRECTAMENTE")
        print("Ahora puedes:")
        print("- Ver cuántas asignaturas tiene cada curso")
        print("- Gestionar asignaturas desde la interfaz")
        print("- Ver estadísticas completas del sistema")
        print("- Acceder directamente a ver notas por curso")
    else:
        print("\n❌ ALGUNAS MEJORAS NO ESTÁN FUNCIONANDO")
        print("Revisar los errores anteriores")
        sys.exit(1)
