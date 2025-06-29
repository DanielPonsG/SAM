#!/usr/bin/env python3
"""
Test script para validar la funcionalidad del RUT en el frontend.
Comprueba que los cambios en el pattern HTML funcionen correctamente.
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.forms import EstudianteForm, ProfesorForm, validar_rut, formatear_rut

def test_validacion_rut():
    """Prueba la validación de RUT en el backend"""
    print("=== TEST VALIDACIÓN RUT ===")
    
    # RUTs de prueba
    ruts_validos = [
        "20.589.644-9",
        "20589644-9", 
        "20589644-K",
        "12.345.678-9",
        "7.654.321-0"
    ]
    
    ruts_invalidos = [
        "20.589.644-8",  # DV incorrecto
        "20589644-8",    # DV incorrecto
        "abc.def.ghi-j", # Caracteres inválidos
        "12345678",      # Sin DV
        ""               # Vacío
    ]
    
    print("\n--- RUTs Válidos ---")
    for rut in ruts_validos:
        es_valido = validar_rut(rut)
        formateado = formatear_rut(rut) if es_valido else "N/A"
        print(f"RUT: {rut:15} -> Válido: {es_valido:5} -> Formateado: {formateado}")
    
    print("\n--- RUTs Inválidos ---")
    for rut in ruts_invalidos:
        es_valido = validar_rut(rut)
        print(f"RUT: {rut:15} -> Válido: {es_valido:5}")

def test_form_validation():
    """Prueba la validación de formularios con RUT"""
    print("\n=== TEST VALIDACIÓN FORMULARIOS ===")
    
    # Datos de prueba para estudiante
    datos_estudiante = {
        'primer_nombre': 'Juan',
        'apellido_paterno': 'Pérez',
        'tipo_documento': 'RUT',
        'numero_documento': '20.589.644-9',
        'fecha_nacimiento': '2005-01-15',
        'genero': 'M',
        'email': 'juan.perez@test.com',
        'codigo_estudiante': 'EST002',
        'username': 'juan.perez',
        'password': 'password123'
    }
    
    # Datos de prueba para profesor
    datos_profesor = {
        'primer_nombre': 'María',
        'apellido_paterno': 'González',
        'tipo_documento': 'RUT',
        'numero_documento': '20.589.644-9',
        'fecha_nacimiento': '1980-05-20',
        'genero': 'F',
        'email': 'maria.gonzalez@test.com',
        'codigo_profesor': 'PROF002',
        'especialidad': 'Matemáticas',
        'username': 'maria.gonzalez',
        'password': 'password123'
    }
    
    print("\n--- Formulario Estudiante ---")
    form_estudiante = EstudianteForm(data=datos_estudiante)
    if form_estudiante.is_valid():
        print("✓ Formulario de estudiante válido")
        print(f"RUT procesado: {form_estudiante.cleaned_data['numero_documento']}")
    else:
        print("✗ Formulario de estudiante inválido")
        print(f"Errores: {form_estudiante.errors}")
    
    print("\n--- Formulario Profesor ---")
    form_profesor = ProfesorForm(data=datos_profesor)
    if form_profesor.is_valid():
        print("✓ Formulario de profesor válido")
        print(f"RUT procesado: {form_profesor.cleaned_data['numero_documento']}")
    else:
        print("✗ Formulario de profesor inválido")
        print(f"Errores: {form_profesor.errors}")

def test_pattern_html():
    """Prueba el patrón HTML actualizado"""
    print("\n=== TEST PATRÓN HTML ===")
    
    # Obtener el patrón del widget
    form_estudiante = EstudianteForm()
    widget_attrs = form_estudiante.fields['numero_documento'].widget.attrs
    pattern = widget_attrs.get('pattern', 'Sin patrón')
    placeholder = widget_attrs.get('placeholder', 'Sin placeholder')
    maxlength = widget_attrs.get('maxlength', 'Sin maxlength')
    
    print(f"Patrón HTML: {pattern}")
    print(f"Placeholder: {placeholder}")
    print(f"Maxlength: {maxlength}")
    
    # Verificar que el patrón sea el correcto
    expected_pattern = '[0-9]{1,2}(\.[0-9]{3}){1,2}-[0-9kK]{1}'
    if pattern == expected_pattern:
        print("✓ Patrón HTML correcto")
    else:
        print("✗ Patrón HTML incorrecto")
        print(f"Esperado: {expected_pattern}")
        print(f"Actual: {pattern}")

if __name__ == "__main__":
    print("Iniciando pruebas de validación RUT...")
    test_validacion_rut()
    test_form_validation()
    test_pattern_html()
    print("\n¡Pruebas completadas!")
