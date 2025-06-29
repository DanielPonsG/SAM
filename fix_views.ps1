$content = Get-Content 'c:\Users\Danie\Desktop\SMA-main\smapp\views.py'
$content = $content -replace "'dia_semana': horario.dia_semana", "'dia': horario.dia"
$content = $content -replace "horario.dia_semana", "horario.dia"
$content | Set-Content 'c:\Users\Danie\Desktop\SMA-main\smapp\views.py'
