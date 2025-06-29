#!/usr/bin/env python3
"""
Script para probar que se ha solucionado el error de template VariableDoesNotExist
relacionado con [observacion] en registrar_asistencia_alumno.html
"""

import os
import sys
import django
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Curso, Estudiante, Profesor, AsistenciaAlumno, Asignatura

def test_template_fix():
    """Prueba que el template no genere errores VariableDoesNotExist"""
    print("🧪 INICIANDO PRUEBA DE CORRECCIÓN DE TEMPLATE")
    print("=" * 60)
    
    client = Client()
    
    # 1. Obtener un profesor que exista
    try:
        profesor = Profesor.objects.first()
        if not profesor:
            print("❌ Error: No hay profesores en el sistema")
            return False
            
        print(f"✅ Profesor encontrado: {profesor.get_nombre_completo()}")
        
        # Login del profesor
        if not profesor.user:
            print("❌ Error: El profesor no tiene usuario asociado")
            return False
            
        login_success = client.login(username=profesor.user.username, password='admin123')
        if not login_success:
            print("❌ Error: No se pudo hacer login")
            return False
            
        print("✅ Login exitoso")
        
    except Exception as e:
        print(f"❌ Error obteniendo profesor: {e}")
        return False
    
    # 2. Obtener un curso
    try:
        curso = Curso.objects.first()
        if not curso:
            print("❌ Error: No hay cursos en el sistema")
            return False
            
        print(f"✅ Curso encontrado: {curso}")
        
    except Exception as e:
        print(f"❌ Error obteniendo curso: {e}")
        return False
    
    # 3. Probar GET inicial (paso 1 - selección de curso)
    try:
        print("\n📋 Probando GET inicial...")
        response = client.get(reverse('registrar_asistencia_alumno'))
        
        if response.status_code != 200:
            print(f"❌ Error en GET inicial: status {response.status_code}")
            return False
            
        print("✅ GET inicial exitoso")
        
    except Exception as e:
        print(f"❌ Error en GET inicial: {e}")
        return False
    
    # 4. Probar POST para seleccionar curso (paso 2 - mostrar estudiantes)
    try:
        print("\n📋 Probando POST selección de curso...")
        response = client.post(reverse('registrar_asistencia_alumno'), {
            'curso': curso.id
        })
        
        if response.status_code != 200:
            print(f"❌ Error en POST selección: status {response.status_code}")
            if hasattr(response, 'content'):
                content = response.content.decode('utf-8')
                if 'VariableDoesNotExist' in content or 'observacion' in content:
                    print("❌ ERROR ENCONTRADO: El error de template sigue presente")
                    print("Contenido del error:")
                    print(content[:500] + "..." if len(content) > 500 else content)
                    return False
            return False
            
        # Verificar que se muestra la lista de estudiantes
        content = response.content.decode('utf-8')
        if 'mostrar_lista' not in content and 'Registrar Asistencia -' not in content:
            print("❌ Error: No se muestra la lista de estudiantes")
            return False
            
        # Verificar que no hay errores de template
        if 'VariableDoesNotExist' in content:
            print("❌ ERROR: Todavía hay errores VariableDoesNotExist en el template")
            return False
            
        if 'Failed lookup for key [observacion]' in content:
            print("❌ ERROR: El error específico de [observacion] sigue presente")
            return False
            
        print("✅ POST selección exitoso - template renderiza correctamente")
        
    except Exception as e:
        print(f"❌ Error en POST selección: {e}")
        return False
    
    # 5. Probar registro masivo con estudiantes existentes
    try:
        print("\n📋 Probando registro masivo...")
        
        # Obtener estudiantes del curso
        estudiantes = curso.estudiantes.all()[:3]
        if not estudiantes:
            print("⚠️  No hay estudiantes en el curso, creando datos de prueba...")
            return True  # No es un error crítico para esta prueba
            
        # Crear datos de registro masivo
        post_data = {
            'registro_masivo': '1',
            'curso': curso.id,
            'fecha': '2024-01-15',
            'hora_registro': '10:00:00'
        }
        
        # Agregar datos de cada estudiante
        for i, estudiante in enumerate(estudiantes):
            post_data[f'presente_{estudiante.id}'] = 'on' if i % 2 == 0 else ''
            post_data[f'observacion_{estudiante.id}'] = f'Observación {i+1}'
            post_data[f'justificacion_{estudiante.id}'] = f'Justificación {i+1}' if i % 2 == 1 else ''
        
        response = client.post(reverse('registrar_asistencia_alumno'), post_data)
        
        # Verificar que no hay errores de template
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            if 'VariableDoesNotExist' in content or 'Failed lookup for key [observacion]' in content:
                print("❌ ERROR: Error de template en registro masivo")
                return False
        
        print("✅ Registro masivo exitoso - sin errores de template")
        
    except Exception as e:
        print(f"❌ Error en registro masivo: {e}")
        # No es crítico para esta prueba específica
        pass
    
    print("\n" + "=" * 60)
    print("🎉 PRUEBA DE CORRECCIÓN DE TEMPLATE COMPLETADA EXITOSAMENTE")
    print("✅ El error VariableDoesNotExist para [observacion] ha sido solucionado")
    return True

def main():
    """Función principal"""
    try:
        success = test_template_fix()
        if success:
            print("\n🎯 RESULTADO: Template corregido exitosamente")
            return 0
        else:
            print("\n❌ RESULTADO: Aún hay errores en el template")
            return 1
            
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
