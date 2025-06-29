#!/usr/bin/env python
"""
Script para verificar que las mejoras del calendario están funcionando
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

def verificar_mejoras_calendario():
    print("🔍 VERIFICANDO MEJORAS DEL CALENDARIO")
    print("=" * 50)
    
    # Leer el archivo del template
    template_path = "templates/calendario.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar las mejoras específicas
        mejoras = {
            "Modal de crear evento": 'id="modalCrearEvento"' in content,
            "Selección de cursos específicos": 'dirigido_especificos' in content,
            "Checkboxes de cursos": 'name="cursos_especificos"' in content,
            "Validación de horas": 'function validarHoras()' in content,
            "Elementos de error de horas": 'error_hora_inicio' in content,
            "Radio buttons para dirigido a": 'name="dirigido_a"' in content,
            "Div de cursos específicos": 'id="cursosEspecificos"' in content,
            "Validación mejorada": 'validarCursosEspecificos' in content,
            "Eventos de JavaScript": 'addEventListener' in content,
            "Gestión del modal": 'shown.bs.modal' in content,
            "Logs de depuración": 'console.log' in content,
            "Validación en tiempo real": 'addEventListener(\'change\', validarHoras)' in content
        }
        
        print("📋 ESTADO DE LAS MEJORAS:")
        for mejora, presente in mejoras.items():
            estado = "✅" if presente else "❌"
            print(f"   {estado} {mejora}")
        
        # Contar elementos específicos
        print(f"\n📊 ESTADÍSTICAS DEL TEMPLATE:")
        cursos_especificos_count = content.count('name="cursos_especificos"')
        print(f"   - Checkboxes de cursos: {cursos_especificos_count}")
        print(f"   - Funciones JavaScript: {content.count('function ')}")
        print(f"   - Event listeners: {content.count('addEventListener')}")
        print(f"   - Console.log (debug): {content.count('console.log')}")
        
        # Verificar estructura del modal
        modal_presente = 'modalCrearEvento' in content
        formulario_presente = 'formCrearEvento' in content
        
        print(f"\n🎯 ESTRUCTURA DEL MODAL:")
        print(f"   - Modal presente: {'✅' if modal_presente else '❌'}")
        print(f"   - Formulario presente: {'✅' if formulario_presente else '❌'}")
        
        if modal_presente and formulario_presente:
            print("   ✅ Estructura del modal completa")
        else:
            print("   ❌ Problemas en la estructura del modal")
            
    except FileNotFoundError:
        print("❌ No se pudo encontrar el archivo calendario.html")
        return
    
    # Verificar que el servidor esté corriendo
    print(f"\n🌐 ESTADO DEL SERVIDOR:")
    import urllib.request
    try:
        response = urllib.request.urlopen('http://127.0.0.1:8000/calendario/', timeout=5)
        if response.getcode() == 200:
            print("   ✅ Servidor accesible en http://127.0.0.1:8000/calendario/")
        else:
            print(f"   ⚠️ Servidor responde con código: {response.getcode()}")
    except Exception as e:
        print(f"   ❌ Servidor no accesible: {e}")
        print("   💡 Ejecuta: python manage.py runserver")
    
    print(f"\n📝 INSTRUCCIONES DE PRUEBA:")
    print("1. Ve a: http://127.0.0.1:8000/calendario/")
    print("2. Haz login si no estás logueado")
    print("3. Haz clic en 'Nuevo Evento' (botón azul arriba a la derecha)")
    print("4. En el modal que se abre:")
    print("   📋 Marca 'Cursos específicos' → deben aparecer checkboxes abajo")
    print("   🕐 Pon hora inicio 10:00 y hora fin 09:00 → debe mostrar error rojo")
    print("   📝 Llena solo título y fecha → debe permitir crear el evento")
    print("5. Abre la consola del navegador (F12) para ver logs de depuración")
    
    print(f"\n🔧 PARA DEPURAR EN EL NAVEGADOR:")
    print("Copia y pega en la consola del navegador:")
    print("   probarCalendario()")
    print("   simularSeleccionCursos()")
    print("   probarValidacionHoras()")

if __name__ == "__main__":
    verificar_mejoras_calendario()
