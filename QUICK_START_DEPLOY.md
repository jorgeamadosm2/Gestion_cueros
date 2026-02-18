# ⚡ Inicio Rápido - Subir a Streamlit Cloud

## 📋 Checklist

- [ ] Tienes cuenta de GitHub
- [ ] Tienes cuenta de Streamlit Cloud
- [ ] Tienes tu archivo `.streamlit/secrets.toml` con las credenciales de Firebase

---

## 🚀 Comandos para Copiar y Pegar

### 1️⃣ Preparar Git

Abre PowerShell en la carpeta de tu proyecto y ejecuta estos comandos:

```powershell
# Ver qué archivos están protegidos (no se subirán)
git status

# Preparar todos los archivos
git add .

# Crear commit inicial
git commit -m "Sistema de Gestión de Cueros - Versión inicial"
```

---

### 2️⃣ Crear Repositorio en GitHub

1. Ve a https://github.com/new
2. Nombre: `sistema-gestion-cueros`
3. Visibilidad: **Privado** ✅
4. NO marques "Initialize with README"
5. Click en "Create repository"

---

### 3️⃣ Conectar con GitHub

**GitHub te mostrará estos comandos. Cópialos y pégalos en PowerShell:**

```powershell
git remote add origin https://github.com/TU_USUARIO/sistema-gestion-cueros.git
git branch -M main
git push -u origin main
```

> ⚠️ **Importante**: Reemplaza `TU_USUARIO` con tu usuario de GitHub

**GitHub te pedirá autenticación:**
- Opción 1: Login con navegador (recomendado)
- Opción 2: Personal Access Token

---

### 4️⃣ Desplegar en Streamlit Cloud

1. Ve a https://share.streamlit.io
2. Login con GitHub
3. Click en **"New app"**
4. Configura:
   - Repository: `TU_USUARIO/sistema-gestion-cueros`
   - Branch: `main`
   - Main file: `gestion_cueros.py`
5. Click en **"Advanced settings"** ⚙️

---

### 5️⃣ Configurar Secrets

En la sección **Secrets**, pega el contenido de tu archivo `.streamlit/secrets.toml`:

**Cómo obtenerlo:**

```powershell
# Ver el contenido del archivo
Get-Content .streamlit\secrets.toml
```

Copia TODO el contenido y pégalo en el campo de Secrets en Streamlit Cloud.

Formato esperado:
```toml
[firebase]
type = "service_account"
project_id = "gestion-de-cueros"
private_key_id = "..."
private_key = """-----BEGIN PRIVATE KEY-----
...
-----END PRIVATE KEY-----"""
client_email = "..."
...
```

---

### 6️⃣ Deploy

1. Click en **"Deploy"** 🚀
2. Espera 2-3 minutos
3. ¡Listo! Tu app estará en línea

Tu URL será algo como:
```
https://tu-usuario-sistema-gestion-cueros-abc123.streamlit.app
```

---

## 📱 Acceso desde Teléfono

### iPhone/iPad (Safari):
1. Abre la URL en Safari
2. Tap en el botón compartir (cuadro con flecha)
3. Desplaza y tap en "Añadir a pantalla de inicio"
4. Nombra el icono: "Gestión Cueros"
5. Tap "Añadir"

### Android (Chrome):
1. Abre la URL en Chrome
2. Tap en el menú (⋮)
3. Tap en "Añadir a pantalla de inicio"
4. Nombra el icono: "Gestión Cueros"
5. Tap "Añadir"

---

## 🔄 Actualizar la App

Cada vez que hagas cambios en el código:

```powershell
# Ver qué cambió
git status

# Preparar cambios
git add .

# Crear commit
git commit -m "Descripción de tus cambios"

# Subir a GitHub
git push
```

Streamlit Cloud detectará los cambios y actualizará automáticamente en ~1 minuto.

---

## ✅ Verificación

Después del deploy, verifica:

- [ ] La URL funciona
- [ ] Puedes hacer login (admin/admin)
- [ ] Firebase está conectado (✅ en la sidebar)
- [ ] Puedes agregar/ver datos
- [ ] La app se ve correctamente en móvil

---

## 🆘 Problemas Comunes

### Error: "npm no se reconoce"
❌ **Incorrecto**: `npm install firebase`
✅ **Correcto**: Las dependencias ya están en `requirements.txt` (usa pip, no npm)

### Error: "Firebase credentials not found"
**Solución**: Verifica que copiaste correctamente los secrets en Streamlit Cloud
- Ve a tu app → Settings → Secrets
- Asegúrate de que el formato TOML sea correcto
- La clave privada debe estar entre `"""triple comillas"""`

### Error: "Repository not found"
**Solución**: Asegúrate de que el repositorio sea accesible por tu cuenta de GitHub

### La app carga muy lento
**Causa**: Primera carga siempre es más lenta (instala dependencias)
**Solución**: Después de la primera carga, será más rápida

---

## 📧 Compartir la App

Para compartir con tu equipo:

1. Copia la URL de tu app
2. Envíala por WhatsApp/Email
3. Comparte también las credenciales de login:
   - Usuario: `admin`
   - Contraseña: (la que hayas configurado)

**Seguridad:**
- Solo quien tenga la URL puede acceder
- Aun así necesitan usuario/contraseña para entrar
- Puedes cambiar a repositorio privado para mayor seguridad

---

## 🎉 ¡Todo Listo!

Ahora puedes:
- ✅ Acceder desde cualquier dispositivo
- ✅ Compartir con tu equipo
- ✅ Actualizar fácilmente
- ✅ Ver datos en tiempo real

**Próximos pasos recomendados:**
1. Cambiar la contraseña por defecto
2. Crear usuarios adicionales
3. Guardar la URL en un lugar seguro
4. Configurar un icono personalizado (opcional)

---

¿Dudas? Revisa la [Guía Completa](DEPLOY_STREAMLIT_CLOUD.md)
