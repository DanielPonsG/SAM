#!/usr/bin/env python  
"""
Script para generar el HTML real del calendario y analizarlo
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client

def generar_html_calendario():
    print("📄 GENERANDO HTML REAL DEL CALENDARIO")
    print("=" * 50)
    
    client = Client()
    admin = User.objects.filter(is_superuser=True).first()
    client.force_login(admin)
    
    # Hacer request GET al calendario
    response = client.get('/calendario/')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Guardar HTML completo
        with open('calendario_debug.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ HTML guardado en 'calendario_debug.html'")
        
        # Extraer y mostrar solo la parte del modal
        start_modal = content.find('id="modalCrearEvento"')
        if start_modal != -1:
            # Buscar hacia atrás para encontrar el inicio del div
            start_div = content.rfind('<div', 0, start_modal)
            # Buscar hacia adelante para encontrar el final del modal
            modal_content = content[start_div:start_modal+2000]  # Tomar una porción grande
            
            print("\n🎯 MODAL ENCONTRADO:")
            print("-" * 30)
            lines = modal_content.split('\n')[:20]  # Primeras 20 líneas
            for i, line in enumerate(lines, 1):
                print(f"{i:2d}: {line}")
            print("...")
            
        else:
            print("❌ Modal NO encontrado")
        
        # Verificar elementos específicos
        elementos_verificar = [
            ('id="modalCrearEvento"', 'Modal principal'),
            ('id="formCrearEvento"', 'Formulario'),
            ('id="dirigido_especificos"', 'Radio cursos específicos'),
            ('id="cursosEspecificos"', 'Div cursos específicos'),
            ('id="hora_inicio"', 'Input hora inicio'),
            ('id="hora_fin"', 'Input hora fin'),
            ('name="cursos_especificos"', 'Checkboxes cursos'),
            ('function validarHoras', 'Función validación'),
        ]
        
        print(f"\n🔍 VERIFICACIÓN DETALLADA:")
        for elemento, desc in elementos_verificar:
            count = content.count(elemento)
            if count > 0:
                print(f"   ✅ {desc}: {count} occurrencias")
            else:
                print(f"   ❌ {desc}: NO encontrado")
        
        # Contar cursos específicos
        import re
        cursos_matches = re.findall(r'name="cursos_especificos".*?value="(\d+)"', content)
        print(f"\n📚 CURSOS ESPECÍFICOS: {len(cursos_matches)} encontrados")
        
        if len(cursos_matches) > 0:
            print("   IDs de cursos:", cursos_matches[:5], "..." if len(cursos_matches) > 5 else "")
        
        # Buscar errores de JavaScript
        js_errors = [
            'SyntaxError',
            'ReferenceError', 
            'TypeError',
            'undefined',
            'null'
        ]
        
        print(f"\n🚀 BÚSQUEDA DE ERRORES JS:")
        for error in js_errors:
            if error in content:
                print(f"   ⚠️ Posible error: {error}")
        
        print(f"\n📊 ESTADÍSTICAS DEL HTML:")
        print(f"   - Tamaño total: {len(content):,} caracteres")
        print(f"   - Líneas: {content.count(chr(10)):,}")
        print(f"   - Scripts: {content.count('<script>')}")
        print(f"   - Divs: {content.count('<div')}")
        
        return True
    
    else:
        print(f"❌ Error: {response.status_code}")
        return False

if __name__ == '__main__':
    success = generar_html_calendario()
    
    if success:
        print("\n✅ HTML generado correctamente")
        print("🌐 Puedes revisar 'calendario_debug.html' para ver el HTML completo")
        print("🔧 El calendario debería estar funcionando en http://127.0.0.1:8000/calendario/")
    else:
        print("\n❌ Error al generar HTML")
