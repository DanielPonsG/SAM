#!/usr/bin/env python
"""
Script para probar el calendario en el navegador
"""
import os
import django
import sys
import time

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

def test_browser():
    print("🌐 PRUEBA DEL CALENDARIO EN EL NAVEGADOR")
    print("=" * 50)
    
    # Ejecutar servidor de desarrollo
    print("🚀 Iniciando servidor de desarrollo...")
    print("📝 Instrucciones:")
    print("   1. El servidor se iniciará en http://127.0.0.1:8000")
    print("   2. Ve al calendario: http://127.0.0.1:8000/calendario/")
    print("   3. Haz login con admin / admin123")
    print("   4. Prueba las siguientes funcionalidades:")
    print("      ✅ Hacer clic en 'Nuevo Evento'")
    print("      ✅ Seleccionar 'Cursos específicos' y verificar que aparezcan los checkboxes")
    print("      ✅ Poner hora de inicio mayor que hora de fin y verificar validación")
    print("      ✅ Intentar crear un evento solo con título y fecha")
    print("      ✅ Crear un evento completo con cursos específicos")
    print("\n🔍 COSAS A VERIFICAR:")
    print("   - Que el modal se abra correctamente")
    print("   - Que aparezcan checkboxes cuando selecciones 'Cursos específicos'")
    print("   - Que la validación de horas funcione en tiempo real")
    print("   - Que se pueda crear un evento exitosamente")
    print("\n⌨️ Presiona Ctrl+C para detener el servidor cuando termines")
    print("=" * 50)
    
    os.system('python manage.py runserver')

if __name__ == "__main__":
    test_browser()
