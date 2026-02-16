import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import hashlib

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Gestión Cueros", layout="wide")
st.title("🐄 Gestión de Stock y Pagos - Cueros")

# --- FUNCIONES DE BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect('cueros.db')
    c = conn.cursor()
    # Tabla única para registrar todo (ingresos y egresos)
    c.execute('''
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            tipo TEXT, -- 'Ingreso' (Compra) o 'Egreso' (Venta)
            descripcion TEXT, -- Tipo de cuero o Cliente
            cantidad INTEGER,
            peso_kg REAL,
            precio_total REAL,
            neto REAL,
            iva_rate REAL,
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
    # Tabla de usuarios
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            password_hash TEXT,
            rol TEXT, -- 'admin' o 'user'
            activo INTEGER -- 1 activo, 0 inactivo
        )
    ''')
    # Crear admin por defecto si no existe
    c.execute('SELECT COUNT(*) FROM usuarios')
    if c.fetchone()[0] == 0:
        password_hash = hashlib.sha256('admin'.encode('utf-8')).hexdigest()
        c.execute('INSERT INTO usuarios (usuario, password_hash, rol, activo) VALUES (?,?,?,?)',
                  ('admin', password_hash, 'admin', 1))
    conn.commit()
    conn.close()

def agregar_movimiento(tipo, descripcion, cantidad, peso, precio_total, neto, iva_rate, estado):
    conn = sqlite3.connect('cueros.db')
    c = conn.cursor()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO movimientos
        (fecha, tipo, descripcion, cantidad, peso_kg, precio_total, neto, iva_rate, estado_pago)
        VALUES (?,?,?,?,?,?,?,?,?)
    ''', (fecha, tipo, descripcion, cantidad, peso, precio_total, neto, iva_rate, estado))
    conn.commit()
    conn.close()

def obtener_datos():
    conn = sqlite3.connect('cueros.db')
    df = pd.read_sql_query("SELECT * FROM movimientos ORDER BY id DESC", conn)
    conn.close()
    return df

def autenticar_usuario(usuario, password):
    conn = sqlite3.connect('cueros.db')
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
    conn = sqlite3.connect('cueros.db')
    c = conn.cursor()
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    c.execute('INSERT INTO usuarios (usuario, password_hash, rol, activo) VALUES (?,?,?,?)',
              (usuario, password_hash, rol, 1))
    conn.commit()
    conn.close()

def obtener_usuarios():
    conn = sqlite3.connect('cueros.db')
    df_users = pd.read_sql_query("SELECT id, usuario, rol, activo FROM usuarios ORDER BY id ASC", conn)
    conn.close()
    return df_users

def actualizar_estado_usuario(user_id, activo):
    conn = sqlite3.connect('cueros.db')
    c = conn.cursor()
    c.execute('UPDATE usuarios SET activo = ? WHERE id = ?', (1 if activo else 0, user_id))
    conn.commit()
    conn.close()

def actualizar_password(user_id, new_password):
    conn = sqlite3.connect('cueros.db')
    c = conn.cursor()
    password_hash = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
    c.execute('UPDATE usuarios SET password_hash = ? WHERE id = ?', (password_hash, user_id))
    conn.commit()
    conn.close()

def actualizar_movimiento(mov_id, tipo, descripcion, cantidad, peso_kg, precio_total, neto, iva_rate, estado_pago):
    conn = sqlite3.connect('cueros.db')
    c = conn.cursor()
    c.execute('''
        UPDATE movimientos
        SET tipo = ?, descripcion = ?, cantidad = ?, peso_kg = ?, precio_total = ?, neto = ?, iva_rate = ?, estado_pago = ?
        WHERE id = ?
    ''', (tipo, descripcion, cantidad, peso_kg, precio_total, neto, iva_rate, estado_pago, mov_id))
    conn.commit()
    conn.close()

# Inicializar DB al arrancar
init_db()

# --- LOGIN ---
if 'auth' not in st.session_state:
    st.session_state.auth = None

with st.sidebar.expander("Acceso", expanded=True):
    if st.session_state.auth:
        st.write(f"Usuario: {st.session_state.auth['usuario']}")
        st.write(f"Rol: {st.session_state.auth['rol']}")
        if st.button("Cerrar sesion"):
            st.session_state.auth = None
            st.rerun()
    else:
        user_input = st.text_input("Usuario", key="login_user")
        pass_input = st.text_input("Contrasena", type="password", key="login_pass")
        if st.button("Ingresar"):
            auth = autenticar_usuario(user_input, pass_input)
            if auth:
                st.session_state.auth = auth
                st.success("Ingreso correcto")
                st.rerun()
            else:
                st.error("Usuario o contrasena incorrectos, o usuario inactivo")

if not st.session_state.auth:
    st.stop()

# --- BARRA LATERAL (ENTRADA DE DATOS) ---
st.sidebar.header("Nuevo Registro")

tipo_operacion = st.sidebar.selectbox("Tipo de Operación", ["Ingreso (Compra)", "Egreso (Venta)"])
desc_input = st.sidebar.text_input("Descripción / Cliente / Proveedor")
col1, col2 = st.sidebar.columns(2)
cant_input = col1.number_input("Cantidad (Unidades)", min_value=1, step=1)
peso_input = col2.number_input("Peso Total (kg)", min_value=0.0, step=0.1)
precio_kg = st.sidebar.number_input("Precio por kg ($)", min_value=0.0, step=10.0)
iva_opcion = st.sidebar.selectbox("IVA", ["0%", "10.5%", "21%"])
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
            desc_input,
            cant_input,
            peso_input,
            total_con_iva,
            neto,
            iva_rate,
            estado_pago
        )
        st.sidebar.success("¡Registrado con éxito!")
        st.rerun() # Recargar la página para ver cambios
    else:
        st.sidebar.error("Falta la descripción")

# --- PANEL PRINCIPAL ---

# 1. Obtener datos
df = obtener_datos()

if not df.empty:
    # 2. Cálculos de Stock y Finanzas
    ingresos = df[df['tipo'] == 'Ingreso (Compra)']
    egresos = df[df['tipo'] == 'Egreso (Venta)']
    
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
    
    # Filtro rapido
    filtro_pago = st.selectbox("Filtrar por estado de pago:", ["Todos", "Impago", "Pagado"])
    clientes = sorted(df['descripcion'].dropna().unique().tolist())
    opciones_clientes = ["Todos"] + clientes
    filtro_cliente = st.selectbox("Filtrar por cliente / descripcion", opciones_clientes, key="filtro_cliente")

    df_show = df
    if filtro_pago != "Todos":
        df_show = df_show[df_show['estado_pago'] == filtro_pago]
    if filtro_cliente != "Todos":
        df_show = df_show[df_show['descripcion'] == filtro_cliente]

    df_show_display = df_show.copy()
    if 'iva_rate' in df_show_display.columns:
        df_show_display['iva_%'] = (df_show_display['iva_rate'].fillna(0) * 100).round(1)
    columnas_base = [
        'id', 'fecha', 'tipo', 'descripcion', 'cantidad', 'peso_kg',
        'neto', 'iva_%', 'precio_total', 'estado_pago'
    ]
    columnas_disponibles = [c for c in columnas_base if c in df_show_display.columns]
    df_show_display = df_show_display[columnas_disponibles]

    st.dataframe(df_show_display, use_container_width=True)

    # --- ADMINISTRACION ---
    if st.session_state.auth['rol'] == 'admin':
        st.markdown("---")
        st.subheader("Administracion de Usuarios")

        with st.expander("Crear usuario"):
            nuevo_usuario = st.text_input("Nuevo usuario", key="new_user")
            nueva_pass = st.text_input("Contrasena", type="password", key="new_pass")
            nuevo_rol = st.selectbox("Rol", ["user", "admin"], key="new_role")
            if st.button("Crear"):
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
            user_id = st.number_input("ID de usuario", min_value=1, step=1)
            activar = st.checkbox("Activo", value=True)
            nueva_pass_admin = st.text_input("Nueva contrasena (opcional)", type="password", key="reset_pass")
            if st.button("Actualizar usuario"):
                actualizar_estado_usuario(user_id, activar)
                if nueva_pass_admin:
                    actualizar_password(user_id, nueva_pass_admin)
                st.success("Usuario actualizado")
                st.rerun()

        st.subheader("Administracion de Movimientos")
        with st.expander("Editar movimiento"):
            mov_id = st.number_input("ID de movimiento", min_value=1, step=1, key="mov_id")
            tipo_edit = st.selectbox("Tipo de Operacion", ["Ingreso (Compra)", "Egreso (Venta)"], key="mov_tipo")
            desc_edit = st.text_input("Descripcion / Cliente / Proveedor", key="mov_desc")
            col_m1, col_m2 = st.columns(2)
            cant_edit = col_m1.number_input("Cantidad (Unidades)", min_value=1, step=1, key="mov_cant")
            peso_edit = col_m2.number_input("Peso Total (kg)", min_value=0.0, step=0.1, key="mov_peso")
            precio_kg_edit = st.number_input("Precio por kg ($)", min_value=0.0, step=10.0, key="mov_precio_kg")
            iva_edit = st.selectbox("IVA", ["0%", "10.5%", "21%"], key="mov_iva")
            estado_edit = st.selectbox("Estado de Pago", ["Pagado", "Impago"], key="mov_estado")

            iva_rate_edit = iva_map[iva_edit]
            neto_edit = precio_kg_edit * peso_edit
            total_con_iva_edit = neto_edit * (1 + iva_rate_edit)
            promedio_unidad_edit = (neto_edit / cant_edit) if cant_edit > 0 else 0.0
            st.write(f"Neto: ${neto_edit:,.2f}")
            st.write(f"Total con IVA: ${total_con_iva_edit:,.2f}")
            st.write(f"Promedio por unidad: ${promedio_unidad_edit:,.2f}")
            if st.button("Actualizar movimiento"):
                if desc_edit:
                    actualizar_movimiento(
                        mov_id,
                        tipo_edit,
                        desc_edit,
                        cant_edit,
                        peso_edit,
                        total_con_iva_edit,
                        neto_edit,
                        iva_rate_edit,
                        estado_edit
                    )
                    st.success("Movimiento actualizado")
                    st.rerun()
                else:
                    st.error("Falta la descripcion")

else:
    st.info("Aún no hay movimientos registrados. Usa el menú de la izquierda.")