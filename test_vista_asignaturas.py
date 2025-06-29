#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
    django.setup()

    from django.contrib.auth.models import User
    from smapp.models import Perfil, Asignatura, HorarioCurso
    from django.test import RequestFactory
    from django.contrib.auth import login
    from smapp.views import listar_asignaturas

    try:
        # Obtener usuario admin
        admin_user = User.objects.get(username='admin')
        print(f"✅ Usuario admin encontrado: {admin_user.username}")
        
        # Crear factory para request mock
        factory = RequestFactory()
        
        # Crear request GET simulado
        request = factory.get('/asignaturas/')
        request.user = admin_user
        
        print("\n--- Probando vista listar_asignaturas ---")
        
        try:
            # Llamar a la vista
            response = listar_asignaturas(request)
            print(f"✅ Vista ejecutada exitosamente")
            print(f"  - Status code: {response.status_code}")
            
            # Verificar contenido del contexto
            if hasattr(response, 'context_data'):
                context = response.context_data
                if 'asignaturas' in context:
                    print(f"  - Asignaturas en contexto: {len(context['asignaturas'])}")
                if 'tipo_usuario' in context:
                    print(f"  - Tipo usuario detectado: {context['tipo_usuario']}")
                if 'puede_gestionar' in context:
                    print(f"  - Puede gestionar: {context['puede_gestionar']}")
        
        except Exception as e:
            print(f"❌ Error en vista: {e}")
            import traceback
            traceback.print_exc()
        
        # Verificar datos existentes
        print("\n--- Verificando datos existentes ---")
        asignaturas_count = Asignatura.objects.count()
        horarios_count = HorarioCurso.objects.count()
        print(f"  - Asignaturas en BD: {asignaturas_count}")
        print(f"  - Horarios en BD: {horarios_count}")
        
        if asignaturas_count > 0:
            asignatura = Asignatura.objects.first()
            print(f"  - Primera asignatura: {asignatura.nombre}")
            print(f"  - Código: {asignatura.codigo_asignatura}")
            if asignatura.profesor_responsable:
                print(f"  - Profesor: {asignatura.profesor_responsable}")
            else:
                print(f"  - Sin profesor asignado")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
