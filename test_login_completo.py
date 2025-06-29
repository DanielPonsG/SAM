#!/usr/bin/env python
"""
Script para probar completamente el flujo de login y calendario
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

def test_login_completo():
    print("🔐 PROBANDO FLUJO COMPLETO DE LOGIN")
    print("=" * 50)
    
    client = Client()
    
    # Usuarios de prueba
    usuarios_test = [
        {
            'username': 'admin',
            'password': 'admin123',
            'tipo': '🔐 ADMINISTRADOR',
            'esperado_redirect': '/calendario/'
        },
        {
            'username': 'director',
            'password': 'director123',
            'tipo': '🏛️ DIRECTOR',
            'esperado_redirect': '/calendario/'
        },
        {
            'username': 'profesor',
            'password': 'profesor123',
            'tipo': '👨‍🏫 PROFESOR',
            'esperado_redirect': '/'
        },
        {
            'username': 'estudiante',
            'password': 'estudiante123',
            'tipo': '🎓 ESTUDIANTE',
            'esperado_redirect': '/'
        }
    ]
    
    resultados = []
    
    for usuario in usuarios_test:
        print(f"\n🧪 Probando {usuario['tipo']}: {usuario['username']}")
        
        # 1. Probar GET a login
        response = client.get('/login/')
        if response.status_code == 200:
            print("   ✅ Página de login accesible")
        else:
            print(f"   ❌ Error en página login: {response.status_code}")
            continue
        
        # 2. Probar POST de login
        login_data = {
            'username': usuario['username'],
            'password': usuario['password']
        }
        
        response = client.post('/login/', data=login_data, follow=True)
        
        if response.status_code == 200:
            # Verificar si se redirigió correctamente
            if hasattr(response, 'redirect_chain') and response.redirect_chain:
                redirect_url = response.redirect_chain[-1][0]
                print(f"   ✅ Login exitoso, redirigido a: {redirect_url}")
                
                # Verificar que esté logueado
                if '_auth_user_id' in client.session:
                    print("   ✅ Sesión iniciada correctamente")
                    
                    # Probar acceso al calendario
                    calendar_response = client.get('/calendario/')
                    if calendar_response.status_code == 200:
                        print("   ✅ Acceso al calendario exitoso")
                        
                        # Verificar contenido del calendario
                        content = calendar_response.content.decode('utf-8')
                        if 'modalCrearEvento' in content:
                            print("   ✅ Modal de eventos presente")
                        else:
                            print("   ⚠️ Modal de eventos no encontrado")
                            
                        if 'puede_crear_eventos' in content:
                            print("   ✅ Permisos de eventos configurados")
                        else:
                            print("   ⚠️ Permisos de eventos no encontrados")
                            
                        resultados.append({
                            'usuario': usuario['username'],
                            'tipo': usuario['tipo'],
                            'login': True,
                            'calendario': True
                        })
                    else:
                        print(f"   ❌ Error accediendo al calendario: {calendar_response.status_code}")
                        resultados.append({
                            'usuario': usuario['username'],
                            'tipo': usuario['tipo'],
                            'login': True,
                            'calendario': False
                        })
                else:
                    print("   ❌ Sesión no iniciada correctamente")
                    resultados.append({
                        'usuario': usuario['username'],
                        'tipo': usuario['tipo'],
                        'login': False,
                        'calendario': False
                    })
            else:
                print("   ❌ No se produjo redirección después del login")
                resultados.append({
                    'usuario': usuario['username'],
                    'tipo': usuario['tipo'],
                    'login': False,
                    'calendario': False
                })
        else:
            print(f"   ❌ Error en login: {response.status_code}")
            resultados.append({
                'usuario': usuario['username'],
                'tipo': usuario['tipo'],
                'login': False,
                'calendario': False
            })
        
        # Logout para siguiente prueba
        client.logout()
        print("   🚪 Logout realizado")
    
    # Mostrar resumen
    print("\n" + "📊" + "=" * 48 + "📊")
    print("                RESUMEN DE PRUEBAS")
    print("📊" + "=" * 48 + "📊")
    
    login_exitosos = sum(1 for r in resultados if r['login'])
    calendario_exitosos = sum(1 for r in resultados if r['calendario'])
    
    print(f"\n✅ Login exitosos: {login_exitosos}/{len(resultados)}")
    print(f"✅ Calendario accesible: {calendario_exitosos}/{len(resultados)}")
    
    for resultado in resultados:
        login_icon = "✅" if resultado['login'] else "❌"
        calendar_icon = "✅" if resultado['calendario'] else "❌"
        print(f"   {resultado['tipo']}: Login {login_icon} | Calendario {calendar_icon}")
    
    return len(resultados) == login_exitosos == calendario_exitosos

def verificar_credenciales():
    print("\n🔍 VERIFICANDO CREDENCIALES EN BASE DE DATOS")
    print("=" * 50)
    
    usuarios_esperados = ['admin', 'director', 'profesor', 'estudiante']
    
    for username in usuarios_esperados:
        try:
            user = User.objects.get(username=username)
            print(f"✅ {username}: Existe en BD")
            print(f"   - Activo: {'Sí' if user.is_active else 'No'}")
            print(f"   - Email: {user.email}")
            print(f"   - Staff: {'Sí' if user.is_staff else 'No'}")
            print(f"   - Superuser: {'Sí' if user.is_superuser else 'No'}")
            
            # Verificar perfil
            if hasattr(user, 'perfil'):
                print(f"   - Perfil: {user.perfil.tipo_usuario}")
            else:
                print("   - Perfil: No tiene")
            print()
            
        except User.DoesNotExist:
            print(f"❌ {username}: NO EXISTE en BD")

if __name__ == '__main__':
    print("🚀 INICIANDO PRUEBAS COMPLETAS DEL SISTEMA")
    print("=" * 60)
    
    verificar_credenciales()
    
    todo_ok = test_login_completo()
    
    if todo_ok:
        print("\n🎉 " + "=" * 50)
        print("   ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("🎉 " + "=" * 50)
        print("   🌐 Accede a: http://127.0.0.1:8000/login/")
        print("   🔐 Usa cualquier usuario creado")
        print("   📅 Calendario funciona perfectamente")
        print("🎉 " + "=" * 50)
    else:
        print("\n⚠️ " + "=" * 50)
        print("   ALGUNOS PROBLEMAS ENCONTRADOS")
        print("⚠️ " + "=" * 50)
        print("   Revisa los errores mostrados arriba")
        print("   y ejecuta nuevamente los scripts de creación")
        print("⚠️ " + "=" * 50)
