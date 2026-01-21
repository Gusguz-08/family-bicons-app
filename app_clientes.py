import streamlit as st
import psycopg2
import pandas as pd
import time
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURACIÓN DE LA APP
# ==========================================
st.set_page_config(page_title="Banca Web | Family Bicons", page_icon="🌱", layout="wide")

# 👇👇 TU ENLACE SEGURO 👇👇
try:
    DB_URL = st.secrets["DB_URL"]
except:
    st.error("⚠️ Error crítico: No se configuró el secreto DB_URL.")
    st.stop()

# ==========================================
# 🎨 ESTILOS CSS (MODO APP ESTÁTICA)
# ==========================================
st.markdown("""
    <style>
    /* 1. CONGELAR PANTALLA (No scroll) */
    [data-testid="stAppViewContainer"] {
        overflow: hidden !important; 
        height: 100vh !important;
    }
    .block-container {
        padding-top: 2rem !important; 
        padding-bottom: 0rem !important;
        max-width: 100% !important;
    }
    
    /* Ocultar barras extra */
    [data-testid="stToolbar"], footer, #MainMenu, header { display: none !important; }

    /* 2. ESTILO GENERAL */
    .stApp {
        background-color: #f2f4f8;
        font-family: 'Segoe UI', sans-serif;
        font-size: 14px;
    }

    /* 3. LOGO */
    [data-testid="stImage"] img {
        border-radius: 50%;
        border: 4px solid white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        background-color: white;
    }

    /* 4. TARJETA CENTRAL */
    [data-testid="stForm"], .recovery-card {
        background-color: white;
        padding: 30px !important;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border: 1px solid #e1e4e8;
        max-width: 400px;
        margin: 0 auto;
    }

    /* 5. INPUTS */
    .stTextInput input {
        padding: 10px;
        font-size: 14px;
        border: 1px solid #ccc;
        border-radius: 6px;
    }
    .stTextInput input:focus {
        border-color: #004d00;
        box-shadow: 0 0 0 2px rgba(0, 77, 0, 0.2);
    }
    .stTextInput label { font-size: 13px !important; margin-bottom: 2px !important; }

    /* 6. BOTONES (VERDES) */
    .stButton button {
        background-color: #004d00 !important;
        color: white !important;
        border: none !important;
        width: 100%;
        padding: 12px !important;
        font-weight: 700 !important;
        border-radius: 6px !important;
        margin-top: 10px !important;
    }
    .stButton button:hover { background-color: #006600 !important; }

    /* Botón secundario (Volver) */
    .btn-secondary button {
        background-color: #666 !important;
    }
    
    /* 7. TEXTO LINK (Olvidaste contraseña) */
    .link-btn button {
        background: transparent !important;
        color: #004d00 !important;
        text-decoration: underline;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
        font-size: 12px !important;
        width: auto !important;
        height: auto !important;
    }
    .link-btn button:hover { color: #006600 !important; background: transparent !important; }

    /* Footer fijo */
    .copyright-fixed {
        position: fixed; bottom: 10px; width: 100%; text-align: center;
        font-size: 11px; color: #aaa; left: 0;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🔌 CONEXIÓN
# ==========================================
@st.cache_resource
def get_connection():
    try: return psycopg2.connect(DB_URL)
    except: return None

# ==========================================
# 🧠 LÓGICA
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

if 'usuario' not in st.session_state: st.session_state.usuario = None
# Variable para saber si estamos viendo el login o la recuperación
if 'vista_login' not in st.session_state: st.session_state.vista_login = 'login' 

# ---------------------------------------------------------
# PANTALLA DE INICIO (LOGIN / RECUPERACIÓN)
# ---------------------------------------------------------
if st.session_state.usuario is None:
    
    col1, col2 = st.columns([1.1, 1], gap="medium")

    # --- IZQUIERDA (INFO) ---
    with col1:
        st.write("") 
        try:
            st.image("logo.png", width=140)
        except:
            st.header("🌱 Family Bicons")

        st.markdown("""
        <h1 style="font-size: 34px; margin-top: 5px; margin-bottom: 0px; color: #0f1c3f;">Family Bicons</h1>
        <h3 style="margin-top: 0px; margin-bottom: 15px; font-size: 16px; color: #555;">Banca Web Segura</h3>
        
        <div style="background-color: white; padding: 12px; border-radius: 8px; border-left: 4px solid #004d00; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <span style="font-size: 14px; margin-right: 8px; color: #004d00;">✅</span>
                <span style="font-size: 12px; color: #555;">Sitio Verificado.</span>
            </div>
            <div style="display: flex; align-items: center;">
                <span style="font-size: 14px; margin-right: 8px; color: #c53030;">🚫</span>
                <span style="font-size: 12px; color: #555;">No compartas tu clave.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- DERECHA (TARJETA DINÁMICA) ---
    with col2:
        st.write("") 
        
        # --- VISTA 1: FORMULARIO DE LOGIN ---
        if st.session_state.vista_login == 'login':
            with st.form("frm_login"):
                st.markdown("<h3 style='text-align: center; margin-bottom: 10px; color:#333; font-weight:600; font-size:20px;'>Bienvenido</h3>", unsafe_allow_html=True)
                
                u = st.text_input("Usuario", placeholder="Tu usuario")
                p = st.text_input("Contraseña", type="password", placeholder="••••••••")
                
                st.write("")
                if st.form_submit_button("INGRESAR"):
                    if validar_login(u, p):
                        st.session_state.usuario = u
                        st.rerun()
                    else:
                        st.error("Datos incorrectos")

            # Botón "Olvidaste tu contraseña" fuera del form para manejar el estado
            st.markdown("<div style='text-align: right; margin-top: 10px;' class='link-btn'>", unsafe_allow_html=True)
            if st.button("¿Olvidaste tu contraseña?"):
                st.session_state.vista_login = 'recuperar' # Cambiamos la vista
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # --- VISTA 2: RECUPERACIÓN DE CONTRASEÑA ---
        elif st.session_state.vista_login == 'recuperar':
            st.markdown("""
            <div class="recovery-card">
                <h3 style="color:#004d00; text-align:center;">Recuperar Acceso</h3>
                <p style="font-size:13px; text-align:center; color:#666;">
                    Por seguridad, el restablecimiento de contraseña debe ser realizado por un administrador.
                </p>
                <div style="background:#f9f9f9; padding:15px; border-radius:8px; margin:15px 0;">
                    <small style="font-weight:bold; color:#333;">📞 Contacto Soporte:</small><br>
                    <span style="color:#004d00;">+593 99 999 9999</span>
                </div>
                <p style="font-size:12px; color:#888;">Envía tu número de cédula y usuario para validar tu identidad.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botón Volver con estilo secundario
            st.markdown("<div class='btn-secondary'>", unsafe_allow_html=True)
            if st.button("⬅ Volver al Login"):
                st.session_state.vista_login = 'login' # Regresamos
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # Copyright fijo
    st.markdown('<div class="copyright-fixed">© 2026 Family Bicons. Todos los derechos reservados.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# DASHBOARD (APP DENTRO)
# ---------------------------------------------------------
else:
    # Habilitar scroll adentro
    st.markdown("<style>[data-testid='stAppViewContainer'] { overflow: auto !important; }</style>", unsafe_allow_html=True)

    user = st.session_state.usuario
    inv, deu = obtener_datos_socio(user)
    
    st.markdown(f"### Hola, **{user}** 👋")
    
    tab1, tab2, tab3, tab4 = st.tabs(["💎 INVERSIONES", "📅 PAGOS", "💸 SOLICITAR", "⚙️ PERFIL"])
    
    with tab1:
        st.write("")
        if not inv.empty:
            valores_texto = inv.iloc[0]['valores_meses']
            if valores_texto:
                valores = [float(x) for x in valores_texto.split(",")]
                total_acciones = sum(valores)
                dinero_total = total_acciones * 5.0
                st.markdown(f"""
                <div style="background:white; padding:25px; border-radius:12px; border-left:6px solid #004d00; box-shadow:0 4px 15px rgba(0,0,0,0.05);">
                    <div style="color:#666; font-size:13px;">CAPITAL ACUMULADO</div>
                    <div style="font-size:36px; font-weight:800; color:#004d00;">${dinero_total:,.2f}</div>
                    <div style="margin-top:10px; font-size:14px; color:#555;"><b>{int(total_acciones)}</b> acciones activas</div>
                </div>
                """, unsafe_allow_html=True)
                df_chart = pd.DataFrame({"Mes": ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"][:len(valores)], "Acciones": valores})
                st.area_chart(df_chart.set_index("Mes"), color="#004d00")
            else: st.warning("Sin datos.")
        else: st.info("Sin inversiones.")

    with tab2:
        st.write("")
        if not deu.empty:
            st.markdown("##### ⚠️ Pendientes")
            for index, row in deu.iterrows():
                monto_total = row['monto']
                plazo = row['plazo']
                cuota = monto_total / plazo if plazo > 0 else monto_total
                st.markdown(f"""
                <div style="background:white; padding:20px; border-radius:10px; border-left:5px solid #c53030; box-shadow:0 2px 8px rgba(0,0,0,0.08); margin-bottom:15px;">
                    <div style="display:flex; justify-content:space-between;"><b>{row['mes']}</b> <span style="color:#c53030; font-weight:bold;">PENDIENTE</span></div>
                    <div style="font-size:26px; color:#c53030; font-weight:bold;">${cuota:,.2f}</div>
                    <div style="color:#666; font-size:13px;">Total: ${monto_total:,.2f}</div>
                </div>""", unsafe_allow_html=True)
        else: st.success("✅ Al día")

    with tab3:
        st.write("")
        st.markdown("##### 📝 Solicitar")
        st.markdown('<div style="background:white; padding:20px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
        with st.form("frm_solicitud"):
            monto_req = st.number_input("Monto ($)", min_value=10.0, step=5.0)
            motivo_req = st.text_area("Motivo")
            if st.form_submit_button("ENVIAR"):
                if solicitar_prestamo(user, monto_req, motivo_req): st.success("Enviado.")
                else: st.error("Error.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab4:
        st.write("")
        with st.expander("🔐 Contraseña"):
            p1 = st.text_input("Nueva", type="password", key="p1")
            p2 = st.text_input("Confirmar", type="password", key="p2")
            if st.button("Guardar"):
                if p1 == p2 and len(p1)>0:
                    if cambiar_password(user, p1):
                        st.success("Listo.")
                        st.session_state.usuario = None
                        st.rerun()
                else: st.warning("Error.")
        st.divider()
        if st.button("Salir"):
            st.session_state.usuario = None
            st.rerun()

