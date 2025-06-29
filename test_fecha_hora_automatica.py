#!/usr/bin/env python
"""
Script para probar que el registro automático de fecha y hora funciona correctamente
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import AsistenciaAlumno, AsistenciaProfesor, Estudiante, Profesor, Curso, Asignatura
from django.contrib.auth.models import User
from django.utils import timezone

def test_fecha_hora_automatica():
    """Prueba que las fechas y horas se establezcan automáticamente"""
    print("🧪 PROBANDO REGISTRO AUTOMÁTICO DE FECHA Y HORA")
    print("=" * 60)
    
    try:
        # Obtener datos necesarios
        estudiante = Estudiante.objects.first()
        profesor = Profesor.objects.first()
        curso = Curso.objects.first()
        asignatura = Asignatura.objects.first()
        user = User.objects.first()
        
        if not all([estudiante, profesor, curso, asignatura, user]):
            print("❌ Error: No hay datos suficientes en la base de datos")
            return False
        
        print(f"📚 Usando estudiante: {estudiante.get_nombre_completo()}")
        print(f"👨‍🏫 Usando profesor: {profesor.get_nombre_completo()}")
        print(f"🏫 Usando curso: {curso}")
        print(f"📖 Usando asignatura: {asignatura.nombre}")
        print()
        
        # Registrar momento antes de crear
        momento_antes = timezone.now()
        print(f"⏰ Momento antes de crear registro: {momento_antes}")
        
        # TEST 1: Asistencia de Alumno
        print("\n1️⃣ PROBANDO ASISTENCIA DE ALUMNO")
        print("-" * 40)
        
        # Eliminar registros existentes para esta prueba
        fecha_local = timezone.localtime(timezone.now()).date()
        AsistenciaAlumno.objects.filter(
            estudiante=estudiante, 
            asignatura=asignatura,
            fecha=fecha_local
        ).delete()
        
        print(f"🗑️ Eliminados registros existentes para fecha: {fecha_local}")
        
        asistencia_alumno = AsistenciaAlumno.objects.create(
            estudiante=estudiante,
            curso=curso,
            asignatura=asignatura,
            profesor_registro=profesor,
            presente=True,
            observacion="Prueba de fecha automática",
            registrado_por_usuario=user
        )
        
        momento_despues = timezone.now()
        print(f"⏰ Momento después de crear registro: {momento_despues}")
        
        print(f"📅 Fecha registrada: {asistencia_alumno.fecha}")
        print(f"🕐 Hora registrada: {asistencia_alumno.hora_registro}")
        print(f"📝 Fecha creación: {asistencia_alumno.fecha_creacion}")
        print(f"📝 Fecha modificación: {asistencia_alumno.fecha_modificacion}")
        
        # Verificaciones (considerando zona horaria local)
        fecha_local = timezone.localtime(timezone.now()).date()
        print(f"📅 Fecha local esperada: {fecha_local}")
        
        assert asistencia_alumno.fecha == fecha_local, "❌ La fecha no es la correcta"
        assert asistencia_alumno.fecha_creacion is not None, "❌ La fecha de creación no se estableció"
        assert asistencia_alumno.fecha_modificacion is not None, "❌ La fecha de modificación no se estableció"
        
        print("✅ Asistencia de alumno registrada correctamente con fecha/hora automática")
        
        # TEST 2: Asistencia de Profesor
        print("\n2️⃣ PROBANDO ASISTENCIA DE PROFESOR")
        print("-" * 40)
        
        # Eliminar registros existentes para esta prueba
        fecha_local = timezone.localtime(timezone.now()).date()
        AsistenciaProfesor.objects.filter(
            profesor=profesor,
            asignatura=asignatura,
            fecha=fecha_local
        ).delete()
        
        print(f"🗑️ Eliminados registros existentes para fecha: {fecha_local}")
        
        momento_antes = timezone.now()
        print(f"⏰ Momento antes de crear registro: {momento_antes}")
        
        asistencia_profesor = AsistenciaProfesor.objects.create(
            profesor=profesor,
            asignatura=asignatura,
            curso=curso,
            presente=True,
            observacion="Prueba de fecha automática profesor",
            registrado_por_usuario=user
        )
        
        momento_despues = timezone.now()
        print(f"⏰ Momento después de crear registro: {momento_despues}")
        
        print(f"📅 Fecha registrada: {asistencia_profesor.fecha}")
        print(f"🕐 Hora registrada: {asistencia_profesor.hora_registro}")
        print(f"📝 Fecha creación: {asistencia_profesor.fecha_creacion}")
        print(f"📝 Fecha modificación: {asistencia_profesor.fecha_modificacion}")
        
        # Verificaciones (considerando zona horaria local)
        fecha_local = timezone.localtime(timezone.now()).date()
        print(f"📅 Fecha local esperada: {fecha_local}")
        
        assert asistencia_profesor.fecha == fecha_local, "❌ La fecha no es la correcta"
        assert asistencia_profesor.fecha_creacion is not None, "❌ La fecha de creación no se estableció"
        assert asistencia_profesor.fecha_modificacion is not None, "❌ La fecha de modificación no se estableció"
        
        print("✅ Asistencia de profesor registrada correctamente con fecha/hora automática")
        
        # TEST 3: Modificación
        print("\n3️⃣ PROBANDO MODIFICACIÓN DE REGISTRO")
        print("-" * 40)
        
        fecha_modificacion_original = asistencia_alumno.fecha_modificacion
        print(f"📝 Fecha modificación original: {fecha_modificacion_original}")
        
        # Esperar un poco para ver diferencia en tiempo
        import time
        time.sleep(1)
        
        asistencia_alumno.observacion = "Observación modificada"
        asistencia_alumno.save()
        
        print(f"📝 Nueva fecha modificación: {asistencia_alumno.fecha_modificacion}")
        
        assert asistencia_alumno.fecha_modificacion > fecha_modificacion_original, "❌ La fecha de modificación no se actualizó"
        
        print("✅ Fecha de modificación se actualiza correctamente")
        
        print("\n🎉 TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("✅ El sistema registra automáticamente fecha y hora actual")
        print("✅ Los campos de auditoría funcionan correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fecha_hora_automatica()
    if success:
        print("\n🎯 RESULTADO: TODAS LAS PRUEBAS EXITOSAS")
    else:
        print("\n💥 RESULTADO: ALGUNAS PRUEBAS FALLARON")
    
    sys.exit(0 if success else 1)
