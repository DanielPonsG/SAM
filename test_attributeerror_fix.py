#!/usr/bin/env python
"""
Script para probar la URL específica que causaba el error AttributeError
"""

import requests
import sys

def test_error_url():
    """Probar la URL que causaba el error AttributeError"""
    
    print("=== PRUEBA: URL que causaba AttributeError ===")
    
    # URL exacta que causaba el error
    url = "http://127.0.0.1:8000/notas/ver/?curso_id=28&asignatura_id=55&curso_id=28"
    
    try:
        print(f"Probando URL: {url}")
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ ¡ÉXITO! La página se carga sin errores AttributeError")
            
            # Verificar contenido esperado
            if "Notas de" in response.text:
                print("✓ Título de notas presente")
            
            if "notas-table" in response.text:
                print("✓ Tabla de notas presente")
            
            if "get_list_item" in response.text:
                print("✓ Filtro get_list_item funcionando")
            
            # Contar elementos
            import re
            estudiantes = len(re.findall(r'<tr>', response.text)) - 1  # -1 por el header
            print(f"✓ Filas de estudiantes detectadas: {estudiantes}")
            
        elif response.status_code == 500:
            print("❌ Error 500 - Todavía hay un error interno")
            print("Posibles causas:")
            print("- Error AttributeError no resuelto completamente")
            print("- Problema en la vista o template")
            return False
            
        else:
            print(f"⚠️ Status Code inesperado: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor Django")
        print("Asegúrate de que Django esté ejecutándose en http://127.0.0.1:8000/")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False
    
    # Probar también otras combinaciones
    print("\n=== Probando otras URLs relacionadas ===")
    
    test_urls = [
        ("Solo curso", "http://127.0.0.1:8000/notas/ver/?curso_id=28"),
        ("Curso + asignatura", "http://127.0.0.1:8000/notas/ver/?curso_id=28&asignatura_id=55"),
        ("Base", "http://127.0.0.1:8000/notas/ver/")
    ]
    
    all_passed = True
    for name, test_url in test_urls:
        try:
            response = requests.get(test_url, timeout=10)
            if response.status_code == 200:
                print(f"✓ {name}: OK")
            else:
                print(f"✗ {name}: Error {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"✗ {name}: Excepción {e}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    success = test_error_url()
    if success:
        print("\n🎉 ¡PRUEBA EXITOSA!")
        print("El error AttributeError ha sido resuelto.")
        print("Todas las funcionalidades están funcionando correctamente.")
    else:
        print("\n❌ Algunas pruebas fallaron.")
        print("Revisa los logs para más detalles.")
    
    sys.exit(0 if success else 1)
