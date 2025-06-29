#!/usr/bin/env python
"""
Script para limpiar y crear usuarios únicos
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Profesor, Estudiante, Perfil, Curso, Asignatura
from datetime import date

def limpiar_y_crear_usuarios():
    print("🧹 LIMPIANDO Y CREANDO USUARIOS ÚNICOS")
    print("=" * 50)
    
    # Limpiar usuarios existentes
    print("🗑️ Limpiando usuarios existentes...")
    
    usuarios_limpiar = ['admin', 'director', 'profesor', 'estudiante']
    for username in usuarios_limpiar:
        try:
            user = User.objects.filter(username=username).first()
            if user:
                # Limpiar perfil asociado
                Perfil.objects.filter(user=user).delete()
                # Limpiar profesor/estudiante asociado
                if hasattr(user, 'profesor'):
                    user.profesor.delete()
                if hasattr(user, 'estudiante'):
                    user.estudiante.delete()
                # Eliminar usuario
                user.delete()
                print(f"   ✅ Usuario {username} eliminado")
        except Exception as e:
            print(f"   ⚠️ Error limpiando {username}: {e}")
    
    # Limpiar profesores y estudiantes huérfanos
    try:
        Profesor.objects.filter(user__isnull=True).delete()
        Estudiante.objects.filter(user__isnull=True).delete()
        print("   ✅ Registros huérfanos eliminados")
    except Exception as e:
        print(f"   ⚠️ Error limpiando huérfanos: {e}")
    
    usuarios_creados = []
    
    # 1. CREAR ADMINISTRADOR
    print("\n🔐 1. CREANDO ADMINISTRADOR")
    try:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@sma.edu',
            password='admin123',
            first_name='Administrador',
            last_name='Sistema'
        )
        
        perfil_admin = Perfil.objects.create(
            user=admin_user,
            tipo_usuario='director'
        )
        
        usuarios_creados.append({
            'tipo': '🔐 ADMINISTRADOR',
            'username': 'admin',
            'password': 'admin123',
            'permisos': 'Acceso completo al sistema'
        })
        
        print("   ✅ Administrador creado")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. CREAR DIRECTOR
    print("\n🏛️ 2. CREANDO DIRECTOR")
    try:
        director_user = User.objects.create_user(
            username='director',
            email='director@sma.edu',
            password='director123',
            first_name='María',
            last_name='González'
        )
        director_user.is_staff = True
        director_user.save()
        
        perfil_director = Perfil.objects.create(
            user=director_user,
            tipo_usuario='director'
        )
        
        usuarios_creados.append({
            'tipo': '🏛️ DIRECTOR',
            'username': 'director',
            'password': 'director123',
            'permisos': 'Gestión académica completa'
        })
        
        print("   ✅ Director creado")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. CREAR PROFESOR
    print("\n👨‍🏫 3. CREANDO PROFESOR")
    try:
        profesor_user = User.objects.create_user(
            username='profesor',
            email='profesor@sma.edu',
            password='profesor123',
            first_name='Carlos',
            last_name='Rodríguez'
        )
        
        profesor = Profesor.objects.create(
            user=profesor_user,
            primer_nombre='Carlos',
            segundo_nombre='Alberto',
            apellido_paterno='Rodríguez',
            apellido_materno='Silva',
            tipo_documento='CC',
            numero_documento='87654321-0',  # RUT único
            fecha_nacimiento=date(1980, 5, 15),
            genero='M',
            direccion='Calle Profesores 123',
            telefono='+56912345678',
            email='profesor@sma.edu',
            codigo_profesor='PROF2025',  # Código único
            especialidad='Matemáticas y Ciencias'
        )
        
        perfil_profesor = Perfil.objects.create(
            user=profesor_user,
            tipo_usuario='profesor'
        )
        
        usuarios_creados.append({
            'tipo': '👨‍🏫 PROFESOR',
            'username': 'profesor',
            'password': 'profesor123',
            'permisos': 'Gestión de cursos asignados'
        })
        
        print("   ✅ Profesor creado")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. CREAR ESTUDIANTE
    print("\n🎓 4. CREANDO ESTUDIANTE")
    try:
        estudiante_user = User.objects.create_user(
            username='estudiante',
            email='estudiante@sma.edu',
            password='estudiante123',
            first_name='Ana',
            last_name='Pérez'
        )
        
        estudiante = Estudiante.objects.create(
            user=estudiante_user,
            primer_nombre='Ana',
            segundo_nombre='Isabel',
            apellido_paterno='Pérez',
            apellido_materno='López',
            tipo_documento='CC',
            numero_documento='12345678-K',  # RUT único
            fecha_nacimiento=date(2005, 8, 20),
            genero='F',
            direccion='Avenida Estudiantes 456',
            telefono='+56987654321',
            email='estudiante@sma.edu',
            codigo_estudiante='EST2025'  # Código único
        )
        
        perfil_estudiante = Perfil.objects.create(
            user=estudiante_user,
            tipo_usuario='alumno'
        )
        
        usuarios_creados.append({
            'tipo': '🎓 ESTUDIANTE',
            'username': 'estudiante',
            'password': 'estudiante123',
            'permisos': 'Visualización de información académica'
        })
        
        print("   ✅ Estudiante creado")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # MOSTRAR CREDENCIALES
    print("\n" + "🎉" + "=" * 60 + "🎉")
    print("              USUARIOS CREADOS EXITOSAMENTE")
    print("🎉" + "=" * 60 + "🎉")
    
    for i, usuario in enumerate(usuarios_creados, 1):
        print(f"\n{i}. {usuario['tipo']}")
        print(f"   👤 Usuario: {usuario['username']}")
        print(f"   🔐 Contraseña: {usuario['password']}")
        print(f"   🎯 Permisos: {usuario['permisos']}")
    
    print(f"\n📊 TOTAL: {len(usuarios_creados)} usuarios creados")
    
    return usuarios_creados

def probar_login():
    print("\n🧪 PROBANDO LOGIN DE USUARIOS")
    print("=" * 40)
    
    from django.contrib.auth import authenticate
    
    usuarios_test = [
        ('admin', 'admin123'),
        ('director', 'director123'),  
        ('profesor', 'profesor123'),
        ('estudiante', 'estudiante123')
    ]
    
    usuarios_ok = 0
    
    for username, password in usuarios_test:
        try:
            user = authenticate(username=username, password=password)
            if user and user.is_active:
                print(f"✅ {username}: Login exitoso")
                usuarios_ok += 1
            else:
                print(f"❌ {username}: Login falló")
        except Exception as e:
            print(f"❌ {username}: Error - {e}")
    
    print(f"\n📊 Resultado: {usuarios_ok}/{len(usuarios_test)} usuarios funcionando")
    return usuarios_ok == len(usuarios_test)

if __name__ == '__main__':
    usuarios = limpiar_y_crear_usuarios()
    
    if usuarios:
        login_ok = probar_login()
        
        print("\n🌐 " + "=" * 50)
        print("        INSTRUCCIONES DE USO")
        print("🌐 " + "=" * 50)
        print("1. 🌐 Ve a: http://127.0.0.1:8000/login/")
        print("2. 🔐 Usa cualquier usuario de la lista")
        print("3. 📅 Después del login: http://127.0.0.1:8000/calendario/")
        print("4. ➕ Administrador y Director pueden crear eventos")
        print("5. 👨‍🏫 Profesor puede crear eventos para sus cursos")
        print("6. 🎓 Estudiante solo puede ver eventos")
        
        if login_ok:
            print("\n✅ SISTEMA COMPLETAMENTE FUNCIONAL")
        else:
            print("\n⚠️ Algunos usuarios pueden tener problemas")
    else:
        print("\n❌ No se crearon usuarios correctamente")
