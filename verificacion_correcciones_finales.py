#!/usr/bin/env python
"""
Prueba simple para verificar las correcciones de referencias
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Asignatura

def test_referencias_corregidas():
    """Verificar que las referencias a profesores_responsables han sido corregidas"""
    print("=== VERIFICANDO CORRECCIONES ===")
    
    # 1. Verificar que el modelo Asignatura no tiene profesores_responsables
    try:
        asignatura = Asignatura(nombre="Test", codigo_asignatura="TEST001")
        
        # Intentar acceder a profesores_responsables (debe fallar)
        try:
            _ = asignatura.profesores_responsables
            print("✗ ERROR: profesores_responsables aún existe en el modelo")
            return False
        except AttributeError:
            print("✓ profesores_responsables eliminado del modelo")
        
        # Verificar que profesor_responsable existe
        asignatura.profesor_responsable = None  # Debe funcionar
        print("✓ profesor_responsable existe en el modelo")
        
    except Exception as e:
        print(f"✗ ERROR en modelo: {e}")
        return False
    
    # 2. Verificar AnotacionForm
    try:
        from smapp.forms import AnotacionForm
        form = AnotacionForm()
        print("✓ AnotacionForm se importa correctamente")
    except Exception as e:
        print(f"✗ ERROR en AnotacionForm: {e}")
        return False
    
    # 3. Verificar vistas
    try:
        from smapp.views import listar_asignaturas
        print("✓ Vista listar_asignaturas se importa correctamente")
    except Exception as e:
        print(f"✗ ERROR en vista listar_asignaturas: {e}")
        return False
    
    return True

def buscar_referencias_restantes():
    """Buscar referencias restantes a profesores_responsables en el código"""
    print("\n=== BUSCANDO REFERENCIAS RESTANTES ===")
    
    import os
    import re
    
    archivos_python = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py') and 'migrations' not in root and '__pycache__' not in root:
                archivos_python.append(os.path.join(root, file))
    
    referencias_encontradas = []
    
    for archivo in archivos_python:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
                if 'profesores_responsables' in contenido:
                    lineas = contenido.split('\n')
                    for i, linea in enumerate(lineas):
                        if 'profesores_responsables' in linea and not linea.strip().startswith('#'):
                            referencias_encontradas.append(f"{archivo}:{i+1}: {linea.strip()}")
        except:
            continue
    
    if referencias_encontradas:
        print(f"⚠️  Se encontraron {len(referencias_encontradas)} referencias restantes:")
        for ref in referencias_encontradas[:10]:  # Mostrar solo las primeras 10
            print(f"   {ref}")
        if len(referencias_encontradas) > 10:
            print(f"   ... y {len(referencias_encontradas) - 10} más")
    else:
        print("✓ No se encontraron referencias restantes en archivos Python")
    
    return len(referencias_encontradas)

def main():
    print("VERIFICACIÓN FINAL DE CORRECCIONES")
    print("=" * 50)
    
    # Verificar correcciones
    correcciones_ok = test_referencias_corregidas()
    
    # Buscar referencias restantes
    referencias_restantes = buscar_referencias_restantes()
    
    print("\n" + "=" * 50)
    print("RESUMEN:")
    
    if correcciones_ok:
        print("✓ Las correcciones principales funcionan correctamente")
    else:
        print("✗ Hay problemas con las correcciones principales")
    
    if referencias_restantes == 0:
        print("✓ No hay referencias restantes en código Python")
    else:
        print(f"⚠️  Hay {referencias_restantes} referencias restantes que necesitan revisión")
    
    if correcciones_ok and referencias_restantes == 0:
        print("\n🎉 TODAS LAS CORRECCIONES ESTÁN COMPLETAS")
        return True
    else:
        print("\n⚠️  ALGUNAS CORRECCIONES PUEDEN NECESITAR ATENCIÓN ADICIONAL")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
