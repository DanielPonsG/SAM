#!/usr/bin/env python
"""
Script para probar la validación del RUT 20.589.644-9
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.forms import validar_rut, formatear_rut

def probar_rut():
    # RUT del usuario: 20.589.644-9
    rut_test = "20.589.644-9"
    
    print(f"=== PRUEBA DE VALIDACIÓN RUT ===")
    print(f"RUT a probar: {rut_test}")
    
    # Probar validación
    es_valido = validar_rut(rut_test)
    print(f"¿Es válido?: {es_valido}")
    
    if es_valido:
        rut_formateado = formatear_rut(rut_test)
        print(f"RUT formateado: {rut_formateado}")
    else:
        # Hacer el cálculo paso a paso para debuggear
        print("\n=== DEBUG MANUAL ===")
        rut_limpio = rut_test.replace(".", "").replace("-", "").upper()
        print(f"RUT limpio: {rut_limpio}")
        
        numero = rut_limpio[:-1]
        dv = rut_limpio[-1]
        print(f"Número: {numero}")
        print(f"DV original: {dv}")
        
        # Calcular dígito verificador
        suma = 0
        multiplicador = 2
        
        for digit in reversed(numero):
            suma += int(digit) * multiplicador
            print(f"Dígito {digit} * {multiplicador} = {int(digit) * multiplicador} (suma: {suma})")
            multiplicador += 1
            if multiplicador > 7:
                multiplicador = 2
        
        resto = suma % 11
        dv_calculado = 11 - resto
        
        print(f"Suma total: {suma}")
        print(f"Resto (suma % 11): {resto}")
        print(f"DV calculado (11 - resto): {dv_calculado}")
        
        if dv_calculado == 11:
            dv_calculado = '0'
        elif dv_calculado == 10:
            dv_calculado = 'K'
        else:
            dv_calculado = str(dv_calculado)
        
        print(f"DV final calculado: {dv_calculado}")
        print(f"¿Coincide?: {dv == dv_calculado}")

if __name__ == "__main__":
    probar_rut()
