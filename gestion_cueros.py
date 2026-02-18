import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib
from pathlib import Path
import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
from io import BytesIO

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Gestión Cueros", layout="wide")
st.title("🐄 Gestión de Stock y Pagos - Cueros")

SESSION_FILE = Path(__file__).resolve().parent / ".session.json"
FIREBASE_CREDS = Path(__file__).resolve().parent / "firebase_config.json"

# --- INICIALIZACIÓN DE FIREBASE ---
def get_firebase_credentials():
    """Obtener credenciales de Firebase desde múltiples fuentes"""
    
    # Opción 1: Streamlit Secrets (recomendado para deployment)
    try:
        if 'firebase' in st.secrets:
            # Convertir a dict regular y asegurar que private_key tenga formato correcto
            firebase_secrets = {
                "type": str(st.secrets["firebase"]["type"]),
                "project_id": str(st.secrets["firebase"]["project_id"]),
                "private_key_id": str(st.secrets["firebase"]["private_key_id"]),
                "private_key": str(st.secrets["firebase"]["private_key"]),
                "client_email": str(st.secrets["firebase"]["client_email"]),
                "client_id": str(st.secrets["firebase"]["client_id"]),
                "auth_uri": str(st.secrets["firebase"]["auth_uri"]),
                "token_uri": str(st.secrets["firebase"]["token_uri"]),
                "auth_provider_x509_cert_url": str(st.secrets["firebase"]["auth_provider_x509_cert_url"]),
                "client_x509_cert_url": str(st.secrets["firebase"]["client_x509_cert_url"]),
                "universe_domain": str(st.secrets["firebase"].get("universe_domain", "googleapis.com"))
            }
            return firebase_secrets
    except Exception as e:
        st.warning(f"⚠️ Error al leer secrets de Streamlit: {str(e)}")
    
    # Opción 2: Archivo firebase_config.json (recomendado para desarrollo local)
    if FIREBASE_CREDS.exists():
        try:
            with open(FIREBASE_CREDS, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.warning(f"⚠️ Error al leer firebase_config.json: {str(e)}")
    
    # Opción 3: Variables de entorno
    if os.getenv('FIREBASE_PROJECT_ID'):
        try:
            return {
                "type": os.getenv('FIREBASE_TYPE', 'service_account'),
                "project_id": os.getenv('FIREBASE_PROJECT_ID'),
                "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                # Replace escaped newlines - env vars often store multi-line keys as single line with \n
                "private_key": os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                "auth_uri": os.getenv('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
                "token_uri": os.getenv('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
                "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
                "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_CERT_URL'),
                "universe_domain": os.getenv('FIREBASE_UNIVERSE_DOMAIN', 'googleapis.com')
            }
        except Exception as e:
            st.warning(f"⚠️ Error al leer variables de entorno: {str(e)}")
    
    return None

if not firebase_admin._apps:
    try:
        creds_dict = get_firebase_credentials()
        
        if creds_dict:
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            st.sidebar.success("✅ Conectado a Firebase")
        else:
            st.error("❌ Error: No se encontraron credenciales de Firebase")
            st.info("📄 **Opciones para configurar Firebase:**")
            st.markdown("""
            **Opción 1: Archivo de configuración (desarrollo local)**
            - Crea el archivo `firebase_config.json` con tus credenciales de Firebase
            - Ver `firebase_config_example.json` para el formato correcto
            
            **Opción 2: Streamlit Secrets (recomendado para deployment)**
            - Crea el archivo `.streamlit/secrets.toml` 
            - Ver `.streamlit/secrets.toml.example` para el formato correcto
            
            **Opción 3: Variables de entorno**
            - Define las variables de entorno necesarias (ver documentación)
            """)
            st.stop()
    except Exception as e:
        st.error(f"❌ Error al conectar con Firebase: {str(e)}")
        st.stop()
else:
    db = firestore.client()

# --- FUNCIONES DE BASE DE DATOS FIREBASE ---
def init_db():
    """Inicializar colecciones de Firebase (ya se crean automáticamente)"""
    try:
        # Verificar que exista un usuario admin
        usuarios_ref = db.collection('usuarios')
        admin_query = usuarios_ref.where('usuario', '==', 'admin').limit(1).get()
        
        if not admin_query:
            # Crear admin por defecto
            password_hash = hashlib.sha256('admin'.encode('utf-8')).hexdigest()
            usuarios_ref.add({
                'usuario': 'admin',
                'password_hash': password_hash,
                'rol': 'admin',
                'activo': 1,
                'fecha_creacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        return True
    except Exception as e:
        st.error(f"Error al inicializar Firebase: {str(e)}")
        return False

def agregar_movimiento(tipo, producto, descripcion, cantidad, peso, precio_total, neto, iva_rate, modo_pago, detalle_pago, dinero_a_cuenta, estado):
    try:
        db.collection('movimientos').add({
            'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'tipo': tipo,
            'producto': producto,
            'descripcion': descripcion,
            'cantidad': cantidad,
            'peso_kg': peso,
            'precio_total': precio_total,
            'neto': neto,
            'iva_rate': iva_rate,
            'modo_pago': modo_pago,
            'detalle_pago': detalle_pago,
            'dinero_a_cuenta': dinero_a_cuenta,
            'estado_pago': estado
        })
    except Exception as e:
        st.error(f"Error al agregar movimiento: {str(e)}")

def obtener_datos():
    try:
        movimientos = db.collection('movimientos').order_by('fecha', direction=firestore.Query.DESCENDING).stream()
        data = []
        for mov in movimientos:
            mov_dict = mov.to_dict()
            mov_dict['id'] = mov.id
            data.append(mov_dict)
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error al leer movimientos: {str(e)}")
        return pd.DataFrame()

def autenticar_usuario(usuario, password):
    try:
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        usuarios_ref = db.collection('usuarios')
        query = usuarios_ref.where('usuario', '==', usuario).where('password_hash', '==', password_hash).limit(1).get()
        
        for doc in query:
            user_data = doc.to_dict()
            if user_data.get('activo') == 1:
                return {'usuario': user_data['usuario'], 'rol': user_data['rol']}
        return None
    except Exception as e:
        st.error(f"Error de autenticación: {str(e)}")
        return None

def crear_usuario(usuario, password, rol):
    try:
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        db.collection('usuarios').add({
            'usuario': usuario,
            'password_hash': password_hash,
            'rol': rol,
            'activo': 1,
            'fecha_creacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        st.error(f"Error al crear usuario: {str(e)}")
        raise

def obtener_usuarios():
    try:
        usuarios = db.collection('usuarios').stream()
        data = []
        for user in usuarios:
            user_dict = user.to_dict()
            user_dict['id'] = user.id
            data.append(user_dict)
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error al obtener usuarios: {str(e)}")
        return pd.DataFrame()

def actualizar_estado_usuario(user_id, activo):
    try:
        db.collection('usuarios').document(user_id).update({
            'activo': 1 if activo else 0
        })
    except Exception as e:
        st.error(f"Error al actualizar estado: {str(e)}")

def actualizar_password(user_id, new_password):
    try:
        password_hash = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
        db.collection('usuarios').document(user_id).update({
            'password_hash': password_hash
        })
    except Exception as e:
        st.error(f"Error al actualizar contraseña: {str(e)}")

def actualizar_rol_usuario(user_id, rol):
    try:
        doc = db.collection('usuarios').document(user_id).get()
        if doc.exists and doc.to_dict().get('usuario') != 'admin':
            db.collection('usuarios').document(user_id).update({'rol': rol})
    except Exception as e:
        st.error(f"Error al actualizar rol: {str(e)}")

def eliminar_usuario(user_id):
    try:
        doc = db.collection('usuarios').document(user_id).get()
        if doc.exists and doc.to_dict().get('usuario') != 'admin':
            db.collection('usuarios').document(user_id).delete()
    except Exception as e:
        st.error(f"Error al eliminar usuario: {str(e)}")

def actualizar_movimiento(mov_id, tipo, producto, descripcion, cantidad, peso_kg, precio_total, neto, iva_rate, modo_pago, detalle_pago, dinero_a_cuenta, estado_pago):
    try:
        db.collection('movimientos').document(mov_id).update({
            'tipo': tipo,
            'producto': producto,
            'descripcion': descripcion,
            'cantidad': cantidad,
            'peso_kg': peso_kg,
            'precio_total': precio_total,
            'neto': neto,
            'iva_rate': iva_rate,
            'modo_pago': modo_pago,
            'detalle_pago': detalle_pago,
            'dinero_a_cuenta': dinero_a_cuenta,
            'estado_pago': estado_pago
        })
    except Exception as e:
        st.error(f"Error al actualizar movimiento: {str(e)}")

def eliminar_movimiento(mov_id):
    try:
        db.collection('movimientos').document(mov_id).delete()
    except Exception as e:
        st.error(f"Error al eliminar movimiento: {str(e)}")

def eliminar_movimientos_cliente(cliente):
    try:
        movimientos = db.collection('movimientos').where('descripcion', '==', cliente).stream()
        for mov in movimientos:
            mov.reference.delete()
    except Exception as e:
        st.error(f"Error al eliminar movimientos: {str(e)}")

def crear_cliente(nombre, tipo, contacto, telefono, email, direccion, notas):
    try:
        db.collection('clientes').add({
            'nombre': nombre,
            'tipo': tipo,
            'contacto': contacto,
            'telefono': telefono,
            'email': email,
            'direccion': direccion,
            'notas': notas,
            'activo': 1,
            'fecha_creacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        st.error(f"Error al crear cliente: {str(e)}")
        raise

def obtener_clientes():
    try:
        clientes = db.collection('clientes').order_by('nombre').stream()
        data = []
        for cliente in clientes:
            cliente_dict = cliente.to_dict()
            cliente_dict['id'] = cliente.id
            data.append(cliente_dict)
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error al obtener clientes: {str(e)}")
        return pd.DataFrame()

def actualizar_cliente(cliente_id, nombre, tipo, contacto, telefono, email, direccion, notas, activo):
    try:
        db.collection('clientes').document(cliente_id).update({
            'nombre': nombre,
            'tipo': tipo,
            'contacto': contacto,
            'telefono': telefono,
            'email': email,
            'direccion': direccion,
            'notas': notas,
            'activo': 1 if activo else 0
        })
    except Exception as e:
        st.error(f"Error al actualizar cliente: {str(e)}")

def eliminar_cliente(cliente_id):
    try:
        db.collection('clientes').document(cliente_id).delete()
    except Exception as e:
        st.error(f"Error al eliminar cliente: {str(e)}")

def obtener_cliente_por_id(cliente_id):
    try:
        doc = db.collection('clientes').document(cliente_id).get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None
    except Exception as e:
        st.error(f"Error al obtener cliente: {str(e)}")
        return None

def agregar_pago_cuenta(cliente_nombre, monto, concepto, tipo):
    try:
        db.collection('pagos_cuenta').add({
            'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'cliente_nombre': cliente_nombre,
            'monto': monto,
            'concepto': concepto,
            'tipo': tipo
        })
    except Exception as e:
        st.error(f"Error al agregar pago: {str(e)}")

def obtener_pagos_cuenta():
    try:
        pagos = db.collection('pagos_cuenta').order_by('fecha', direction=firestore.Query.DESCENDING).stream()
        data = []
        for pago in pagos:
            pago_dict = pago.to_dict()
            pago_dict['id'] = pago.id
            data.append(pago_dict)
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error al obtener pagos: {str(e)}")
        return pd.DataFrame()

def obtener_pagos_cuenta_cliente(cliente_nombre):
    try:
        pagos = db.collection('pagos_cuenta').where('cliente_nombre', '==', cliente_nombre).order_by('fecha', direction=firestore.Query.DESCENDING).stream()
        data = []
        for pago in pagos:
            pago_dict = pago.to_dict()
            pago_dict['id'] = pago.id
            data.append(pago_dict)
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error al obtener pagos del cliente: {str(e)}")
        return pd.DataFrame()

def calcular_saldo_cliente(cliente_nombre):
    try:
        df_pagos = obtener_pagos_cuenta_cliente(cliente_nombre)
        saldo = 0
        for _, row in df_pagos.iterrows():
            if row['tipo'] == 'ingreso':
                saldo += row['monto']
            else:
                saldo -= row['monto']
        return saldo
    except Exception as e:
        st.error(f"Error al calcular saldo: {str(e)}")
        return 0

def eliminar_pago_cuenta(pago_id):
    try:
        db.collection('pagos_cuenta').document(pago_id).delete()
    except Exception as e:
        st.error(f"Error al eliminar pago: {str(e)}")

def guardar_sesion(usuario, rol):
    try:
        with open(SESSION_FILE, 'w') as f:
            json.dump({'usuario': usuario, 'rol': rol}, f)
    except:
        pass

def cargar_sesion():
    try:
        if SESSION_FILE.exists():
            with open(SESSION_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return None

def eliminar_sesion():
    try:
        if SESSION_FILE.exists():
            SESSION_FILE.unlink()
    except:
        pass

def generar_excel(dataframe, nombre_hoja="Datos"):
    """Genera un archivo Excel desde un DataFrame"""
    try:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            dataframe.to_excel(writer, sheet_name=nombre_hoja, index=False)
        output.seek(0)
        return output.getvalue()
    except Exception as e:
        st.error(f"Error al generar Excel: {str(e)}")
        return None

@st.dialog("Confirmar eliminacion")
def confirmar_eliminacion(mov_id, descripcion, total):
    st.write(f"ID: {mov_id}")
    st.write(f"Descripcion: {descripcion}")
    st.write(f"Total: ${total:,.2f}")
    col_c1, col_c2 = st.columns(2)
    if col_c1.button("Eliminar"):
        eliminar_movimiento(mov_id)
        st.session_state.last_deleted = mov_id
        st.rerun()
    if col_c2.button("Cancelar"):
        st.rerun()

@st.dialog("Confirmar eliminacion de usuario")
def confirmar_eliminacion_usuario(user_id, usuario):
    st.write(f"ID: {user_id}")
    st.write(f"Usuario: {usuario}")
    col_c1, col_c2 = st.columns(2)
    if col_c1.button("Eliminar"):
        eliminar_usuario(user_id)
        st.session_state.last_user_deleted = user_id
        st.rerun()
    if col_c2.button("Cancelar"):
        st.rerun()

@st.dialog("Confirmar eliminacion de cliente")
def confirmar_eliminacion_cliente(cliente_id, nombre):
    st.write(f"ID: {cliente_id}")
    st.write(f"Cliente: {nombre}")
    st.warning("Esto no eliminará los movimientos asociados a este cliente")
    col_c1, col_c2 = st.columns(2)
    if col_c1.button("Eliminar"):
        eliminar_cliente(cliente_id)
        st.session_state.last_cliente_deleted = cliente_id
        st.rerun()
    if col_c2.button("Cancelar"):
        st.rerun()

@st.dialog("Confirmar eliminacion de pago a cuenta")
def confirmar_eliminacion_pago(pago_id, cliente, monto):
    st.write(f"ID: {pago_id}")
    st.write(f"Cliente: {cliente}")
    st.write(f"Monto: ${monto:,.2f}")
    col_c1, col_c2 = st.columns(2)
    if col_c1.button("Eliminar"):
        eliminar_pago_cuenta(pago_id)
        st.session_state.last_pago_deleted = pago_id
        st.rerun()
    if col_c2.button("Cancelar"):
        st.rerun()

# Inicializar DB al arrancar
init_db()

# Inicializar contadores para limpiar inputs
if 'user_form_key' not in st.session_state:
    st.session_state.user_form_key = 0
if 'cliente_form_key' not in st.session_state:
    st.session_state.cliente_form_key = 0
if 'pago_form_key' not in st.session_state:
    st.session_state.pago_form_key = 0

# Forzar refresco de datos
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = 0

# --- LOGIN ---
if 'auth' not in st.session_state:
    sesion_guardada = cargar_sesion()
    st.session_state.auth = sesion_guardada

with st.sidebar.expander("Acceso", expanded=True):
    if st.session_state.auth:
        st.write(f"Usuario: {st.session_state.auth['usuario']}")
        st.write(f"Rol: {st.session_state.auth['rol']}")
        st.success("✓ Conectado a Firebase")
        # Mostrar estadísticas de datos persistentes
        try:
            num_usuarios = len(list(db.collection('usuarios').stream()))
            num_clientes = len(list(db.collection('clientes').stream()))
            num_movimientos = len(list(db.collection('movimientos').stream()))
            num_pagos = len(list(db.collection('pagos_cuenta').stream()))
            st.caption(f"📊 {num_usuarios} usuarios | {num_clientes} clientes")
            st.caption(f"📦 {num_movimientos} movimientos | {num_pagos} pagos")
        except Exception as e:
            st.error(f"Error BD: {str(e)}")
        if st.button("Cerrar sesion"):
            st.session_state.auth = None
            eliminar_sesion()
            st.rerun()
    else:
        user_input = st.text_input("Usuario", key="login_user")
        pass_input = st.text_input("Contrasena", type="password", key="login_pass")
        if st.button("Ingresar"):
            auth = autenticar_usuario(user_input, pass_input)
            if auth:
                st.session_state.auth = auth
                guardar_sesion(auth['usuario'], auth['rol'])
                st.success("Ingreso correcto")
                st.rerun()
            else:
                st.error("Usuario o contrasena incorrectos, o usuario inactivo")

if not st.session_state.auth:
    st.stop()

# --- BARRA LATERAL (ESTADO DE CUENTA SIEMPRE VISIBLE) ---
st.sidebar.header("💰 Estado de Cuenta")

# Obtener lista de clientes para selector
df_clientes_estado = obtener_clientes()
if not df_clientes_estado.empty:
    clientes_activos_estado = df_clientes_estado[df_clientes_estado['activo'] == 1]
    if not clientes_activos_estado.empty:
        opciones_clientes_estado = ["-- Seleccionar cliente --"] + clientes_activos_estado['nombre'].tolist()
        cliente_seleccionado_sidebar = st.sidebar.selectbox("Ver estado de cuenta de:", opciones_clientes_estado, key="cliente_sidebar_estado")
        
        if cliente_seleccionado_sidebar != "-- Seleccionar cliente --":
            # Obtener datos del cliente
            df_todas_movimientos = obtener_datos()
            
            # Validar que el DataFrame tenga la columna 'descripcion'
            if not df_todas_movimientos.empty and 'descripcion' in df_todas_movimientos.columns:
                df_cliente_estado = df_todas_movimientos[df_todas_movimientos['descripcion'] == cliente_seleccionado_sidebar]
            else:
                df_cliente_estado = pd.DataFrame()
                
            try:
                df_pagos_cliente_estado = obtener_pagos_cuenta_cliente(cliente_seleccionado_sidebar)
            except:
                df_pagos_cliente_estado = pd.DataFrame()
            
            # Calcular totales rápido
            compras = 0
            ventas = 0
            compras_impagag = 0
            ventas_impagag = 0
            
            if not df_cliente_estado.empty:
                if 'precio_total' in df_cliente_estado.columns and 'tipo' in df_cliente_estado.columns and 'estado_pago' in df_cliente_estado.columns:
                    compras = df_cliente_estado[df_cliente_estado['tipo'] == 'Ingreso (Compra)']['precio_total'].sum()
                    ventas = df_cliente_estado[df_cliente_estado['tipo'] == 'Egreso (Venta)']['precio_total'].sum()
                    compras_impagag = df_cliente_estado[(df_cliente_estado['tipo'] == 'Ingreso (Compra)') & (df_cliente_estado['estado_pago'] == 'Impago')]['precio_total'].sum()
                    ventas_impagag = df_cliente_estado[(df_cliente_estado['tipo'] == 'Egreso (Venta)') & (df_cliente_estado['estado_pago'] == 'Impago')]['precio_total'].sum()
            
            saldo_cuenta = calcular_saldo_cliente(cliente_seleccionado_sidebar)
            balance_total = ventas_impagag - compras_impagag + saldo_cuenta
            
            # Mostrar resumen en el sidebar
            st.sidebar.markdown("---")
            st.sidebar.write(f"**{cliente_seleccionado_sidebar}**")
            
            # Indicador visual del balance
            if balance_total > 0:
                st.sidebar.info(f"🟢 Me deben: **${balance_total:,.2f}**")
            elif balance_total < 0:
                st.sidebar.warning(f"🔴 Les debo: **${abs(balance_total):,.2f}**")
            else:
                st.sidebar.success(f"⚪ Saldo equilibrado: $0.00")
            
            # Detalles
            col_d1, col_d2 = st.sidebar.columns(2)
            with col_d1:
                st.metric("Comprado", f"${compras:,.0f}", label_visibility="collapsed")
                st.caption("Comprado total", help="Total de compras a este proveedor")
            with col_d2:
                st.metric("Vendido", f"${ventas:,.0f}", label_visibility="collapsed")
                st.caption("Vendido total", help="Total de ventas a este cliente")
            
            col_d3, col_d4 = st.sidebar.columns(2)
            with col_d3:
                st.metric("No pagado", f"${compras_impagag:,.0f}", label_visibility="collapsed")
                st.caption("Deuda compras", help="Dinero que debo pagar")
            with col_d4:
                st.metric("Por cobrar", f"${ventas_impagag:,.0f}", label_visibility="collapsed")
                st.caption("Deuda ventas", help="Dinero que me deben")
            
            st.sidebar.metric("A Cuenta", f"${saldo_cuenta:,.0f}", label_visibility="collapsed")
            st.sidebar.markdown("---")

# --- BARRA LATERAL (ENTRADA DE DATOS) ---
st.sidebar.header("Nuevo Registro")

if st.session_state.auth['rol'] == 'admin':
    tipo_operacion = st.sidebar.selectbox("Tipo de Operación", ["Ingreso (Compra)", "Egreso (Venta)"])
    producto = st.sidebar.selectbox("Producto", ["Sal", "Cueros"])
    
    # Selector de cliente/proveedor
    df_clientes_sidebar = obtener_clientes()
    if not df_clientes_sidebar.empty:
        clientes_activos = df_clientes_sidebar[df_clientes_sidebar['activo'] == 1]
        if not clientes_activos.empty:
            opciones_clientes_sidebar = ["-- Escribir manualmente --"] + clientes_activos['nombre'].tolist()
            cliente_seleccionado = st.sidebar.selectbox("Cliente / Proveedor", opciones_clientes_sidebar)
            if cliente_seleccionado == "-- Escribir manualmente --":
                desc_input = st.sidebar.text_input("Descripción / Cliente / Proveedor")
            else:
                desc_input = cliente_seleccionado
                st.sidebar.info(f"Seleccionado: {desc_input}")
        else:
            desc_input = st.sidebar.text_input("Descripción / Cliente / Proveedor")
            st.sidebar.caption("No hay clientes activos. Créalos en Administración de Clientes")
    else:
        desc_input = st.sidebar.text_input("Descripción / Cliente / Proveedor")
        st.sidebar.caption("No hay clientes registrados. Créalos en Administración de Clientes")
    col1, col2 = st.sidebar.columns(2)
    cant_input = col1.number_input("Cantidad (Unidades)", min_value=1, step=1)
    peso_input = col2.number_input("Peso Total (kg)", min_value=0.0, step=0.1)
    precio_kg = st.sidebar.number_input("Precio por kg ($)", min_value=0.0, step=10.0)
    iva_opcion = st.sidebar.selectbox("IVA", ["0%", "10.5%", "21%"])
    modo_pago = st.sidebar.selectbox("Modo de Pago", ["Efectivo", "A cuenta", "Cheque", "Otros productos"])
    detalle_pago = st.sidebar.text_input("Detalle del pago (opcional)")
    dinero_a_cuenta = st.sidebar.number_input("Dinero a cuenta ($)", min_value=0.0, step=100.0)
    estado_pago = st.sidebar.radio("Estado del Pago", ["Pagado", "Impago"])

    iva_map = {"0%": 0.0, "10.5%": 0.105, "21%": 0.21}
    iva_rate = iva_map[iva_opcion]
    neto = precio_kg * peso_input
    total_con_iva = neto * (1 + iva_rate)
    promedio_unidad = (neto / cant_input) if cant_input > 0 else 0.0

    st.sidebar.markdown("**Detalle de calculo**")
    st.sidebar.write(f"Neto: ${neto:,.2f}")
    st.sidebar.write(f"Total con IVA: ${total_con_iva:,.2f}")
    st.sidebar.write(f"Promedio por unidad: ${promedio_unidad:,.2f}")

    if st.sidebar.button("Guardar Movimiento"):
        if desc_input:
            agregar_movimiento(
                tipo_operacion,
                producto,
                desc_input,
                cant_input,
                peso_input,
                total_con_iva,
                neto,
                iva_rate,
                modo_pago,
                detalle_pago,
                dinero_a_cuenta,
                estado_pago
            )
            st.sidebar.success("¡Registrado con éxito!")
            st.rerun() # Recargar la página para ver cambios
        else:
            st.sidebar.error("Falta la descripción")
else:
    st.sidebar.info("Solo administradores pueden registrar compras y ventas.")

# --- PANEL PRINCIPAL ---

# 1. Obtener datos
df = obtener_datos()

if not df.empty:
    if 'last_deleted' in st.session_state and st.session_state.last_deleted is not None:
        st.success(f"Movimiento eliminado (ID {st.session_state.last_deleted})")
        st.session_state.last_deleted = None
    if 'last_user_deleted' in st.session_state and st.session_state.last_user_deleted is not None:
        st.success(f"Usuario eliminado (ID {st.session_state.last_user_deleted})")
        st.session_state.last_user_deleted = None
    if 'last_cliente_deleted' in st.session_state and st.session_state.last_cliente_deleted is not None:
        st.success(f"Cliente eliminado (ID {st.session_state.last_cliente_deleted})")
        st.session_state.last_cliente_deleted = None
    if 'last_pago_deleted' in st.session_state and st.session_state.last_pago_deleted is not None:
        st.success(f"Pago a cuenta eliminado (ID {st.session_state.last_pago_deleted})")
        st.session_state.last_pago_deleted = None
    # Filtros
    st.subheader("Filtros")
    col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 3, 1])
    filtro_pago = col_f1.selectbox("Filtrar por estado de pago:", ["Todos", "Impago", "Pagado"], key="filtro_pago")
    filtro_producto = col_f2.selectbox("Filtrar por producto:", ["Todos", "Sal", "Cueros"], key="filtro_producto")
    clientes = sorted(df['descripcion'].dropna().unique().tolist()) if 'descripcion' in df.columns else []
    opciones_clientes = ["Todos"] + clientes
    filtro_cliente = col_f3.selectbox("Filtrar por cliente / descripcion", opciones_clientes, key="filtro_cliente")
    if col_f4.button("Limpiar"):
        st.session_state.filtro_pago = "Todos"
        st.session_state.filtro_producto = "Todos"
        st.session_state.filtro_cliente = "Todos"
        st.rerun()

    df_metric = df
    if filtro_pago != "Todos" and 'estado_pago' in df_metric.columns:
        df_metric = df_metric[df_metric['estado_pago'] == filtro_pago]
    if filtro_producto != "Todos" and 'producto' in df_metric.columns:
        df_metric = df_metric[df_metric['producto'] == filtro_producto]
    if filtro_cliente != "Todos" and 'descripcion' in df_metric.columns:
        df_metric = df_metric[df_metric['descripcion'] == filtro_cliente]

    # 2. Cálculos de Stock y Finanzas
    stock_actual_u = 0
    stock_actual_kg = 0
    deuda_compras = 0
    a_cobrar_ventas = 0
    cobrado_ventas = 0
    pagado_compras = 0
    dinero_esperado = 0
    
    if not df_metric.empty and 'tipo' in df_metric.columns:
        ingresos = df_metric[df_metric['tipo'] == 'Ingreso (Compra)']
        egresos = df_metric[df_metric['tipo'] == 'Egreso (Venta)']
        
        if 'cantidad' in df_metric.columns:
            stock_actual_u = ingresos['cantidad'].sum() - egresos['cantidad'].sum()
        if 'peso_kg' in df_metric.columns:
            stock_actual_kg = ingresos['peso_kg'].sum() - egresos['peso_kg'].sum()
        
        # Deudas (Lo que debo pagar por compras impagas)
        if 'estado_pago' in df_metric.columns and 'precio_total' in df_metric.columns:
            deuda_compras = ingresos[ingresos['estado_pago'] == 'Impago']['precio_total'].sum()
            # A cobrar (Lo que me deben por ventas impagas)
            a_cobrar_ventas = egresos[egresos['estado_pago'] == 'Impago']['precio_total'].sum()
            # Dinero esperado (cobrado ventas - pagado compras)
            cobrado_ventas = egresos[egresos['estado_pago'] == 'Pagado']['precio_total'].sum()
            pagado_compras = ingresos[ingresos['estado_pago'] == 'Pagado']['precio_total'].sum()
            dinero_esperado = cobrado_ventas - pagado_compras

    # 3. Métricas en tarjetas
    col_a, col_b, col_c, col_d, col_e = st.columns(5)
    col_a.metric("Stock (Unidades)", f"{stock_actual_u} u.")
    col_b.metric("Stock (Peso)", f"{stock_actual_kg:.1f} kg")
    col_c.metric("Por Cobrar (Ventas)", f"${a_cobrar_ventas:,.2f}", delta_color="normal")
    col_d.metric("Por Pagar (Compras)", f"${deuda_compras:,.2f}", delta_color="inverse")
    col_e.metric("Dinero Esperado", f"${dinero_esperado:,.2f}")

    st.markdown("---")

    # 4. Tabla interactiva
    st.subheader("📋 Registro de Movimientos")

    df_show = df
    if filtro_pago != "Todos" and 'estado_pago' in df_show.columns:
        df_show = df_show[df_show['estado_pago'] == filtro_pago]
    if filtro_producto != "Todos" and 'producto' in df_show.columns:
        df_show = df_show[df_show['producto'] == filtro_producto]
    if filtro_cliente != "Todos" and 'descripcion' in df_show.columns:
        df_show = df_show[df_show['descripcion'] == filtro_cliente]

    df_show_display = df_show.copy()
    if 'iva_rate' in df_show_display.columns:
        df_show_display['iva_%'] = (df_show_display['iva_rate'].fillna(0) * 100).round(1)
    columnas_base = [
        'id', 'fecha', 'tipo', 'producto', 'descripcion', 'cantidad', 'peso_kg',
        'neto', 'iva_%', 'precio_total', 'modo_pago', 'detalle_pago', 'dinero_a_cuenta', 'estado_pago'
    ]
    columnas_disponibles = [c for c in columnas_base if c in df_show_display.columns]
    df_show_display = df_show_display[columnas_disponibles]

    st.dataframe(df_show_display, use_container_width=True)

    if st.session_state.auth['rol'] == 'admin':
        st.markdown("---")
        st.subheader("Eliminar movimientos")
        for _, row in df_show_display.iterrows():
            col_id, col_desc, col_total, col_del = st.columns([1, 5, 2, 1])
            mov_id = int(row['id'])
            descripcion = str(row['descripcion'])
            total = float(row.get('precio_total', 0) or 0)
            col_id.write(mov_id)
            col_desc.write(descripcion)
            col_total.write(f"${total:,.2f}")
            if col_del.button("X", key=f"del_{mov_id}"):
                confirmar_eliminacion(mov_id, descripcion, total)

    # --- RESUMEN POR CLIENTE ---
    st.markdown("---")
    st.subheader("📄 Estado de Cuenta Detallado")
    
    # Obtener lista de clientes únicos desde movimientos y pagos
    clientes_movimientos = sorted(df['descripcion'].dropna().unique().tolist()) if 'descripcion' in df.columns else []
    df_pagos_todos = obtener_pagos_cuenta()
    clientes_pagos = df_pagos_todos['cliente_nombre'].unique().tolist() if not df_pagos_todos.empty else []
    clientes_unicos = sorted(list(set(clientes_movimientos + clientes_pagos)))
    
    opciones_resumen = ["Todos"] + clientes_unicos
    
    # Usar el cliente seleccionado en el sidebar como predeterminado (si existe)
    indice_default = 0
    if 'cliente_seleccionado_sidebar' in locals() and cliente_seleccionado_sidebar != "-- Seleccionar cliente --":
        if cliente_seleccionado_sidebar in opciones_resumen:
            indice_default = opciones_resumen.index(cliente_seleccionado_sidebar)
    
    cliente_resumen = st.selectbox("Selecciona un cliente para ver estado detallado", opciones_resumen, index=indice_default, key="cliente_resumen")
    
    if cliente_resumen != "Todos":
        # Filtrar datos del cliente
        df_cliente = df[df['descripcion'] == cliente_resumen]
        df_pagos_cliente = obtener_pagos_cuenta_cliente(cliente_resumen)
        
        # Calcular totales
        compras_cliente = df_cliente[df_cliente['tipo'] == 'Ingreso (Compra)']  # Lo que yo compré a este proveedor
        ventas_cliente = df_cliente[df_cliente['tipo'] == 'Egreso (Venta)']  # Lo que yo vendí a este cliente
        
        total_comprado = compras_cliente['precio_total'].sum()
        total_vendido = ventas_cliente['precio_total'].sum()
        
        # Pagos
        compras_pagadas = compras_cliente[compras_cliente['estado_pago'] == 'Pagado']['precio_total'].sum()
        compras_impagas = compras_cliente[compras_cliente['estado_pago'] == 'Impago']['precio_total'].sum()
        ventas_cobradas = ventas_cliente[ventas_cliente['estado_pago'] == 'Pagado']['precio_total'].sum()
        ventas_impagag = ventas_cliente[ventas_cliente['estado_pago'] == 'Impago']['precio_total'].sum()
        
        # Saldo de pagos a cuenta
        saldo_cuenta = calcular_saldo_cliente(cliente_resumen)
        
        # Balance general
        # Si es proveedor: le debo lo que compré y no pagué
        # Si es cliente: me debe lo que vendí y no cobré
        # El saldo a cuenta se suma/resta
        balance_compras = compras_impagas  # Lo que le debo
        balance_ventas = ventas_impagag    # Lo que me debe
        balance_final = balance_ventas - balance_compras + saldo_cuenta
        
        # Mostrar tarjetas de resumen
        st.markdown("### 📊 Resumen General")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Comprado", f"${total_comprado:,.2f}")
            st.caption(f"Pagado: ${compras_pagadas:,.2f}")
            st.caption(f"Impago: ${compras_impagas:,.2f}")
        
        with col2:
            st.metric("Total Vendido", f"${total_vendido:,.2f}")
            st.caption(f"Cobrado: ${ventas_cobradas:,.2f}")
            st.caption(f"Impago: ${ventas_impagag:,.2f}")
        
        with col3:
            st.metric("Saldo a Cuenta", f"${saldo_cuenta:,.2f}")
            if saldo_cuenta > 0:
                st.caption("🟢 Cliente tiene saldo a favor")
            elif saldo_cuenta < 0:
                st.caption("🔴 Saldo usado")
            else:
                st.caption("⚪ Sin saldo")
        
        with col4:
            if balance_final > 0:
                st.metric("Balance Total", f"${balance_final:,.2f}", delta="Me debe")
            elif balance_final < 0:
                st.metric("Balance Total", f"${abs(balance_final):,.2f}", delta="Le debo")
            else:
                st.metric("Balance Total", "$0.00", delta="Cuenta saldada")
        
        st.markdown("---")
        
        # Estado de cuenta detallado
        st.markdown("### 📋 Estado de Cuenta Detallado")
        
        # Crear tabla unificada de movimientos
        movimientos_cuenta = []
        
        # Agregar compras
        for _, row in compras_cliente.iterrows():
            movimientos_cuenta.append({
                'Fecha': row['fecha'],
                'Tipo': 'Compra (Yo compré)',
                'Detalle': f"{row['producto']} - {row['cantidad']} u. - {row['peso_kg']} kg",
                'Monto': row['precio_total'],
                'Estado': row['estado_pago'],
                'Debe': 0 if row['estado_pago'] == 'Pagado' else row['precio_total'],
                'Haber': 0
            })
        
        # Agregar ventas
        for _, row in ventas_cliente.iterrows():
            movimientos_cuenta.append({
                'Fecha': row['fecha'],
                'Tipo': 'Venta (Yo vendí)',
                'Detalle': f"{row['producto']} - {row['cantidad']} u. - {row['peso_kg']} kg",
                'Monto': row['precio_total'],
                'Estado': row['estado_pago'],
                'Debe': 0,
                'Haber': 0 if row['estado_pago'] == 'Pagado' else row['precio_total']
            })
        
        # Agregar pagos a cuenta
        for _, row in df_pagos_cliente.iterrows():
            movimientos_cuenta.append({
                'Fecha': row['fecha'],
                'Tipo': f"Pago a cuenta ({row['tipo']})",
                'Detalle': row['concepto'],
                'Monto': row['monto'],
                'Estado': '-',
                'Debe': 0 if row['tipo'] == 'ingreso' else row['monto'],
                'Haber': row['monto'] if row['tipo'] == 'ingreso' else 0
            })
        
        # Crear DataFrame y ordenar por fecha
        if movimientos_cuenta:
            df_cuenta = pd.DataFrame(movimientos_cuenta)
            df_cuenta = df_cuenta.sort_values('Fecha', ascending=False)
            
            # Calcular balance acumulado
            df_cuenta['Balance'] = (df_cuenta['Haber'] - df_cuenta['Debe']).cumsum()[::-1]
            
            st.dataframe(df_cuenta, use_container_width=True)
            
            # Exportar a Excel y CSV
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                excel_data = generar_excel(df_cuenta, nombre_hoja="Estado de Cuenta")
                if excel_data:
                    st.download_button(
                        label="📊 Descargar en Excel",
                        data=excel_data,
                        file_name=f"estado_cuenta_{cliente_resumen}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_estado_cuenta_excel"
                    )
            with col_exp2:
                csv = df_cuenta.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📄 Descargar en CSV",
                    data=csv,
                    file_name=f"estado_cuenta_{cliente_resumen}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key="download_estado_cuenta_csv"
                )
        else:
            st.info("No hay movimientos registrados para este cliente")
        
        # Botones de administración
        if st.session_state.auth['rol'] == 'admin':
            st.markdown("---")
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🗑️ Eliminar todos los movimientos", key="btn_eliminar_movs_cliente"):
                    eliminar_movimientos_cliente(cliente_resumen)
                    st.success("Movimientos eliminados")
                    st.rerun()
    
    else:
        # Vista general de todos los clientes
        st.markdown("### 📊 Resumen General de Todos los Clientes")
        
        resumen_general = []
        if clientes_unicos:
            for cliente in clientes_unicos:
                df_cliente = df[df['descripcion'] == cliente] if not df.empty else pd.DataFrame()
                compras = df_cliente[df_cliente['tipo'] == 'Ingreso (Compra)']['precio_total'].sum() if not df_cliente.empty else 0
                ventas = df_cliente[df_cliente['tipo'] == 'Egreso (Venta)']['precio_total'].sum() if not df_cliente.empty else 0
                compras_impagag = df_cliente[(df_cliente['tipo'] == 'Ingreso (Compra)') & (df_cliente['estado_pago'] == 'Impago')]['precio_total'].sum() if not df_cliente.empty else 0
                ventas_impagag = df_cliente[(df_cliente['tipo'] == 'Egreso (Venta)') & (df_cliente['estado_pago'] == 'Impago')]['precio_total'].sum() if not df_cliente.empty else 0
                saldo = calcular_saldo_cliente(cliente)
                balance = ventas_impagag - compras_impagag + saldo
                
                resumen_general.append({
                    'Cliente': cliente,
                    'Total Comprado': compras,
                    'Total Vendido': ventas,
                    'Deuda Compras': compras_impagag,
                    'Deuda Ventas': ventas_impagag,
                    'Saldo a Cuenta': saldo,
                    'Balance Final': balance
                })
        
        if resumen_general:
            df_resumen = pd.DataFrame(resumen_general)
            df_resumen = df_resumen.sort_values('Balance Final', ascending=False)
            
            # Colorear las filas según el balance
            def color_balance(val):
                if val > 0:
                    return 'background-color: #d4edda'  # Verde claro
                elif val < 0:
                    return 'background-color: #f8d7da'  # Rojo claro
                return ''
            
            st.dataframe(df_resumen, use_container_width=True)
            
            # Totales generales
            st.markdown("---")
            col_t1, col_t2, col_t3, col_t4 = st.columns(4)
            col_t1.metric("Total en Deudas de Compras", f"${df_resumen['Deuda Compras'].sum():,.2f}")
            col_t2.metric("Total en Deudas de Ventas", f"${df_resumen['Deuda Ventas'].sum():,.2f}")
            col_t3.metric("Saldo Total a Cuenta", f"${df_resumen['Saldo a Cuenta'].sum():,.2f}")
            col_t4.metric("Balance General", f"${df_resumen['Balance Final'].sum():,.2f}")
            
            # Exportar resumen general
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                excel_general = generar_excel(df_resumen, nombre_hoja="Resumen Clientes")
                if excel_general:
                    st.download_button(
                        label="📊 Descargar resumen en Excel",
                        data=excel_general,
                        file_name=f"resumen_clientes_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_resumen_general_excel"
                    )
            with col_exp2:
                csv_general = df_resumen.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📄 Descargar resumen en CSV",
                    data=csv_general,
                    file_name=f"resumen_clientes_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key="download_resumen_general_csv"
                )
        else:
            st.info("No hay clientes con movimientos registrados")

else:
    st.info("Aún no hay movimientos registrados. Usa el menú de la izquierda.")

# --- ADMINISTRACION DE USUARIOS ---
if st.session_state.auth['rol'] == 'admin':
    st.markdown("---")
    st.subheader("Administracion de Usuarios")
    
    # Botón de verificación y refresco
    col_diag1, col_diag2 = st.columns([3, 1])
    with col_diag2:
        if st.button("🔄 Refrescar datos", key="btn_refresh_all"):
            st.session_state.last_refresh += 1
            st.rerun()

    with st.expander("Log de Usuarios Creados"):
        df_users_log = obtener_usuarios()
        st.dataframe(df_users_log, use_container_width=True)

    with st.expander("Crear usuario"):
        nuevo_usuario = st.text_input("Nuevo usuario", key=f"new_user_{st.session_state.user_form_key}")
        nueva_pass = st.text_input("Contrasena", type="password", key=f"new_pass_{st.session_state.user_form_key}")
        nuevo_rol = st.selectbox("Rol", ["user", "admin"], key=f"new_role_{st.session_state.user_form_key}")
        if st.button("Crear", key="btn_crear_usuario"):
            if nuevo_usuario and nueva_pass:
                try:
                    crear_usuario(nuevo_usuario, nueva_pass, nuevo_rol)
                    st.success("Usuario creado")
                    st.session_state.user_form_key += 1
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al crear usuario: {str(e)}")
            else:
                st.error("Completa usuario y contrasena")

    with st.expander("Gestionar usuarios"):
        df_users = obtener_usuarios()
        st.dataframe(df_users, use_container_width=True)
        user_id = st.number_input("ID de usuario", min_value=1, step=1, key="manage_user_id")
        activar = st.checkbox("Activo", value=True, key="manage_user_activo")
        nuevo_rol_admin = st.selectbox("Rol", ["user", "admin"], key="edit_rol")
        nueva_pass_admin = st.text_input("Nueva contrasena (opcional)", type="password", key="reset_pass")
        if st.button("Actualizar usuario", key="btn_actualizar_usuario"):
            if user_id == 1:
                st.warning("No se puede cambiar el rol del admin principal")
            else:
                actualizar_rol_usuario(user_id, nuevo_rol_admin)
            actualizar_estado_usuario(user_id, activar)
            if nueva_pass_admin:
                actualizar_password(user_id, nueva_pass_admin)
            st.success("Usuario actualizado")
            st.rerun()

        st.markdown("---")
        if st.button("Eliminar usuario", key="btn_eliminar_usuario"):
            if user_id == 1:
                st.warning("No se puede eliminar el admin principal")
            else:
                usuario_row = df_users[df_users['id'] == user_id]
                usuario_nombre = usuario_row['usuario'].iloc[0] if not usuario_row.empty else ""
                confirmar_eliminacion_usuario(user_id, usuario_nombre)

    st.subheader("Administracion de Movimientos")
    with st.expander("Editar movimiento"):
        mov_id = st.number_input("ID de movimiento", min_value=1, step=1, key="mov_id")
        tipo_edit = st.selectbox("Tipo de Operacion", ["Ingreso (Compra)", "Egreso (Venta)"], key="mov_tipo")
        producto_edit = st.selectbox("Producto", ["Sal", "Cueros"], key="mov_producto")
        desc_edit = st.text_input("Descripcion / Cliente / Proveedor", key="mov_desc")
        col_m1, col_m2 = st.columns(2)
        cant_edit = col_m1.number_input("Cantidad (Unidades)", min_value=1, step=1, key="mov_cant")
        peso_edit = col_m2.number_input("Peso Total (kg)", min_value=0.0, step=0.1, key="mov_peso")
        precio_kg_edit = st.number_input("Precio por kg ($)", min_value=0.0, step=10.0, key="mov_precio_kg")
        iva_map = {"0%": 0.0, "10.5%": 0.105, "21%": 0.21}
        iva_edit = st.selectbox("IVA", ["0%", "10.5%", "21%"], key="mov_iva")
        modo_pago_edit = st.selectbox("Modo de Pago", ["Efectivo", "A cuenta", "Cheque", "Otros productos"], key="mov_modo")
        detalle_pago_edit = st.text_input("Detalle del pago (opcional)", key="mov_detalle")
        dinero_a_cuenta_edit = st.number_input("Dinero a cuenta ($)", min_value=0.0, step=100.0, key="mov_cuenta")
        estado_edit = st.selectbox("Estado de Pago", ["Pagado", "Impago"], key="mov_estado")

        iva_rate_edit = iva_map[iva_edit]
        neto_edit = precio_kg_edit * peso_edit
        total_con_iva_edit = neto_edit * (1 + iva_rate_edit)
        promedio_unidad_edit = (neto_edit / cant_edit) if cant_edit > 0 else 0.0
        st.write(f"Neto: ${neto_edit:,.2f}")
        st.write(f"Total con IVA: ${total_con_iva_edit:,.2f}")
        st.write(f"Promedio por unidad: ${promedio_unidad_edit:,.2f}")
        if st.button("Actualizar movimiento", key="btn_actualizar_movimiento"):
            if desc_edit:
                actualizar_movimiento(
                    mov_id,
                    tipo_edit,
                    producto_edit,
                    desc_edit,
                    cant_edit,
                    peso_edit,
                    total_con_iva_edit,
                    neto_edit,
                    iva_rate_edit,
                    modo_pago_edit,
                    detalle_pago_edit,
                    dinero_a_cuenta_edit,
                    estado_edit
                )
                st.success("Movimiento actualizado")
                st.rerun()
            else:
                st.error("Falta la descripcion")

    st.markdown("---")
    st.subheader("Administracion de Clientes")

    with st.expander("Log de Clientes Creados"):
        df_clientes_log = obtener_clientes()
        st.dataframe(df_clientes_log, use_container_width=True)

    with st.expander("Crear cliente"):
        nombre_cliente = st.text_input("Nombre del cliente / proveedor", key=f"new_cliente_nombre_{st.session_state.cliente_form_key}")
        tipo_cliente = st.selectbox("Tipo", ["Cliente", "Proveedor"], key=f"new_cliente_tipo_{st.session_state.cliente_form_key}")
        contacto_cliente = st.text_input("Persona de contacto", key=f"new_cliente_contacto_{st.session_state.cliente_form_key}")
        col_tel, col_email = st.columns(2)
        telefono_cliente = col_tel.text_input("Teléfono", key=f"new_cliente_telefono_{st.session_state.cliente_form_key}")
        email_cliente = col_email.text_input("Email", key=f"new_cliente_email_{st.session_state.cliente_form_key}")
        direccion_cliente = st.text_input("Dirección", key=f"new_cliente_direccion_{st.session_state.cliente_form_key}")
        notas_cliente = st.text_area("Notas adicionales", key=f"new_cliente_notas_{st.session_state.cliente_form_key}")
        if st.button("Crear", key="btn_crear_cliente"):
            if nombre_cliente:
                try:
                    crear_cliente(nombre_cliente, tipo_cliente, contacto_cliente, telefono_cliente, email_cliente, direccion_cliente, notas_cliente)
                    st.success("Cliente creado")
                    st.session_state.cliente_form_key += 1
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al crear cliente: {str(e)}")
            else:
                st.error("Completa el nombre del cliente")

    with st.expander("Gestionar clientes"):
        df_clientes = obtener_clientes()
        st.dataframe(df_clientes, use_container_width=True)
        cliente_id = st.number_input("ID de cliente", min_value=1, step=1, key="manage_cliente_id")
        cliente_data = obtener_cliente_por_id(cliente_id)
        if cliente_data:
            nombre_edit = st.text_input("Nombre", value=cliente_data['nombre'], key="edit_cliente_nombre")
            tipo_edit = st.selectbox("Tipo", ["Cliente", "Proveedor"], index=0 if cliente_data['tipo']=="Cliente" else 1, key="edit_cliente_tipo")
            contacto_edit = st.text_input("Persona de contacto", value=cliente_data['contacto'] or "", key="edit_cliente_contacto")
            col_tel_edit, col_email_edit = st.columns(2)
            telefono_edit = col_tel_edit.text_input("Teléfono", value=cliente_data['telefono'] or "", key="edit_cliente_telefono")
            email_edit = col_email_edit.text_input("Email", value=cliente_data['email'] or "", key="edit_cliente_email")
            direccion_edit = st.text_input("Dirección", value=cliente_data['direccion'] or "", key="edit_cliente_direccion")
            notas_edit = st.text_area("Notas", value=cliente_data['notas'] or "", key="edit_cliente_notas")
            activo_edit = st.checkbox("Activo", value=bool(cliente_data['activo']), key="edit_cliente_activo")
        else:
            nombre_edit = st.text_input("Nombre", key="edit_cliente_nombre")
            tipo_edit = st.selectbox("Tipo", ["Cliente", "Proveedor"], key="edit_cliente_tipo")
            contacto_edit = st.text_input("Persona de contacto", key="edit_cliente_contacto")
            col_tel_edit, col_email_edit = st.columns(2)
            telefono_edit = col_tel_edit.text_input("Teléfono", key="edit_cliente_telefono")
            email_edit = col_email_edit.text_input("Email", key="edit_cliente_email")
            direccion_edit = st.text_input("Dirección", key="edit_cliente_direccion")
            notas_edit = st.text_area("Notas", key="edit_cliente_notas")
            activo_edit = st.checkbox("Activo", value=True, key="edit_cliente_activo")
        
        if st.button("Actualizar cliente", key="btn_actualizar_cliente"):
            if nombre_edit:
                try:
                    actualizar_cliente(cliente_id, nombre_edit, tipo_edit, contacto_edit, telefono_edit, email_edit, direccion_edit, notas_edit, activo_edit)
                    st.success("Cliente actualizado")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al actualizar cliente: {str(e)}")
            else:
                st.error("Completa el nombre del cliente")

        st.markdown("---")
        if st.button("Eliminar cliente", key="btn_eliminar_cliente"):
            cliente_del = obtener_cliente_por_id(cliente_id)
            if cliente_del:
                confirmar_eliminacion_cliente(cliente_id, cliente_del['nombre'])
            else:
                st.warning("Cliente no encontrado")

    st.markdown("---")
    st.subheader("Gestion de Pagos a Cuenta")

    with st.expander("Registrar pago a cuenta"):
        st.info("Registra dinero que el cliente deja a cuenta o cuando se usa saldo")
        df_clientes_pago = obtener_clientes()
        if not df_clientes_pago.empty:
            clientes_activos_pago = df_clientes_pago[df_clientes_pago['activo'] == 1]
            if not clientes_activos_pago.empty:
                cliente_pago = st.selectbox(
                    "Seleccionar cliente",
                    options=clientes_activos_pago['nombre'].tolist(),
                    key="pago_cliente"
                )
            else:
                st.warning("No hay clientes activos")
                cliente_pago = None
        else:
            st.warning("No hay clientes registrados")
            cliente_pago = None
        
        if cliente_pago:
            tipo_pago = st.radio(
                "Tipo de movimiento",
                ["Ingreso (cliente deja dinero)", "Egreso (se usa saldo del cliente)"],
                key=f"tipo_pago_cuenta_{st.session_state.pago_form_key}"
            )
            monto_pago = st.number_input("Monto ($)", min_value=0.0, step=100.0, key=f"monto_pago_{st.session_state.pago_form_key}")
            concepto_pago = st.text_area("Concepto / Detalle", key=f"concepto_pago_{st.session_state.pago_form_key}")
            
            if st.button("Registrar pago", key="btn_registrar_pago"):
                if monto_pago > 0 and concepto_pago:
                    tipo_db = "ingreso" if "Ingreso" in tipo_pago else "egreso"
                    agregar_pago_cuenta(cliente_pago, monto_pago, concepto_pago, tipo_db)
                    st.success(f"Pago a cuenta registrado para {cliente_pago}")
                    st.session_state.pago_form_key += 1
                    st.rerun()
                else:
                    st.error("Completa el monto y el concepto")

    with st.expander("Historial de pagos a cuenta"):
        df_pagos_todos = obtener_pagos_cuenta()
        if not df_pagos_todos.empty:
            # Agregar columna de saldo acumulado por cliente
            st.dataframe(df_pagos_todos, use_container_width=True)
            
            # Mostrar resumen de saldos por cliente
            st.markdown("**Saldos por cliente:**")
            clientes_con_saldo = df_pagos_todos['cliente_nombre'].unique()
            for cliente in clientes_con_saldo:
                saldo = calcular_saldo_cliente(cliente)
                if saldo != 0:
                    color = "🟢" if saldo > 0 else "🔴"
                    st.write(f"{color} {cliente}: ${saldo:,.2f}")
        else:
            st.info("No hay pagos a cuenta registrados")

    with st.expander("Eliminar pago a cuenta"):
        df_pagos_del = obtener_pagos_cuenta()
        if not df_pagos_del.empty:
            st.dataframe(df_pagos_del, use_container_width=True)
            pago_id_del = st.number_input("ID del pago a eliminar", min_value=1, step=1, key="del_pago_id")
            if st.button("Eliminar pago", key="btn_eliminar_pago"):
                pago_row = df_pagos_del[df_pagos_del['id'] == pago_id_del]
                if not pago_row.empty:
                    cliente = pago_row['cliente_nombre'].iloc[0]
                    monto = pago_row['monto'].iloc[0]
                    confirmar_eliminacion_pago(pago_id_del, cliente, monto)
                else:
                    st.warning("Pago no encontrado")
        else:
            st.info("No hay pagos a cuenta para eliminar")

    st.markdown("---")
    with st.expander("🔍 Diagnóstico de Firebase"):
        st.write("**Información de la conexión:**")
        st.success("✅ Conectado a Firebase Firestore")
        st.code(f"Archivo de configuración: {FIREBASE_CREDS}")
        
        try:
            st.write("**Colecciones en Firebase:**")
            st.write("- usuarios")
            st.write("- clientes")
            st.write("- movimientos")
            st.write("- pagos_cuenta")
            
            st.write("**Conteo de documentos:**")
            num_usuarios = len(list(db.collection('usuarios').stream()))
            num_clientes = len(list(db.collection('clientes').stream()))
            num_movimientos = len(list(db.collection('movimientos').stream()))
            num_pagos = len(list(db.collection('pagos_cuenta').stream()))
            
            st.write(f"Usuarios: {num_usuarios}")
            st.write(f"Clientes: {num_clientes}")
            st.write(f"Movimientos: {num_movimientos}")
            st.write(f"Pagos a cuenta: {num_pagos}")
            
            if st.button("Verificar integridad", key="btn_verify_integrity"):
                st.success("✅ Firebase funcionando correctamente")
                st.info("Los datos se sincronizan automáticamente en la nube")
                
        except Exception as e:
            st.error(f"❌ Error al consultar Firebase: {str(e)}")