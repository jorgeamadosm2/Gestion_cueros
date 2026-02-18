# 🐄 Gestión de Stock y Pagos - Cueros

Sistema de gestión de inventario y pagos para negocios de cueros, construido con Streamlit y Firebase.

## 🚀 Inicio Rápido

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Firebase

⚠️ **IMPORTANTE:** Debes configurar las credenciales de Firebase antes de ejecutar la aplicación.

La aplicación soporta **3 métodos** de configuración (elige uno):

1. **Archivo JSON** (recomendado para desarrollo local)
2. **Streamlit Secrets** (recomendado para deployment/cloud)
3. **Variables de Entorno** (flexible)

📚 **[Ver guía completa de configuración →](CONFIGURACION_FIREBASE.md)**

#### Configuración Rápida con Archivo JSON:

1. Descarga tus credenciales de Firebase Console
2. Renombra el archivo a `firebase_config.json`
3. Coloca el archivo en la raíz del proyecto
4. Ver `firebase_config_example.json` para el formato correcto

### 3. Ejecutar la Aplicación

```bash
streamlit run gestion_cueros.py
```

La aplicación estará disponible en: http://localhost:8501

## 🔐 Acceso Inicial

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin`

⚠️ Cambia la contraseña después del primer ingreso.

## ✨ Características

- 📦 **Gestión de Inventario** - Control de compras y ventas
- 💰 **Control de Pagos** - Seguimiento de pagos y cuentas por cobrar/pagar
- 👥 **Gestión de Clientes** - Administración de clientes y proveedores
- 📊 **Reportes** - Visualización de movimientos y estados de cuenta
- ☁️ **Cloud Storage** - Datos almacenados en Firebase Firestore
- 🔒 **Seguridad** - Sistema de autenticación de usuarios

## 📁 Estructura del Proyecto

```
.
├── gestion_cueros.py              # Aplicación principal
├── firebase_config_example.json   # Ejemplo de configuración Firebase (JSON)
├── .streamlit/
│   └── secrets.toml.example      # Ejemplo de configuración Firebase (Secrets)
├── CONFIGURACION_FIREBASE.md      # Guía completa de configuración
├── FIREBASE_SETUP.md              # Guía de setup inicial de Firebase
├── README_FIREBASE.md             # Documentación de Firebase
└── requirements.txt               # Dependencias Python
```

## 📚 Documentación

- **[CONFIGURACION_FIREBASE.md](CONFIGURACION_FIREBASE.md)** - Guía completa de configuración de Firebase (3 métodos)
- **[FIREBASE_SETUP.md](FIREBASE_SETUP.md)** - Setup inicial de Firebase Console
- **[README_FIREBASE.md](README_FIREBASE.md)** - Información sobre Firebase y funcionalidades

## 🛠️ Tecnologías

- **[Streamlit](https://streamlit.io/)** - Framework de aplicaciones web en Python
- **[Firebase Firestore](https://firebase.google.com/docs/firestore)** - Base de datos NoSQL en la nube
- **[Pandas](https://pandas.pydata.org/)** - Análisis y manipulación de datos

## 🆘 Solución de Problemas

### Error: "No se encontraron credenciales de Firebase"

**Causa:** No se configuró ningún método de credenciales de Firebase.

**Solución:** Configura al menos uno de los tres métodos disponibles. Ver [CONFIGURACION_FIREBASE.md](CONFIGURACION_FIREBASE.md) para instrucciones detalladas.

### Error: "Error al conectar con Firebase"

**Posibles causas:**
- Credenciales incorrectas o inválidas
- Sin conexión a internet
- Proyecto de Firebase no existe o no tiene Firestore habilitado

**Solución:**
1. Verifica que las credenciales sean correctas
2. Verifica tu conexión a internet
3. Verifica que Firestore esté habilitado en Firebase Console

### La aplicación carga pero no guarda datos

**Posibles causas:**
- Reglas de seguridad de Firestore muy restrictivas
- Sin conexión a internet

**Solución:**
1. Revisa las reglas de Firestore en Firebase Console
2. Para desarrollo, usa reglas permisivas (ver FIREBASE_SETUP.md)

## 🔒 Seguridad

⚠️ **IMPORTANTE - Protege tus credenciales:**

- ❌ **NUNCA** subas `firebase_config.json` a GitHub
- ❌ **NUNCA** subas `.streamlit/secrets.toml` a GitHub
- ✅ Estos archivos ya están en `.gitignore`
- ✅ Usa secretos de plataforma para deployment en producción

## 💰 Plan Gratuito de Firebase

Firebase ofrece un plan gratuito generoso:

- **Lecturas:** 50,000 por día
- **Escrituras:** 20,000 por día
- **Almacenamiento:** 1 GB

Suficiente para pequeñas y medianas empresas.

## 📄 Licencia

Este proyecto es de uso libre para fines educativos y comerciales.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, asegúrate de no incluir credenciales de Firebase en tus pull requests.

---

**¿Necesitas ayuda?** Consulta la documentación completa o abre un issue en GitHub.
