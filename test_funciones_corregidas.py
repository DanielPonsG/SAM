#!/usr/bin/env python3
"""
Script final para probar específicamente las funciones que no funcionaban:
- Edición de asignaturas
- Asignación de profesores
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Asignatura, Profesor, Curso
from smapp.forms import AsignaturaCompletaForm
from django.test import Client
from django.urls import reverse

def test_edicion_asignatura():
    """Probar edición de asignatura específicamente"""
    print("=== PRUEBA: EDICIÓN DE ASIGNATURA ===")
    
    # Tomar una asignatura existente
    asignatura = Asignatura.objects.first()
    if not asignatura:
        print("✗ No hay asignaturas para probar")
        return False
    
    print(f"Probando edición de: {asignatura.nombre}")
    
    # Datos para el formulario
    form_data = {
        'nombre': asignatura.nombre,
        'codigo_asignatura': asignatura.codigo_asignatura,
        'descripcion': f"Descripción editada para {asignatura.nombre}",
        'profesor_responsable': asignatura.profesor_responsable.id if asignatura.profesor_responsable else '',
    }
    
    # Probar formulario
    form = AsignaturaCompletaForm(data=form_data, instance=asignatura)
    
    if form.is_valid():
        # Guardar cambios
        asignatura_editada = form.save()
        print(f"✓ Asignatura editada exitosamente")
        print(f"  Descripción actualizada: {asignatura_editada.descripcion[:50]}...")
        return True
    else:
        print("✗ Error en formulario de edición:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
        return False

def test_asignacion_profesor():
    """Probar asignación de profesor específicamente"""
    print("\n=== PRUEBA: ASIGNACIÓN DE PROFESOR ===")
    
    # Buscar asignatura sin profesor
    asignatura_sin_prof = Asignatura.objects.filter(profesor_responsable__isnull=True).first()
    if not asignatura_sin_prof:
        print("No hay asignaturas sin profesor, creando una...")
        asignatura_sin_prof = Asignatura.objects.create(
            nombre="Asignatura de Prueba",
            codigo_asignatura="PRUEBA-001"
        )
    
    # Buscar profesor disponible
    profesor = Profesor.objects.first()
    if not profesor:
        print("✗ No hay profesores disponibles")
        return False
    
    print(f"Asignando profesor {profesor.primer_nombre} {profesor.apellido_paterno}")
    print(f"a la asignatura: {asignatura_sin_prof.nombre}")
    
    # Simular asignación (como lo haría el AJAX)
    asignatura_sin_prof.profesor_responsable = profesor
    asignatura_sin_prof.save()
    
    # Verificar que se guardó
    asignatura_sin_prof.refresh_from_db()
    
    if asignatura_sin_prof.profesor_responsable == profesor:
        print("✓ Profesor asignado exitosamente")
        print(f"  Verificado: {asignatura_sin_prof.profesor_responsable}")
        return True
    else:
        print("✗ Error: La asignación no se guardó correctamente")
        return False

def test_ajax_simulation():
    """Simular una petición AJAX para asignar profesor"""
    print("\n=== PRUEBA: SIMULACIÓN AJAX ===")
    
    # Crear cliente de prueba
    client = Client()
    
    # Autenticar como admin
    admin_user = User.objects.filter(username='admin').first()
    if admin_user:
        client.force_login(admin_user)
    
    # Buscar asignatura y profesor
    asignatura = Asignatura.objects.first()
    profesor = Profesor.objects.last()  # Usar otro profesor
    
    if not asignatura or not profesor:
        print("✗ No hay datos suficientes para la prueba")
        return False
    
    print(f"Simulando AJAX para asignar {profesor.primer_nombre} a {asignatura.nombre}")
    
    # Simular petición AJAX
    response = client.post(
        reverse('asignar_profesor_asignatura', args=[asignatura.id]),
        {
            'profesor_id': profesor.id
        },
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    if response.status_code == 200:
        import json
        data = json.loads(response.content)
        if data.get('success'):
            print("✓ Petición AJAX exitosa")
            print(f"  Mensaje: {data.get('message')}")
            return True
        else:
            print(f"✗ Error en AJAX: {data.get('error')}")
            return False
    else:
        print(f"✗ Error HTTP: {response.status_code}")
        return False

def test_vista_editar():
    """Probar que la vista de editar funcione"""
    print("\n=== PRUEBA: VISTA DE EDICIÓN ===")
    
    client = Client()
    
    # Autenticar como admin
    admin_user = User.objects.filter(username='admin').first()
    if admin_user:
        client.force_login(admin_user)
    
    asignatura = Asignatura.objects.first()
    if not asignatura:
        print("✗ No hay asignaturas para probar")
        return False
    
    # Probar GET (cargar formulario)
    response = client.get(reverse('editar_asignatura', args=[asignatura.id]))
    
    if response.status_code == 200:
        print("✓ Vista de edición carga correctamente")
        
        # Probar POST (enviar formulario)
        response = client.post(
            reverse('editar_asignatura', args=[asignatura.id]),
            {
                'nombre': asignatura.nombre,
                'codigo_asignatura': asignatura.codigo_asignatura,
                'descripcion': f"Editado via POST - {asignatura.descripcion or ''}",
                'profesor_responsable': asignatura.profesor_responsable.id if asignatura.profesor_responsable else '',
            }
        )
        
        if response.status_code == 302:  # Redirect después de éxito
            print("✓ Formulario enviado exitosamente")
            return True
        else:
            print(f"✗ Error en POST: {response.status_code}")
            return False
    else:
        print(f"✗ Error al cargar vista: {response.status_code}")
        return False

def main():
    """Ejecutar todas las pruebas específicas"""
    print("PRUEBAS ESPECÍFICAS DE FUNCIONALIDAD PROBLEMÁTICA")
    print("=" * 60)
    
    resultados = []
    
    # Ejecutar pruebas
    resultados.append(test_edicion_asignatura())
    resultados.append(test_asignacion_profesor())
    resultados.append(test_ajax_simulation())
    resultados.append(test_vista_editar())
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS:")
    exitosas = sum(resultados)
    total = len(resultados)
    
    print(f"✅ Exitosas: {exitosas}/{total}")
    print(f"❌ Fallidas: {total - exitosas}/{total}")
    
    if exitosas == total:
        print("\n🎉 ¡TODAS LAS FUNCIONES FUNCIONAN CORRECTAMENTE!")
        print("✅ Edición de asignaturas: FUNCIONAL")
        print("✅ Asignación de profesores: FUNCIONAL")
        print("✅ Peticiones AJAX: FUNCIONAL")
        print("✅ Vistas y formularios: FUNCIONAL")
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisar los errores arriba.")
    
    print(f"\n🌐 El sistema está listo para usar en: http://127.0.0.1:8000/asignaturas/")

if __name__ == '__main__':
    main()
