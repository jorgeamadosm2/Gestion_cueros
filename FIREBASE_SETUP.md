# 🔥 Configuración de Firebase para Gestión de Cueros

## 📋 Requisitos Previos
- Cuenta de Google
- Python instalado
- Conexión a internet

## 🚀 Pasos de Configuración

### 1. Crear Proyecto en Firebase

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Haz clic en **"Agregar proyecto"**
3. Nombre del proyecto: `gestion-cueros` (o el que prefieras)
4. Desactiva Google Analytics (opcional)
5. Haz clic en **"Crear proyecto"**

### 2. Habilitar Firestore Database

1. En el panel lateral, haz clic en **"Firestore Database"**
2. Haz clic en **"Crear base de datos"**
3. Selecciona **"Producción"**
4. Elige la ubicación más cercana (por ejemplo: `southamerica-east1`)
5. Haz clic en **"Habilitar"**

### 3. Configurar Reglas de Seguridad

En la pestaña **"Reglas"** de Firestore, pega estas reglas:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

⚠️ **IMPORTANTE**: Estas reglas permiten acceso completo. Para producción, debes implementar reglas más restrictivas.

### 4. Obtener Credenciales de Firebase

1. Ve a **Configuración del proyecto** (ícono de engranaje)
2. Pestaña **"Cuentas de servicio"**
3. Haz clic en **"Generar nueva clave privada"**
4. Se descargará un archivo JSON
5. **Renombra** el archivo a `firebase_config.json`
6. **Mueve** el archivo a la carpeta del proyecto:
   ```
   C:\Users\jorge\OneDrive\Escritorio\sistema_cueros\firebase_config.json
   ```

### 5. Instalar Dependencias

Abre PowerShell en la carpeta del proyecto y ejecuta:

```powershell
.venv\Scripts\activate
pip install firebase-admin
```

O reinstala todas las dependencias:

```powershell
pip install -r requirements.txt
```

### 6. Iniciar la Aplicación

```powershell
.venv\Scripts\streamlit run gestion_cueros.py
```

## ✅ Verificación

Si todo está correcto, verás:
- ✅ "Conectado a Firebase" en el sidebar
- Contadores de usuarios, clientes, movimientos y pagos
- No hay mensajes de error

## 🔒 Seguridad

### ⚠️ MUY IMPORTANTE

1. **NO subas `firebase_config.json` a GitHub o repositorios públicos**
2. Agrega este archivo al `.gitignore`:
   ```
   firebase_config.json
   ```

3. Para reglas de seguridad en producción, usa algo como:
   ```javascript
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /{document=**} {
         allow read, write: if request.auth != null;
       }
     }
   }
   ```

## 💰 Límites del Plan Gratuito (Spark)

Firebase ofrece un plan gratuito generoso:

- **Lecturas**: 50,000 por día
- **Escrituras**: 20,000 por día
- **Eliminaciones**: 20,000 por día
- **Almacenamiento**: 1 GB

Para una gestión pequeña/mediana, esto es más que suficiente.

## 🔄 Migrar Datos de SQLite a Firebase (Opcional)

Si ya tienes datos en `cueros.db`, puedes crear un script para migrarlos:

```python
import sqlite3
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path

# Inicializar Firebase
cred = credentials.Certificate('firebase_config.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Conectar SQLite
conn = sqlite3.connect('cueros.db')
cursor = conn.cursor()

# Migrar usuarios
cursor.execute("SELECT * FROM usuarios")
for row in cursor.fetchall():
    db.collection('usuarios').add({
        'usuario': row[1],
        'password_hash': row[2],
        'rol': row[3],
        'activo': row[4],
        'fecha_creacion': row[5]
    })

print("Migración completada")
```

## 🆘 Solución de Problemas

### Error: "firebase_config.json no encontrado"
- Verifica que el archivo esté en la carpeta correcta
- Verifica que se llame exactamente `firebase_config.json`

### Error: "Could not resolve firebase_admin"
- Instala el paquete: `pip install firebase-admin`

### Error de conexión a Firebase
- Verifica tu conexión a internet
- Verifica que las credenciales sean correctas
- Revisa la consola de Firebase para ver si hay problemas

## 📚 Recursos

- [Documentación de Firebase](https://firebase.google.com/docs)
- [Firestore Python SDK](https://firebase.google.com/docs/firestore/quickstart)
- [Consola de Firebase](https://console.firebase.google.com/)

## ✨ Ventajas de Firebase

✅ Almacenamiento en la nube (accesible desde cualquier lugar)
✅ Sincronización automática
✅ Backups automáticos
✅ Escalable
✅ Sin necesidad de servidor propio
✅ Plan gratuito generoso

---

**¡Tu sistema ahora está en la nube! 🎉**
