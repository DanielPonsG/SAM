@echo off
echo === INICIANDO SERVIDOR DE PRUEBA ===
echo.

cd /d "c:\Users\Danie\Desktop\SMA-main"

echo Arreglando eventos sin usuario...
python arreglar_eventos.py

echo.
echo Iniciando servidor Django...
echo Abre tu navegador en: http://localhost:8000/calendario/
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python manage.py runserver 127.0.0.1:8000
