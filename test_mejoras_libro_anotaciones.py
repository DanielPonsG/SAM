#!/usr/bin/env python
"""
Script para probar las mejoras en el libro de anotaciones:
1. Filtro dinámico de estudiantes por curso
2. Edición de anotaciones con campos bloqueados
3. Funcionalidad AJAX
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Curso, Estudiante, Anotacion, Profesor
from django.utils import timezone
from django.test import Client
from django.urls import reverse

def test_ajax_estudiantes_filtro():
    """Probar el endpoint AJAX para filtrar estudiantes por curso"""
    print("="*60)
    print("PROBANDO FILTRO AJAX DE ESTUDIANTES POR CURSO")
    print("="*60)
    
    # Obtener un curso con estudiantes
    curso = Curso.objects.filter(estudiantes__isnull=False).first()
    if not curso:
        print("❌ No hay cursos con estudiantes")
        return False
    
    print(f"✅ Curso encontrado: {curso}")
    print(f"📚 Estudiantes en el curso: {curso.estudiantes.count()}")
    
    # Listar estudiantes
    estudiantes = curso.estudiantes.all()
    for est in estudiantes[:3]:  # Mostrar solo los primeros 3
        print(f"   - {est.get_nombre_completo()} ({est.numero_documento})")
    
    # Crear un cliente de prueba
    client = Client()
    
    # Crear un usuario profesor para hacer la petición
    try:
        profesor_user = User.objects.filter(perfil__tipo_usuario='profesor').first()
        if profesor_user:
            client.force_login(profesor_user)
            print(f"✅ Logueado como profesor: {profesor_user.username}")
        else:
            # Crear usuario admin
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                client.force_login(admin_user)
                print(f"✅ Logueado como admin: {admin_user.username}")
            else:
                print("❌ No hay usuarios disponibles")
                return False
    except Exception as e:
        print(f"❌ Error al configurar usuario: {e}")
        return False
    
    # Hacer petición AJAX
    url = reverse('ajax_obtener_estudiantes_filtro')
    response = client.get(url, {'curso_id': curso.id})
    
    print(f"🌐 URL: {url}?curso_id={curso.id}")
    print(f"📡 Status: {response.status_code}")
    
    if response.status_code == 200:
        import json
        data = json.loads(response.content.decode('utf-8'))
        print(f"✅ Respuesta exitosa: {len(data.get('estudiantes', []))} estudiantes")
        
        for est in data.get('estudiantes', [])[:3]:
            print(f"   - {est['nombre']} ({est['rut']})")
        return True
    else:
        print(f"❌ Error en la petición: {response.content.decode('utf-8')}")
        return False

def test_formulario_edicion():
    """Probar el formulario de edición de anotaciones"""
    print("\n" + "="*60)
    print("PROBANDO FORMULARIO DE EDICIÓN DE ANOTACIONES")
    print("="*60)
    
    # Buscar una anotación existente
    anotacion = Anotacion.objects.first()
    if not anotacion:
        print("❌ No hay anotaciones en el sistema")
        return False
    
    print(f"✅ Anotación encontrada:")
    print(f"   ID: {anotacion.id}")
    print(f"   Estudiante: {anotacion.estudiante.get_nombre_completo()}")
    print(f"   Curso: {anotacion.curso}")
    print(f"   Título: {anotacion.titulo}")
    print(f"   Tipo: {anotacion.get_tipo_display()}")
    print(f"   Puntos: {anotacion.puntos}")
    
    # Probar el formulario de edición
    from smapp.forms import AnotacionForm
    
    # Crear formulario para edición
    form = AnotacionForm(instance=anotacion, profesor=None)
    
    print(f"\n📝 Estado del formulario:")
    print(f"   Curso deshabilitado: {'disabled' in form.fields['curso'].widget.attrs}")
    print(f"   Estudiante deshabilitado: {'disabled' in form.fields['estudiante'].widget.attrs}")
    print(f"   Queryset curso: {form.fields['curso'].queryset.count()} opciones")
    print(f"   Queryset estudiante: {form.fields['estudiante'].queryset.count()} opciones")
    
    # Verificar que solo tenga el curso y estudiante actual
    if form.fields['curso'].queryset.count() == 1:
        curso_form = form.fields['curso'].queryset.first()
        if curso_form == anotacion.curso:
            print("✅ Campo curso correctamente limitado al curso actual")
        else:
            print("❌ Campo curso no coincide con el curso de la anotación")
            return False
    else:
        print(f"❌ Campo curso tiene {form.fields['curso'].queryset.count()} opciones, debería tener 1")
        return False
    
    if form.fields['estudiante'].queryset.count() == 1:
        estudiante_form = form.fields['estudiante'].queryset.first()
        if estudiante_form == anotacion.estudiante:
            print("✅ Campo estudiante correctamente limitado al estudiante actual")
        else:
            print("❌ Campo estudiante no coincide con el estudiante de la anotación")
            return False
    else:
        print(f"❌ Campo estudiante tiene {form.fields['estudiante'].queryset.count()} opciones, debería tener 1")
        return False
    
    return True

def test_filtro_anotaciones():
    """Probar el filtro de anotaciones mejorado"""
    print("\n" + "="*60)
    print("PROBANDO FILTRO DE ANOTACIONES MEJORADO")
    print("="*60)
    
    from smapp.forms import FiltroAnotacionesForm
    
    # Obtener un curso con estudiantes
    curso = Curso.objects.filter(estudiantes__isnull=False).first()
    if not curso:
        print("❌ No hay cursos con estudiantes")
        return False
    
    print(f"✅ Curso para filtro: {curso}")
    
    # Simular datos de formulario con curso seleccionado
    data = {'curso': str(curso.id)}
    form = FiltroAnotacionesForm(data=data, profesor=None)
    
    print(f"📝 Formulario con curso seleccionado:")
    print(f"   Estudiantes disponibles: {form.fields['estudiante'].queryset.count()}")
    
    # Verificar que solo muestre estudiantes del curso seleccionado
    estudiantes_curso = curso.estudiantes.count()
    estudiantes_form = form.fields['estudiante'].queryset.count()
    
    if estudiantes_curso == estudiantes_form:
        print("✅ Filtro de estudiantes funciona correctamente")
        
        # Mostrar algunos estudiantes
        for est in form.fields['estudiante'].queryset[:3]:
            print(f"   - {est.get_nombre_completo()}")
        
        return True
    else:
        print(f"❌ Discrepancia: Curso tiene {estudiantes_curso} estudiantes, formulario muestra {estudiantes_form}")
        return False

def mostrar_estadisticas():
    """Mostrar estadísticas del sistema"""
    print("\n" + "="*60)
    print("ESTADÍSTICAS DEL SISTEMA")
    print("="*60)
    
    cursos = Curso.objects.filter(anio=timezone.now().year)
    estudiantes = Estudiante.objects.all()
    anotaciones = Anotacion.objects.all()
    profesores = Profesor.objects.all()
    
    print(f"📊 Cursos ({timezone.now().year}): {cursos.count()}")
    print(f"👥 Estudiantes: {estudiantes.count()}")
    print(f"📝 Anotaciones: {anotaciones.count()}")
    print(f"👨‍🏫 Profesores: {profesores.count()}")
    
    # Mostrar algunos cursos con estudiantes
    print(f"\n📚 Cursos con estudiantes:")
    for curso in cursos.filter(estudiantes__isnull=False)[:5]:
        print(f"   - {curso}: {curso.estudiantes.count()} estudiantes")
    
    # Mostrar tipos de anotaciones
    if anotaciones.exists():
        print(f"\n📝 Tipos de anotaciones:")
        for tipo in ['positiva', 'negativa', 'neutra']:
            count = anotaciones.filter(tipo=tipo).count()
            print(f"   - {tipo.title()}: {count}")

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DEL LIBRO DE ANOTACIONES MEJORADO")
    print("="*60)
    
    # Mostrar estadísticas
    mostrar_estadisticas()
    
    # Probar funcionalidades
    tests = [
        ("AJAX Filtro Estudiantes", test_ajax_estudiantes_filtro),
        ("Formulario Edición", test_formulario_edicion),
        ("Filtro Anotaciones", test_filtro_anotaciones),
    ]
    
    resultados = []
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")
            resultados.append((nombre, False))
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE PRUEBAS")
    print("="*60)
    
    exitosos = 0
    for nombre, resultado in resultados:
        status = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"{status} - {nombre}")
        if resultado:
            exitosos += 1
    
    print(f"\n🏆 Resultado: {exitosos}/{len(resultados)} pruebas exitosas")
    
    if exitosos == len(resultados):
        print("🎉 ¡Todas las mejoras funcionan correctamente!")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar la implementación.")

if __name__ == "__main__":
    main()
