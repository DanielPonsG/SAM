#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Perfil

print("Usuarios y perfiles existentes:")
print("-" * 40)

for user in User.objects.all():
    try:
        perfil = user.perfil
        print(f"{user.username}: {perfil.tipo_usuario}")
    except:
        print(f"{user.username}: SIN PERFIL")

print("\nConteo por tipo:")
print("-" * 20)
tipos = ['director', 'profesor', 'alumno']
for tipo in tipos:
    count = Perfil.objects.filter(tipo_usuario=tipo).count()
    print(f"{tipo}: {count}")
