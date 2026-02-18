#!/usr/bin/env python3
"""
Script para verificar que Firestore esté habilitado y funcionando.
"""
import time
import sys
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore

FIREBASE_CREDS = Path(__file__).resolve().parent / "firebase_config.json"

def verificar_firestore():
    """Intenta conectar a Firestore y verifica que funcione."""
    print("🔍 Verificando conexión a Firebase Firestore...")
    print(f"📄 Archivo de credenciales: {FIREBASE_CREDS}")
    
    if not FIREBASE_CREDS.exists():
        print("❌ ERROR: firebase_config.json no encontrado")
        return False
    
    try:
        # Inicializar Firebase
        if not firebase_admin._apps:
            cred = credentials.Certificate(str(FIREBASE_CREDS))
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        
        # Intentar una operación simple
        print("⏳ Intentando conectar a Firestore...")
        test_collection = db.collection('_test_connection')
        test_collection.add({'timestamp': time.time()})
        
        # Si llegamos aquí, funcionó
        print("✅ ¡CONEXIÓN EXITOSA!")
        print("✅ Firestore está habilitado y funcionando correctamente")
        
        # Limpiar documento de prueba
        for doc in test_collection.stream():
            doc.reference.delete()
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "SERVICE_DISABLED" in error_msg or "403" in error_msg:
            print("❌ ERROR: Firestore API no está habilitada")
            print()
            print("📋 DEBES HABILITAR FIRESTORE:")
            print("👉 https://console.firebase.google.com/project/gestion-de-cueros/firestore")
            print()
            print("Pasos:")
            print("1. Haz clic en 'Create database' (Crear base de datos)")
            print("2. Selecciona 'Production mode' (Modo de producción)")
            print("3. Selecciona ubicación: southamerica-east1")
            print("4. Haz clic en 'Enable' (Habilitar)")
            print("5. Espera 2-3 minutos")
            print()
        else:
            print(f"❌ ERROR: {error_msg}")
        
        return False

def modo_espera():
    """Modo que espera hasta que Firestore esté disponible."""
    print("\n🔄 MODO ESPERA ACTIVADO")
    print("Este script verificará automáticamente cada 30 segundos...")
    print("Presiona Ctrl+C para cancelar")
    print()
    
    intentos = 0
    while True:
        intentos += 1
        print(f"\n⏳ Intento #{intentos} - {time.strftime('%H:%M:%S')}")
        
        if verificar_firestore():
            print("\n" + "="*50)
            print("🎉 ¡FIRESTORE ESTÁ LISTO!")
            print("="*50)
            print()
            print("Ahora puedes:")
            print("1. Ir a http://localhost:8501")
            print("2. Refrescar tu navegador (Ctrl + Shift + R)")
            print("3. ¡Usar tu aplicación!")
            break
        
        print(f"⏰ Esperando 30 segundos antes del próximo intento...")
        time.sleep(30)

if __name__ == "__main__":
    print("="*60)
    print("🔧 VERIFICADOR DE FIRESTORE")
    print("="*60)
    print()
    
    # Primera verificación
    if verificar_firestore():
        print("\n✅ Todo está funcionando correctamente")
        sys.exit(0)
    
    # Preguntar si quiere modo espera
    print("\n¿Quieres que verifique automáticamente hasta que funcione?")
    print("(Debes habilitar Firestore en Firebase Console primero)")
    respuesta = input("Escribe 'si' para continuar, o Enter para salir: ").strip().lower()
    
    if respuesta in ['si', 'sí', 's', 'yes', 'y']:
        try:
            modo_espera()
        except KeyboardInterrupt:
            print("\n\n👋 Verificación cancelada por el usuario")
            sys.exit(1)
    else:
        print("\n👋 Saliendo...")
        sys.exit(1)
