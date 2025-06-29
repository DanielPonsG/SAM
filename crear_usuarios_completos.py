#!/usr/bin/env python
"""
Script para crear usuarios completos del sistema: admin, director, profesor y alumno
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

def crear_usuarios_completos():
    print("👥 CREANDO USUARIOS COMPLETOS DEL SISTEMA")
    print("=" * 60)
    
    usuarios_creados = []
    
    # 1. CREAR ADMINISTRADOR
    print("\n🔐 1. CREANDO USUARIO ADMINISTRADOR")
    try:
        # Eliminar admin existente si existe
        User.objects.filter(username='admin').delete()
        
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@sma.edu',
            password='admin123',
            first_name='Administrador',
            last_name='Sistema'
        )
        
        # Crear perfil de administrador
        perfil_admin, created = Perfil.objects.get_or_create(
            user=admin_user,
            defaults={'tipo_usuario': 'director'}  # Administrador como director
        )
        
        usuarios_creados.append({
            'tipo': 'Administrador',
            'username': 'admin',
            'password': 'admin123',
            'email': 'admin@sma.edu'
        })
        
        print("   ✅ Administrador creado exitosamente")
        
    except Exception as e:
        print(f"   ❌ Error creando administrador: {e}")
    
    # 2. CREAR DIRECTOR
    print("\n🏛️ 2. CREANDO USUARIO DIRECTOR")
    try:
        # Eliminar director existente si existe
        User.objects.filter(username='director').delete()
        
        director_user = User.objects.create_user(
            username='director',
            email='director@sma.edu',
            password='director123',
            first_name='María',
            last_name='González'
        )
        director_user.is_staff = True  # Dar permisos de staff
        director_user.save()
        
        # Crear perfil de director
        perfil_director, created = Perfil.objects.get_or_create(
            user=director_user,
            defaults={'tipo_usuario': 'director'}
        )
        
        usuarios_creados.append({
            'tipo': 'Director',
            'username': 'director',
            'password': 'director123',
            'email': 'director@sma.edu'
        })
        
        print("   ✅ Director creado exitosamente")
        
    except Exception as e:
        print(f"   ❌ Error creando director: {e}")
    
    # 3. CREAR PROFESOR
    print("\n👨‍🏫 3. CREANDO USUARIO PROFESOR")
    try:
        # Eliminar profesor existente si existe
        User.objects.filter(username='profesor').delete()
        Profesor.objects.filter(numero_documento='12345678-9').delete()
        
        profesor_user = User.objects.create_user(
            username='profesor',
            email='profesor@sma.edu',
            password='profesor123',
            first_name='Carlos',
            last_name='Rodríguez'
        )
        
        # Crear instancia de Profesor
        profesor = Profesor.objects.create(
            user=profesor_user,
            primer_nombre='Carlos',
            segundo_nombre='Alberto',
            apellido_paterno='Rodríguez',
            apellido_materno='Silva',
            tipo_documento='CC',
            numero_documento='12345678-9',
            fecha_nacimiento=date(1980, 5, 15),
            genero='M',
            direccion='Calle 123 #45-67',
            telefono='+56912345678',
            email='profesor@sma.edu',
            codigo_profesor='PROF001',
            especialidad='Matemáticas'
        )
        
        # Crear perfil de profesor
        perfil_profesor, created = Perfil.objects.get_or_create(
            user=profesor_user,
            defaults={'tipo_usuario': 'profesor'}
        )
        
        # Asignar asignaturas al profesor
        try:
            matematicas, created = Asignatura.objects.get_or_create(
                codigo_asignatura='MAT001',
                defaults={
                    'nombre': 'Matemáticas',
                    'descripcion': 'Matemáticas básicas y avanzadas',
                    'profesor_responsable': profesor
                }
            )
            profesor.asignaturas.add(matematicas)
        except Exception as e:
            print(f"   ⚠️ No se pudo asignar asignatura: {e}")
        
        usuarios_creados.append({
            'tipo': 'Profesor',
            'username': 'profesor',
            'password': 'profesor123',
            'email': 'profesor@sma.edu'
        })
        
        print("   ✅ Profesor creado exitosamente")
        
    except Exception as e:
        print(f"   ❌ Error creando profesor: {e}")
    
    # 4. CREAR ESTUDIANTE
    print("\n🎓 4. CREANDO USUARIO ESTUDIANTE")
    try:
        # Eliminar estudiante existente si existe
        User.objects.filter(username='estudiante').delete()
        Estudiante.objects.filter(numero_documento='98765432-1').delete()
        
        estudiante_user = User.objects.create_user(
            username='estudiante',
            email='estudiante@sma.edu',
            password='estudiante123',
            first_name='Ana',
            last_name='Pérez'
        )
        
        # Crear instancia de Estudiante
        estudiante = Estudiante.objects.create(
            user=estudiante_user,
            primer_nombre='Ana',
            segundo_nombre='Isabel',
            apellido_paterno='Pérez',
            apellido_materno='López',
            tipo_documento='CC',
            numero_documento='98765432-1',
            fecha_nacimiento=date(2005, 8, 20),
            genero='F',
            direccion='Avenida 456 #78-90',
            telefono='+56987654321',
            email='estudiante@sma.edu',
            codigo_estudiante='EST001'
        )
        
        # Crear perfil de estudiante
        perfil_estudiante, created = Perfil.objects.get_or_create(
            user=estudiante_user,
            defaults={'tipo_usuario': 'alumno'}
        )
        
        # Asignar estudiante a un curso si existe
        try:
            curso = Curso.objects.first()
            if curso:
                estudiante.cursos.add(curso)
                print(f"   📚 Estudiante asignado al curso: {curso}")
        except Exception as e:
            print(f"   ⚠️ No se pudo asignar curso: {e}")
        
        usuarios_creados.append({
            'tipo': 'Estudiante',
            'username': 'estudiante',
            'password': 'estudiante123',
            'email': 'estudiante@sma.edu'
        })
        
        print("   ✅ Estudiante creado exitosamente")
        
    except Exception as e:
        print(f"   ❌ Error creando estudiante: {e}")
    
    # MOSTRAR RESUMEN
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE USUARIOS CREADOS")
    print("=" * 60)
    
    for usuario in usuarios_creados:
        print(f"\n🔹 {usuario['tipo'].upper()}:")
        print(f"   Usuario: {usuario['username']}")
        print(f"   Contraseña: {usuario['password']}")
        print(f"   Email: {usuario['email']}")
    
    print("\n🌐 INSTRUCCIONES DE LOGIN:")
    print("1. Ve a: http://127.0.0.1:8000/login/")
    print("2. Usa cualquiera de las credenciales mostradas arriba")
    print("3. Después del login, ve a: http://127.0.0.1:8000/calendario/")
    
    print("\n🎯 RECOMENDACIONES POR TIPO DE USUARIO:")
    print("• ADMINISTRADOR/DIRECTOR: Acceso completo, puede crear eventos para todos los cursos")
    print("• PROFESOR: Puede crear eventos para sus cursos asignados")
    print("• ESTUDIANTE: Solo puede ver eventos de sus cursos")
    
    return len(usuarios_creados)

def verificar_login_sistema():
    print("\n🔍 VERIFICANDO SISTEMA DE LOGIN")
    print("=" * 40)
    
    # Verificar vista de login
    try:
        from smapp.views import login_view
        print("✅ Vista de login encontrada")
    except ImportError:
        print("❌ Vista de login no encontrada")
    
    # Verificar template de login
    import os
    login_template = os.path.join('templates', 'login.html')
    if os.path.exists(login_template):
        print("✅ Template de login encontrado")
    else:
        print("❌ Template de login no encontrado")
    
    # Verificar configuración de URLs
    try:
        from sma.urls import urlpatterns
        login_urls = [url for url in urlpatterns if 'login' in str(url.pattern)]
        if login_urls:
            print("✅ URLs de login configuradas")
        else:
            print("❌ URLs de login no configuradas")
    except Exception as e:
        print(f"⚠️ Error verificando URLs: {e}")

def test_login_usuarios():
    print("\n🧪 PROBANDO LOGIN DE USUARIOS")
    print("=" * 40)
    
    from django.test import Client
    from django.contrib.auth import authenticate
    
    client = Client()
    usuarios_test = [
        ('admin', 'admin123'),
        ('director', 'director123'),
        ('profesor', 'profesor123'),
        ('estudiante', 'estudiante123')
    ]
    
    for username, password in usuarios_test:
        try:
            # Test authentication
            user = authenticate(username=username, password=password)
            if user:
                print(f"✅ {username}: Autenticación exitosa")
                
                # Test login via client
                login_success = client.login(username=username, password=password)
                if login_success:
                    print(f"   ✅ Login web exitoso")
                else:
                    print(f"   ❌ Login web falló")
                
                client.logout()
            else:
                print(f"❌ {username}: Fallo en autenticación")
                
        except Exception as e:
            print(f"❌ {username}: Error - {e}")

if __name__ == '__main__':
    usuarios_creados = crear_usuarios_completos()
    
    if usuarios_creados > 0:
        verificar_login_sistema()
        test_login_usuarios()
        
        print("\n🎉 " + "=" * 50)
        print("   SISTEMA LISTO PARA USAR")
        print("🎉 " + "=" * 50)
        print("   URL: http://127.0.0.1:8000/login/")
        print("   Usa cualquier usuario creado arriba")
        print("🎉 " + "=" * 50)
    else:
        print("\n❌ No se crearon usuarios. Revisa los errores arriba.")
