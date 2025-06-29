#!/usr/bin/env python
"""
Verificar HTML renderizado del calendario
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
import re

def verificar_html_calendario():
    """Verificar el HTML renderizado del calendario"""
    print("🔍 VERIFICANDO HTML DEL CALENDARIO")
    print("=" * 60)
    
    # Crear cliente y hacer login
    client = Client()
    admin_user = User.objects.filter(is_superuser=True).first()
    client.force_login(admin_user)
    
    # Obtener la página
    response = client.get('/calendario/')
    content = response.content.decode('utf-8')
    
    # 1. Verificar que el modal existe
    print("\n🔧 VERIFICANDO MODAL:")
    if 'id="modalCrearEvento"' in content:
        print("   ✅ Modal de crear evento encontrado")
    else:
        print("   ❌ Modal NO encontrado")
        return
    
    # 2. Verificar sección de cursos específicos
    print("\n📚 VERIFICANDO SECCIÓN DE CURSOS:")
    if 'id="cursosEspecificos"' in content:
        print("   ✅ Contenedor de cursos específicos encontrado")
    else:
        print("   ❌ Contenedor de cursos específicos NO encontrado")
        return
    
    # 3. Buscar checkboxes de cursos
    checkboxes_pattern = r'<input[^>]*name="cursos_especificos"[^>]*value="(\d+)"[^>]*>'
    checkboxes = re.findall(checkboxes_pattern, content)
    print(f"   📋 Checkboxes encontrados: {len(checkboxes)}")
    
    if len(checkboxes) > 0:
        print("   ✅ Los checkboxes se están generando correctamente")
        for i, curso_id in enumerate(checkboxes[:3]):  # Mostrar primeros 3
            print(f"      - Curso ID: {curso_id}")
    else:
        print("   ❌ NO se encontraron checkboxes de cursos")
        # Buscar la sección específica
        cursos_section_start = content.find('id="cursosEspecificos"')
        if cursos_section_start != -1:
            cursos_section = content[cursos_section_start:cursos_section_start+1000]
            print("\n   📝 Contenido de la sección de cursos:")
            print("   " + "="*50)
            print("   " + cursos_section[:500] + "...")
            print("   " + "="*50)
    
    # 4. Verificar labels de cursos
    labels_pattern = r'<label[^>]*for="curso_(\d+)"[^>]*>'
    labels = re.findall(labels_pattern, content)
    print(f"   🏷️  Labels de cursos encontrados: {len(labels)}")
    
    # 5. Verificar JavaScript de control
    print("\n⚙️ VERIFICANDO JAVASCRIPT:")
    js_checks = [
        ('dirigido_especificos', 'Control de radio button'),
        ('cursosEspecificos', 'Referencia al contenedor'),
        ('cursos_especificos', 'Selector de checkboxes'),
        ('validarCursosEspecificos', 'Función de validación')
    ]
    
    for check, description in js_checks:
        if check in content:
            print(f"   ✅ {description}: encontrado")
        else:
            print(f"   ❌ {description}: NO encontrado")
    
    # 6. Extraer y mostrar la sección específica del modal
    print("\n📄 EXTRAYENDO SECCIÓN DEL MODAL:")
    modal_start = content.find('id="modalCrearEvento"')
    modal_end = content.find('</div>', content.find('</form>', modal_start)) + 6
    
    if modal_start != -1 and modal_end != -1:
        modal_content = content[modal_start:modal_end]
        
        # Buscar específicamente la sección de cursos
        cursos_start = modal_content.find('Dirigido a')
        cursos_end = modal_content.find('</div>', modal_content.find('cursosEspecificos', cursos_start)) + 6
        
        if cursos_start != -1 and cursos_end != -1:
            cursos_section = modal_content[cursos_start:cursos_end]
            print("   ✅ Sección de cursos extraída correctamente")
            print(f"   📏 Tamaño: {len(cursos_section)} caracteres")
            
            # Contar elementos específicos en la sección
            radio_count = cursos_section.count('type="radio"')
            checkbox_count = cursos_section.count('type="checkbox"')
            print(f"   📻 Radio buttons: {radio_count}")
            print(f"   ☑️  Checkboxes: {checkbox_count}")
        else:
            print("   ❌ No se pudo extraer la sección de cursos")
    
    print("\n" + "=" * 60)
    print("✅ VERIFICACIÓN COMPLETADA")
    
    # Crear archivo de debug con el HTML
    with open('debug_calendario_html.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("💾 HTML completo guardado en 'debug_calendario_html.html'")

if __name__ == "__main__":
    verificar_html_calendario()
