#!/usr/bin/env python
"""
Script para probar el modal del calendario y verificar la funcionalidad
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from smapp.models import Estudiante, Curso, Profesor
from django.urls import reverse
import json

def test_modal_calendar():
    print("🔍 PROBANDO MODAL DEL CALENDARIO")
    print("=" * 50)
    
    # Crear cliente de prueba
    client = Client()
    
    # Verificar usuarios existentes
    users = User.objects.all()
    print(f"👥 Usuarios disponibles: {users.count()}")
    for user in users:
        print(f"   - {user.username} ({user.first_name} {user.last_name})")
    
    if not users.exists():
        print("❌ No hay usuarios. Creando uno de prueba...")
        user = User.objects.create_user('admin', 'admin@test.com', 'admin123')
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"✅ Usuario admin creado")
    
    # Login con el primer usuario disponible (o el recién creado)
    user = users.first() if users.exists() else User.objects.get(username='admin')
    client.force_login(user)
    print(f"🔐 Logueado como: {user.username}")
    
    # Obtener la vista del calendario
    try:
        response = client.get(reverse('calendario'))
        print(f"📅 Status de respuesta del calendario: {response.status_code}")
        
        if response.status_code == 200:
            # Verificar contenido del contexto
            context = response.context
            print(f"🎯 Contexto disponible:")
            
            if context:
                for key in context.keys():
                    if key in ['cursos', 'puede_crear_eventos', 'user_type', 'tipos_evento', 'prioridades']:
                        value = context[key]
                        if hasattr(value, '__len__') and not isinstance(value, str):
                            print(f"   - {key}: {len(value)} elementos")
                        else:
                            print(f"   - {key}: {value}")
                
                # Verificar cursos específicamente
                cursos = context.get('cursos', [])
                print(f"\n📚 CURSOS DISPONIBLES: {len(cursos)}")
                for i, curso in enumerate(cursos):
                    print(f"   {i+1}. {curso} (ID: {curso.id})")
                    if hasattr(curso, 'profesor_jefe') and curso.profesor_jefe:
                        print(f"      Profesor jefe: {curso.profesor_jefe}")
            else:
                print("❌ Contexto no disponible")
            
            # Buscar elementos específicos en el HTML
            content = response.content.decode('utf-8')
            
            # Buscar modal
            if 'modalCrearEvento' in content:
                print("✅ Modal de crear evento encontrado en HTML")
            else:
                print("❌ Modal de crear evento NO encontrado")
            
            # Buscar checkboxes de cursos
            checkbox_count = content.count('name="cursos_especificos"')
            print(f"📋 Checkboxes de cursos en HTML: {checkbox_count}")
            
            # Buscar JavaScript de validación
            if 'function validarHoras' in content:
                print("✅ Función validarHoras encontrada")
            else:
                print("❌ Función validarHoras NO encontrada")
            
            if 'dirigido_especificos' in content:
                print("✅ Radio button para cursos específicos encontrado")
            else:
                print("❌ Radio button para cursos específicos NO encontrado")
                
            # Buscar elementos de validación de horas
            if 'error_hora_inicio' in content:
                print("✅ Elementos de error de horas encontrados")
            else:
                print("❌ Elementos de error de horas NO encontrados")
        
        else:
            print(f"❌ Error en respuesta: {response.status_code}")
            if hasattr(response, 'content'):
                print(f"Contenido: {response.content[:500]}")
                
    except Exception as e:
        print(f"❌ Error al obtener calendario: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🔚 FIN DE LA PRUEBA")

if __name__ == "__main__":
    test_modal_calendar()
