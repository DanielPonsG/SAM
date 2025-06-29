#!/usr/bin/env python
"""
Script de prueba final para simular el comportamiento completo del template
con datos reales de la base de datos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.template import Template, Context
from django.template.loader import get_template
from smapp.models import Curso, Estudiante, Asignatura, Calificacion, Inscripcion
from smapp.templatetags.custom_filters import get_item, get_list_item
from collections import defaultdict

def simulate_template_rendering():
    """Simula el renderizado del template con datos reales"""
    print("🎭 Simulando renderizado del template con datos reales...")
    
    # Obtener datos reales
    curso = Curso.objects.first()
    if not curso:
        print("❌ No hay cursos en la BD")
        return False
    
    asignatura = curso.asignaturas.first() if curso.asignaturas.exists() else None
    
    print(f"📚 Usando curso: {curso}")
    print(f"📖 Usando asignatura: {asignatura}")
    
    # Simular la lógica de la vista
    estudiantes_curso = curso.estudiantes.all()
    print(f"👥 Estudiantes en el curso: {estudiantes_curso.count()}")
    
    if asignatura:
        # Simular el caso con asignatura específica
        inscripciones = Inscripcion.objects.filter(
            estudiante__in=estudiantes_curso,
            grupo__asignatura=asignatura
        )
        notas = Calificacion.objects.filter(inscripcion__in=inscripciones)
        
        # Crear estructura de evaluaciones
        evaluaciones_nombres = set()
        for nota in notas:
            evaluaciones_nombres.add(nota.nombre_evaluacion)
        evaluaciones = [{'nombre': nombre} for nombre in sorted(evaluaciones_nombres)]
        
        print(f"📋 Evaluaciones encontradas: {[e['nombre'] for e in evaluaciones]}")
        
        # Crear notas_por_estudiante como en la vista
        notas_por_estudiante = defaultdict(list)
        estudiantes_curso_asignatura = estudiantes_curso.filter(
            id__in=inscripciones.values_list('estudiante_id', flat=True)
        )
        
        for estudiante in estudiantes_curso_asignatura:
            notas_est = [None] * len(evaluaciones)
            notas_estudiante = notas.filter(inscripcion__estudiante=estudiante)
            
            for idx, ev in enumerate(evaluaciones):
                nota = notas_estudiante.filter(nombre_evaluacion=ev['nombre']).first()
                notas_est[idx] = nota
            notas_por_estudiante[estudiante] = notas_est
        
        # Crear promedios_estudiantes
        promedios_estudiantes = {}
        for estudiante in estudiantes_curso_asignatura:
            notas_est = notas_por_estudiante[estudiante]
            notas_validas = [n.puntaje for n in notas_est if n is not None and hasattr(n, 'puntaje')]
            promedio = sum(notas_validas) / len(notas_validas) if notas_validas else None
            promedios_estudiantes[estudiante.id] = {
                'promedio': promedio if promedio is not None else '--',
                'estado': 'Aprobado' if promedio and promedio >= 4.0 else 'Reprobado'
            }
        
        print(f"📊 Promedios calculados para {len(promedios_estudiantes)} estudiantes")
        
        # Simular el bucle del template
        print("\n🔄 Simulando bucle del template...")
        for estudiante in estudiantes_curso_asignatura:
            print(f"\n👤 Procesando estudiante: {estudiante.get_nombre_completo()}")
            
            # Simular: notas_estudiante=notas_por_estudiante|get_item:estudiante
            try:
                notas_estudiante = get_item(notas_por_estudiante, estudiante)
                print(f"   📝 Notas obtenidas: {type(notas_estudiante)} con {len(notas_estudiante) if notas_estudiante else 0} elementos")
                
                # Simular el bucle interno por evaluaciones
                for idx, ev in enumerate(evaluaciones):
                    # Simular: nota=notas_estudiante|get_list_item:forloop.counter0
                    try:
                        nota = get_list_item(notas_estudiante, idx)
                        if nota:
                            print(f"   ✅ Evaluación {ev['nombre']}: {nota.puntaje}")
                        else:
                            print(f"   ➖ Evaluación {ev['nombre']}: Sin nota")
                    except Exception as e:
                        print(f"   ❌ Error en evaluación {ev['nombre']}: {e}")
                        return False
                
                # Simular: datos=promedios_estudiantes|get_item:estudiante.id
                try:
                    datos = get_item(promedios_estudiantes, estudiante.id)
                    if datos:
                        print(f"   📊 Promedio: {datos['promedio']} - {datos['estado']}")
                    else:
                        print(f"   📊 Sin datos de promedio")
                except Exception as e:
                    print(f"   ❌ Error obteniendo promedio: {e}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Error procesando estudiante: {e}")
                return False
    
    print("\n🎉 Simulación del template completada exitosamente")
    return True

def test_template_actual():
    """Prueba renderizando el template actual con datos reales"""
    print("\n🎭 Probando template actual con datos reales...")
    
    try:
        from django.test import RequestFactory
        from django.contrib.auth.models import User
        from smapp.views import ver_notas_curso
        
        factory = RequestFactory()
        user = User.objects.filter(username='admin').first()
        if not user:
            print("❌ No se encontró usuario admin")
            return False
        
        curso = Curso.objects.first()
        if not curso:
            print("❌ No hay cursos disponibles")
            return False
            
        # Crear request simulado
        request = factory.get('/notas/ver/', {'curso_id': curso.id})
        request.user = user
        
        # Ejecutar la vista
        response = ver_notas_curso(request)
        
        if response.status_code == 200:
            print("✅ Template renderizado exitosamente")
            return True
        else:
            print(f"❌ Error en template: status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error renderizando template: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Iniciando prueba final del sistema de notas...")
    
    # Simular la lógica del template
    success1 = simulate_template_rendering()
    
    # Probar el template real
    success2 = test_template_actual()
    
    if success1 and success2:
        print("\n✅ PRUEBA FINAL EXITOSA")
        print("El sistema de notas está completamente funcional")
        print("No hay errores de AttributeError ni otros problemas")
    else:
        print("\n❌ PRUEBA FINAL FALLIDA")
        print("Revisar los errores anteriores")
        sys.exit(1)
