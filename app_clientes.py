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
# 🎨 ESTILOS CSS (CORRIGIENDO EL CUADRO VACÍO)
# ==========================================
st.markdown("""
    <style>
    /* 1. Fondo General y Centrado */
    .stApp {
        background-color: #f0f2f5; /* Gris muy suave */
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Esto centra el contenido verticalmente para que no se vea vacío */
    [data-testid="stAppViewContainer"] > .main {
        justify-content: center;
        padding-top: 5vh; 
    }

    /* 2. LOGO REDONDO (Mantiene tu logo limpio) */
    [data-testid="stImage"] img {
        border-radius: 50%;
        border: 5px solid white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        background-color: white;
    }

    /* 3. LA TARJETA MÁGICA (Estilizamos el FORMULARIO directamente) */
    /* Eliminamos el cuadro vacío estilizandolo directo al contenedor del form */
    [data-testid="stForm"] {
        background-color: white;
        padding: 40px;
        border-radius: 12px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08); /* Sombra elegante */
        border: 1px solid #e1e4e8;
    }

    /* 4. Inputs (Cajas de texto) */
    .stTextInput input {
        border: 1px solid #ccc;
        border-radius: 6px;
        padding: 10px;
        background-color: #fff;
        color: #333;
    }
    .stTextInput input:focus {
        border-color: #ffdd00;
        box-shadow: 0 0 0 2px rgba(255, 221, 0, 0.3);
    }

    /* 5. EL BOTÓN AMARILLO (FORZADO CON ALTA PRIORIDAD) */
    /* Usamos selectores especificos para asegurar que se ponga amarillo */
    div[data-testid="stForm"] button {
        background-color: #ffdd00 !important; /* AMARILLO */
        color: #0f1c3f !important; /* AZUL OSCURO */
        border: none !important;
        width: 100%;
        padding: 15px;
        font-weight: 700;
        font-size: 16px;
        border-radius: 6px;
        margin-top: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    div[data-testid="stForm"] button:hover {
        background-color: #ffe64d !important;
        transform: translateY(-2px);
    }

    /* 6. Textos */
    h1 { color: #0f1c3f; font-weight: 800; }
    h3 { color: #444; font-weight: 400; }
    p, span { color: #666; }
    a { color: #004d00 !important; font-weight: bold; }

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

if 'usuario' not in st.session_state: st.session_state.usuario = None

# ---------------------------------------------------------
# PANTALLA DE LOGIN (ARREGLADA Y CENTRADA)
# ---------------------------------------------------------
if st.session_state.usuario is None:
    
    # Usamos columnas centradas con mejor proporción (1 vs 1)
    col1, col2 = st.columns([1, 1], gap="large")

    # --- IZQUIERDA: INFORMACIÓN Y LOGO ---
    with col1:
        st.write("") # Espaciador
        
        # LOGO
        try:
            st.image("logo.png", width=200)
        except:
            st.header("🌱 Family Bicons")

        st.markdown("""
        <h1 style="font-size: 48px; margin-top: 10px; margin-bottom: 0px;">Family Bicons</h1>
        <h3 style="margin-top: 0px; margin-bottom: 30px;">Banca Web Segura</h3>
        
        <div style="background-color: white; padding: 20px; border-radius: 10px; border-left: 5px solid #004d00; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 20px; margin-right: 10px;">✅</span>
                <span style="font-size: 15px; font-weight: 500;">Sitio Verificado: Tus datos viajan encriptados.</span>
            </div>
            <div style="display: flex; align-items: center;">
                <span style="font-size: 20px; margin-right: 10px;">🚫</span>
                <span style="font-size: 15px; font-weight: 500;">Nunca compartas tu contraseña con terceros.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- DERECHA: FORMULARIO (AHORA ES LA TARJETA) ---
    with col2:
        # Aquí eliminé el div vacio. El formulario ES la tarjeta.
        
        st.markdown("<br>", unsafe_allow_html=True) # Un poco de aire arriba para alinear con el logo
        
        # Título DENTRO de la columna, fuera del form para que se vea limpio
        st.markdown("<h2 style='text-align: center; color: #0f1c3f; margin-bottom: 5px;'>Bienvenido</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 14px; margin-bottom: 20px;'>Ingresa tus credenciales</p>", unsafe_allow_html=True)

        # El formulario tiene el estilo [data-testid="stForm"] que definimos en CSS
        with st.form("frm_login"):
            st.markdown("##### Usuario")
            u = st.text_input("Usuario", placeholder="Ej: JuanPerez", label_visibility="collapsed")
            
            st.markdown("##### Contraseña")
            p = st.text_input("Contraseña", type="password", placeholder="••••••••", label_visibility="collapsed")
            
            st.markdown("""
            <div style="text-align: right; margin-bottom: 15px;">
                <a href="#" style="font-size: 12px; text-decoration: none; color: #666;">¿Olvidaste tu usuario?</a>
            </div>
            """, unsafe_allow_html=True)
            
            # ESTE BOTÓN AHORA SERÁ AMARILLO GRACIAS AL CSS
            btn = st.form_submit_button("INGRESAR")
            
            if btn:
                if validar_login(u, p):
                    st.session_state.usuario = u
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")

        # Footer fuera de la tarjeta
        st.markdown("""
        <div style="margin-top: 20px; display: flex; justify-content: space-between; padding: 0 10px;">
             <div style="cursor: pointer; opacity: 0.7;">🔒 <small>¿Bloqueada?</small></div>
             <div style="cursor: pointer; opacity: 0.7;">👤 <small>Regístrate</small></div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# DENTRO DE LA APP (DASHBOARD)
# ---------------------------------------------------------
else:
    user = st.session_state.usuario
    inv, deu = obtener_datos_socio(user)
    
    st.markdown(f"### Hola, **{user}** 👋")
    
    tab1, tab2, tab3, tab4 = st.tabs(["💎 INVERSIONES", "📅 PAGOS", "💸 SOLICITAR", "⚙️ PERFIL"])
    
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
                <div style="background:white; padding:25px; border-radius:12px; border-left:6px solid #004d00; box-shadow:0 4px 15px rgba(0,0,0,0.05);">
                    <div style="color:#666; font-size:13px; text-transform:uppercase; letter-spacing: 1px; font-weight: 600;">Capital Acumulado</div>
                    <div style="font-size:36px; font-weight:800; color:#004d00; margin-top: 5px;">${dinero_total:,.2f}</div>
                    <div style="border-top:1px solid #f0f0f0; margin-top: 15px; padding-top: 10px; color: #555; font-size: 14px;">
                        Posees <b>{int(total_acciones)}</b> acciones activas
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### 📈 Rendimiento Anual")
                df_chart = pd.DataFrame({"Mes": ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"][:len(valores)], "Acciones": valores})
                st.area_chart(df_chart.set_index("Mes"), color="#004d00")
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
                <div style="background:white; padding:20px; border-radius:10px; border-left:5px solid #c53030; box-shadow:0 2px 8px rgba(0,0,0,0.08); margin-bottom:15px;">
                    <div style="display:flex; justify-content:space-between; align-items: center;">
                        <b style="color: #333; font-size: 16px;">PRÉSTAMO ({row['mes']})</b>
                        <span style="background:#fff1f0; color:#c53030; padding:4px 10px; border-radius:20px; font-size:11px; font-weight: 700;">PENDIENTE</span>
                    </div>
                    <div style="font-size:26px; color:#c53030; font-weight:bold; margin-top:10px;">${cuota:,.2f} <small style="font-size: 14px; color: #666; font-weight: normal;">/ mes</small></div>
                    <div style="color:#666; font-size:13px; margin-top: 5px;">Total Deuda: ${monto_total:,.2f} • Plazo: {plazo} meses</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ ¡Estás al día!")

    # ---------------- TAB 3: SOLICITAR ----------------
    with tab3:
        st.write("")
        st.markdown("##### 📝 Nueva Solicitud")
        
        # Tarjeta para solicitud
        st.markdown('<div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
        with st.form("frm_solicitud"):
            monto_req = st.number_input("Monto a solicitar ($)", min_value=10.0, step=5.0)
            motivo_req = st.text_area("Motivo", placeholder="Ej: Compra de mercadería...")
            
            # CSS Específico para este botón verde
            st.markdown("""<style>div[data-testid="stForm"] button {background-color: #004d00 !important; color: white !important;}</style>""", unsafe_allow_html=True)
            
            if st.form_submit_button("ENVIAR SOLICITUD"):
                if solicitar_prestamo(user, monto_req, motivo_req):
                    st.success("✅ Solicitud enviada.")
                else:
                    st.error("Error al enviar.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- TAB 4: PERFIL ----------------
    with tab4:
        st.write("")
        with st.expander("🔐 Cambiar Contraseña"):
            p1 = st.text_input("Nueva contraseña", type="password", key="p1")
            p2 = st.text_input("Confirmar contraseña", type="password", key="p2")
            if st.button("Actualizar"):
                if p1 == p2 and len(p1) > 0:
                    if cambiar_password(user, p1):
                        st.success("Hecho. Reingresa.")
                        st.session_state.usuario = None
                        st.rerun()
                else:
                    st.warning("No coinciden.")
        
        st.divider()
        if st.button("Cerrar Sesión"):
            st.session_state.usuario = None
            st.rerun()
