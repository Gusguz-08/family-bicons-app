import streamlit as st
import psycopg2
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime
import os

# ==========================================
# ⚙️ CONFIGURACIÓN DE LA APP
# ==========================================
st.set_page_config(page_title="Banca Web | Family Bicons", page_icon="🌱", layout="wide")

# 👇👇 TU ENLACE SEGURO 👇👇
try:
    DB_URL = st.secrets["DB_URL"]
except:
    DB_URL = "" 

# ==========================================
# 🎨 ESTILOS CSS (ARREGLADO: LOGO, CENTRADO Y SIN CUADROS FEOS)
# ==========================================
st.markdown("""
    <style>
    /* 1. FUENTE GLOBAL */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #f2f4f8;
        color: #0f1c3f;
    }
    
    /* 2. QUITAR ESPACIOS BLANCOS GIGANTES (PARA QUE NO HAYA SCROLL) */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 2rem !important;
        max-width: 1000px !important;
    }
    
    /* Ocultar elementos de Streamlit */
    [data-testid="stToolbar"], footer, header { display: none !important; }

    /* 3. TARJETAS (ESTILO LIMPIO) */
    .card-dashboard {
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid #e1e4e8;
        margin-bottom: 20px;
    }

    /* 4. INPUTS */
    .stTextInput input {
        color: #000 !important;
        background-color: #fff !important;
        border: 1px solid #ced4da !important;
        border-radius: 8px !important;
    }
    
    /* 5. BOTÓN PRINCIPAL (VERDE BIEN DEFINIDO) */
    .stButton button {
        background-color: #004d00 !important; /* Verde original */
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        height: 45px;
        width: 100%;
        margin-top: 10px;
    }
    .stButton button:hover {
        background-color: #006600 !important;
        box-shadow: 0 4px 10px rgba(0,77,0,0.2);
    }

    /* 6. BOTÓN SECUNDARIO (OLVIDASTE CONTRASEÑA) - ESTILO LINK */
    /* Usamos un selector específico para el segundo botón si es posible, 
       o aplicamos estilo inline en el python para diferenciarlo */
    
    /* Botón Salir (Rojo) */
    .logout-btn button {
        background-color: white !important;
        color: #c53030 !important;
        border: 1px solid #c53030 !important;
    }
    .logout-btn button:hover {
        background-color: #c53030 !important;
        color: white !important;
    }

    /* 7. PESTAÑAS (TABS) */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; margin-bottom: 20px; }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: transparent !important;
        border-bottom: 3px solid #004d00 !important;
        color: #004d00 !important;
        font-weight: bold !important;
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
    if not conn: return True
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
    
    # Usamos columnas centradas verticalmente (gap adjustment)
    col1, col2 = st.columns([1, 1], gap="large")

    # --- IZQUIERDA: LOGO Y BIENVENIDA ---
    with col1:
        st.write("") 
        st.write("") 
        
        # INTENTO DE CARGAR LOGO.PNG (Si no existe, pone texto)
        if os.path.exists("logo.png"):
            st.image("logo.png", width=250)
        else:
            # Si no has subido la imagen, usa este título bonito
            st.markdown("""<h1 style="color:#004d00 !important; font-size: 50px; margin-bottom:0;">Family<br>Bicons</h1>""", unsafe_allow_html=True)
            
        st.markdown("""
        <h3 style="color: #555 !important; font-weight: 400; margin-top: 10px;">Tu banca segura y transparente.</h3>
        <br>
        <div style="background-color: white; padding: 20px; border-radius: 12px; border-left: 5px solid #004d00; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
            <p style="margin:0; font-size:15px; color:#444 !important;">
                <b>💡 Consejo de seguridad:</b><br>
                Nunca compartas tu contraseña con terceros. El equipo de soporte nunca te la pedirá.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # --- DERECHA: FORMULARIO LOGIN (SOLO UN CUADRO) ---
    with col2:
        # Alineación vertical manual para centrarlo con el texto de la izquierda
        st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
        
        if st.session_state.vista_login == 'login':
            # Inicio Tarjeta Blanca
            st.markdown('<div class="card-dashboard">', unsafe_allow_html=True)
            
            st.markdown("<h3 style='text-align: center; color:#0f1c3f !important; margin-bottom: 25px;'>Iniciar Sesión</h3>", unsafe_allow_html=True)
            
            with st.form("frm_login"):
                u = st.text_input("Usuario", placeholder="Ingresa tu usuario")
                p = st.text_input("Contraseña", type="password", placeholder="••••••••")
                
                st.write("")
                submitted = st.form_submit_button("INGRESAR")
                
                if submitted:
                    if validar_login(u, p):
                        st.toast(f"¡Bienvenido, {u}!", icon="👋")
                        time.sleep(0.5)
                        st.session_state.usuario = u
                        st.rerun()
                    else:
                        st.toast("Credenciales incorrectas", icon="❌")
            
            st.markdown('</div>', unsafe_allow_html=True) # Fin Tarjeta Blanca

            # Botón de Olvidaste fuera del form para que no se vea verde fuerte
            col_b1, col_b2, col_b3 = st.columns([1,2,1])
            with col_b2:
                if st.button("¿Olvidaste tu contraseña?", type="secondary"):
                    st.session_state.vista_login = 'recuperar'
                    st.rerun()

        elif st.session_state.vista_login == 'recuperar':
            st.markdown("""
            <div class="card-dashboard" style="text-align: center;">
                <h3 style="color:#004d00 !important;">Recuperar Acceso</h3>
                <p style="color:#666; margin-top:10px;">
                    Para restablecer tu contraseña, por favor envía tu <b>Nombre de Usuario</b> y una <b>foto de tu Cédula</b> al administrador.
                </p>
                <div style="background:#f0fdf4; padding:15px; border-radius:8px; margin: 20px 0; border: 1px dashed #004d00;">
                    <span style="color:#004d00; font-weight:bold; font-size: 18px;">📞 +593 96 734 2110</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("⬅ Volver al inicio"):
                st.session_state.vista_login = 'login'
                st.rerun()

    # Footer fijo abajo
    st.markdown('<div style="position: fixed; bottom: 10px; width: 100%; text-align: center; color: #aaa; font-size: 11px;">© 2026 Family Bicons System</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# DASHBOARD (ADENTRO)
# ---------------------------------------------------------
else:
    user = st.session_state.usuario
    inv, deu = obtener_datos_socio(user)
    
    # Header
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 20px; border-bottom: 1px solid #ddd; padding-bottom: 15px;">
        <div>
            <h2 style="margin:0; color: #004d00 !important; font-weight: 700;">Hola, {user} 👋</h2>
            <p style="margin:0; color: #666; font-size: 14px;">Bienvenido a tu panel financiero</p>
        </div>
        <div style="background:white; padding:5px 15px; border-radius:20px; border:1px solid #ccc; font-size:12px; color:#333;">
            🟢 Conectado
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # TABS
    tab1, tab2, tab3, tab4 = st.tabs(["💎 Inversiones", "📅 Pagos Pendientes", "💸 Solicitar Crédito", "⚙️ Mi Perfil"])
    
    # --- TAB 1: INVERSIONES ---
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
                            <div style="color:#666; font-size:13px; text-transform:uppercase;">Capital Total</div>
                            <div style="font-size:38px; font-weight:800; color:#004d00;">${dinero_total:,.2f}</div>
                            <div style="color:#888; font-size:14px; margin-top:5px;">
                                💼 <b>{int(total_acciones)}</b> acciones acumuladas
                            </div>
                        </div>
                        <div style="font-size:30px;">💰</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Gráfico
                st.markdown('<div class="card-dashboard">', unsafe_allow_html=True)
                st.markdown('<h5 style="margin-bottom: 15px;">📈 Rendimiento</h5>', unsafe_allow_html=True)
                
                meses_labels = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
                df_chart = pd.DataFrame({"Mes": meses_labels[:len(valores)], "Acciones": valores})

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_chart["Mes"], 
                    y=df_chart["Acciones"],
                    mode='lines',
                    line=dict(color='#004d00', width=3),
                    fill='tozeroy',
                    fillcolor='rgba(0, 77, 0, 0.1)'
                ))

                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=0, r=0, t=10, b=0),
                    height=220,
                    xaxis=dict(showgrid=False, linecolor='#eee'),
                    yaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
                    dragmode=False
                )

                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                 st.info("Datos incompletos.")
        else:
            st.info("No tienes inversiones registradas.")

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
                            <span style="font-size:11px; background:#fff5f5; color:#c53030; padding:3px 8px; border-radius:10px; border: 1px solid #feb2b2;">PENDIENTE</span>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-size:22px; font-weight:bold; color:#333;">${cuota:,.2f}</div>
                            <small style="color:#777;">Total: ${monto:,.2f}</small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card-dashboard" style="text-align:center; padding:40px;">
                <h1>🎉</h1>
                <h3 style="color:#004d00 !important;">¡Estás al día!</h3>
                <p style="color:#666;">No tienes pagos pendientes.</p>
            </div>
            """, unsafe_allow_html=True)

    # --- TAB 3: SOLICITAR ---
    with tab3:
        st.write("")
        st.markdown('<div class="card-dashboard">', unsafe_allow_html=True)
        st.markdown("<h4>📝 Nueva Solicitud</h4>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            monto_req = st.number_input("Monto ($)", min_value=10.0, step=5.0, value=50.0)
        with c2:
            motivo_req = st.text_input("Motivo", placeholder="Ej: Salud")
            
        st.write("")
        if st.button("Enviar Solicitud"):
            with st.spinner("Procesando..."):
                time.sleep(1)
                if solicitar_prestamo(user, monto_req, motivo_req):
                    st.toast("Solicitud enviada correctamente", icon="✅")
                else:
                    st.toast("Error al procesar", icon="⚠️")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 4: PERFIL ---
    with tab4:
        st.write("")
        st.markdown(f"""
        <div class="card-dashboard">
            <h4 style="margin-bottom:15px;">👤 Mis Datos</h4>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                <div style="background:#f8fafc; padding:10px; border-radius:8px;">
                    <small style="color:#666;">Usuario</small><br><b>{user}</b>
                </div>
                <div style="background:#f0fdf4; padding:10px; border-radius:8px;">
                    <small style="color:#666;">Estado</small><br><b style="color:green">Activo</b>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="card-dashboard">', unsafe_allow_html=True)
        st.markdown('<h4>🔐 Seguridad</h4>', unsafe_allow_html=True)
        
        with st.expander("Cambiar Contraseña"):
            curr_pass = st.text_input("Contraseña Actual", type="password")
            new_p1 = st.text_input("Nueva Contraseña", type="password")
            new_p2 = st.text_input("Repetir Nueva Contraseña", type="password")
            
            if st.button("Actualizar Clave"):
                if new_p1 == new_p2 and len(new_p1) > 0:
                    if cambiar_password(user, new_p1):
                        st.toast("Contraseña actualizada. Inicia sesión de nuevo.", icon="✅")
                        time.sleep(2)
                        st.session_state.usuario = None
                        st.rerun()
                    else:
                        st.toast("Error al actualizar.", icon="❌")
                else:
                    st.toast("Las contraseñas no coinciden.", icon="⚠️")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.write("")
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("Cerrar Sesión"):
            st.session_state.usuario = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
