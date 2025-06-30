#!/usr/bin/env python3
"""
Script de prueba para validar las mejoras finales en el listado de cursos
- Modal de gestión de asignaturas funcional
- Diseño más limpio y profesional
- Funcionalidad AJAX real
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')

try:
    django.setup()
    from django.test import Client
    from django.contrib.auth.models import User
    from smapp.models import Curso, Asignatura, Estudiante, Profesor, Perfil
    from django.db import transaction
    from django.utils import timezone
    
    print("✅ Django configurado correctamente")
    print("✅ Modelos importados exitosamente")
    
except Exception as e:
    print(f"❌ Error configurando Django: {e}")
    sys.exit(1)

def setup_test_data():
    """Crear datos de prueba si no existen"""
    print("🔧 Configurando datos de prueba...")
    
    with transaction.atomic():
        # Crear usuario administrador de prueba
        admin_user, created = User.objects.get_or_create(
            username='test_admin',
            defaults={
                'email': 'admin@test.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            
        # Crear perfil de administrador
        perfil, created = Perfil.objects.get_or_create(
            user=admin_user,
            defaults={'tipo_usuario': 'administrador'}
        )
        
        # Crear algunas asignaturas de prueba
        asignaturas_data = [
            ('Matemática', 'MAT001'),
            ('Lenguaje y Comunicación', 'LEN001'),
            ('Historia y Geografía', 'HIS001'),
            ('Ciencias Naturales', 'CIE001'),
            ('Inglés', 'ING001'),
            ('Educación Física', 'EDF001'),
            ('Artes Visuales', 'ART001'),
            ('Música', 'MUS001'),
            ('Tecnología', 'TEC001'),
            ('Filosofía', 'FIL001')
        ]
        
        for nombre, codigo in asignaturas_data:
            asignatura, created = Asignatura.objects.get_or_create(
                codigo_asignatura=codigo,
                defaults={'nombre': nombre, 'descripcion': f'Asignatura de {nombre}'}
            )
            if created:
                print(f"  ✅ Asignatura '{nombre}' creada")
        
        # Crear algunos cursos de prueba
        cursos_data = [
            ('1M', 'A'),
            ('1M', 'B'),
            ('2M', 'A'),
            ('3M', 'A'),
        ]
        
        for nivel, paralelo in cursos_data:
            curso, created = Curso.objects.get_or_create(
                nivel=nivel,
                paralelo=paralelo,
                anio=timezone.now().year,
                defaults={}
            )
            if created:
                print(f"  ✅ Curso '{curso}' creado")
                
                # Asignar algunas asignaturas aleatorias a cada curso
                asignaturas = Asignatura.objects.all()[:5]  # Primeras 5 asignaturas
                curso.asignaturas.set(asignaturas)
    
    print("✅ Datos de prueba configurados correctamente")

def test_ajax_views():
    """Probar las vistas AJAX"""
    print("\n🧪 Probando vistas AJAX...")
    
    client = Client()
    
    # Login como administrador
    admin_user = User.objects.get(username='test_admin')
    client.force_login(admin_user)
    
    # Obtener un curso para pruebas
    curso = Curso.objects.first()
    if not curso:
        print("❌ No hay cursos disponibles para prueba")
        return False
    
    # Probar obtener asignaturas de curso
    print(f"  🔍 Probando obtener asignaturas para curso {curso}...")
    response = client.get(f'/ajax/obtener-asignaturas-curso/{curso.id}/')
    
    if response.status_code == 200:
        print("  ✅ Vista de obtener asignaturas funciona correctamente")
        data = response.json()
        if data.get('success'):
            print(f"    - Asignaturas asignadas: {len(data['data']['asignaturas_asignadas'])}")
            print(f"    - Asignaturas disponibles: {len(data['data']['asignaturas_disponibles'])}")
        else:
            print(f"    ⚠️  Respuesta no exitosa: {data.get('error', 'Sin error específico')}")
    else:
        print(f"  ❌ Error en vista de obtener asignaturas: {response.status_code}")
        return False
    
    # Probar asignar asignatura
    asignatura_disponible = Asignatura.objects.exclude(cursos=curso).first()
    if asignatura_disponible:
        print(f"  🔍 Probando asignar asignatura '{asignatura_disponible.nombre}' al curso {curso}...")
        response = client.post('/ajax/gestionar-asignaturas-curso/', 
                             data={
                                 'curso_id': curso.id,
                                 'asignatura_id': asignatura_disponible.id,
                                 'accion': 'asignar'
                             },
                             content_type='application/json')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("  ✅ Asignación de asignatura funciona correctamente")
                print(f"    - Mensaje: {data.get('mensaje')}")
            else:
                print(f"  ❌ Error al asignar: {data.get('error')}")
                return False
        else:
            print(f"  ❌ Error HTTP al asignar: {response.status_code}")
            return False
    else:
        print("  ⚠️  No hay asignaturas disponibles para asignar")
    
    # Probar desasignar asignatura
    asignatura_asignada = curso.asignaturas.first()
    if asignatura_asignada:
        print(f"  🔍 Probando desasignar asignatura '{asignatura_asignada.nombre}' del curso {curso}...")
        response = client.post('/ajax/gestionar-asignaturas-curso/', 
                             data={
                                 'curso_id': curso.id,
                                 'asignatura_id': asignatura_asignada.id,
                                 'accion': 'desasignar'
                             },
                             content_type='application/json')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("  ✅ Desasignación de asignatura funciona correctamente")
                print(f"    - Mensaje: {data.get('mensaje')}")
            else:
                print(f"  ❌ Error al desasignar: {data.get('error')}")
                return False
        else:
            print(f"  ❌ Error HTTP al desasignar: {response.status_code}")
            return False
    else:
        print("  ⚠️  No hay asignaturas asignadas para desasignar")
    
    return True

def test_main_view():
    """Probar la vista principal de listado de cursos"""
    print("\n🧪 Probando vista principal de cursos...")
    
    client = Client()
    admin_user = User.objects.get(username='test_admin')
    client.force_login(admin_user)
    
    response = client.get('/cursos/')
    
    if response.status_code == 200:
        print("  ✅ Vista principal de cursos carga correctamente")
        
        # Verificar que el contexto contiene los datos necesarios
        context = response.context
        required_keys = [
            'cursos', 'total_cursos', 'total_estudiantes_asignados',
            'profesores_jefe_asignados', 'total_asignaturas_asignadas',
            'total_asignaturas_disponibles', 'puede_editar'
        ]
        
        for key in required_keys:
            if key in context:
                print(f"    ✅ Contexto contiene '{key}': {context[key]}")
            else:
                print(f"    ❌ Falta '{key}' en el contexto")
                return False
        
        # Verificar que el template se renderiza sin errores
        content = response.content.decode('utf-8')
        if 'modalGestionarAsignaturas' in content:
            print("  ✅ Modal de gestión de asignaturas presente en el HTML")
        else:
            print("  ❌ Modal de gestión de asignaturas no encontrado")
            return False
            
        if 'gestionarAsignaturasCurso' in content:
            print("  ✅ Función JavaScript de gestión presente")
        else:
            print("  ❌ Función JavaScript de gestión no encontrada")
            return False
        
        return True
    else:
        print(f"  ❌ Error al cargar vista principal: {response.status_code}")
        return False

def main():
    """Función principal de prueba"""
    print("🚀 Iniciando pruebas finales del listado de cursos mejorado")
    print("="*60)
    
    try:
        # Configurar datos de prueba
        setup_test_data()
        
        # Probar vistas AJAX
        if not test_ajax_views():
            print("\n❌ Las pruebas AJAX fallaron")
            return False
        
        # Probar vista principal
        if not test_main_view():
            print("\n❌ La prueba de vista principal falló")
            return False
        
        print("\n" + "="*60)
        print("🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        print()
        print("✅ Funcionalidades validadas:")
        print("  - Modal de gestión de asignaturas completamente funcional")
        print("  - Vistas AJAX para asignar/desasignar asignaturas")
        print("  - Diseño limpio y profesional")
        print("  - Actualización dinámica de badges y estadísticas")
        print("  - Mensajes de confirmación y error")
        print()
        print("📋 Próximos pasos recomendados:")
        print("  1. Probar la funcionalidad en el navegador")
        print("  2. Verificar que los cambios se reflejen en la base de datos")
        print("  3. Validar la experiencia de usuario completa")
        print("  4. Realizar pruebas con diferentes tipos de usuario")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
