import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import hashlib
from pathlib import Path
import json

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Gestión Cueros", layout="wide")
st.title("🐄 Gestión de Stock y Pagos - Cueros")

DB_PATH = Path(__file__).resolve().parent / "cueros.db"
SESSION_FILE = Path(__file__).resolve().parent / ".session.json"

# --- FUNCIONES DE BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Tabla única para registrar todo (ingresos y egresos)
    c.execute('''
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            tipo TEXT, -- 'Ingreso' (Compra) o 'Egreso' (Venta)
            producto TEXT, -- 'Sal' o 'Cueros'
            descripcion TEXT, -- Tipo de cuero o Cliente
            cantidad INTEGER,
            peso_kg REAL,
            precio_total REAL,
            neto REAL,
            iva_rate REAL,
            modo_pago TEXT,
            detalle_pago TEXT,
            dinero_a_cuenta REAL,
            estado_pago TEXT -- 'Pagado' o 'Impago'
        )
    ''')
    # Migracion simple para columnas nuevas
    c.execute("PRAGMA table_info(movimientos)")
    columnas = {row[1] for row in c.fetchall()}
    if 'neto' not in columnas:
        c.execute('ALTER TABLE movimientos ADD COLUMN neto REAL')
    if 'iva_rate' not in columnas:
        c.execute('ALTER TABLE movimientos ADD COLUMN iva_rate REAL')
    if 'modo_pago' not in columnas:
        c.execute('ALTER TABLE movimientos ADD COLUMN modo_pago TEXT')
    if 'detalle_pago' not in columnas:
        c.execute('ALTER TABLE movimientos ADD COLUMN detalle_pago TEXT')
    if 'producto' not in columnas:
        c.execute('ALTER TABLE movimientos ADD COLUMN producto TEXT')
    if 'dinero_a_cuenta' not in columnas:
        c.execute('ALTER TABLE movimientos ADD COLUMN dinero_a_cuenta REAL')
    # Tabla de usuarios
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            password_hash TEXT,
            rol TEXT, -- 'admin' o 'user'
            activo INTEGER, -- 1 activo, 0 inactivo
            fecha_creacion TEXT
        )
    ''')
    # Migrar fecha_creacion
    c.execute("PRAGMA table_info(usuarios)")
    columnas_usuarios = {row[1] for row in c.fetchall()}
    if 'fecha_creacion' not in columnas_usuarios:
        c.execute('ALTER TABLE usuarios ADD COLUMN fecha_creacion TEXT')
    # Crear admin por defecto si no existe
    c.execute('SELECT COUNT(*) FROM usuarios')
    if c.fetchone()[0] == 0:
        password_hash = hashlib.sha256('admin'.encode('utf-8')).hexdigest()
        c.execute('INSERT INTO usuarios (usuario, password_hash, rol, activo) VALUES (?,?,?,?)',
                  ('admin', password_hash, 'admin', 1))
    # Tabla de clientes
    c.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE,
            tipo TEXT, -- 'Cliente' o 'Proveedor'
            contacto TEXT,
            telefono TEXT,
            email TEXT,
            direccion TEXT,
            notas TEXT,
            activo INTEGER, -- 1 activo, 0 inactivo
            fecha_creacion TEXT
        )
    ''')
    # Tabla de pagos a cuenta
    c.execute('''
        CREATE TABLE IF NOT EXISTS pagos_cuenta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            cliente_nombre TEXT,
            monto REAL,
            concepto TEXT,
            tipo TEXT -- 'ingreso' (cliente deja plata) o 'egreso' (se usa saldo)
        )
    ''')
    conn.commit()
    conn.close()

def agregar_movimiento(tipo, producto, descripcion, cantidad, peso, precio_total, neto, iva_rate, modo_pago, detalle_pago, dinero_a_cuenta, estado):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO movimientos
        (fecha, tipo, producto, descripcion, cantidad, peso_kg, precio_total, neto, iva_rate, modo_pago, detalle_pago, dinero_a_cuenta, estado_pago)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (fecha, tipo, producto, descripcion, cantidad, peso, precio_total, neto, iva_rate, modo_pago, detalle_pago, dinero_a_cuenta, estado))
    conn.commit()
    conn.close()

def obtener_datos():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM movimientos ORDER BY id DESC", conn)
    conn.close()
    return df

