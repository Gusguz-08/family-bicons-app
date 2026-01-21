import streamlit as st
import psycopg2
import pandas as pd
import time
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURACIÓN DE LA APP
# ==========================================
st.set_page_config(page_title="Family Bicons - Banca Web", page_icon="🌱", layout="wide")

# 👇👇 TU ENLACE SEGURO 👇👇
try:
    DB_URL = st.secrets["DB_URL"]
except:
    st.error("⚠️ Error crítico: No se configuró el secreto DB_URL.")
    st.stop()

# ==========================================
# 🎨 ESTILOS CSS (MEJORADOS: DISEÑO TIPO PICHINCHA)
# ==========================================
st.markdown("""
    <style>
    /* 1. Fondo General */
    .stApp {
        background-color: #f4f6f9; /* Gris muy suave para el fondo */
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* 2. Contenedor de la Tarjeta de Login */
    .login-card-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
    }
    
    /* 3. Tarjeta de Login Blanca y con Sombra */
    .login-card {
        background-color: white;
        padding: 40px;
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); /* Sombra suave y moderna */
        width: 100%;
        max-width: 450px; /* Ancho máximo para que no se estire demasiado */
    }

    /* 4. Título Principal dentro de la Tarjeta */
    .login-title {
        color: #0f1c3f; /* Azul oscuro elegante */
        font-weight: 700;
        font-size: 28px;
        margin-bottom: 25px;
        text-align: center;
    }

    /* 5. Botón INGRESAR (AMARILLO PICHINCHA) */
    div.stButton > button:first-child {
        width: 100%; 
        border-radius: 8px; 
        background-color: #ffdd00 !important; /* Amarillo intenso */
        color: #0f1c3f !important; /* Texto azul oscuro */
        border: none; 
        font-weight: 700; /* Negrita */
        padding: 14px;
        font-size: 18px;
        box-shadow: 0 4px 6px rgba(255, 221, 0, 0.3);
        transition: all 0.2s ease-in-out;
        margin-top: 20px;
    }
    div.stButton > button:first-child:hover {
        background-color: #ffe64d !important; /* Amarillo más claro al pasar mouse */
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(255, 221, 0, 0.4);
    }

    /* 6. Estilos para los Inputs */
    .stTextInput > div > div > input {
        border: 1px solid #d1d5db;
        border-radius: 8px;
        padding: 12px;
        background-color: #f9fafb;
        color: #333;
        font-size: 16px;
    }
    .stTextInput > div > div > input:focus {
        border-color: #ffdd00; /* Borde amarillo al escribir */
        box-shadow: 0 0 0 2px rgba(255, 221, 0, 0.2);
        background-color: white;
    }

    /* Ocultar menú de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🔌 CONEXIÓN
# ==========================================
@st.cache_resource
def get_connection():
    try:
        return psycopg2.connect(DB_URL)
    except Exception:
        return None

# ==========================================
# 🧠 LÓGICA DE NEGOCIO
# ==========================================
def validar_login(usuario, password):
    conn = get_connection()
    if not conn: return False
    try:
        df = pd.read_sql("SELECT * FROM usuarios WHERE usuario = %s AND password = %s", conn, params=(usuario, password))
        return not df.empty
    except: return False

def obtener_datos_socio(usuario):
    conn = get_connection()
    if not conn: return pd.DataFrame(), pd.DataFrame()
    inv = pd.read_sql("SELECT * FROM inversiones WHERE nombre = %s", conn, params=(usuario,))
    deu = pd.read_sql("SELECT * FROM deudores WHERE nombre = %s AND estado = 'Pendiente'", conn, params=(usuario,))
    return inv, deu

def cambiar_password(usuario, nueva_pass):
    conn = get_connection()
    if not conn: return False
    try:
        cur = conn.cursor()
        cur.execute("UPDATE usuarios SET password = %s WHERE usuario = %s", (nueva_pass, usuario))
        conn.commit()
        cur.close()
        return True
    except: return False

def solicitar_prestamo(usuario, monto, motivo):
    conn = get_connection()
    if not conn: return False
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO solicitudes (usuario, monto, motivo, fecha, estado) VALUES (%s, %s, %s, %s, 'Pendiente')", 
                    (usuario, monto, motivo, datetime.now()))
        conn.commit()
        cur.close()
        return True
    except: return False

# ==========================================
# 📱 INTERFAZ PRINCIPAL
# ==========================================

# --- ESTADO DE SESIÓN ---
if 'usuario' not in st.session_state: st.session_state.usuario = None

# ==========================================
# 🔐 PANTALLA DE LOGIN (DISEÑO PROFESIONAL)
# ==========================================
if st.session_state.usuario is None:
    # Layout de dos columnas: Izquierda (Visual/Info) | Derecha (Tarjeta Login)
    col_izquierda, col_derecha = st.columns([1, 1], gap="large")

    # --- COLUMNA IZQUIERDA (Información y Logo) ---
    with col_izquierda:
        st.write("") # Espacio superior
        st.write("")
        
        with st.container():
            # Muestra tu logo en grande
            try:
                st.image("logo.png", use_container_width=True)
            except:
                st.header("🌱 Family Bicons")
            
            st.markdown("""
            <div style="margin-top: 40px; color: #0f1c3f;">
                <h1 style="font-weight: 800; font-size: 3.5rem; margin-bottom: 10px;">Bienvenido a tu Banca Web</h1>
                <p style="font-size: 1.2rem; color: #4b5563;">
                    Gestiona tus inversiones y créditos de forma segura y sencilla.
                </p>
                <div style="margin-top: 30px;">
                    <span style="font-size: 14px; color: #004d00;">✅ Acceso Seguro las 24h</span><br>
                    <span style="font-size: 14px; color: #004d00;">✅ Consulta tus saldos al instante</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # --- COLUMNA DERECHA (Tarjeta de Login Centrada) ---
    with col_derecha:
        # Usamos un contenedor para centrar la tarjeta verticalmente
        with st.container():
            st.markdown('<div class="login-card-container">', unsafe_allow_html=True)
            
            # Inicio de la Tarjeta Blanca
            st.markdown('<div class="login-card">', unsafe_allow_html=True)
            
            # Título de la tarjeta
            st.markdown('<div class="login-title">Ingresa a tu Cuenta</div>', unsafe_allow_html=True)
            
            # FORMULARIO
            with st.form("frm_login"):
                u = st.text_input("Usuario", placeholder="Tu nombre de usuario")
                p = st.text_input("Contraseña", type="password", placeholder="Tu contraseña")
                
                # El botón se estiliza con el CSS de arriba para ser AMARILLO
                btn = st.form_submit_button("INGRESAR")
                
                if btn:
                    if validar_login(u, p):
                        st.session_state.usuario = u
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas")

            # Enlace de "Olvidaste tu contraseña"
            st.markdown("""
            <div style="text-align: center; margin-top: 25px;">
                <a href="#" style="color:#004d00; text-decoration:none; font-size:14px; font-weight:600;">¿Olvidaste tu contraseña?</a>
                <br><br>
                <span style="color:#9ca3af; font-size:13px;">🔒 Conexión Segura SSL | Family Bicons © 2026</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Fin de la Tarjeta Blanca
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🏦 DENTRO DE LA APP (DASHBOARD)
# ==========================================
else:
    user = st.session_state.usuario
    inv, deu = obtener_datos_socio(user)
    
    # Header
    st.markdown(f"### Hola, **{user}** 👋")
    
    tab1, tab2, tab3, tab4 = st.tabs(["💎 ACCIONES", "📅 PAGOS", "💸 SOLICITAR", "⚙️ PERFIL"])
    
    # ---------------- TAB 1: ACCIONES ----------------
    with tab1:
        st.write("")
        if not inv.empty:
            valores_texto = inv.iloc[0]['valores_meses']
            if valores_texto:
                valores = [float(x) for x in valores_texto.split(",")]
                total_acciones = sum(valores)
                dinero_total = total_acciones * 5.0
                
                st.markdown(f"""
                <div class="card">
                    <div style="color:#666; font-size:14px; text-transform:uppercase; letter-spacing: 1px; font-weight: 600;">Capital Acumulado</div>
                    <div class="big-money">${dinero_total:,.2f}</div>
                    <div style="margin-top:15px; border-top:1px solid #eee; padding-top:15px; font-size:14px; color:#555;">
                        Tienes <b>{int(total_acciones)}</b> acciones activas
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.caption("📈 Evolución de tu inversión")
                df_chart = pd.DataFrame({"Mes": ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"][:len(valores)], "Acciones": valores})
                st.area_chart(df_chart.set_index("Mes"), color="#004d00") # VERDE
            else:
                st.warning("Datos incompletos.")
        else:
            st.info("No tienes inversiones activas.")

    # ---------------- TAB 2: DEUDAS ----------------
    with tab2:
        st.write("")
        if not deu.empty:
            st.markdown("##### ⚠️ Pagos Pendientes")
            for index, row in deu.iterrows():
                monto_total = row['monto']
                plazo = row['plazo']
                cuota = monto_total / plazo if plazo > 0 else monto_total
                
                st.markdown(f"""
                <div class="card-debt">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:bold; color:#333; font-size: 16px;">PRÉSTAMO ({row['mes']})</span>
                        <span style="background:#ffebee; color:#c53030; padding:4px 12px; border-radius:15px; font-size:12px; font-weight:bold;">POR PAGAR</span>
                    </div>
                    <div style="margin-top:15px; font-size:14px; color:#666;">Cuota mensual:</div>
                    <div style="font-size:24px; font-weight:bold; color:#c53030;">${cuota:,.2f}</div>
                    <div style="margin-top:8px; font-size:13px; color:#888;">
                        Total restante: ${monto_total:,.2f} (Plazo: {plazo} meses)
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ ¡Todo pagado! Estás libre de deudas.")

    # ---------------- TAB 3: SOLICITAR ----------------
    with tab3:
        st.write("")
        st.markdown("##### 📝 Nueva Solicitud")
        st.info("Completa los datos para solicitar un nuevo crédito.")
        
        with st.form("frm_solicitud"):
            monto_req = st.number_input("Monto a solicitar ($)", min_value=10.0, step=5.0)
            motivo_req = st.text_area("¿Para qué es el dinero?", placeholder="Ej: Compra de mercadería...")
            st.write("")
            btn_sol = st.form_submit_button("ENVIAR SOLICITUD")
            
            if btn_sol:
                if solicitar_prestamo(user, monto_req, motivo_req):
                    st.success("✅ Solicitud enviada correctamente.")
                else:
                    st.error("Error al enviar.")

    # ---------------- TAB 4: PERFIL ----------------
    with tab4:
        st.write("")
        st.markdown("##### 👤 Mi Seguridad")
        
        with st.expander("🔐 Cambiar Contraseña"):
            st.write("Ingresa tu nueva contraseña dos veces para confirmar.")
            p1 = st.text_input("Nueva contraseña", type="password", key="p1")
            p2 = st.text_input("Confirmar contraseña", type="password", key="p2")
            if st.button("Actualizar Clave"):
                if p1 == p2 and len(p1) > 0:
                    if cambiar_password(user, p1):
                        st.success("Contraseña actualizada.")
                        st.session_state.usuario = None
                        st.rerun()
                else:
                    st.warning("Las contraseñas no coinciden.")

        st.divider()
        if st.button("Cerrar Sesión", type="secondary"):
            st.session_state.usuario = None
            st.rerun()
