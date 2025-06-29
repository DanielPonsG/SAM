#!/usr/bin/env python
"""
Script para probar específicamente el manejo de listas vs diccionarios
en los filtros del template y reproducir el error AttributeError si existe
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.templatetags.custom_filters import get_item, get_list_item
from smapp.models import Estudiante

def test_attributeerror_scenarios():
    """Prueba específica para casos que podrían causar AttributeError"""
    print("🧪 Probando escenarios que podrían causar AttributeError...")
    
    # Crear objetos de prueba similares a los del template
    estudiante = Estudiante.objects.first()
    if not estudiante:
        print("❌ No hay estudiantes en la BD para la prueba")
        return False
    
    # Escenario 1: Diccionario con clave de objeto estudiante
    print("\n📝 Escenario 1: Diccionario con objeto estudiante como clave")
    dict_con_estudiante = {estudiante: ['nota1', 'nota2', 'nota3']}
    
    try:
        result = get_item(dict_con_estudiante, estudiante)
        print(f"✅ get_item con objeto estudiante: {type(result)} - {result}")
        
        # Ahora probar get_list_item en el resultado (que debe ser una lista)
        if isinstance(result, list):
            item = get_list_item(result, 0)
            print(f"✅ get_list_item en resultado: {item}")
        else:
            print(f"❌ El resultado no es una lista: {type(result)}")
            
    except AttributeError as e:
        print(f"❌ AttributeError en escenario 1: {e}")
        return False
    except Exception as e:
        print(f"❌ Otro error en escenario 1: {e}")
        return False
    
    # Escenario 2: Lista pasada donde se espera diccionario
    print("\n📝 Escenario 2: Lista pasada a get_item donde se esperaría dict")
    lista_incorrecta = ['item0', 'item1', 'item2']
    
    try:
        result = get_item(lista_incorrecta, estudiante)
        print(f"✅ get_item con lista y objeto: {result}")
    except AttributeError as e:
        print(f"❌ AttributeError en escenario 2: {e}")
        return False
    except Exception as e:
        print(f"✅ Otro error controlado en escenario 2: {e}")
    
    # Escenario 3: Simular el contexto real del template
    print("\n📝 Escenario 3: Simulando contexto real del template")
    
    # Crear estructura similar a notas_por_estudiante
    notas_por_estudiante = {estudiante: [None, None, None]}  # Lista de notas
    promedios_estudiantes = {estudiante.id: {'promedio': 5.5, 'estado': 'Aprobado'}}
    
    try:
        # Simular: notas_estudiante=notas_por_estudiante|get_item:estudiante
        notas_estudiante = get_item(notas_por_estudiante, estudiante)
        print(f"✅ notas_estudiante obtenido: {type(notas_estudiante)}")
        
        # Simular: nota=notas_estudiante|get_list_item:forloop.counter0
        if notas_estudiante is not None:
            nota = get_list_item(notas_estudiante, 0)
            print(f"✅ nota individual obtenida: {nota}")
        
        # Simular: datos=promedios_estudiantes|get_item:estudiante.id
        datos = get_item(promedios_estudiantes, estudiante.id)
        print(f"✅ datos de promedio obtenidos: {datos}")
        
    except AttributeError as e:
        print(f"❌ AttributeError en escenario 3: {e}")
        return False
    except Exception as e:
        print(f"❌ Otro error en escenario 3: {e}")
        return False
    
    # Escenario 4: Valores None o vacíos
    print("\n📝 Escenario 4: Valores None o vacíos")
    
    try:
        result = get_item(None, estudiante)
        print(f"✅ get_item con None: {result}")
        
        result = get_item({}, estudiante)
        print(f"✅ get_item con dict vacío: {result}")
        
        result = get_list_item([], 0)
        print(f"✅ get_list_item con lista vacía: {result}")
        
    except AttributeError as e:
        print(f"❌ AttributeError en escenario 4: {e}")
        return False
    except Exception as e:
        print(f"✅ Otro error controlado en escenario 4: {e}")
    
    print("\n🎉 Todos los escenarios de AttributeError pasaron correctamente")
    return True

if __name__ == "__main__":
    print("🔧 Iniciando pruebas específicas de AttributeError...")
    
    success = test_attributeerror_scenarios()
    
    if success:
        print("\n✅ NO SE ENCONTRARON ERRORES AttributeError")
        print("Los filtros manejan correctamente todos los casos problemáticos")
    else:
        print("\n❌ SE ENCONTRARON ERRORES AttributeError")
        print("Es necesario revisar los filtros")
        sys.exit(1)
