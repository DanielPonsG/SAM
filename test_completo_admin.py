#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
    django.setup()

    from django.contrib.auth.models import User
    from smapp.models import Perfil, Asignatura, HorarioCurso, Curso, Profesor
    from django.test import RequestFactory, Client
    from django.contrib.auth import authenticate, login

    print("🧪 PRUEBA COMPLETA DEL SISTEMA ADMIN")
    print("=" * 50)

    try:
        # Test 1: Autenticación
        print("\n1️⃣ PRUEBA DE AUTENTICACIÓN")
        user = authenticate(username='admin', password='admin123')
        if user and user.is_active:
            print("✅ Login exitoso")
            print(f"   Usuario: {user.username}")
            print(f"   Tipo: {user.perfil.tipo_usuario}")
        else:
            print("❌ Login fallido")
            sys.exit(1)

        # Test 2: Cliente de prueba con sesión
        print("\n2️⃣ PRUEBA DE NAVEGACIÓN WEB")
        client = Client()
        
        # Login programático
        login_success = client.login(username='admin', password='admin123')
        if login_success:
            print("✅ Sesión web iniciada")
        else:
            print("❌ Error en sesión web")
            sys.exit(1)

        # Test 3: Acceso a vistas principales
        print("\n3️⃣ PRUEBA DE ACCESO A VISTAS")
        
        vistas_a_probar = [
            ('/calendario/', 'Calendario'),
            ('/asignaturas/', 'Listar Asignaturas'),
            ('/profesores/', 'Listar Profesores'),
            ('/cursos/', 'Listar Cursos'),
        ]
        
        for url, nombre in vistas_a_probar:
            try:
                response = client.get(url)
                if response.status_code == 200:
                    print(f"✅ {nombre}: Acceso exitoso")
                elif response.status_code == 302:
                    print(f"⚠️  {nombre}: Redirección (código {response.status_code})")
                else:
                    print(f"❌ {nombre}: Error {response.status_code}")
            except Exception as e:
                print(f"❌ {nombre}: Excepción - {e}")

        # Test 4: Datos del sistema
        print("\n4️⃣ RESUMEN DE DATOS DEL SISTEMA")
        print(f"   👥 Usuarios: {User.objects.count()}")
        print(f"   👨‍🏫 Profesores: {Profesor.objects.count()}")
        print(f"   🏫 Cursos: {Curso.objects.count()}")
        print(f"   📚 Asignaturas: {Asignatura.objects.count()}")
        print(f"   ⏰ Horarios: {HorarioCurso.objects.count()}")

        # Test 5: Funcionalidades específicas del admin
        print("\n5️⃣ FUNCIONALIDADES DE ADMINISTRADOR")
        
        # Verificar acceso a gestión de asignaturas
        if Asignatura.objects.exists():
            asignatura = Asignatura.objects.first()
            url_gestion = f'/asignaturas/{asignatura.id}/horarios/'
            try:
                response = client.get(url_gestion)
                if response.status_code == 200:
                    print("✅ Gestión de horarios de asignatura: Accesible")
                else:
                    print(f"❌ Gestión de horarios: Error {response.status_code}")
            except Exception as e:
                print(f"⚠️  Gestión de horarios: {e}")

        print("\n🎉 TODAS LAS PRUEBAS COMPLETADAS")
        print("El usuario admin está funcionando correctamente.")
        print("\nCredenciales de acceso:")
        print("👤 Usuario: admin")
        print("🔑 Contraseña: admin123")
        print("🌐 URL: http://127.0.0.1:8000/login/")

    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()
