#!/usr/bin/env python3
"""
Script para probar la funcionalidad completa del calendario
Incluye: creación de eventos, validación de permisos, y verificación de funcionalidad
"""

import os
import sys
import django
from datetime import datetime, date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from smapp.models import EventoCalendario, Curso, Profesor, Estudiante
import json

class TestCalendarioCompleto:
    def __init__(self):
        self.client = Client()
        self.resultados = []
        
    def log(self, mensaje, tipo="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {tipo}: {mensaje}")
        self.resultados.append(f"{tipo}: {mensaje}")
        
    def test_acceso_calendario_sin_login(self):
        """Test: Acceso al calendario sin login debe redirigir"""
        try:
            response = self.client.get('/calendario/')
            if response.status_code == 302:  # Redirección esperada
                self.log("✅ Acceso sin login correctamente restringido", "PASS")
                return True
            else:
                self.log(f"❌ Acceso sin login no redirige (código: {response.status_code})", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ Error al probar acceso sin login: {e}", "ERROR")
            return False
    
    def test_login_admin(self):
        """Test: Login como administrador"""
        try:
            # Crear usuario admin si no existe
            admin_user, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@test.com',
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            if created:
                admin_user.set_password('admin123')
                admin_user.save()
                self.log("✅ Usuario admin creado", "INFO")
            
            # Intentar login
            login_success = self.client.login(username='admin', password='admin123')
            if login_success:
                self.log("✅ Login admin exitoso", "PASS")
                return True
            else:
                self.log("❌ Login admin fallido", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ Error en login admin: {e}", "ERROR")
            return False
    
    def test_acceso_calendario_admin(self):
        """Test: Acceso al calendario como administrador"""
        try:
            response = self.client.get('/calendario/')
            if response.status_code == 200:
                # Verificar contenido del template
                content = response.content.decode('utf-8')
                
                checks = [
                    ('modalCrearEvento', 'Modal de crear evento presente'),
                    ('formCrearEvento', 'Formulario de crear evento presente'),
                    ('Nuevo Evento', 'Botón nuevo evento presente'),
                    ('FullCalendar', 'Biblioteca FullCalendar cargada'),
                    ('dirigido_a', 'Opciones de dirigido a presentes')
                ]
                
                all_checks_passed = True
                for check, description in checks:
                    if check in content:
                        self.log(f"✅ {description}", "CHECK")
                    else:
                        self.log(f"❌ {description}", "CHECK")
                        all_checks_passed = False
                
                if all_checks_passed:
                    self.log("✅ Calendario accesible para admin con todos los elementos", "PASS")
                    return True
                else:
                    self.log("❌ Calendario accesible pero faltan elementos", "FAIL")
                    return False
            else:
                self.log(f"❌ Calendario no accesible (código: {response.status_code})", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ Error al acceder al calendario: {e}", "ERROR")
            return False
    
    def test_crear_evento_todos_los_cursos(self):
        """Test: Crear evento para todos los cursos"""
        try:
            fecha_evento = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
            
            data = {
                'titulo': 'Evento Prueba - Todos los Cursos',
                'descripcion': 'Descripción del evento de prueba',
                'fecha': fecha_evento,
                'hora_inicio': '08:00',
                'hora_fin': '10:00',
                'tipo_evento': 'general',
                'prioridad': 'alta',
                'dirigido_a': 'todos'
            }
            
            response = self.client.post(
                '/calendario/',
                data,
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            
            if response.status_code == 200:
                response_data = json.loads(response.content)
                if response_data.get('success'):
                    self.log("✅ Evento 'todos los cursos' creado exitosamente", "PASS")
                    return True
                else:
                    self.log(f"❌ Error al crear evento: {response_data.get('error', 'Error desconocido')}", "FAIL")
                    return False
            else:
                self.log(f"❌ Error HTTP al crear evento (código: {response.status_code})", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ Error al crear evento para todos: {e}", "ERROR")
            return False
    
    def test_crear_evento_solo_profesores(self):
        """Test: Crear evento solo para profesores"""
        try:
            fecha_evento = (date.today() + timedelta(days=2)).strftime('%Y-%m-%d')
            
            data = {
                'titulo': 'Reunión de Profesores',
                'descripcion': 'Reunión mensual de profesores',
                'fecha': fecha_evento,
                'hora_inicio': '14:00',
                'hora_fin': '16:00',
                'tipo_evento': 'administrativo',
                'prioridad': 'alta',
                'dirigido_a': 'solo_profesores'
            }
            
            response = self.client.post(
                '/calendario/',
                data,
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            
            if response.status_code == 200:
                response_data = json.loads(response.content)
                if response_data.get('success'):
                    self.log("✅ Evento 'solo profesores' creado exitosamente", "PASS")
                    return True
                else:
                    self.log(f"❌ Error al crear evento: {response_data.get('error', 'Error desconocido')}", "FAIL")
                    return False
            else:
                self.log(f"❌ Error HTTP al crear evento (código: {response.status_code})", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ Error al crear evento solo profesores: {e}", "ERROR")
            return False
    
    def test_crear_evento_cursos_especificos(self):
        """Test: Crear evento para cursos específicos"""
        try:
            # Crear cursos de prueba si no existen
            curso1, created1 = Curso.objects.get_or_create(
                nivel='1B',
                paralelo='A',
                anio=2025
            )
            
            curso2, created2 = Curso.objects.get_or_create(
                nivel='2B',
                paralelo='B',
                anio=2025
            )
            
            if created1 or created2:
                self.log("✅ Cursos de prueba creados", "INFO")
            
            fecha_evento = (date.today() + timedelta(days=3)).strftime('%Y-%m-%d')
            
            data = {
                'titulo': 'Evento Cursos Específicos',
                'descripcion': 'Evento para cursos seleccionados',
                'fecha': fecha_evento,
                'hora_inicio': '09:00',
                'hora_fin': '11:00',
                'tipo_evento': 'academico',
                'prioridad': 'media',
                'dirigido_a': 'cursos_especificos',
                'cursos_especificos': [str(curso1.id), str(curso2.id)]
            }
            
            response = self.client.post(
                '/calendario/',
                data,
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            
            if response.status_code == 200:
                response_data = json.loads(response.content)
                if response_data.get('success'):
                    self.log("✅ Evento 'cursos específicos' creado exitosamente", "PASS")
                    return True
                else:
                    self.log(f"❌ Error al crear evento: {response_data.get('error', 'Error desconocido')}", "FAIL")
                    return False
            else:
                self.log(f"❌ Error HTTP al crear evento (código: {response.status_code})", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ Error al crear evento cursos específicos: {e}", "ERROR")
            return False
    
    def test_validacion_horas(self):
        """Test: Validación de horas (hora inicio >= hora fin)"""
        try:
            fecha_evento = (date.today() + timedelta(days=4)).strftime('%Y-%m-%d')
            
            data = {
                'titulo': 'Evento Horas Inválidas',
                'descripcion': 'Test de validación',
                'fecha': fecha_evento,
                'hora_inicio': '10:00',
                'hora_fin': '08:00',  # Hora fin menor que hora inicio
                'tipo_evento': 'general',
                'prioridad': 'media',
                'dirigido_a': 'todos'
            }
            
            response = self.client.post(
                '/calendario/',
                data,
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            
            if response.status_code == 200:
                response_data = json.loads(response.content)
                if not response_data.get('success') and 'hora' in response_data.get('error', '').lower():
                    self.log("✅ Validación de horas funciona correctamente", "PASS")
                    return True
                else:
                    self.log("❌ Validación de horas no funciona correctamente", "FAIL")
                    return False
            else:
                self.log(f"❌ Error HTTP en validación de horas (código: {response.status_code})", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ Error en test de validación de horas: {e}", "ERROR")
            return False
    
    def test_validacion_campos_obligatorios(self):
        """Test: Validación de campos obligatorios"""
        try:
            # Test sin título
            data = {
                'titulo': '',  # Campo obligatorio vacío
                'descripcion': 'Test sin título',
                'fecha': (date.today() + timedelta(days=5)).strftime('%Y-%m-%d'),
                'tipo_evento': 'general',
                'prioridad': 'media',
                'dirigido_a': 'todos'
            }
            
            response = self.client.post(
                '/calendario/',
                data,
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            
            if response.status_code == 200:
                response_data = json.loads(response.content)
                if not response_data.get('success') and 'título' in response_data.get('error', '').lower():
                    self.log("✅ Validación de título obligatorio funciona", "PASS")
                    return True
                else:
                    self.log("❌ Validación de título obligatorio no funciona", "FAIL")
                    return False
            else:
                self.log(f"❌ Error HTTP en validación de campos (código: {response.status_code})", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ Error en test de validación de campos: {e}", "ERROR")
            return False
    
    def test_eventos_en_calendario(self):
        """Test: Verificar que los eventos aparecen en el calendario"""
        try:
            response = self.client.get('/calendario/')
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                
                # Verificar que existe el JavaScript con datos de eventos
                if 'eventosData' in content or 'eventos_json' in content:
                    self.log("✅ Datos de eventos presentes en el calendario", "PASS")
                    
                    # Verificar que hay eventos creados
                    eventos_count = EventoCalendario.objects.count()
                    self.log(f"📊 Total de eventos en BD: {eventos_count}", "INFO")
                    
                    if eventos_count > 0:
                        self.log("✅ Eventos disponibles para mostrar", "PASS")
                        return True
                    else:
                        self.log("⚠️ No hay eventos para mostrar", "WARN")
                        return True  # No es un error, simplemente no hay eventos
                else:
                    self.log("❌ Datos de eventos no encontrados en el template", "FAIL")
                    return False
            else:
                self.log(f"❌ Error al acceder al calendario (código: {response.status_code})", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ Error al verificar eventos en calendario: {e}", "ERROR")
            return False
    
    def test_resumen_eventos(self):
        """Test: Mostrar resumen de eventos creados"""
        try:
            eventos = EventoCalendario.objects.all().order_by('fecha')
            
            self.log("📋 RESUMEN DE EVENTOS CREADOS:", "INFO")
            self.log("=" * 50, "INFO")
            
            for evento in eventos:
                audiencia = "Todos los cursos" if evento.para_todos_los_cursos else \
                           "Solo profesores" if evento.solo_profesores else \
                           f"Cursos específicos ({evento.cursos.count()})"
                
                horario = ""
                if evento.hora_inicio and evento.hora_fin:
                    horario = f" ({evento.hora_inicio.strftime('%H:%M')} - {evento.hora_fin.strftime('%H:%M')})"
                
                self.log(f"• {evento.titulo}", "INFO")
                self.log(f"  Fecha: {evento.fecha.strftime('%d/%m/%Y')}{horario}", "INFO")
                self.log(f"  Audiencia: {audiencia}", "INFO")
                self.log(f"  Tipo: {evento.get_tipo_evento_display()}", "INFO")
                self.log("", "INFO")
            
            return True
        except Exception as e:
            self.log(f"❌ Error al generar resumen: {e}", "ERROR")
            return False
    
    def ejecutar_todas_las_pruebas(self):
        """Ejecutar todas las pruebas"""
        self.log("🚀 INICIANDO PRUEBAS COMPLETAS DEL CALENDARIO", "INFO")
        self.log("=" * 60, "INFO")
        
        tests = [
            ("Acceso sin login", self.test_acceso_calendario_sin_login),
            ("Login como admin", self.test_login_admin),
            ("Acceso calendario admin", self.test_acceso_calendario_admin),
            ("Crear evento todos los cursos", self.test_crear_evento_todos_los_cursos),
            ("Crear evento solo profesores", self.test_crear_evento_solo_profesores),
            ("Crear evento cursos específicos", self.test_crear_evento_cursos_especificos),
            ("Validación de horas", self.test_validacion_horas),
            ("Validación campos obligatorios", self.test_validacion_campos_obligatorios),
            ("Eventos en calendario", self.test_eventos_en_calendario),
            ("Resumen de eventos", self.test_resumen_eventos)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            self.log(f"\n🔍 Ejecutando: {test_name}", "TEST")
            try:
                result = test_func()
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log(f"❌ Error en {test_name}: {e}", "ERROR")
                failed += 1
        
        # Resumen final
        self.log("\n" + "=" * 60, "INFO")
        self.log("📊 RESUMEN FINAL DE PRUEBAS", "INFO")
        self.log("=" * 60, "INFO")
        self.log(f"✅ Pruebas pasadas: {passed}", "INFO")
        self.log(f"❌ Pruebas fallidas: {failed}", "INFO")
        self.log(f"📈 Porcentaje de éxito: {(passed/(passed+failed)*100):.1f}%", "INFO")
        
        if failed == 0:
            self.log("🎉 ¡TODAS LAS PRUEBAS PASARON! El calendario está funcionando correctamente.", "SUCCESS")
        else:
            self.log("⚠️ Algunas pruebas fallaron. Revisa los logs para más detalles.", "WARN")
        
        return failed == 0

if __name__ == "__main__":
    print("🔧 Iniciando pruebas del calendario...")
    
    tester = TestCalendarioCompleto()
    success = tester.ejecutar_todas_las_pruebas()
    
    if success:
        print("\n✅ Todas las pruebas completadas exitosamente!")
        sys.exit(0)
    else:
        print("\n❌ Algunas pruebas fallaron. Revisa los logs.")
        sys.exit(1)
