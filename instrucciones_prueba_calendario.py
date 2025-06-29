#!/usr/bin/env python
"""
Instrucciones paso a paso para probar el calendario
"""

def instrucciones_prueba():
    """Mostrar instrucciones para probar el calendario"""
    print("📋 INSTRUCCIONES PARA PROBAR EL CALENDARIO")
    print("=" * 60)
    
    print("\n🌐 PASO 1: ABRIR CALENDARIO")
    print("   1. Ir a: http://127.0.0.1:8000/calendario/")
    print("   2. Hacer login como usuario administrador si es necesario")
    
    print("\n➕ PASO 2: CREAR NUEVO EVENTO")
    print("   1. Hacer clic en el botón 'Nuevo Evento' (azul, arriba derecha)")
    print("   2. Se abrirá un modal titulado 'Crear Nuevo Evento'")
    
    print("\n📚 PASO 3: SELECCIONAR CURSOS ESPECÍFICOS")
    print("   1. En la sección 'Dirigido a', verás dos opciones:")
    print("      • 'Todos los cursos' (seleccionado por defecto)")
    print("      • 'Cursos específicos'")
    print("   2. Hacer clic en 'Cursos específicos'")
    print("   3. Debería aparecer una sección con checkboxes de cursos")
    
    print("\n✅ RESULTADO ESPERADO:")
    print("   - Al seleccionar 'Cursos específicos' debe aparecer:")
    print("     • Una caja gris clara con borde")
    print("     • Título 'Seleccionar cursos:'")
    print("     • Lista de cursos con checkboxes")
    print("     • Cada curso muestra: nivel, paralelo y profesor")
    
    print("\n🔧 SI NO FUNCIONA:")
    print("   1. Abrir Developer Tools (F12)")
    print("   2. Ir a la pestaña Console")
    print("   3. Buscar errores de JavaScript")
    print("   4. Verificar que los elementos existan:")
    print("      • document.getElementById('dirigido_especificos')")
    print("      • document.getElementById('cursosEspecificos')")
    
    print("\n🐛 DEBUGGING ADICIONAL:")
    print("   En la consola del navegador, ejecutar:")
    print("   → console.log(document.querySelectorAll('input[name=\"cursos_especificos\"]'))")
    print("   → document.getElementById('cursosEspecificos').style.display = 'block'")
    
    print("\n" + "=" * 60)
    print("💡 NOTA: Los cursos disponibles son:")
    
    # Mostrar cursos disponibles
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
    django.setup()
    
    from smapp.models import Curso
    from django.utils import timezone
    
    cursos = Curso.objects.filter(anio=timezone.now().year).order_by('nivel', 'paralelo')
    for curso in cursos:
        print(f"   • {curso} - Prof: {curso.profesor_jefe or 'Sin asignar'}")
    
    print("\n📞 CONTACTO:")
    print("   Si el problema persiste, proporcionar:")
    print("   1. Screenshots del modal")
    print("   2. Errores de la consola")
    print("   3. Resultado de los comandos de debugging")

if __name__ == "__main__":
    instrucciones_prueba()
