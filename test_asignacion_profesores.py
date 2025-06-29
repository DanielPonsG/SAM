#!/usr/bin/env python3
"""
Script para probar la funcionalidad de asignación de profesores a asignaturas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Profesor, Asignatura, Perfil
from django.test import Client
from django.urls import reverse
import json

def verificar_datos():
    """Verificar que tenemos datos para probar"""
    print("=== VERIFICANDO DATOS DISPONIBLES ===")
    
    # Verificar usuarios administradores
    admin_users = User.objects.filter(is_superuser=True)
    perfil_admins = Perfil.objects.filter(tipo_usuario='administrador')
    
    print(f"Usuarios superuser: {admin_users.count()}")
    print(f"Perfiles administrador: {perfil_admins.count()}")
    
    if admin_users.exists():
        admin_user = admin_users.first()
        print(f"Admin user: {admin_user.username}")
    elif perfil_admins.exists():
        admin_user = perfil_admins.first().user
        print(f"Admin user from perfil: {admin_user.username}")
    else:
        print("ERROR: No hay usuarios administradores")
        return None, None, None
    
    # Verificar profesores
    profesores = Profesor.objects.all()
    print(f"Profesores disponibles: {profesores.count()}")
    for prof in profesores[:3]:
        print(f"  - {prof.get_nombre_completo()} (ID: {prof.id})")
    
    # Verificar asignaturas
    asignaturas = Asignatura.objects.all()
    print(f"Asignaturas disponibles: {asignaturas.count()}")
    for asig in asignaturas[:3]:
        profesores_actuales = asig.get_profesores_display()
        print(f"  - {asig.nombre} (ID: {asig.id})")
        if profesores_actuales:
            print(f"    Profesores: {[p.get_nombre_completo() for p in profesores_actuales]}")
        else:
            print(f"    Sin profesores asignados")
    
    if not profesores.exists() or not asignaturas.exists():
        print("ERROR: Faltan profesores o asignaturas para probar")
        return None, None, None
        
    return admin_user, profesores.first(), asignaturas.first()

def probar_asignacion_profesor():
    """Probar la asignación de profesor a asignatura"""
    print("\n=== PROBANDO ASIGNACIÓN DE PROFESOR ===")
    
    admin_user, profesor, asignatura = verificar_datos()
    if not all([admin_user, profesor, asignatura]):
        return False
        
    # Crear cliente de prueba
    client = Client()
    
    # Iniciar sesión como administrador
    login_success = client.login(username=admin_user.username, password='admin123')
    if not login_success:
        # Intentar con diferentes contraseñas comunes
        passwords = ['admin', '123456', 'password', 'adminadmin']
        for pwd in passwords:
            if client.login(username=admin_user.username, password=pwd):
                login_success = True
                print(f"Login exitoso con password: {pwd}")
                break
    
    if not login_success:
        print(f"ERROR: No se pudo hacer login con usuario {admin_user.username}")
        return False
    
    print(f"Login exitoso como: {admin_user.username}")
    
    # Estado inicial
    profesores_iniciales = list(asignatura.get_profesores_display())
    print(f"Profesores iniciales en {asignatura.nombre}: {[p.get_nombre_completo() for p in profesores_iniciales]}")
    
    # Intentar asignar profesor
    print(f"\nAsignando profesor {profesor.get_nombre_completo()} a {asignatura.nombre}...")
    
    data = {
        'asignar_profesor': '1',
        'asignatura_id': asignatura.id,
        'profesor_id': profesor.id,
    }
    
    response = client.post(reverse('listar_asignaturas'), data)
    
    print(f"Status code: {response.status_code}")
    if hasattr(response, 'url'):
        print(f"Redirect URL: {response.url}")
    
    # Verificar resultado
    asignatura.refresh_from_db()
    profesores_finales = list(asignatura.get_profesores_display())
    print(f"Profesores finales en {asignatura.nombre}: {[p.get_nombre_completo() for p in profesores_finales]}")
    
    # Verificar si el profesor fue asignado
    profesor_asignado = profesor in profesores_finales
    print(f"¿Profesor asignado correctamente? {profesor_asignado}")
    
    return profesor_asignado

def probar_remocion_profesor():
    """Probar la remoción de profesor de asignatura"""
    print("\n=== PROBANDO REMOCIÓN DE PROFESOR ===")
    
    admin_user, profesor, asignatura = verificar_datos()
    if not all([admin_user, profesor, asignatura]):
        return False
        
    # Asegurar que el profesor esté asignado primero
    asignatura.profesores_responsables.add(profesor)
    
    # Crear cliente de prueba
    client = Client()
    
    # Iniciar sesión
    login_success = client.login(username=admin_user.username, password='admin123')
    if not login_success:
        passwords = ['admin', '123456', 'password', 'adminadmin']
        for pwd in passwords:
            if client.login(username=admin_user.username, password=pwd):
                login_success = True
                break
    
    if not login_success:
        print(f"ERROR: No se pudo hacer login")
        return False
    
    # Estado inicial
    profesores_iniciales = list(asignatura.get_profesores_display())
    print(f"Profesores iniciales en {asignatura.nombre}: {[p.get_nombre_completo() for p in profesores_iniciales]}")
    
    # Intentar remover profesor
    print(f"\nRemoviendo profesor {profesor.get_nombre_completo()} de {asignatura.nombre}...")
    
    data = {
        'remover_profesor': '1',
        'asignatura_id': asignatura.id,
        'profesor_id': profesor.id,
    }
    
    response = client.post(reverse('listar_asignaturas'), data)
    
    print(f"Status code: {response.status_code}")
    
    # Verificar resultado
    asignatura.refresh_from_db()
    profesores_finales = list(asignatura.get_profesores_display())
    print(f"Profesores finales en {asignatura.nombre}: {[p.get_nombre_completo() for p in profesores_finales]}")
    
    # Verificar si el profesor fue removido
    profesor_removido = profesor not in profesores_finales
    print(f"¿Profesor removido correctamente? {profesor_removido}")
    
    return profesor_removido

def probar_vista_listar():
    """Probar que la vista listar_asignaturas funciona correctamente"""
    print("\n=== PROBANDO VISTA LISTAR ASIGNATURAS ===")
    
    admin_user, profesor, asignatura = verificar_datos()
    if not all([admin_user, profesor, asignatura]):
        return False
        
    # Crear cliente de prueba
    client = Client()
    
    # Iniciar sesión
    login_success = client.login(username=admin_user.username, password='admin123')
    if not login_success:
        passwords = ['admin', '123456', 'password', 'adminadmin']
        for pwd in passwords:
            if client.login(username=admin_user.username, password=pwd):
                login_success = True
                break
    
    if not login_success:
        print(f"ERROR: No se pudo hacer login")
        return False
    
    # Hacer GET request
    response = client.get(reverse('listar_asignaturas'))
    
    print(f"Status code: {response.status_code}")
    print(f"Template used: {[t.name for t in response.templates] if hasattr(response, 'templates') else 'N/A'}")
    
    # Verificar contexto
    if hasattr(response, 'context') and response.context:
        context = response.context
        print(f"Asignaturas en contexto: {len(context.get('asignaturas', []))}")
        print(f"Profesores en contexto: {len(context.get('profesores', []))}")
        print(f"Puede editar: {context.get('puede_editar', False)}")
        print(f"Tipo usuario: {context.get('tipo_usuario', 'N/A')}")
        
        # Verificar estadísticas
        print(f"Total asignaturas: {context.get('total_asignaturas', 0)}")
        print(f"Con profesor: {context.get('asignaturas_con_profesor', 0)}")
        print(f"Sin profesor: {context.get('asignaturas_sin_profesor_count', 0)}")
    else:
        print("No hay contexto disponible o es None")
    return response.status_code == 200

def main():
    print("TESTING: Funcionalidad de Asignación de Profesores")
    print("=" * 50)
    
    resultados = {
        'vista_lista': probar_vista_listar(),
        'asignacion': probar_asignacion_profesor(),
        'remocion': probar_remocion_profesor(),
    }
    
    print("\n" + "=" * 50)
    print("RESUMEN DE RESULTADOS:")
    for test, resultado in resultados.items():
        status = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"  {test}: {status}")
    
    all_passed = all(resultados.values())
    print(f"\nRESULTADO GENERAL: {'✅ TODOS LOS TESTS PASARON' if all_passed else '❌ ALGUNOS TESTS FALLARON'}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
