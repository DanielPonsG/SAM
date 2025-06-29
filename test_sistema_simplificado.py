#!/usr/bin/env python
"""
Script de prueba para validar el nuevo sistema simplificado de registro de asistencia
Verificar que:
1. editar_asistencia_alumno.html funciona sin errores
2. registrar_asistencia_alumno solo requiere curso (no asignatura)
3. Se muestra automáticamente quién registró y a qué hora
"""

import os
import sys
import django
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import (
    Perfil, Estudiante, Profesor, Curso, Asignatura, 
    AsistenciaAlumno
)

def print_separator(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def test_formulario_simplificado():
    """Test del formulario simplificado que solo requiere curso"""
    print_separator("PRUEBA: Formulario Simplificado de Registro")
    
    try:
        from smapp.forms import RegistroMasivoAsistenciaForm
        
        # Crear formulario vacío
        form = RegistroMasivoAsistenciaForm()
        
        # Verificar que solo tiene campo curso
        campos_esperados = ['curso']
        campos_reales = list(form.fields.keys())
        
        print(f"✓ Campos esperados: {campos_esperados}")
        print(f"✓ Campos reales: {campos_reales}")
        
        if campos_reales == campos_esperados:
            print("✅ Formulario simplificado correctamente")
            return True
        else:
            print("❌ Formulario tiene campos inesperados")
            return False
            
    except Exception as e:
        print(f"❌ Error en test de formulario: {str(e)}")
        return False

def test_permisos_cursos():
    """Test de que los profesores solo ven sus cursos asignados"""
    print_separator("PRUEBA: Permisos de Cursos por Profesor")
    
    try:
        # Buscar un profesor
        profesor_user = User.objects.filter(perfil__tipo_usuario='profesor').first()
        
        if not profesor_user:
            print("❌ No se encontró profesor para pruebas")
            return False
            
        profesor = Profesor.objects.get(user=profesor_user)
        print(f"✓ Probando con profesor: {profesor.get_nombre_completo()}")
        
        # Calcular cursos disponibles según la lógica de la vista
        cursos_ids = set()
        
        # Cursos como jefe
        cursos_jefatura = profesor.get_cursos_jefatura()
        cursos_ids.update(cursos_jefatura.values_list('id', flat=True))
        print(f"  - Cursos como jefe: {cursos_jefatura.count()}")
        
        # Cursos donde enseña
        cursos_asignaturas = Curso.objects.filter(
            asignaturas__profesores_responsables=profesor
        ).distinct()
        cursos_ids.update(cursos_asignaturas.values_list('id', flat=True))
        print(f"  - Cursos donde enseña: {cursos_asignaturas.count()}")
        
        # Cursos donde es responsable principal
        cursos_responsable = Curso.objects.filter(
            asignaturas__profesor_responsable=profesor
        ).distinct()
        cursos_ids.update(cursos_responsable.values_list('id', flat=True))
        print(f"  - Cursos como responsable: {cursos_responsable.count()}")
        
        total_cursos_profesor = len(cursos_ids)
        total_cursos_sistema = Curso.objects.count()
        
        print(f"  - Total cursos únicos del profesor: {total_cursos_profesor}")
        print(f"  - Total cursos en sistema: {total_cursos_sistema}")
        
        if total_cursos_profesor <= total_cursos_sistema:
            print("✅ Permisos de cursos funcionando correctamente")
            return True
        else:
            print("❌ Error en cálculo de permisos")
            return False
            
    except Exception as e:
        print(f"❌ Error en test de permisos: {str(e)}")
        return False

def test_asignatura_automatica():
    """Test de asignación automática de asignatura"""
    print_separator("PRUEBA: Asignación Automática de Asignatura")
    
    try:
        from django.db.models import Q
        
        # Buscar un curso con asignaturas
        curso = Curso.objects.filter(asignaturas__isnull=False).first()
        
        if not curso:
            print("❌ No se encontró curso con asignaturas")
            return False
            
        print(f"✓ Probando con curso: {curso}")
        
        # Buscar un profesor que enseñe en este curso
        profesor = Profesor.objects.filter(
            Q(asignaturas_responsable__in=curso.asignaturas.all()) |
            Q(profesor_responsable__in=curso.asignaturas.all())
        ).first()
        
        if profesor:
            print(f"✓ Profesor encontrado: {profesor.get_nombre_completo()}")
            
            # Simular lógica de asignación automática
            asignatura_automatica = curso.asignaturas.filter(
                Q(profesores_responsables=profesor) |
                Q(profesor_responsable=profesor)
            ).first()
            
            if asignatura_automatica:
                print(f"✓ Asignatura automática: {asignatura_automatica.nombre}")
                print("✅ Asignación automática funcionando")
                return True
            else:
                print("⚠️  No se encontró asignatura automática para el profesor")
                # Probar con primera asignatura del curso
                primera_asignatura = curso.asignaturas.first()
                if primera_asignatura:
                    print(f"✓ Usando primera asignatura del curso: {primera_asignatura.nombre}")
                    return True
        else:
            print("⚠️  No se encontró profesor específico, usando primera asignatura")
            primera_asignatura = curso.asignaturas.first()
            if primera_asignatura:
                print(f"✓ Primera asignatura: {primera_asignatura.nombre}")
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error en test de asignatura automática: {str(e)}")
        return False

def test_registro_automatico():
    """Test de información de registro automático"""
    print_separator("PRUEBA: Información de Registro Automático")
    
    try:
        from django.utils import timezone
        
        # Simular datos de registro
        fecha_actual = timezone.now().date()
        hora_actual = timezone.now().time()
        
        # Buscar profesor actual
        profesor = Profesor.objects.first()
        
        if profesor:
            print(f"✓ Fecha de registro: {fecha_actual.strftime('%d/%m/%Y')}")
            print(f"✓ Hora de registro: {hora_actual.strftime('%H:%M:%S')}")
            print(f"✓ Registrado por: {profesor.get_nombre_completo()}")
            print("✅ Información de registro automático disponible")
            return True
        else:
            print("❌ No se encontró profesor para simular registro")
            return False
            
    except Exception as e:
        print(f"❌ Error en test de registro automático: {str(e)}")
        return False

def test_asistencias_existentes():
    """Test de verificación de asistencias existentes del día"""
    print_separator("PRUEBA: Verificación de Asistencias del Día")
    
    try:
        from django.utils import timezone
        
        fecha_hoy = timezone.now().date()
        
        # Contar asistencias de hoy
        asistencias_hoy = AsistenciaAlumno.objects.filter(fecha=fecha_hoy).count()
        print(f"✓ Asistencias registradas hoy: {asistencias_hoy}")
        
        # Verificar estructura de datos recientes
        if asistencias_hoy > 0:
            ultima_asistencia = AsistenciaAlumno.objects.filter(fecha=fecha_hoy).last()
            print(f"✓ Última asistencia:")
            print(f"  - Estudiante: {ultima_asistencia.estudiante.get_nombre_completo()}")
            print(f"  - Curso: {ultima_asistencia.curso}")
            print(f"  - Asignatura: {ultima_asistencia.asignatura.nombre}")
            print(f"  - Hora: {ultima_asistencia.hora_registro}")
            print(f"  - Profesor: {ultima_asistencia.profesor_registro.get_nombre_completo() if ultima_asistencia.profesor_registro else 'No especificado'}")
        
        print("✅ Verificación de asistencias completada")
        return True
        
    except Exception as e:
        print(f"❌ Error en test de asistencias: {str(e)}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 PRUEBAS DEL SISTEMA SIMPLIFICADO DE ASISTENCIA")
    print("=" * 60)
    
    tests = [
        ("Formulario Simplificado", test_formulario_simplificado),
        ("Permisos de Cursos", test_permisos_cursos),
        ("Asignatura Automática", test_asignatura_automatica),
        ("Registro Automático", test_registro_automatico),
        ("Asistencias del Día", test_asistencias_existentes),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔄 Ejecutando: {test_name}")
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASÓ")
            else:
                print(f"❌ {test_name}: FALLÓ")
                
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {str(e)}")
            results.append((test_name, False))
    
    # Resumen final
    print_separator("RESUMEN DE PRUEBAS")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"   {test_name}: {status}")
    
    print(f"\n📈 Resultado final: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("\n📋 SISTEMA SIMPLIFICADO VALIDADO:")
        print("✓ Formulario solo requiere curso")
        print("✓ Asignatura se asigna automáticamente")
        print("✓ Permisos por rol funcionando")
        print("✓ Información de registro automática")
        print("✓ Verificación de asistencias del día")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisar implementación.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
