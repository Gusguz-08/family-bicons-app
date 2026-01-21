import streamlit as st
import psycopg2
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURACIÓN DE LA APP
# ==========================================
st.set_page_config(page_title="Banca Web | Family Bicons", page_icon="🌱", layout="wide")

# 👇👇 TU ENLACE SEGURO 👇👇
try:
    DB_URL = st.secrets["DB_URL"]
except:
    # Para pruebas locales si no hay secretos
    DB_URL = "" 

# ==========================================
# 🎨 ESTILOS CSS (MODO PREMIUM)
# ==========================================
st.markdown("""
    <style>
    /* 1. FUENTE MODERNA (Inter) - Estilo Bancario */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    /* 2. COLORES GLOBALES */
    .stApp {
        background-color: #f4f6f9; /* Gris azulado muy suave */
        color: #0f1c3f !important; /* Azul oscuro corporativo */
    }
    
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stTextInput > label, div[data-testid="stExpander"] p {
        color: #0f1c3f !important;
    }

    /* 3. LIMPIEZA INTERFAZ */
    [data-testid="stToolbar"], footer, #MainMenu, header { display: none !important; }
    .block-container {
        padding-top: 3rem !important; 
        padding-bottom: 3rem !important;
        max-width: 950px !important; 
    }

    /* 4. TARJETAS DASHBOARD (CON EFECTO HOVER) */
    .card-dashboard {
        background-color: white;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid #eef0f3;
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .card-dashboard:hover {
        transform: translateY(-4px); /* Efecto de elevación */
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    }

    /* 5. ESTILOS DE LOGIN */
    [data-testid="stForm"], .recovery-card {
        background-color: white !important;
        padding: 40px !important;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.06);
        border: 1px solid #eef0f3;
    }

    /* 6. INPUTS MEJORADOS */
    .stTextInput input {
        color: #333 !important;
        background-color: #fff !important;
        border: 1px solid #dfe1e5 !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    
    /* 7. BOTONES */
    .stButton button {
        background-color: #004d00 !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #006600 !important;
        box-shadow: 0 4px 12px rgba(0,77,0,0.2);
    }

    /* Botón de salir */
    .logout-btn button {
        background-color: white !important;
        color: #c53030 !important;
        border: 1px solid #c53030 !important;
    }
    .logout-btn button:hover {
        background-color: #c53030 !important;
        color: white !important;
    }

    /* 8. PESTAÑAS (TABS) PERSONALIZADAS */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: white !important;
        border-bottom: 3px solid #004d00 !important;
        color: #004d00 !important;
        font-weight: 700 !important;
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
    if not conn: return True # MODO PRUEBA
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
            <h1 style="font-size: 42px; margin-bottom: 10px; color: #004d00 !important; font-weight: 800;">Family Bicons</h1>
            <h3 style="color: #555 !important; font-weight: 400;">Tu banca segura y transparente.</h3>
            <br>
            <div style="background-color: white; padding: 25px; border-radius: 12px; border-left: 5px solid #004d00; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
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
                st.markdown("<h3 style='text-align: center; color:#0f1c3f !important; font-weight:700;'>Iniciar Sesión</h3>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color:#888 !important; font-size: 14px; margin-bottom: 25px;'>Ingresa tus credenciales para continuar</p>", unsafe_allow_html=True)
                
                u = st.text_input("Usuario", placeholder="Ej: diegoballa")
                p = st.text_input("Contraseña", type="password", placeholder="••••••••")
                
                st.write("")
                if st.form_submit_button("INGRESAR"):
                    if validar_login(u, p):
                        # Feedback elegante con Toast
                        st.toast(f"¡Bienvenido, {u}!", icon="👋")
                        time.sleep(0.8)
                        st.session_state.usuario = u
                        st.rerun()
                    else:
                        st.toast("Credenciales incorrectas", icon="❌")

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
    st.markdown('<div style="position: fixed; bottom: 20px; width: 100%; text-align: center; color: #aaa; font-size: 12px; font-family: Inter;">© 2026 Family Bicons System</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# DASHBOARD (INTERIOR)
# ---------------------------------------------------------
else:
    user = st.session_state.usuario
    inv, deu = obtener_datos_socio(user)
    
    # Header minimalista
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 25px;">
        <div>
            <h2 style="margin:0; color: #004d00 !important; font-weight: 700;">Hola, {user} 👋</h2>
            <p style="margin:0; color: #666 !important;">Bienvenido a tu panel financiero</p>
        </div>
        <div style="background:white; padding:6px 16px; border-radius:20px; border:1px solid #e0e0e0; font-size:13px; color:#444; font-weight:600;">
            <span style="color:#22c55e;">●</span> Conectado
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # TABS
    tab1, tab2, tab3, tab4 = st.tabs(["💎 Inversiones", "📅 Pagos Pendientes", "💸 Solicitar Crédito", "⚙️ Mi Perfil"])
    
    # --- TAB 1: INVERSIONES (CON PLOTLY) ---
    with tab1:
        st.write("")
        if not inv.empty:
            valores_texto = inv.iloc[0]['valores_meses']
            valores = [float(x) for x in valores_texto.split(",")] if valores_texto else []
            
            if valores:
                total_acciones = sum(valores)
                dinero_total = total_acciones * 5.0
                
                # Tarjeta Resumen
                st.markdown(f"""
                <div class="card-dashboard">
                    <div style="display:flex; align-items:center; justify-content: space-between;">
                        <div>
                            <div style="color:#666; font-size:12px; font-weight: 600; text-transform:uppercase; letter-spacing:1px;">Capital Total</div>
                            <div style="font-size:38px; font-weight:800; color:#004d00; font-family: 'Inter', sans-serif;">${dinero_total:,.2f}</div>
                            <div style="color:#888; font-size:14px; margin-top:5px;">
                                💼 <span style="font-weight:600; color:#333;">{int(total_acciones)}</span> acciones acumuladas
                            </div>
                        </div>
                        <div style="background:#f0fdf4; padding:15px; border-radius:50%; border:1px solid #dcfce7;">
                            <span style="font-size:30px;">💰</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Gráfico Plotly
                st.markdown('<div class="card-dashboard">', unsafe_allow_html=True)
                st.markdown('<h5 style="margin-bottom: 20px; font-weight: 600;">📈 Rendimiento Histórico</h5>', unsafe_allow_html=True)
                
                # Datos y Gráfico
                meses_labels = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
                df_chart = pd.DataFrame({
                    "Mes": meses_labels[:len(valores)], 
                    "Acciones": valores
                })

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_chart["Mes"], 
                    y=df_chart["Acciones"],
                    mode='lines',
                    name='Acciones',
                    line=dict(color='#004d00', width=3),
                    fill='tozeroy',
                    fillcolor='rgba(0, 77, 0, 0.08)'
                ))

                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=0, r=0, t=10, b=0),
                    height=250,
                    xaxis=dict(showgrid=False, linecolor='#eee', tickfont=dict(color='#888')),
                    yaxis=dict(showgrid=True, gridcolor='#f4f4f4', gridwidth=1, tickfont=dict(color='#888')),
                    dragmode=False
                )

                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                 st.info("Datos de inversión incompletos.")
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
                            <h4 style="margin:0; color:#c53030 !important; font-weight: 700;">{row['mes']}</h4>
                            <span style="font-size:12px; background:#fff5f5; color:#c53030; padding:4px 10px; border-radius:20px; font-weight:600; border: 1px solid #fed7d7;">PENDIENTE</span>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-size:24px; font-weight:bold; color:#1a202c;">${cuota:,.2f}</div>
                            <small style="color:#718096;">Total: ${monto:,.2f}</small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card-dashboard" style="text-align:center; padding:50px 20px;">
                <h1 style="font-size:60px; margin-bottom:10px;">🎉</h1>
                <h3 style="color:#004d00 !important; font-weight:700;">¡Estás al día!</h3>
                <p style="color:#666;">No tienes pagos pendientes por el momento.</p>
            </div>
            """, unsafe_allow_html=True)

    # --- TAB 3: SOLICITAR (CON SPINNER) ---
    with tab3:
        st.write("")
        st.markdown('<div class="card-dashboard">', unsafe_allow_html=True)
        st.markdown("<h4 style='font-weight:700;'>📝 Nueva Solicitud</h4>", unsafe_allow_html=True)
        st.markdown("<p style='color:#666; font-size:14px; margin-bottom:25px;'>Completa los datos para solicitar un adelanto o préstamo.</p>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            monto_req = st.number_input("Monto a solicitar ($)", min_value=10.0, step=5.0, value=50.0)
        with c2:
            motivo_req = st.text_input("Motivo (Breve)", placeholder="Ej: Emergencia médica")
            
        st.write("")
        if st.button("Enviar Solicitud"):
            with st.spinner("Procesando solicitud con el banco..."):
                time.sleep(1.5) # Simulación de proceso
                if solicitar_prestamo(user, monto_req, motivo_req):
                    st.toast("Solicitud enviada correctamente", icon="✅")
                    time.sleep(1)
                else:
                    st.toast("Error al procesar la solicitud", icon="⚠️")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 4: PERFIL ---
    with tab4:
        st.write("")
        # Tarjeta Datos
        st.markdown(f"""
        <div class="card-dashboard">
            <h4 style="margin-bottom:20px; font-weight:700;">👤 Mis Datos</h4>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px;">
                <div style="background:#f8fafc; padding:15px; border-radius:10px;">
                    <label style="font-size:12px; color:#64748b; font-weight:600;">USUARIO</label>
                    <div style="font-weight:bold; font-size:18px; color:#334155;">{user}</div>
                </div>
                <div style="background:#f0fdf4; padding:15px; border-radius:10px; border:1px solid #dcfce7;">
                    <label style="font-size:12px; color:#15803d; font-weight:600;">ESTADO</label>
                    <div style="color:#166534; font-weight:bold; font-size:18px;">Activo</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Tarjeta Seguridad
        st.markdown('<div class="card-dashboard">', unsafe_allow_html=True)
        st.markdown('<h4 style="margin-bottom:15px; font-weight:700;">🔐 Seguridad</h4>', unsafe_allow_html=True)
        
        with st.expander("Cambiar Contraseña"):
            curr_pass = st.text_input("Contraseña Actual", type="password")
            new_p1 = st.text_input("Nueva Contraseña", type="password")
            new_p2 = st.text_input("Repetir Nueva Contraseña", type="password")
            
            if st.button("Actualizar Clave"):
                if new_p1 == new_p2 and len(new_p1) > 0:
                    with st.spinner("Actualizando credenciales..."):
                        if cambiar_password(user, new_p1):
                            st.toast("Contraseña actualizada exitosamente", icon="🔒")
                            time.sleep(2)
                            st.session_state.usuario = None
                            st.rerun()
                        else:
                            st.toast("Error al actualizar en base de datos", icon="⚠️")
                else:
                    st.toast("Las contraseñas no coinciden", icon="⚠️")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botón Salir
        st.write("")
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("Cerrar Sesión"):
            st.session_state.usuario = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