def autenticar_usuario(usuario, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    c.execute('SELECT usuario, rol, activo FROM usuarios WHERE usuario = ? AND password_hash = ?',
              (usuario, password_hash))
    row = c.fetchone()
    conn.close()
    if row and row[2] == 1:
        return {'usuario': row[0], 'rol': row[1]}
    return None

def crear_usuario(usuario, password, rol):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('INSERT INTO usuarios (usuario, password_hash, rol, activo, fecha_creacion) VALUES (?,?,?,?,?)',
              (usuario, password_hash, rol, 1, fecha))
    conn.commit()
    conn.close()

def obtener_usuarios():
    conn = sqlite3.connect(DB_PATH)
    df_users = pd.read_sql_query("SELECT id, usuario, rol, activo, fecha_creacion FROM usuarios ORDER BY id ASC", conn)
    conn.close()
    return df_users

def actualizar_estado_usuario(user_id, activo):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE usuarios SET activo = ? WHERE id = ?', (1 if activo else 0, user_id))
    conn.commit()
    conn.close()

def actualizar_password(user_id, new_password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    password_hash = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
    c.execute('UPDATE usuarios SET password_hash = ? WHERE id = ?', (password_hash, user_id))
    conn.commit()
    conn.close()

def actualizar_rol_usuario(user_id, rol):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE usuarios SET rol = ? WHERE id = ? AND usuario != ?', (rol, user_id, 'admin'))
    conn.commit()
    conn.close()

def eliminar_usuario(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM usuarios WHERE id = ? AND usuario != ?', (user_id, 'admin'))
    conn.commit()
    conn.close()

def actualizar_movimiento(mov_id, tipo, producto, descripcion, cantidad, peso_kg, precio_total, neto, iva_rate, modo_pago, detalle_pago, dinero_a_cuenta, estado_pago):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE movimientos
        SET tipo = ?, producto = ?, descripcion = ?, cantidad = ?, peso_kg = ?, precio_total = ?, neto = ?, iva_rate = ?, modo_pago = ?, detalle_pago = ?, dinero_a_cuenta = ?, estado_pago = ?
        WHERE id = ?
    ''', (tipo, producto, descripcion, cantidad, peso_kg, precio_total, neto, iva_rate, modo_pago, detalle_pago, dinero_a_cuenta, estado_pago, mov_id))
    conn.commit()
    conn.close()

def eliminar_movimiento(mov_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM movimientos WHERE id = ?', (mov_id,))
    conn.commit()
    conn.close()

def eliminar_movimientos_cliente(cliente):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM movimientos WHERE descripcion = ?', (cliente,))
    conn.commit()
    conn.close()

def crear_cliente(nombre, tipo, contacto, telefono, email, direccion, notas):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO clientes (nombre, tipo, contacto, telefono, email, direccion, notas, activo, fecha_creacion)
        VALUES (?,?,?,?,?,?,?,?,?)
    ''', (nombre, tipo, contacto, telefono, email, direccion, notas, 1, fecha))
    conn.commit()
    conn.close()

def obtener_clientes():
    conn = sqlite3.connect(DB_PATH)
    df_clientes = pd.read_sql_query("SELECT * FROM clientes ORDER BY nombre ASC", conn)
    conn.close()
    return df_clientes

def actualizar_cliente(cliente_id, nombre, tipo, contacto, telefono, email, direccion, notas, activo):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE clientes
        SET nombre = ?, tipo = ?, contacto = ?, telefono = ?, email = ?, direccion = ?, notas = ?, activo = ?
        WHERE id = ?
    ''', (nombre, tipo, contacto, telefono, email, direccion, notas, 1 if activo else 0, cliente_id))
    conn.commit()
    conn.close()

def eliminar_cliente(cliente_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM clientes WHERE id = ?', (cliente_id,))
    conn.commit()
    conn.close()

def obtener_cliente_por_id(cliente_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'nombre': row[1],
            'tipo': row[2],
            'contacto': row[3],
            'telefono': row[4],
            'email': row[5],
            'direccion': row[6],
            'notas': row[7],
            'activo': row[8],
            'fecha_creacion': row[9]
        }
    return None

def agregar_pago_cuenta(cliente_nombre, monto, concepto, tipo):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO pagos_cuenta (fecha, cliente_nombre, monto, concepto, tipo)
        VALUES (?,?,?,?,?)
    ''', (fecha, cliente_nombre, monto, concepto, tipo))
    conn.commit()
    conn.close()

def obtener_pagos_cuenta():
    conn = sqlite3.connect(DB_PATH)
    df_pagos = pd.read_sql_query("SELECT * FROM pagos_cuenta ORDER BY fecha DESC", conn)
    conn.close()
    return df_pagos

def obtener_pagos_cuenta_cliente(cliente_nombre):
    conn = sqlite3.connect(DB_PATH)
    df_pagos = pd.read_sql_query(
        "SELECT * FROM pagos_cuenta WHERE cliente_nombre = ? ORDER BY fecha DESC",
        conn,
        params=(cliente_nombre,)
    )
    conn.close()
    return df_pagos

def calcular_saldo_cliente(cliente_nombre):
    conn = sqlite3.connect(DB_PATH)
    df_pagos = pd.read_sql_query(
        "SELECT tipo, monto FROM pagos_cuenta WHERE cliente_nombre = ?",
        conn,
        params=(cliente_nombre,)
    )
    conn.close()
    
    saldo = 0
    for _, row in df_pagos.iterrows():
        if row['tipo'] == 'ingreso':
            saldo += row['monto']
        else:  # egreso
            saldo -= row['monto']
    return saldo

def eliminar_pago_cuenta(pago_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM pagos_cuenta WHERE id = ?', (pago_id,))
    conn.commit()
    conn.close()

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

# --- LOGIN ---
if 'auth' not in st.session_state:
    sesion_guardada = cargar_sesion()
    st.session_state.auth = sesion_guardada

with st.sidebar.expander("Acceso", expanded=True):
    if st.session_state.auth:
        st.write(f"Usuario: {st.session_state.auth['usuario']}")
        st.write(f"Rol: {st.session_state.auth['rol']}")
        st.caption(f"DB: {DB_PATH}")
        if DB_PATH.exists():
            st.success(f"✓ BD activa ({DB_PATH.stat().st_size} bytes)")
        else:
            st.error("✗ Base de datos no encontrada")
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
    clientes = sorted(df['descripcion'].dropna().unique().tolist())
    opciones_clientes = ["Todos"] + clientes
    filtro_cliente = col_f3.selectbox("Filtrar por cliente / descripcion", opciones_clientes, key="filtro_cliente")
    if col_f4.button("Limpiar"):
        st.session_state.filtro_pago = "Todos"
        st.session_state.filtro_producto = "Todos"
        st.session_state.filtro_cliente = "Todos"
        st.rerun()

    df_metric = df
    if filtro_pago != "Todos":
        df_metric = df_metric[df_metric['estado_pago'] == filtro_pago]
    if filtro_producto != "Todos":
        df_metric = df_metric[df_metric['producto'] == filtro_producto]
    if filtro_cliente != "Todos":
        df_metric = df_metric[df_metric['descripcion'] == filtro_cliente]

    # 2. Cálculos de Stock y Finanzas
    ingresos = df_metric[df_metric['tipo'] == 'Ingreso (Compra)']
    egresos = df_metric[df_metric['tipo'] == 'Egreso (Venta)']
    
    stock_actual_u = ingresos['cantidad'].sum() - egresos['cantidad'].sum()
    stock_actual_kg = ingresos['peso_kg'].sum() - egresos['peso_kg'].sum()
    
    # Deudas (Lo que debo pagar por compras impagas)
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
    if filtro_pago != "Todos":
        df_show = df_show[df_show['estado_pago'] == filtro_pago]
    if filtro_producto != "Todos":
        df_show = df_show[df_show['producto'] == filtro_producto]
    if filtro_cliente != "Todos":
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
    st.subheader("Resumen por Cliente")
    clientes_resumen = sorted(df['descripcion'].dropna().unique().tolist())
    opciones_resumen = ["Todos"] + clientes_resumen
    cliente_resumen = st.selectbox("Selecciona un cliente", opciones_resumen, key="cliente_resumen")
    df_cliente = df
    if cliente_resumen != "Todos":
        df_cliente = df_cliente[df_cliente['descripcion'] == cliente_resumen]
        
        # Mostrar saldo a cuenta del cliente
        saldo_cliente = calcular_saldo_cliente(cliente_resumen)
        if saldo_cliente > 0:
            st.success(f"💰 Saldo a favor del cliente: ${saldo_cliente:,.2f}")
        elif saldo_cliente < 0:
            st.warning(f"💸 Cliente debe: ${abs(saldo_cliente):,.2f}")
        else:
            st.info("💵 Sin saldo a cuenta")

    if st.session_state.auth['rol'] == 'admin' and cliente_resumen != "Todos":
        if st.button("Eliminar todos los movimientos de este cliente", key="btn_eliminar_movs_cliente"):
            eliminar_movimientos_cliente(cliente_resumen)
            st.success("Movimientos eliminados")
            st.rerun()

    ingresos_cliente = df_cliente[df_cliente['tipo'] == 'Ingreso (Compra)']
    egresos_cliente = df_cliente[df_cliente['tipo'] == 'Egreso (Venta)']

    st.write("Ingresos (Compras)")
    st.dataframe(ingresos_cliente, use_container_width=True)
    st.write("Egresos (Ventas)")
    st.dataframe(egresos_cliente, use_container_width=True)
    
    # Mostrar pagos a cuenta del cliente
    if cliente_resumen != "Todos":
        st.write("Pagos a Cuenta")
        df_pagos_cliente = obtener_pagos_cuenta_cliente(cliente_resumen)
        if not df_pagos_cliente.empty:
            st.dataframe(df_pagos_cliente, use_container_width=True)
        else:
            st.info("No hay pagos a cuenta registrados")

else:
    st.info("Aún no hay movimientos registrados. Usa el menú de la izquierda.")

# --- ADMINISTRACION DE USUARIOS ---
if st.session_state.auth['rol'] == 'admin':
    st.markdown("---")
    st.subheader("Administracion de Usuarios")

    with st.expander("Log de Usuarios Creados"):
        df_users_log = obtener_usuarios()
        st.dataframe(df_users_log, use_container_width=True)

    with st.expander("Crear usuario"):
        nuevo_usuario = st.text_input("Nuevo usuario", key="new_user")
        nueva_pass = st.text_input("Contrasena", type="password", key="new_pass")
        nuevo_rol = st.selectbox("Rol", ["user", "admin"], key="new_role")
        if st.button("Crear", key="btn_crear_usuario"):
            if nuevo_usuario and nueva_pass:
                try:
                    crear_usuario(nuevo_usuario, nueva_pass, nuevo_rol)
                    st.success("Usuario creado")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("El usuario ya existe")
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
        nombre_cliente = st.text_input("Nombre del cliente / proveedor", key="new_cliente_nombre")
        tipo_cliente = st.selectbox("Tipo", ["Cliente", "Proveedor"], key="new_cliente_tipo")
        contacto_cliente = st.text_input("Persona de contacto", key="new_cliente_contacto")
        col_tel, col_email = st.columns(2)
        telefono_cliente = col_tel.text_input("Teléfono", key="new_cliente_telefono")
        email_cliente = col_email.text_input("Email", key="new_cliente_email")
        direccion_cliente = st.text_input("Dirección", key="new_cliente_direccion")
        notas_cliente = st.text_area("Notas adicionales", key="new_cliente_notas")
        if st.button("Crear", key="btn_crear_cliente"):
            if nombre_cliente:
                try:
                    crear_cliente(nombre_cliente, tipo_cliente, contacto_cliente, telefono_cliente, email_cliente, direccion_cliente, notas_cliente)
                    st.success("Cliente creado")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Ya existe un cliente con ese nombre")
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
                except sqlite3.IntegrityError:
                    st.error("Ya existe otro cliente con ese nombre")
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
                key="tipo_pago_cuenta"
            )
            monto_pago = st.number_input("Monto ($)", min_value=0.0, step=100.0, key="monto_pago")
            concepto_pago = st.text_area("Concepto / Detalle", key="concepto_pago")
            
            if st.button("Registrar pago", key="btn_registrar_pago"):
                if monto_pago > 0 and concepto_pago:
                    tipo_db = "ingreso" if "Ingreso" in tipo_pago else "egreso"
                    agregar_pago_cuenta(cliente_pago, monto_pago, concepto_pago, tipo_db)
                    st.success(f"Pago a cuenta registrado para {cliente_pago}")
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