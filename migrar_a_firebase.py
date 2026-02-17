"""
Script para migrar datos de SQLite a Firebase
Ejecuta este script SOLO si ya tienes datos en cueros.db
"""

import sqlite3
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path

print("🔄 Script de Migración: SQLite → Firebase")
print("=" * 50)

# Verificar que existe cueros.db
DB_PATH = Path(__file__).resolve().parent / "cueros.db"
if not DB_PATH.exists():
    print("❌ No se encontró cueros.db")
    print("✅ No hay datos para migrar. Puedes empezar a usar Firebase directamente.")
    exit()

# Verificar que existe firebase_config.json
FIREBASE_CREDS = Path(__file__).resolve().parent / "firebase_config.json"
if not FIREBASE_CREDS.exists():
    print("❌ Error: firebase_config.json no encontrado")
    print("📝 Por favor, configura Firebase primero (ver FIREBASE_SETUP.md)")
    exit()

try:
    # Inicializar Firebase
    print("\n🔥 Conectando a Firebase...")
    cred = credentials.Certificate(str(FIREBASE_CREDS))
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Conectado a Firebase")

    # Conectar a SQLite
    print("\n📂 Abriendo cueros.db...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print("✅ Base de datos SQLite abierta")

    # Migrar usuarios
    print("\n👥 Migrando usuarios...")
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    for row in usuarios:
        db.collection('usuarios').add({
            'usuario': row[1],
            'password_hash': row[2],
            'rol': row[3],
            'activo': row[4],
            'fecha_creacion': row[5] if len(row) > 5 else None
        })
    print(f"✅ {len(usuarios)} usuarios migrados")

    # Migrar clientes
    print("\n👤 Migrando clientes...")
    try:
        cursor.execute("SELECT * FROM clientes")
        clientes = cursor.fetchall()
        for row in clientes:
            db.collection('clientes').add({
                'nombre': row[1],
                'tipo': row[2] if len(row) > 2 else None,
                'contacto': row[3] if len(row) > 3 else None,
                'telefono': row[4] if len(row) > 4 else None,
                'email': row[5] if len(row) > 5 else None,
                'direccion': row[6] if len(row) > 6 else None,
                'notas': row[7] if len(row) > 7 else None,
                'activo': row[8] if len(row) > 8 else 1,
                'fecha_creacion': row[9] if len(row) > 9 else None
            })
        print(f"✅ {len(clientes)} clientes migrados")
    except sqlite3.OperationalError:
        print("⚠️  Tabla de clientes no existe (OK si es nueva)")

    # Migrar movimientos
    print("\n📦 Migrando movimientos...")
    cursor.execute("SELECT * FROM movimientos")
    movimientos = cursor.fetchall()
    for row in movimientos:
        db.collection('movimientos').add({
            'fecha': row[1],
            'tipo': row[2],
            'producto': row[3] if len(row) > 3 else None,
            'descripcion': row[4] if len(row) > 4 else None,
            'cantidad': row[5] if len(row) > 5 else 0,
            'peso_kg': row[6] if len(row) > 6 else 0.0,
            'precio_total': row[7] if len(row) > 7 else 0.0,
            'neto': row[8] if len(row) > 8 else 0.0,
            'iva_rate': row[9] if len(row) > 9 else 0.0,
            'modo_pago': row[10] if len(row) > 10 else None,
            'detalle_pago': row[11] if len(row) > 11 else None,
            'dinero_a_cuenta': row[12] if len(row) > 12 else 0.0,
            'estado_pago': row[13] if len(row) > 13 else 'Pagado'
        })
    print(f"✅ {len(movimientos)} movimientos migrados")

    # Migrar pagos a cuenta
    print("\n💰 Migrando pagos a cuenta...")
    try:
        cursor.execute("SELECT * FROM pagos_cuenta")
        pagos = cursor.fetchall()
        for row in pagos:
            db.collection('pagos_cuenta').add({
                'fecha': row[1],
                'cliente_nombre': row[2],
                'monto': row[3],
                'concepto': row[4],
                'tipo': row[5]
            })
        print(f"✅ {len(pagos)} pagos a cuenta migrados")
    except sqlite3.OperationalError:
        print("⚠️  Tabla de pagos_cuenta no existe (OK si es nueva)")

    conn.close()

    print("\n" + "=" * 50)
    print("🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
    print("=" * 50)
    print("\n📝 PRÓXIMOS PASOS:")
    print("1. Verifica que los datos estén en Firebase Console")
    print("2. Haz un backup de cueros.db por seguridad")
    print("3. Reinicia la aplicación con: streamlit run gestion_cueros.py")
    print("\n💡 TIP: Puedes renombrar cueros.db a cueros.db.backup")

except Exception as e:
    print(f"\n❌ Error durante la migración: {str(e)}")
    print("Por favor, verifica la configuración e intenta nuevamente")
