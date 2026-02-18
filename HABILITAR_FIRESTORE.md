# 🚀 HABILITAR FIRESTORE - PASOS SIMPLES

## Se abrió tu navegador en Firebase Console

Si no se abrió, haz clic aquí:
👉 https://console.firebase.google.com/project/gestion-de-cueros/firestore

---

## 📋 SIGUE ESTOS 3 PASOS:

### PASO 1: Hacer clic en "Create database" o "Crear base de datos"
![Botón grande y azul en el centro de la pantalla]

### PASO 2: Seleccionar "Start in production mode" 
- O "Comenzar en modo de producción"
- Hacer clic en **"Next"** (Siguiente)

### PASO 3: Seleccionar ubicación
- Recomendado: **southamerica-east1** (São Paulo, Brasil)
- O cualquier ubicación de EEUU
- Hacer clic en **"Enable"** (Habilitar)

---

## ⏱️ ESPERAR 2-3 MINUTOS

Después de hacer clic en "Enable":
1. ✅ Firestore se está creando (verás una barra de progreso)
2. ✅ Espera a que termine (2-3 minutos)
3. ✅ Verás la pantalla de Firestore con pestañas: Data, Rules, Indexes, Usage

---

## 🔐 CONFIGURAR REGLAS (OPCIONAL PERO RECOMENDADO)

Si ves la pestaña **"Rules"**:
1. Haz clic en **"Rules"**
2. Copia y pega esto:

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

3. Haz clic en **"Publish"** (Publicar)

---

## ✅ VERIFICAR QUE FUNCIONÓ

Después de esperar 2-3 minutos:

1. Ve a tu navegador: http://localhost:8501
2. Presiona `Ctrl + Shift + R` para refrescar
3. Deberías ver **"✓ Conectado a Firebase"** en la sidebar

---

## ❌ SI TODAVÍA NO FUNCIONA

Espera 5 minutos más (la API puede tardar en propagarse)

Luego vuelve a refrescar el navegador.

---

**¿Listo?** Una vez que hayas completado estos pasos, vuelve a tu aplicación.
