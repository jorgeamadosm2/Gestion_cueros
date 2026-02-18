# 🔥 Configuración de Firebase - Múltiples Opciones

Esta aplicación soporta **tres métodos** para configurar las credenciales de Firebase. Elige el que mejor se adapte a tu caso:

## 📋 Opción 1: Archivo JSON (Recomendado para Desarrollo Local)

### Pasos:
1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Selecciona tu proyecto
3. Ve a **Configuración del proyecto** (ícono de engranaje) → **Cuentas de servicio**
4. Haz clic en **"Generar nueva clave privada"**
5. Descarga el archivo JSON
6. **Renombra** el archivo a `firebase_config.json`
7. **Copia** el archivo a la raíz del proyecto

### Ventajas:
✅ Fácil de configurar para desarrollo local  
✅ No requiere configuración adicional  
✅ Ideal para pruebas locales

### Desventajas:
⚠️ No debe subirse a GitHub  
⚠️ No funciona en algunos servicios de deployment

---

## ☁️ Opción 2: Streamlit Secrets (Recomendado para Deployment)

### Pasos:
1. Crea el archivo `.streamlit/secrets.toml` (si no existe)
2. Copia el contenido de `.streamlit/secrets.toml.example`
3. Completa con tus credenciales de Firebase
4. Guarda el archivo

### Ejemplo de `.streamlit/secrets.toml`:
```toml
[firebase]
type = "service_account"
project_id = "tu-proyecto-id"
private_key_id = "tu-private-key-id"
private_key = """-----BEGIN PRIVATE KEY-----
TU_PRIVATE_KEY_AQUI
-----END PRIVATE KEY-----
"""
client_email = "tu-service-account@tu-proyecto.iam.gserviceaccount.com"
client_id = "tu-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/tu-service-account%40tu-proyecto.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

### Ventajas:
✅ Ideal para Streamlit Cloud y otros deployments  
✅ Más seguro que archivos JSON  
✅ Soportado nativamente por Streamlit

### Para Streamlit Cloud:
1. Ve a tu app en Streamlit Cloud
2. Click en **"⚙️ Settings"** → **"Secrets"**
3. Pega el contenido del archivo `secrets.toml`
4. Guarda los cambios

---

## 🔐 Opción 3: Variables de Entorno

### Variables requeridas:
```bash
FIREBASE_TYPE="service_account"
FIREBASE_PROJECT_ID="tu-proyecto-id"
FIREBASE_PRIVATE_KEY_ID="tu-private-key-id"
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nTU_KEY\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL="tu-service-account@tu-proyecto.iam.gserviceaccount.com"
FIREBASE_CLIENT_ID="tu-client-id"
FIREBASE_AUTH_URI="https://accounts.google.com/o/oauth2/auth"
FIREBASE_TOKEN_URI="https://oauth2.googleapis.com/token"
FIREBASE_AUTH_PROVIDER_CERT_URL="https://www.googleapis.com/oauth2/v1/certs"
FIREBASE_CLIENT_CERT_URL="https://www.googleapis.com/robot/v1/metadata/x509/..."
FIREBASE_UNIVERSE_DOMAIN="googleapis.com"
```

### En Linux/Mac:
```bash
export FIREBASE_PROJECT_ID="tu-proyecto-id"
export FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----..."
# ... más variables
```

### En Windows (PowerShell):
```powershell
$env:FIREBASE_PROJECT_ID="tu-proyecto-id"
$env:FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----..."
# ... más variables
```

### Ventajas:
✅ Funciona en cualquier entorno  
✅ Ideal para CI/CD  
✅ No requiere archivos

### Desventajas:
⚠️ Más complejo de configurar  
⚠️ Puede ser difícil manejar el private_key multilinea

---

## 🚀 Iniciar la Aplicación

Una vez configurado cualquiera de los métodos anteriores:

```bash
streamlit run gestion_cueros.py
```

O si usas un entorno virtual:

```bash
.venv/Scripts/streamlit run gestion_cueros.py  # Windows
source .venv/bin/activate && streamlit run gestion_cueros.py  # Linux/Mac
```

---

## ✅ Verificación

Si la configuración es correcta, verás:
- ✅ "Conectado a Firebase" en la barra lateral
- Sin mensajes de error
- La aplicación carga normalmente

---

## 🔒 Seguridad - MUY IMPORTANTE

### ⚠️ NO subas credenciales a GitHub:

Los siguientes archivos **YA ESTÁN** en `.gitignore`:
- `firebase_config.json`
- `.streamlit/secrets.toml`

**NUNCA:**
- Subas credenciales de Firebase a GitHub
- Compartas tus credenciales públicamente
- Uses credenciales de producción en desarrollo

---

## 🆘 Solución de Problemas

### Error: "No se encontraron credenciales de Firebase"
**Solución:** Configura al menos uno de los tres métodos anteriores.

### Error: "Error al leer firebase_config.json"
**Solución:** 
- Verifica que el archivo exista en la raíz del proyecto
- Verifica que el JSON sea válido
- Revisa que el nombre sea exactamente `firebase_config.json`

### Error: "Error al leer secrets de Streamlit"
**Solución:**
- Verifica que `.streamlit/secrets.toml` exista
- Verifica que el formato TOML sea correcto
- Asegúrate de que la sección `[firebase]` esté presente

### Error de conexión a Firebase
**Solución:**
- Verifica tu conexión a internet
- Verifica que las credenciales sean correctas
- Revisa la consola de Firebase para ver si hay problemas con el proyecto

---

## 📚 Recursos Adicionales

- [Documentación de Firebase](https://firebase.google.com/docs)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Firestore Python SDK](https://firebase.google.com/docs/firestore/quickstart)

---

## 🎯 Recomendaciones por Escenario

| Escenario | Método Recomendado |
|-----------|-------------------|
| Desarrollo Local | Opción 1: `firebase_config.json` |
| Streamlit Cloud | Opción 2: Streamlit Secrets |
| Heroku/Railway/etc | Opción 3: Variables de Entorno |
| Docker | Opción 2 o 3 |
| CI/CD | Opción 3: Variables de Entorno |

---

**¡Elige el método que mejor se adapte a tu entorno y comienza a usar la aplicación! 🎉**
