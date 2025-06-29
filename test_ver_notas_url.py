#!/usr/bin/env python
"""
Script para probar la URL de ver notas que estaba dando error
"""

import requests
import sys

def test_ver_notas_url():
    """Prueba la URL que estaba dando el error AttributeError"""
    
    print("=== PRUEBA: URL ver_notas_curso ===")
    
    # URL que estaba dando error
    url = "http://127.0.0.1:8000/notas/ver/?curso_id=30&asignatura_id=57&curso_id=28"
    
    try:
        print(f"Probando URL: {url}")
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ La página se carga correctamente")
            
            # Verificar si contiene elementos esperados
            if "Notas por Estudiante" in response.text:
                print("✓ Contiene el título de la tabla de notas")
            
            if "agregar-btn" in response.text:
                print("✓ Contiene botones de agregar nota")
            
            if "nota-btn" in response.text:
                print("✓ Contiene botones de nota existente")
                
            print("✓ Prueba exitosa - no hay errores AttributeError")
            
        elif response.status_code == 500:
            print(f"✗ Error 500 - Error interno del servidor")
            print("Contenido del error:")
            print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
            
        else:
            print(f"✗ Status Code inesperado: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("✗ No se pudo conectar al servidor. ¿Está Django ejecutándose?")
        return False
    except requests.exceptions.Timeout:
        print("✗ Timeout - el servidor no responde")
        return False
    except Exception as e:
        print(f"✗ Error inesperado: {str(e)}")
        return False
    
    print("\n=== PRUEBA COMPLETADA ===")
    return True

if __name__ == "__main__":
    success = test_ver_notas_url()
    sys.exit(0 if success else 1)
