# 🚀 Desplegar en Streamlit Cloud

Esta guía te ayudará a subir tu aplicación de Gestión de Cueros a Streamlit Cloud para acceder desde cualquier dispositivo (teléfono, tablet, computadora).

## 📋 Requisitos Previos

1. ✅ Cuenta de GitHub (gratuita) - [Crear cuenta](https://github.com/signup)
2. ✅ Cuenta de Streamlit Cloud (gratuita) - [Crear cuenta](https://share.streamlit.io/signup)
3. ✅ Tus credenciales de Firebase (archivo `firebase_config.json`)

---

## 🔧 Paso 1: Subir el Código a GitHub

### 1.1 Inicializar Git (si no está hecho)

Abre PowerShell en la carpeta de tu proyecto y ejecuta:

```powershell
git init
git add .
git commit -m "Primera versión - Sistema de Gestión de Cueros"
```

### 1.2 Crear Repositorio en GitHub

1. Ve a [GitHub](https://github.com) e inicia sesión
2. Haz clic en el botón verde **"New"** (Nuevo repositorio)
3. Nombre del repositorio: `sistema-gestion-cueros` (o el que prefieras)
4. Marca como **Privado** (para proteger tus datos)
5. **NO** marques "Initialize with README" (ya tienes archivos)
6. Haz clic en **"Create repository"**

### 1.3 Conectar y Subir al Repositorio

GitHub te mostrará comandos. Copia y pega en PowerShell:

```powershell
git remote add origin https://github.com/TU_USUARIO/sistema-gestion-cueros.git
git branch -M main
git push -u origin main
```

> **Nota**: Reemplaza `TU_USUARIO` con tu nombre de usuario de GitHub

⚠️ **IMPORTANTE**: El archivo `.gitignore` ya está configurado para NO subir:
- `firebase_config.json` (tus credenciales)
- `.streamlit/secrets.toml` (tu configuración local)
- Bases de datos locales

---

## ☁️ Paso 2: Conectar con Streamlit Cloud

### 2.1 Crear Nueva App

1. Ve a [Streamlit Cloud](https://share.streamlit.io)
2. Inicia sesión con tu cuenta de GitHub
3. Haz clic en **"New app"**
4. Selecciona:
   - **Repository**: `TU_USUARIO/sistema-gestion-cueros`
   - **Branch**: `main`
   - **Main file path**: `gestion_cueros.py`
5. Haz clic en **"Advanced settings"** (antes de Deploy)

### 2.2 Configurar Secrets

En la sección **"Secrets"**, pega el contenido de tu archivo `.streamlit/secrets.toml`:

```toml
[firebase]
type = "service_account"
project_id = "gestion-de-cueros"
private_key_id = "TU_PRIVATE_KEY_ID"
private_key = """-----BEGIN PRIVATE KEY-----
TU_CLAVE_PRIVADA_COMPLETA_AQUI
-----END PRIVATE KEY-----"""
client_email = "firebase-adminsdk-xxxxx@gestion-de-cueros.iam.gserviceaccount.com"
client_id = "TU_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40gestion-de-cueros.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

> **Cómo obtener estos valores**: 
> - Abre tu archivo `.streamlit/secrets.toml` local
> - Copia todo el contenido
> - Pégalo en el campo de Secrets en Streamlit Cloud

### 2.3 Desplegar

1. Haz clic en **"Deploy"**
2. Espera 2-3 minutos mientras se instalan las dependencias
3. ¡Tu app estará lista! 🎉

---

## 📱 Paso 3: Acceder desde Cualquier Dispositivo

### Tu URL será algo como:

```
https://TU_USUARIO-sistema-gestion-cueros-xxxxxx.streamlit.app
```

### Acceso desde Teléfono/Tablet:

1. **Comparte la URL** con quien necesite acceso
2. Abre en cualquier navegador (Chrome, Safari, etc.)
3. **Guarda como acceso directo** en la pantalla de inicio:
   - **iPhone**: Safari → Compartir → Añadir a pantalla de inicio
   - **Android**: Chrome → Menú (⋮) → Añadir a pantalla de inicio

### Seguridad:

- La app require login (usuario/contraseña)
- Los datos están en Firebase (protegidos por Google)
- Solo quienes tengan la URL y credenciales pueden acceder

---

## 🔄 Paso 4: Actualizar la App (cuando hagas cambios)

Cada vez que modifiques el código localmente:

```powershell
git add .
git commit -m "Descripción de los cambios"
git push
```

Streamlit Cloud detectará los cambios automáticamente y actualizará la app en ~1 minuto.

---

## ⚙️ Configuración Adicional (Opcional)

### Cambiar el Tema

Edita `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

Luego:
```powershell
git add .streamlit/config.toml
git commit -m "Actualizar tema"
git push
```

---

## 🆘 Solución de Problemas

### ❌ Error "ModuleNotFoundError"
- **Causa**: Falta una dependencia en `requirements.txt`
- **Solución**: Agrega el módulo faltante a `requirements.txt` y haz push

### ❌ Error de Firebase
- **Causa**: Secrets mal configurados
- **Solución**: 
  1. Ve a Streamlit Cloud → Tu app → Settings → Secrets
  2. Verifica que el formato TOML sea correcto
  3. Asegúrate de que la clave privada esté entre `"""triple comillas"""`

### ❌ App muy lenta
- **Causa**: Streamlit Cloud gratuito tiene recursos limitados
- **Solución**: Considera optimizar consultas a Firebase o usar caché

### 🔄 Reiniciar la App

En Streamlit Cloud:
1. Ve a tu app
2. Menú (⋮) → **Reboot app**

---

## 📊 Características de Streamlit Cloud (Plan Gratuito)

✅ **Incluye:**
- 1 app privada + apps públicas ilimitadas
- 1 GB de recursos
- 1 GB de almacenamiento
- Acceso desde cualquier dispositivo
- SSL/HTTPS automático
- Actualizaciones automáticas desde GitHub

❌ **No incluye:**
- Dominio personalizado (usa el subdominio .streamlit.app)
- Recursos dedicados
- Soporte prioritario

---

## 🎯 Próximos Pasos

1. ✅ Subir código a GitHub
2. ✅ Desplegar en Streamlit Cloud
3. ✅ Configurar secrets
4. ✅ Acceder desde tu teléfono
5. 🔐 Cambiar la contraseña por defecto (admin/admin)
6. 📱 Compartir la URL con tu equipo

---

## 🔗 Enlaces Útiles

- [Documentación de Streamlit Cloud](https://docs.streamlit.io/streamlit-community-cloud)
- [Configurar Secrets](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Firebase Console](https://console.firebase.google.com/project/gestion-de-cueros/firestore)
- [GitHub](https://github.com)

---

## 💡 Consejo Final

**Guarda tu URL de Streamlit Cloud** en un lugar seguro. Si pierdes la URL, puedes encontrarla en tu [dashboard de Streamlit Cloud](https://share.streamlit.io).

¡Listo! Ahora podrás gestionar tus cueros desde cualquier lugar. 🎉
