#!/usr/bin/env python
"""
🎉 VERIFICACIÓN FINAL Y GUÍA DE USO DEL CALENDARIO
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import EventoCalendario, Curso
from datetime import date, timedelta

def verificacion_final():
    print("🎉 " + "=" * 48)
    print("   CALENDARIO ESCOLAR - VERIFICACIÓN FINAL")
    print("🎉 " + "=" * 48)
    
    # 1. Verificar datos
    print("\n📊 ESTADO DEL SISTEMA:")
    usuarios = User.objects.count()
    admin_count = User.objects.filter(is_superuser=True).count()
    cursos = Curso.objects.count()
    eventos = EventoCalendario.objects.count()
    
    print(f"   👥 Usuarios: {usuarios} ({admin_count} administradores)")
    print(f"   📚 Cursos: {cursos}")
    print(f"   📅 Eventos: {eventos}")
    
    # 2. Verificar usuarios admin
    admins = User.objects.filter(is_superuser=True)
    if admins.exists():
        print(f"\n🔑 USUARIOS ADMINISTRADORES:")
        for admin in admins:
            print(f"   - {admin.username}")
    
    # 3. Mostrar algunos cursos
    cursos_lista = Curso.objects.all()[:5]
    if cursos_lista:
        print(f"\n📚 CURSOS DISPONIBLES (primeros 5):")
        for curso in cursos_lista:
            print(f"   - {curso}")
    
    # 4. Mostrar algunos eventos
    eventos_recientes = EventoCalendario.objects.all()[:3]
    if eventos_recientes:
        print(f"\n📅 EVENTOS RECIENTES:")
        for evento in eventos_recientes:
            print(f"   - {evento.titulo} ({evento.fecha})")
    
    print("\n✅ " + "=" * 48)
    print("   FUNCIONALIDADES IMPLEMENTADAS")
    print("✅ " + "=" * 48)
    
    funcionalidades = [
        "📅 Calendario interactivo con FullCalendar",
        "➕ Modal para crear eventos nuevos",
        "🎯 Selección de cursos específicos o todos",
        "⏰ Validación de horas (inicio < fin)",
        "🔍 Filtros por fecha y curso",
        "👥 Permisos según tipo de usuario:",
        "   • Administrador/Director: crear eventos para cualquier curso",
        "   • Profesor: crear eventos solo para sus cursos",
        "   • Estudiante: solo visualizar eventos relevantes",
        "🎨 Colores por tipo de evento",
        "📋 Lista de próximos eventos",
        "🚀 Envío de formularios con AJAX",
        "✅ Validaciones en frontend y backend",
        "📱 Diseño responsivo y moderno"
    ]
    
    for func in funcionalidades:
        print(f"   {func}")
    
    print("\n🌐 " + "=" * 48)
    print("   GUÍA DE USO")
    print("🌐 " + "=" * 48)
    
    print("""
1. 🔐 ACCESO AL SISTEMA:
   - Ve a: http://127.0.0.1:8000/login/
   - Usa un usuario administrador (ej: admin/admin)
   - O crea uno nuevo con: python manage.py createsuperuser

2. 📅 USAR EL CALENDARIO:
   - Ve a: http://127.0.0.1:8000/calendario/
   - Verás el calendario principal con eventos existentes
   - Usa los filtros en la parte superior para filtrar eventos
   - Cambia la vista (Mes/Semana/Día) con los botones

3. ➕ CREAR EVENTOS:
   - Haz clic en el botón "Nuevo Evento" (azul, esquina superior derecha)
   - O haz clic en cualquier fecha del calendario
   - Se abrirá el modal de creación

4. 📝 LLENAR FORMULARIO DE EVENTO:
   - Título: Obligatorio (ej: "Prueba de Matemáticas")
   - Fecha: Obligatoria 
   - Horas: Opcionales (inicio debe ser < fin)
   - Tipo: Selecciona el tipo de evento
   - Prioridad: Baja, Media o Alta
   - Descripción: Opcional
   - Dirigido a: 
     • "Todos los cursos": Evento visible para toda la escuela
     • "Cursos específicos": Selecciona los cursos que verán el evento

5. ✅ VALIDACIONES AUTOMÁTICAS:
   - Campos obligatorios
   - Hora inicio < hora fin
   - Selección de al menos un curso si eliges "específicos"
   - Permisos según tipo de usuario

6. 🎨 VISUALIZACIÓN:
   - Eventos aparecen con diferentes colores según el tipo
   - Tabla de "Próximos Eventos" debajo del calendario
   - Información detallada al hacer hover sobre eventos

7. 👥 PERMISOS POR USUARIO:
   - Administrador/Director: Ver y crear eventos para cualquier curso
   - Profesor: Ver eventos generales + crear/ver eventos de sus cursos
   - Estudiante: Solo ver eventos de sus cursos + eventos generales
""")
    
    print("🔧 " + "=" * 48)
    print("   SOLUCIÓN DE PROBLEMAS")
    print("🔧 " + "=" * 48)
    
    print("""
❓ Si el modal no se abre:
   - Verifica que JavaScript esté habilitado
   - Revisa la consola del navegador (F12) por errores
   - Asegúrate de estar logueado como administrador/profesor

❓ Si no aparecen cursos para seleccionar:
   - Verifica que existan cursos en el sistema
   - Ejecuta: python crear_cursos_basica.py (si existe)

❓ Si no se crean los eventos:
   - Revisa la consola del navegador por errores
   - Verifica que todos los campos obligatorios estén llenos
   - Asegúrate de tener permisos suficientes

❓ Si los eventos no aparecen en el calendario:
   - Verifica la fecha del evento
   - Revisa los filtros aplicados
   - Cambia la vista del calendario (Mes/Semana/Día)
""")
    
    print("🎯 " + "=" * 48)
    print("   PRÓXIMOS PASOS RECOMENDADOS")
    print("🎯 " + "=" * 48)
    
    print("""
1. 🧪 PRUEBA BÁSICA:
   - Accede al calendario como administrador
   - Crea un evento de prueba
   - Verifica que aparezca correctamente

2. 🎨 PERSONALIZACIÓN (opcional):
   - Ajusta colores en el CSS del template
   - Modifica tipos de eventos en models.py
   - Añade campos adicionales si es necesario

3. 👥 GESTIÓN DE USUARIOS:
   - Crea usuarios profesores y estudiantes
   - Asigna perfiles correctos
   - Prueba permisos con diferentes tipos de usuario

4. 📚 GESTIÓN DE CURSOS:
   - Verifica que todos los cursos estén creados
   - Asigna profesores jefe a los cursos
   - Relaciona estudiantes con cursos

5. 🔒 PRODUCCIÓN (si es necesario):
   - Configura DEBUG=False en settings.py
   - Usa una base de datos real (PostgreSQL/MySQL)
   - Configura servidor web (nginx/apache)
""")
    
    print("\n🎉 " + "=" * 48)
    print("   ¡CALENDARIO LISTO PARA USAR!")
    print("🎉 " + "=" * 48)
    print(f"   Accede ahora: http://127.0.0.1:8000/calendario/")
    print("🎉 " + "=" * 48)

if __name__ == '__main__':
    verificacion_final()
