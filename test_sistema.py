"""
Script de prueba para verificar el funcionamiento del sistema SMA
"""
import os
import django
import requests
from urllib.parse import urljoin

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

BASE_URL = 'http://127.0.0.1:8000'

def test_url(path, expected_status=200, description=""):
    """Función para probar una URL específica"""
    url = urljoin(BASE_URL, path)
    try:
        response = requests.get(url, timeout=5)
        status = "✅" if response.status_code == expected_status else "❌"
        print(f"{status} {path:<30} | Status: {response.status_code:<3} | {description}")
        return response.status_code == expected_status
    except requests.exceptions.RequestException as e:
        print(f"❌ {path:<30} | Error: {str(e):<20} | {description}")
        return False

def test_login(username, password):
    """Función para probar el login"""
    session = requests.Session()
    
    # Obtener CSRF token
    login_url = urljoin(BASE_URL, '/login/')
    response = session.get(login_url)
    
    if response.status_code != 200:
        print(f"❌ No se pudo acceder a la página de login: {response.status_code}")
        return False
    
    # Buscar CSRF token en el HTML
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    
    if not csrf_token:
        print("❌ No se encontró CSRF token en la página de login")
        return False
    
    # Hacer login
    login_data = {
        'username': username,
        'password': password,
        'csrfmiddlewaretoken': csrf_token['value']
    }
    
    response = session.post(login_url, data=login_data)
    
    if response.status_code == 200 and 'login' not in response.url:
        print(f"✅ Login exitoso con {username}")
        return session
    else:
        print(f"❌ Login fallido con {username}: {response.status_code}")
        return False

def main():
    print("=" * 80)
    print("PRUEBAS DEL SISTEMA SMA")
    print("=" * 80)
    
    # Pruebas básicas de URLs
    print("\n📋 PRUEBAS DE URLs BÁSICAS:")
    test_url('/', description="Página de inicio")
    test_url('/login/', description="Página de login")
    test_url('/admin/', description="Admin de Django")
    
    # Pruebas de páginas protegidas (deberían redirigir a login)
    print("\n🔒 PRUEBAS DE PÁGINAS PROTEGIDAS (esperando redirección 302):")
    test_url('/horarios/', expected_status=302, description="Selección de horarios")
    test_url('/cursos/', expected_status=302, description="Lista de cursos")
    test_url('/calendario/', expected_status=302, description="Calendario")
    test_url('/asignaturas/', expected_status=302, description="Lista de asignaturas")
    
    # Probar login si beautifulsoup está disponible
    try:
        import bs4
        print("\n🔑 PRUEBAS DE LOGIN:")
        session = test_login('admin', 'admin123')
        
        if session:
            print("\n🔓 PRUEBAS DE PÁGINAS AUTENTICADAS:")
            # Usar la sesión autenticada para probar páginas protegidas
            authenticated_urls = [
                '/horarios/',
                '/cursos/',
                '/calendario/',
                '/asignaturas/',
                '/profesores/',
                '/estudiantes/listar/'
            ]
            
            for url in authenticated_urls:
                try:
                    response = session.get(urljoin(BASE_URL, url), timeout=5)
                    status = "✅" if response.status_code == 200 else "❌"
                    print(f"{status} {url:<30} | Status: {response.status_code}")
                except Exception as e:
                    print(f"❌ {url:<30} | Error: {str(e)}")
        
    except ImportError:
        print("\n⚠️  beautifulsoup4 no disponible, saltando pruebas de login")
    
    print("\n" + "=" * 80)
    print("PRUEBAS COMPLETADAS")
    print("=" * 80)

if __name__ == "__main__":
    main()
