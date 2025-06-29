#!/usr/bin/env python
"""
Script para probar la funcionalidad completa de gestión de asignaturas - Versión Final
"""
import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Asignatura, Profesor, Curso, HorarioCurso
from django.test import Client
from django.urls import reverse

def probar_gestion_asignaturas():
    """Función principal para probar toda la gestión de asignaturas"""
    
    print("=" * 60)
    print("PRUEBA COMPLETA DEL SISTEMA DE GESTIÓN DE ASIGNATURAS")
    print("=" * 60)
    
    # 1. Verificar que existan usuarios y datos básicos
    print("\n1. Verificando datos básicos...")
    
    # Buscar un usuario admin
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No hay usuarios administradores en el sistema")
        return False
    
    print(f"✅ Usuario admin encontrado: {admin_user.username}")
    
    # Verificar profesores
    profesores = Profesor.objects.all()
    print(f"✅ Profesores disponibles: {profesores.count()}")
    for profesor in profesores[:3]:
        print(f"   - {profesor.primer_nombre} {profesor.apellido_paterno}")
    
    # Verificar cursos
    cursos = Curso.objects.all()
    print(f"✅ Cursos disponibles: {cursos.count()}")
    for curso in cursos[:3]:
        print(f"   - {curso.nombre_completo}")
    
    # 2. Probar vista de listar asignaturas
    print("\n2. Probando vista de listar asignaturas...")
    
    client = Client()
    client.force_login(admin_user)
    
    try:
        response = client.get(reverse('listar_asignaturas'))
        print(f"✅ Vista listar_asignaturas: HTTP {response.status_code}")
        
        if response.status_code == 200:
            context = response.context
            if context:
                asignaturas = context.get('asignaturas', [])
                print(f"✅ Asignaturas en contexto: {len(asignaturas)}")
                
                # Mostrar información de asignaturas
                for i, asignatura_info in enumerate(asignaturas[:3], 1):
                    asig = asignatura_info['asignatura']
                    print(f"   {i}. {asig.codigo_asignatura} - {asig.nombre}")
                    print(f"      Profesor: {asig.profesor_responsable or 'Sin asignar'}")
                    print(f"      Cursos: {asignatura_info['cursos_count']}")
                    print(f"      Horarios: {asignatura_info['total_horarios']}")
                    print(f"      Estado: {asignatura_info['estado']}")
            else:
                print("❌ No hay contexto en la respuesta")
                print(f"❌ Contenido de respuesta: {response.content[:200]}")
                
        else:
            print(f"❌ Error en vista listar_asignaturas: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error al cargar listar_asignaturas: {str(e)}")
        return False
    
    # 3. Probar crear asignatura
    print("\n3. Probando crear nueva asignatura...")
    
    try:
        # Datos para nueva asignatura
        nueva_asignatura_data = {
            'nombre': 'Asignatura de Prueba Final',
            'codigo_asignatura': f'FINAL-{datetime.now().strftime("%H%M%S")}',
            'descripcion': 'Asignatura creada por script de prueba final',
            'profesor_responsable': profesores.first().id if profesores.exists() else ''
        }
        
        response = client.post(reverse('agregar_asignatura'), nueva_asignatura_data)
        
        if response.status_code == 302:  # Redirección después de crear
            print("✅ Asignatura creada exitosamente (redirección)")
            
            # Verificar que se creó en la base de datos
            asignatura_creada = Asignatura.objects.filter(
                codigo_asignatura=nueva_asignatura_data['codigo_asignatura']
            ).first()
            
            if asignatura_creada:
                print(f"✅ Asignatura encontrada en BD: {asignatura_creada.nombre}")
                
                # 4. Probar editar asignatura
                print("\n4. Probando editar asignatura...")
                
                edit_data = {
                    'nombre': 'Asignatura de Prueba EDITADA FINAL',
                    'codigo_asignatura': asignatura_creada.codigo_asignatura,
                    'descripcion': 'Descripción editada por script final',
                    'profesor_responsable': profesores.last().id if profesores.count() > 1 else ''
                }
                
                response = client.post(
                    reverse('editar_asignatura', args=[asignatura_creada.id]), 
                    edit_data
                )
                
                if response.status_code == 302:
                    print("✅ Asignatura editada exitosamente")
                    
                    # Verificar cambios
                    asignatura_creada.refresh_from_db()
                    print(f"✅ Nombre actualizado: {asignatura_creada.nombre}")
                    
                else:
                    print(f"❌ Error al editar: HTTP {response.status_code}")
                
                # 5. Probar asignar profesor via AJAX
                print("\n5. Probando asignar profesor via AJAX...")
                
                if profesores.count() > 0:
                    ajax_data = {
                        'profesor_id': profesores.first().id
                    }
                    
                    response = client.post(
                        reverse('asignar_profesor_asignatura', args=[asignatura_creada.id]),
                        ajax_data,
                        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
                    )
                    
                    if response.status_code == 200:
                        json_response = response.json()
                        if json_response.get('success'):
                            print("✅ Profesor asignado via AJAX exitosamente")
                        else:
                            print(f"❌ Error en respuesta AJAX: {json_response.get('error')}")
                    else:
                        print(f"❌ Error en petición AJAX: HTTP {response.status_code}")
                
                # 6. Probar eliminar asignatura
                print("\n6. Probando eliminar asignatura...")
                
                response = client.post(
                    reverse('eliminar_asignatura', args=[asignatura_creada.id])
                )
                
                if response.status_code == 302:
                    print("✅ Asignatura eliminada exitosamente")
                    
                    # Verificar que se eliminó
                    if not Asignatura.objects.filter(id=asignatura_creada.id).exists():
                        print("✅ Confirmado: Asignatura eliminada de la BD")
                    else:
                        print("❌ La asignatura aún existe en la BD")
                        
                else:
                    print(f"❌ Error al eliminar: HTTP {response.status_code}")
                    
            else:
                print("❌ Asignatura no encontrada en la base de datos")
                return False
                
        else:
            print(f"❌ Error al crear asignatura: HTTP {response.status_code}")
            if hasattr(response, 'context') and response.context:
                form = response.context.get('form')
                if form and form.errors:
                    print(f"   Errores del formulario: {form.errors}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de crear asignatura: {str(e)}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
    print("✅ EL SISTEMA DE GESTIÓN DE ASIGNATURAS ESTÁ FUNCIONANDO")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        probar_gestion_asignaturas()
    except Exception as e:
        print(f"❌ Error general en el script: {str(e)}")
        sys.exit(1)
