import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import *
from django.core.exceptions import ValidationError
from datetime import date, time

def test_validaciones():
    print("=== PRUEBAS DE VALIDACIONES ===\n")
    
    # 1. Probar validaciones de HorarioCurso
    print("1. Probando validaciones de HorarioCurso:")
    
    # Obtener un curso para las pruebas
    curso = Curso.objects.first()
    asignatura = Asignatura.objects.first()
    
    if curso and asignatura:
        # Prueba 1: Horario con hora_inicio >= hora_fin (debería fallar)
        try:
            horario_malo = HorarioCurso(
                curso=curso,
                asignatura=asignatura,
                dia='LU',
                hora_inicio=time(10, 0),
                hora_fin=time(9, 0)  # Hora fin menor que inicio
            )
            horario_malo.clean()
            print("   - ERROR: Debería haber fallado la validación de horas")
        except ValidationError as e:
            print(f"   - ✓ Validación de horas correcta: {e}")
        
        # Prueba 2: Crear horario válido
        try:
            horario_bueno = HorarioCurso(
                curso=curso,
                asignatura=asignatura,
                dia='MA',
                hora_inicio=time(9, 0),
                hora_fin=time(10, 30)
            )
            horario_bueno.clean()
            print("   - ✓ Horario válido creado correctamente")
        except ValidationError as e:
            print(f"   - Error inesperado: {e}")
        
    else:
        print("   - No hay curso o asignatura para probar")
    
    # 2. Probar métodos de utilidad de Curso
    print("\n2. Probando métodos de utilidad de Curso:")
    
    if curso:
        # Verificar conflicto de horarios
        tiene_conflicto = curso.tiene_conflicto_horario('LU', time(8, 0), time(9, 30))
        print(f"   - Conflicto horario Lunes 8:00-9:30: {tiene_conflicto}")
        
        tiene_conflicto_2 = curso.tiene_conflicto_horario('DO', time(8, 0), time(9, 30))
        print(f"   - Conflicto horario Domingo 8:00-9:30: {tiene_conflicto_2}")
    
    # 3. Probar propiedades calculadas
    print("\n3. Probando propiedades calculadas:")
    
    # Probar edad
    estudiante = Estudiante.objects.first()
    if estudiante:
        print(f"   - Edad del estudiante {estudiante.primer_nombre}: {estudiante.edad} años")
        print(f"   - Fecha nacimiento: {estudiante.fecha_nacimiento}")
    
    # Probar duración de horarios
    horario = HorarioCurso.objects.first()
    if horario:
        print(f"   - Duración horario {horario}: {horario.duracion_minutos} minutos")
    
    # 4. Probar orden de cursos
    print("\n4. Probando ordenamiento de cursos:")
    cursos = Curso.objects.all()[:5]  # Primeros 5 cursos
    for curso in cursos:
        print(f"   - {curso.nombre} (orden: {curso.orden_nivel})")
    
    # 5. Probar colores de eventos
    print("\n5. Probando colores de eventos:")
    eventos = EventoCalendario.objects.all()[:3]  # Primeros 3 eventos
    for evento in eventos:
        print(f"   - {evento.titulo} ({evento.tipo_evento}): {evento.color_por_tipo}")
    
    print("\n=== VALIDACIONES COMPLETADAS ===")

if __name__ == "__main__":
    test_validaciones()
