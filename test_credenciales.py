import json
import os
from pathlib import Path

print("🔍 Verificando configuración de Firebase...\n")

# Verificar archivo firebase_config.json
firebase_file = Path("firebase_config.json")
if firebase_file.exists():
    print("✅ firebase_config.json existe")
    try:
        with open(firebase_file, 'r') as f:
            data = json.load(f)
        print(f"✅ JSON válido")
        print(f"   Project ID: {data.get('project_id')}")
        print(f"   Client Email: {data.get('client_email')}")
        print(f"   Tiene private_key: {'Sí' if data.get('private_key') else 'No'}")
    except Exception as e:
        print(f"❌ Error leyendo JSON: {e}")
else:
    print("❌ firebase_config.json NO existe")

print("\n" + "="*50)

# Verificar si Streamlit puede leerlo
print("\n🔍 Probando carga de credenciales (como lo hace la app)...\n")

try:
    import streamlit as st
    print("✅ Streamlit importado")
    
    # Intentar leer secrets
    try:
        if hasattr(st, 'secrets') and 'firebase' in st.secrets:
            print("✅ st.secrets['firebase'] disponible")
        else:
            print("⚠️  st.secrets['firebase'] NO disponible (normal en CLI)")
    except Exception as e:
        print(f"⚠️  No se pueden leer secrets: {e}")
    
    # Intentar leer archivo
    if firebase_file.exists():
        with open(firebase_file, 'r') as f:
            creds = json.load(f)
        print("✅ Archivo firebase_config.json se puede leer")
        
        # Verificar campos requeridos
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 
                          'client_email', 'client_id']
        missing = [f for f in required_fields if f not in creds]
        
        if missing:
            print(f"❌ Campos faltantes: {missing}")
        else:
            print("✅ Todos los campos requeridos presentes")
            
except ImportError as e:
    print(f"⚠️  Streamlit no instalado o no disponible: {e}")

print("\n" + "="*50)
print("\n💡 Diagnóstico:")
print("   Si ves ✅ en todos los checks, las credenciales están OK")
print("   El error puede ser porque la app ya estaba corriendo")
print("   Solución: Recarga la página de Streamlit (F5 o Ctrl+R)")
