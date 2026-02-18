# 🔒 Verificar antes de Subir a GitHub

Este script verifica que no subas archivos sensibles o innecesarios a GitHub.

## ✅ Archivos que NO deben aparecer en GitHub:

```
❌ firebase_config.json (credenciales)
❌ .streamlit/secrets.toml (credenciales locales)
❌ .session.json (sesiones)
❌ *.db, *.sqlite (bases de datos locales)
❌ __pycache__/ (archivos temporales Python)
❌ .venv/, venv/ (entorno virtual)
```

## 🛡️ Verificación Manual

### Opción 1: Comando Git Status

```powershell
git status
```

**Revisa que NO aparezcan:**
- `firebase_config.json`
- `.streamlit/secrets.toml`
- Archivos `.db` o `.sqlite`

Si aparecen, significa que **NO están protegidos** y se subirán a GitHub. ⚠️

---

### Opción 2: Ver archivos que se subirán

```powershell
git ls-files
```

Este comando muestra TODOS los archivos que git está rastreando.

**Busca manualmente:**
```powershell
git ls-files | Select-String "firebase_config.json"
git ls-files | Select-String "secrets.toml"
git ls-files | Select-String ".db"
```

Si alguno de estos comandos devuelve resultados, **DETENTE** y no hagas push.

---

## 🚨 Si encontraste archivos sensibles

### Caso 1: Aún no hiciste commit

```powershell
# Quitar archivo del staging
git reset HEAD firebase_config.json
git reset HEAD .streamlit/secrets.toml
```

### Caso 2: Ya hiciste commit (pero no push)

```powershell
# Deshacer último commit (mantener cambios)
git reset --soft HEAD~1

# Agregar al .gitignore
echo "firebase_config.json" >> .gitignore
echo ".streamlit/secrets.toml" >> .gitignore

# Volver a hacer commit sin los archivos sensibles
git add .
git commit -m "Sistema de Gestión de Cueros - Versión inicial"
```

### Caso 3: Ya hiciste push a GitHub

⚠️ **MUY IMPORTANTE**: Si ya subiste credenciales a GitHub:

1. **REVOCA inmediatamente** las credenciales en Firebase Console
2. Genera nuevas credenciales
3. Limpia el historial de Git:

```powershell
# Contacta a GitHub Support o usa git filter-branch
# Mejor: elimina el repositorio y crea uno nuevo
```

---

## ✅ Verificación de .gitignore

Verifica que tu `.gitignore` contenga:

```gitignore
# Firebase credentials
firebase_config.json
**/firebase_config.json

# Streamlit secrets
.streamlit/secrets.toml

# Session files
.session.json

# Databases
*.db
*.sqlite
*.sqlite3

# Python
__pycache__/
*.pyc
.venv/
venv/
```

---

## 🧪 Test Final antes de Push

```powershell
# 1. Ver archivos que se subirán
git ls-files

# 2. Ver tamaño del repositorio
git count-objects -vH

# 3. Ver último commit y archivos incluidos
git show --name-only

# 4. Hacer un dry-run del push (NO sube nada)
git push --dry-run origin main
```

---

## ✅ Lista de Verificación

Antes de hacer `git push`, confirma:

- [ ] `firebase_config.json` NO está en git ls-files
- [ ] `.streamlit/secrets.toml` NO está en git ls-files
- [ ] No hay archivos `.db` en git ls-files
- [ ] El archivo `.gitignore` existe y está configurado
- [ ] Hiciste backup de tus credenciales localmente
- [ ] Tienes las credenciales listas para Streamlit Cloud

---

## 🚀 Si todo está OK

```powershell
# Subir a GitHub
git push -u origin main
```

---

## 📝 Recordatorios

1. **NUNCA** compartas tu `firebase_config.json` por chat/email
2. **SIEMPRE** usa Secrets en Streamlit Cloud
3. **REVOCA** credenciales si sospechas que se expusieron
4. **MONITOREA** tu proyecto Firebase Console por actividad inusual

---

## 🔗 Recursos

- [Firebase Console](https://console.firebase.google.com)
- [Revocar credenciales](https://console.firebase.google.com/project/gestion-de-cueros/settings/serviceaccounts/adminsdk)
- [Streamlit Secrets](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
