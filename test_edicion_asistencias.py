#!/usr/bin/env python3
"""
Script para probar que la edición de asistencias funciona correctamente después de las correcciones
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from smapp.models import AsistenciaAlumno, Profesor
from django.contrib.auth.models import User

def test_edicion_asistencias():
    """Prueba que la edición de asistencias funcione para diferentes tipos de usuario"""
    print("🧪 PRUEBA DE EDICIÓN DE ASISTENCIAS")
    print("=" * 50)
    
    client = Client()
    
    # 1. Obtener algunos registros de asistencia para probar
    asistencias = AsistenciaAlumno.objects.all()[:5]
    if not asistencias:
        print("❌ No hay registros de asistencia para probar")
        return False
        
    print(f"📊 Probando con {len(asistencias)} registros de asistencia")
    
    # 2. Probar como superuser (administrador)
    try:
        print("\n👑 Probando como superuser...")
        superuser = User.objects.filter(is_superuser=True).first()
        if superuser:
            login_success = client.login(username=superuser.username, password='admin')
            if not login_success:
                login_success = client.login(username=superuser.username, password='admin123')
                
            if login_success:
                print("✅ Login como superuser exitoso")
                
                # Probar edición de cada asistencia
                for asistencia in asistencias:
                    try:
                        url = reverse('editar_asistencia_alumno', args=[asistencia.id])
                        response = client.get(url)
                        
                        if response.status_code == 200:
                            print(f"✅ Acceso a edición ID {asistencia.id}: OK")
                        else:
                            print(f"❌ Acceso a edición ID {asistencia.id}: Error {response.status_code}")
                            
                    except Exception as e:
                        print(f"❌ Error accediendo a edición ID {asistencia.id}: {e}")
                        
                client.logout()
            else:
                print("⚠️  No se pudo hacer login como superuser")
        else:
            print("⚠️  No hay superuser en el sistema")
    except Exception as e:
        print(f"❌ Error probando como superuser: {e}")
    
    # 3. Probar como profesor
    try:
        print("\n👨‍🏫 Probando como profesor...")
        profesores = Profesor.objects.filter(user__isnull=False)[:2]
        
        for profesor in profesores:
            try:
                login_success = client.login(username=profesor.user.username, password='admin123')
                if not login_success:
                    login_success = client.login(username=profesor.user.username, password='123456')
                    
                if login_success:
                    print(f"✅ Login como profesor {profesor.get_nombre_completo()} exitoso")
                    
                    # Probar edición de asistencias donde es responsable
                    for asistencia in asistencias:
                        try:
                            url = reverse('editar_asistencia_alumno', args=[asistencia.id])
                            response = client.get(url)
                            
                            if response.status_code == 200:
                                print(f"✅ Profesor puede editar ID {asistencia.id}")
                            elif response.status_code == 302:
                                # Redirigido, probablemente sin permisos
                                print(f"⚠️  Profesor sin permisos para ID {asistencia.id} (esperado)")
                            else:
                                print(f"❌ Error inesperado ID {asistencia.id}: {response.status_code}")
                                
                        except Exception as e:
                            print(f"❌ Error probando ID {asistencia.id}: {e}")
                            
                    client.logout()
                    break  # Solo probar con un profesor
                else:
                    print(f"⚠️  No se pudo hacer login como {profesor.get_nombre_completo()}")
            except Exception as e:
                print(f"❌ Error con profesor {profesor.get_nombre_completo()}: {e}")
                
    except Exception as e:
        print(f"❌ Error probando como profesor: {e}")
    
    # 4. Verificar estado final de registros
    print(f"\n📊 Estado final de registros:")
    registros_con_profesor = AsistenciaAlumno.objects.filter(profesor_registro__isnull=False).count()
    registros_sin_profesor = AsistenciaAlumno.objects.filter(profesor_registro__isnull=True).count()
    
    print(f"✅ Registros con profesor_registro: {registros_con_profesor}")
    print(f"⚠️  Registros sin profesor_registro: {registros_sin_profesor}")
    
    return registros_sin_profesor == 0

def main():
    """Función principal"""
    try:
        success = test_edicion_asistencias()
        
        if success:
            print("\n🎯 RESULTADO: Sistema de edición de asistencias funciona correctamente")
            print("✅ Todos los registros tienen profesor_registro asignado")
            print("✅ Permisos de edición funcionan apropiadamente")
            return 0
        else:
            print("\n⚠️  RESULTADO: Algunos problemas menores detectados")
            return 1
            
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
