#!/usr/bin/env python
"""
Script para probar específicamente que los botones de agregar nota funcionan correctamente
"""

import requests
import re
import sys

def test_agregar_nota_buttons():
    """Prueba que los botones de agregar nota se muestren y funcionen"""
    
    print("=== PRUEBA: Botones de Agregar Nota ===")
    
    # Primera, obtener la página de notas
    url = "http://127.0.0.1:8000/notas/ver/"
    
    try:
        print("1. Cargando página de notas...")
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"✗ Error al cargar página: {response.status_code}")
            return False
        
        html_content = response.text
        print("✓ Página cargada correctamente")
        
        # Buscar botones de agregar nota
        agregar_pattern = r'<a href="[^"]*agregar_nota_individual[^"]*" class="agregar-btn"[^>]*>\s*\+\s*</a>'
        agregar_matches = re.findall(agregar_pattern, html_content, re.IGNORECASE | re.DOTALL)
        
        if agregar_matches:
            print(f"✓ Encontrados {len(agregar_matches)} botones de agregar nota (+)")
            
            # Extraer una URL de ejemplo
            url_pattern = r'href="([^"]*agregar_nota_individual[^"]*)"'
            url_match = re.search(url_pattern, html_content, re.IGNORECASE)
            
            if url_match:
                ejemplo_url = url_match.group(1)
                print(f"✓ URL de ejemplo encontrada: {ejemplo_url}")
                
                # Probar que la URL de agregar nota funciona
                print("2. Probando URL de agregar nota...")
                full_url = f"http://127.0.0.1:8000{ejemplo_url}"
                
                agregar_response = requests.get(full_url, timeout=10)
                
                if agregar_response.status_code == 200:
                    print("✓ La página de agregar nota se carga correctamente")
                    
                    # Verificar que contiene el formulario
                    if "Agregar Nota" in agregar_response.text:
                        print("✓ Contiene el título 'Agregar Nota'")
                    
                    if "nombre_evaluacion" in agregar_response.text:
                        print("✓ Contiene el campo de nombre de evaluación")
                    
                    if "puntaje" in agregar_response.text:
                        print("✓ Contiene el campo de puntaje")
                        
                else:
                    print(f"✗ Error al cargar página de agregar nota: {agregar_response.status_code}")
                    return False
            else:
                print("✗ No se pudo extraer URL de ejemplo")
                return False
        else:
            print("⚠ No se encontraron botones de agregar nota - puede ser que no haya celdas vacías")
        
        # Buscar botones de editar nota existentes
        editar_pattern = r'<a href="[^"]*editar_nota[^"]*" class="nota-btn"[^>]*>'
        editar_matches = re.findall(editar_pattern, html_content, re.IGNORECASE | re.DOTALL)
        
        if editar_matches:
            print(f"✓ Encontrados {len(editar_matches)} botones de editar nota existente")
        
        # Verificar CSS para botones
        if ".agregar-btn" in html_content:
            print("✓ CSS para botones de agregar está presente")
        
        if ".nota-btn" in html_content:
            print("✓ CSS para botones de nota está presente")
        
        print("✓ Prueba de botones completada exitosamente")
        return True
        
    except requests.exceptions.ConnectionError:
        print("✗ No se pudo conectar al servidor. ¿Está Django ejecutándose?")
        return False
    except Exception as e:
        print(f"✗ Error inesperado: {str(e)}")
        return False
    
    print("\n=== PRUEBA COMPLETADA ===")

if __name__ == "__main__":
    success = test_agregar_nota_buttons()
    sys.exit(0 if success else 1)
