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
    # Para pruebas locales si no hay secretos, usa un pass
    DB_URL = "" 
    # st.error("⚠️ Error crítico: No se configuró el secreto DB_URL.")
    # st.stop()

# ==========================================
# 🎨 ESTILOS CSS (CORREGIDOS Y UNIFICADOS)
# ==========================================
st.markdown("""
    <style>
    /* 1. FORZAR MODO CLARO Y TEXTO OSCURO (SOLUCIÓN AL TEXTO INVISIBLE) */
    .stApp {
        background-color: #f2f4f8;
        color: #0f1c3f !important; /* Texto Azul Oscuro SIEMPRE */
    }
    
    /* Forzar color en títulos y textos de Streamlit */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stTextInput > label, div[data-testid="stExpander"] p {
        color: #0f1c3f !important;
    }

    /* 2. LIMPIEZA DE INTERFAZ */
    [data-testid="stToolbar"], footer, #MainMenu, header { display: none !important; }
    .block-container {
        padding-top: 2rem !important; 
        padding-bottom: 2rem !important;
        max-width: 900px !important; /* Centrar el contenido para que no se estire demasiado */
    }

    /* 3. TARJETAS DEL DASHBOARD (Para que lo de adentro no se vea feo) */
    .card-dashboard {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #e1e4e8;
        margin-bottom: 20px;
    }

    /* 4. ESTILOS DE LOGIN (MANTENIDOS) */
    [data-testid="stForm"], .recovery-card {
        background-color: white !important;
        padding: 40px !important;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border: 1px solid #e1e4e8;
    }

    /* 5. INPUTS MEJORADOS */
    .stTextInput input {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 1px solid #ced4da !important;
    }
    
    /* 6. BOTONES */
    .stButton button {
        background-color: #004d00 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background-color: #006600 !important;
        box-shadow: 0 4px 10px rgba(0,77,0,0.2);
    }

    /* Botón de salir (Rojo suave) */
    .logout-btn button {
        background-color: #fff !important;
        color: #c53030 !important;
        border: 1px solid #c53030 !important;
    }
    .logout-btn button:hover {
        background-color: #c53030 !important;
        color: white !important;
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
    if not conn: return True # MODO PRUEBA: Permite entrar si no hay base de datos
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
if 'vista_login' not in st.session_state: st.session_state.vista_login = 'login' 

# ---------------------------------------------------------
# PANTALLA DE INICIO (LOGIN)
# ---------------------------------------------------------
if st.session_state.usuario is None:
    
    col1, col2 = st.columns([1, 1], gap="large")

    # --- IZQUIERDA ---
    with col1:
        st.write("") 
        st.markdown("""
        <div style="padding-top: 40px;">
            <h1 style="font-size: 42px; margin-bottom: 10px; color: #004d00 !important;">Family Bicons</h1>
            <h3 style="color: #666 !important; font-weight: 400;">Tu banca segura y transparente.</h3>
            <br>
            <div style="background-color: white; padding: 20px; border-radius: 12px; border-left: 5px solid #004d00; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                <p style="margin:0; font-size:15px; color:#444 !important;">
                    <b>💡 Consejo de seguridad:</b><br>
                    Nunca compartas tu contraseña con terceros. El equipo de soporte nunca te la pedirá.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- DERECHA (LOGIN) ---
    with col2:
        st.write("")
        st.write("")
        if st.session_state.vista_login == 'login':
            with st.form("frm_login"):
                st.markdown("<h3 style='text-align: center; color:#0f1c3f !important;'>Iniciar Sesión</h3>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color:#888 !important; font-size: 13px;'>Ingresa tus credenciales para continuar</p>", unsafe_allow_html=True)
                
                u = st.text_input("Usuario", placeholder="Ej: diegoballa")
                p = st.text_input("Contraseña", type="password", placeholder="••••••••")
                
                st.write("")
                if st.form_submit_button("INGRESAR"):
                    if validar_login(u, p):
                        st.session_state.usuario = u
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas")

            if st.button("¿Olvidaste tu contraseña?", type="secondary"):
                st.session_state.vista_login = 'recuperar'
                st.rerun()

        elif st.session_state.vista_login == 'recuperar':
            st.markdown("""
            <div class="recovery-card">
                <h3 style="text-align:center;">Recuperar Acceso</h3>
                <p style="text-align:center; color:#666;">Contacta al administrador para restablecer tu clave.</p>
                <div style="background:#f0fdf4; padding:15px; border-radius:8px; text-align:center; margin: 15px 0;">
                    <span style="color:#004d00; font-weight:bold; font-size: 18px;">📞 +593 96 734 2110</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("⬅ Volver"):
                st.session_state.vista_login = 'login'
                st.rerun()

    # Footer
    st.markdown('<div style="position: fixed; bottom: 20px; width: 100%; text-align: center; color: #aaa; font-size: 12px;">© 2026 Family Bicons System</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# DASHBOARD (AHORA VISIBLE Y BONITO)
# ---------------------------------------------------------
else:
    user = st.session_state.usuario
    inv, deu = obtener_datos_socio(user)
    
    # Header minimalista
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 20px;">
        <div>
            <h2 style="margin:0; color: #004d00 !important;">Hola, {user} 👋</h2>
            <p style="margin:0; color: #666 !important;">Bienvenido a tu panel financiero</p>
        </div>
        <div style="background:white; padding:5px 15px; border-radius:20px; border:1px solid #ddd; font-size:12px; color:#555;">
            🟢 Conectado
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # TABS
    tab1, tab2, tab3, tab4 = st.tabs(["💎 Inversiones", "📅 Pagos Pendientes", "💸 Solicitar Crédito", "⚙️ Mi Perfil"])
    
    # --- TAB 1: INVERSIONES ---
    with tab1:
        st.write("")
        # Usamos HTML para crear la tarjeta visual
        if not inv.empty:
            valores_texto = inv.iloc[0]['valores_meses']
            valores = [float(x) for x in valores_texto.split(",")] if valores_texto else []
            total_acciones = sum(valores)
            dinero_total = total_acciones * 5.0
            
            st.markdown(f"""
            <div class="card-dashboard">
                <div style="display:flex; align-items:center; margin-bottom:15px;">
                    <div style="font-size:30px; margin-right:10px;">💰</div>
                    <div>
                        <div style="color:#666; font-size:13px; text-transform:uppercase; letter-spacing:1px;">Capital Total</div>
                        <div style="font-size:32px; font-weight:800; color:#004d00;">${dinero_total:,.2f}</div>
                    </div>
                </div>
                <hr style="border:0; border-top:1px solid #eee; margin:15px 0;">
                <div style="display:flex; justify-content:space-between; color:#555; font-size:14px;">
                    <span>Acciones Acumuladas:</span>
                    <span style="font-weight:bold;">{int(total_acciones)} u.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Gráfico en su propia tarjeta
            with st.container():
                st.markdown('<div class="card-dashboard"><h5>📈 Rendimiento</h5>', unsafe_allow_html=True)
                df_chart = pd.DataFrame({"Mes": ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"][:len(valores)], "Acciones": valores})
                st.area_chart(df_chart.set_index("Mes"), color="#004d00")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Aún no tienes inversiones registradas.")

    # --- TAB 2: PAGOS ---
    with tab2:
        st.write("")
        if not deu.empty:
            for index, row in deu.iterrows():
                monto = row['monto']
                plazo = row['plazo'] if row['plazo'] > 0 else 1
                cuota = monto / plazo
                
                st.markdown(f"""
                <div class="card-dashboard" style="border-left: 5px solid #c53030;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <h4 style="margin:0; color:#c53030 !important;">{row['mes']}</h4>
                            <span style="font-size:12px; background:#ffebeb; color:#c53030; padding:2px 8px; border-radius:4px;">PENDIENTE</span>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-size:24px; font-weight:bold; color:#333;">${cuota:,.2f}</div>
                            <small style="color:#888;">de ${monto:,.2f}</small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card-dashboard" style="text-align:center; padding:40px;">
                <h1 style="font-size:50px;">🎉</h1>
                <h3 style="color:#004d00 !important;">¡Estás al día!</h3>
                <p style="color:#666;">No tienes pagos pendientes por ahora.</p>
            </div>
            """, unsafe_allow_html=True)

    # --- TAB 3: SOLICITAR ---
    with tab3:
        st.write("")
        # Aquí metemos el formulario dentro de una tarjeta visual usando Markdown antes y después
        st.markdown('<div class="card-dashboard">', unsafe_allow_html=True)
        st.markdown("#### 📝 Nueva Solicitud")
        st.markdown("<p style='color:#666; font-size:14px; margin-bottom:20px;'>Completa los datos para solicitar un adelanto o préstamo.</p>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            monto_req = st.number_input("Monto a solicitar ($)", min_value=10.0, step=5.0, value=50.0)
        with c2:
            motivo_req = st.text_input("Motivo (Breve)", placeholder="Ej: Emergencia médica")
            
        st.write("")
        if st.button("Enviar Solicitud"):
            if solicitar_prestamo(user, monto_req, motivo_req):
                st.success("Solicitud enviada correctamente.")
            else:
                st.error("Hubo un error al procesar la solicitud.")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 4: PERFIL ---
    with tab4:
        st.write("")
        # Tarjeta de Datos
        st.markdown(f"""
        <div class="card-dashboard">
            <h4 style="margin-bottom:15px;">👤 Mis Datos</h4>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px;">
                <div>
                    <label style="font-size:12px; color:#888;">Usuario</label>
                    <div style="font-weight:bold; font-size:16px;">{user}</div>
                </div>
                <div>
                    <label style="font-size:12px; color:#888;">Estado</label>
                    <div style="color:#004d00; font-weight:bold;">Activo</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Tarjeta de Seguridad
        st.markdown('<div class="card-dashboard">', unsafe_allow_html=True)
        st.markdown('<h4 style="margin-bottom:15px;">🔐 Seguridad</h4>', unsafe_allow_html=True)
        
        with st.expander("Cambiar Contraseña"):
            curr_pass = st.text_input("Contraseña Actual", type="password")
            new_p1 = st.text_input("Nueva Contraseña", type="password")
            new_p2 = st.text_input("Repetir Nueva Contraseña", type="password")
            
            if st.button("Actualizar Clave"):
                if new_p1 == new_p2 and len(new_p1) > 0:
                    if cambiar_password(user, new_p1):
                        st.success("Contraseña actualizada. Inicia sesión de nuevo.")
                        time.sleep(2)
                        st.session_state.usuario = None
                        st.rerun()
                    else:
                        st.error("Error al actualizar.")
                else:
                    st.warning("Las contraseñas no coinciden.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botón Salir
        st.write("")
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("Cerrar Sesión"):
            st.session_state.usuario = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
