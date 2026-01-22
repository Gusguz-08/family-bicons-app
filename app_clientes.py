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
    DB_URL = "" 

# ==========================================
# 🎨 ESTILOS CSS (CORREGIDO: LIMPIO Y SIN SCROLL EXTRA)
# ==========================================
st.markdown("""
    <style>
    /* 1. FUENTE Y FONDO */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #f2f4f8; /* Color original que te gustaba */
        color: #0f1c3f;
    }
    
    /* Textos oscuros */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stTextInput > label {
        color: #0f1c3f !important;
    }

    /* 2. AJUSTE DE CONTENEDOR (PARA QUE NO HAYA SCROLL RARO) */
    .block-container {
        padding-top: 2rem !important; /* Menos espacio arriba para ver el logo */
        padding-bottom: 2rem !important;
        max-width: 1000px !important;
    }
    
    /* Ocultar elementos molestos de Streamlit */
    [data-testid="stToolbar"], footer, header { display: none !important; }

    /* 3. TARJETAS (VUELVEN A TENER BUEN ESPACIO) */
    .card-dashboard {
        background-color: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #e1e4e8;
        margin-bottom: 20px; /* Separación entre tarjetas */
    }

    /* 4. INPUTS Y BOTONES */
    .stTextInput input {
        color: #000 !important;
        background-color: #fff !important;
        border: 1px solid #ced4da !important;
        border-radius: 8px !important;
    }
    
    .stButton button {
        background-color: #004d00 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        height: 45px; /* Altura fija para que se vean bien */
        width: 100%;
    }
    .stButton button:hover {
        background-color: #006600 !important;
        box-shadow: 0 4px 10px rgba(0,77,0,0.2);
    }

    /* Botón rojo de salir */
    .logout-btn button {
        background-color: white !important;
        color: #c53030 !important;
        border: 1px solid #c53030 !important;
    }
    .logout-btn button:hover {
        background-color: #c53030 !important;
        color: white !important;
    }

    /* 5. ARREGLO DE TABS (PESTAÑAS) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px; /* Separación entre pestañas */
        margin-bottom: 20px;
    }
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
    
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.write("") 
        # Volvemos a usar el estilo que funcionaba, pero con la fuente nueva
        st.markdown("""
        <div style="padding-top: 20px;">
            <h1 style="font-size: 45px; margin-bottom: 10px; color: #004d00 !important; line-height: 1.2;">Family<br>Bicons</h1>
            <h3 style="color: #666 !important; font-weight: 400; margin-top: 0;">Tu banca segura.</h3>
            <br>
            <div style="background-color: white; padding: 20px; border-radius: 10px; border-left: 5px solid #004d00; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                <p style="margin:0; font-size:14px; color:#444 !important;">
                    <b>💡 Consejo:</b><br>
                    Nunca compartas tu contraseña.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.write("")
        st.write("")
        if st.session_state.vista_login == 'login':
            # Formulario dentro de una tarjeta blanca limpia
            st.markdown('<div class="card-dashboard" style="padding: 40px;">', unsafe_allow_html=True)
            with st.form("frm_login"):
                st.markdown("<h3 style='text-align: center; margin-bottom: 20px;'>Iniciar Sesión</h3>", unsafe_allow_html=True)
                
                u = st.text_input("Usuario", placeholder="Ingresa tu usuario")
                p = st.text_input("Contraseña", type="password", placeholder="••••••••")
                
                st.write("") # Espacio
                if st.form_submit_button("INGRESAR"):
                    if validar_login(u, p):
                        st.toast(f"¡Hola de nuevo, {u}!", icon="👋")
                        time.sleep(0.5)
                        st.session_state.usuario = u
                        st.rerun()
                    else:
                        st.toast("Credenciales incorrectas", icon="❌")
            st.markdown('</div>', unsafe_allow_html=True)

            if st.button("¿Olvidaste tu contraseña?", type="secondary"):
                st.session_state.vista_login = 'recuperar'
                st.rerun()

        elif st.session_state.vista_login == 'recuperar':
            st.markdown("""
            <div class="card-dashboard" style="text-align: center; padding: 40px;">
                <h3>Recuperar Acceso</h3>
                <p style="color:#666;">Contacta al administrador:</p>
                <div style="background:#f0fdf4; padding:15px; border-radius:8px; margin: 15px 0;">
                    <span style="color:#004d00; font-weight:bold; font-size: 18px;">📞 +593 96 734 2110</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("⬅ Volver"):
                st.session_state.vista_login = 'login'
                st.rerun()

# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------
else:
    user = st.session_state.usuario
    inv, deu = obtener_datos_socio(user)
    
    # Header simple y limpio (Sin cosas raras, como lo tenías antes)
    st.markdown(f"""
    <div style="margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #ddd; display:flex; justify-content:space-between; align-items:center;">
        <h2 style="margin:0; color: #004d00 !important;">Hola, {user} 👋</h2>
        <div style="color:green; font-size:12px; border:1px solid green; padding: 2px 8px; border-radius: 10px;">Conectado</div>
    </div>
    """, unsafe_allow_html=True)
    
    # TABS
    tab1, tab2, tab3, tab4 = st.tabs(["💎 Inversiones", "📅 Pagos", "💸 Crédito", "⚙️ Perfil"])
    
    # --- TAB 1: INVERSIONES ---
    with tab1:
        st.write("")
        if not inv.empty:
            valores_texto = inv.iloc[0]['valores_meses']
            valores = [float(x) for x in valores_texto.split(",")] if valores_texto else []
            
            if valores:
                total_acciones = sum(valores)
                dinero_total = total_acciones * 5.0
                
                # Tarjeta de Datos
                st.markdown(f"""
                <div class="card-dashboard">
                    <div style="color:#666; font-size:14px;">Capital Total</div>
                    <div style="font-size:36px; font-weight:800; color:#004d00;">${dinero_total:,.2f}</div>
                    <hr style="margin: 10px 0; border:0; border-top: 1px solid #eee;">
                    <div style="color:#444;">Acciones Acumuladas: <b>{int(total_acciones)}</b></div>
                </div>
                """, unsafe_allow_html=True)
                
                # Gráfico Plotly (Mantenemos el bonito pero en contenedor limpio)
                st.markdown('<div class="card-dashboard">', unsafe_allow_html=True)
                st.markdown('<h5>📈 Rendimiento</h5>', unsafe_allow_html=True)
                
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
                    height=200,
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='#eee'),
                    dragmode=False
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                 st.info("Sin datos suficientes.")
        else:
            st.info("No tienes inversiones.")

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
                        <h4 style="margin:0; color:#c53030 !important;">{row['mes']}</h4>
                        <div style="text-align:right;">
                            <div style="font-size:20px; font-weight:bold;">${cuota:,.2f}</div>
                            <small>de ${monto:,.2f}</small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("¡Estás al día! No tienes pagos pendientes.")

    # --- TAB 3: SOLICITAR ---
    with tab3:
        st.write("")
        st.markdown('<div class="card-dashboard">', unsafe_allow_html=True)
        st.markdown("<h4>Nueva Solicitud</h4>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            monto_req = st.number_input("Monto ($)", min_value=10.0, step=5.0, value=50.0)
        with c2:
            motivo_req = st.text_input("Motivo", placeholder="Ej: Salud")
            
        st.write("")
        if st.button("Enviar Solicitud"):
            with st.spinner("Enviando..."):
                time.sleep(1)
                if solicitar_prestamo(user, monto_req, motivo_req):
                    st.toast("Solicitud enviada", icon="✅")
                else:
                    st.toast("Error al enviar", icon="❌")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 4: PERFIL ---
    with tab4:
        st.write("")
        st.markdown(f"""
        <div class="card-dashboard">
            <h4>Mis Datos</h4>
            <p>Usuario: <b>{user}</b> | Estado: <b style='color:green'>Activo</b></p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="card-dashboard">', unsafe_allow_html=True)
        st.markdown("<h4>Seguridad</h4>", unsafe_allow_html=True)
        with st.expander("Cambiar Contraseña"):
            curr_pass = st.text_input("Contraseña Actual", type="password")
            new_p1 = st.text_input("Nueva Contraseña", type="password")
            new_p2 = st.text_input("Repetir", type="password")
            
            if st.button("Actualizar"):
                if new_p1 == new_p2 and len(new_p1) > 0:
                    if cambiar_password(user, new_p1):
                        st.toast("Clave actualizada. Reinicia sesión.", icon="🔒")
                        time.sleep(2)
                        st.session_state.usuario = None
                        st.rerun()
                    else:
                        st.error("Error al actualizar.")
                else:
                    st.warning("No coinciden.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.write("")
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("Cerrar Sesión"):
            st.session_state.usuario = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
