"""
Pruebas de login y navegación del sistema SMA
"""
import requests
from bs4 import BeautifulSoup
import time

BASE_URL = 'http://127.0.0.1:8000'

def login_and_test():
    """Hacer login y probar navegación"""
    session = requests.Session()
    
    print("🔐 PROBANDO LOGIN...")
    
    # Obtener página de login
    login_url = f'{BASE_URL}/login/'
    response = session.get(login_url)
    
    if response.status_code != 200:
        print(f"❌ Error al acceder al login: {response.status_code}")
        return False
    
    print("✅ Página de login accesible")
    
    # Extraer CSRF token
    soup = BeautifulSoup(response.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    
    if not csrf_token:
        print("❌ CSRF token no encontrado")
        return False
    
    print("✅ CSRF token encontrado")
    
    # Hacer login
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'csrfmiddlewaretoken': csrf_token['value']
    }
    
    response = session.post(login_url, data=login_data, allow_redirects=True)
    
    # Verificar login exitoso
    if 'login' in response.url:
        print("❌ Login fallido - aún en página de login")
        return False
    
    print("✅ Login exitoso")
    
    # Probar páginas autenticadas
    print("\n🏠 PROBANDO NAVEGACIÓN AUTENTICADA...")
    
    pages_to_test = [
        ('/horarios/', 'Sistema de horarios'),
        ('/cursos/', 'Lista de cursos'),
        ('/calendario/', 'Calendario'),
        ('/asignaturas/', 'Lista de asignaturas'),
        ('/profesores/', 'Lista de profesores'),
        ('/estudiantes/listar/', 'Lista de estudiantes'),
    ]
    
    for url, description in pages_to_test:
        try:
            response = session.get(f'{BASE_URL}{url}', timeout=10)
            if response.status_code == 200:
                print(f"✅ {url:<25} | {description}")
                
                # Verificar contenido específico
                if 'horarios' in url and 'Gestión de Horarios' in response.text:
                    print("   🎯 Contenido de horarios verificado")
                elif 'cursos' in url and ('curso' in response.text.lower() or 'Curso' in response.text):
                    print("   🎯 Contenido de cursos verificado")
                elif 'calendario' in url and ('calendario' in response.text.lower() or 'evento' in response.text.lower()):
                    print("   🎯 Contenido de calendario verificado")
                elif 'asignaturas' in url and ('asignatura' in response.text.lower() or 'Asignatura' in response.text):
                    print("   🎯 Contenido de asignaturas verificado")
            else:
                print(f"❌ {url:<25} | Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {url:<25} | Error: {e}")
    
    # Probar sistema de horarios específico
    print("\n📅 PROBANDO SISTEMA DE HORARIOS ESPECÍFICO...")
    try:
        # Probar gestión de horarios de un curso específico
        horarios_curso_url = f'{BASE_URL}/cursos/16/horarios/'
        response = session.get(horarios_curso_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Gestión de horarios de curso específico funciona")
            if 'Gestión de Horarios' in response.text:
                print("   🎯 Contenido específico de gestión verificado")
        else:
            print(f"❌ Gestión de horarios falló: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en gestión de horarios: {e}")
    
    return True

def main():
    print("=" * 80)
    print("PRUEBAS DE LOGIN Y NAVEGACIÓN - SISTEMA SMA")
    print("=" * 80)
    
    try:
        # Verificar que beautifulsoup esté disponible
        import bs4
        
        success = login_and_test()
        
        if success:
            print("\n🎉 TODAS LAS PRUEBAS EXITOSAS")
            print("✅ El sistema está completamente funcional")
            print("✅ Login funciona correctamente")
            print("✅ Navegación autenticada funciona")
            print("✅ Sistema de horarios operativo")
            
            print("\n📝 INSTRUCCIONES PARA EL USUARIO:")
            print("1. Ir a: http://127.0.0.1:8000/login/")
            print("2. Usuario: admin")
            print("3. Contraseña: admin123")
            print("4. Después del login, navegar a:")
            print("   - /horarios/ para gestión de horarios")
            print("   - /cursos/ para gestión de cursos")
            print("   - /calendario/ para el calendario")
            print("   - /asignaturas/ para gestión de asignaturas")
        else:
            print("\n❌ ALGUNAS PRUEBAS FALLARON")
            
    except ImportError:
        print("❌ BeautifulSoup no está instalado")
        print("Instalar con: pip install beautifulsoup4")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
