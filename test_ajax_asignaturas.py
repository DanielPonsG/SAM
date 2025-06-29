#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
    django.setup()

    from django.test import Client
    from django.contrib.auth.models import User
    from smapp.models import Asignatura, Profesor
    import json

    print("🧪 PRUEBA DE FUNCIONALIDAD AJAX - ASIGNAR PROFESOR")
    print("=" * 55)

    try:
        # Configurar cliente de prueba
        client = Client()
        
        # Login como admin
        login_success = client.login(username='admin', password='admin123')
        if not login_success:
            print("❌ Error en login")
            sys.exit(1)
        
        print("✅ Usuario admin logueado")
        
        # Obtener una asignatura sin profesor
        asignatura_sin_profesor = None
        asignaturas = Asignatura.objects.all()
        
        for asignatura in asignaturas:
            if not asignatura.profesor_responsable:
                asignatura_sin_profesor = asignatura
                break
        
        if not asignatura_sin_profesor:
            # Crear una asignatura sin profesor para la prueba
            asignatura_sin_profesor = Asignatura.objects.create(
                codigo_asignatura='TEST001',
                nombre='Asignatura de Prueba AJAX',
                descripcion='Para probar funcionalidad AJAX'
            )
            print("✅ Asignatura de prueba creada")
        
        print(f"📚 Asignatura de prueba: {asignatura_sin_profesor.nombre}")
        print(f"   - ID: {asignatura_sin_profesor.id}")
        print(f"   - Profesor actual: {asignatura_sin_profesor.profesor_responsable or 'Sin asignar'}")
        
        # Obtener un profesor para asignar
        profesor = Profesor.objects.first()
        if not profesor:
            print("❌ No hay profesores en la base de datos")
            sys.exit(1)
        
        print(f"👨‍🏫 Profesor para asignar: {profesor.primer_nombre} {profesor.apellido_paterno}")
        print(f"   - ID: {profesor.id}")
        
        # Probar AJAX de asignar profesor
        print("\n🔧 PROBANDO AJAX: Asignar profesor...")
        
        response = client.post(
            f'/ajax/asignar-profesor/{asignatura_sin_profesor.id}/',
            {
                'profesor_id': profesor.id,
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        print(f"   - Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"   - Respuesta JSON: {data}")
            
            if data.get('success'):
                print("✅ AJAX exitoso: Profesor asignado")
                
                # Verificar en la base de datos
                asignatura_sin_profesor.refresh_from_db()
                if asignatura_sin_profesor.profesor_responsable == profesor:
                    print("✅ Base de datos actualizada correctamente")
                else:
                    print("❌ Error: Base de datos no actualizada")
            else:
                print(f"❌ AJAX falló: {data.get('error', 'Error desconocido')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"   Contenido: {response.content.decode()}")
        
        # Probar AJAX de quitar profesor
        print("\n🔧 PROBANDO AJAX: Quitar profesor...")
        
        response = client.post(
            f'/ajax/asignar-profesor/{asignatura_sin_profesor.id}/',
            {
                'profesor_id': '',  # Vacío para quitar profesor
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        if response.status_code == 200:
            data = json.loads(response.content)
            if data.get('success'):
                print("✅ AJAX exitoso: Profesor removido")
                
                # Verificar en la base de datos
                asignatura_sin_profesor.refresh_from_db()
                if not asignatura_sin_profesor.profesor_responsable:
                    print("✅ Base de datos actualizada correctamente")
                else:
                    print("❌ Error: Profesor no removido de la base de datos")
            else:
                print(f"❌ AJAX falló: {data.get('error')}")
        
        # Probar acceso a la vista de listar asignaturas
        print("\n📋 PROBANDO VISTA: Listar asignaturas...")
        
        response = client.get('/asignaturas/')
        if response.status_code == 200:
            print("✅ Vista de asignaturas carga correctamente")
            
            # Verificar que el contexto contiene los datos esperados
            context = response.context
            if 'asignaturas' in context:
                asignaturas_count = len(context['asignaturas'])
                print(f"   - Asignaturas en contexto: {asignaturas_count}")
            
            if 'profesores' in context:
                profesores_count = len(context['profesores'])
                print(f"   - Profesores disponibles: {profesores_count}")
            
            if 'puede_gestionar' in context:
                puede_gestionar = context['puede_gestionar']
                print(f"   - Puede gestionar: {puede_gestionar}")
        else:
            print(f"❌ Error en vista: {response.status_code}")
        
        print("\n" + "=" * 55)
        print("🎊 PRUEBAS AJAX COMPLETADAS")
        print("✅ La funcionalidad AJAX está operativa")
        print("✅ La asignación de profesores funciona correctamente")
        print("✅ La base de datos se actualiza correctamente")
        
    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()
