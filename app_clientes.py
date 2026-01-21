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
# 🎨 ESTILOS CSS (VERSIÓN "TODO EN UNA PANTALLA")
# ==========================================
st.markdown("""
    <style>
    /* 1. Ajuste General: Fuente un poco más pequeña para que todo quepa */
    .stApp {
        background-color: #f2f4f8;
        font-family: 'Segoe UI', sans-serif;
        font-size: 14px; 
    }
    
    /* Centrado vertical: Reducimos el padding superior para subir todo */
    [data-testid="stAppViewContainer"] > .main {
        padding-top: 3vh !important; 
    }

    /* 2. LOGO REDONDO */
    [data-testid="stImage"] img {
        border-radius: 50%;
        border: 4px solid white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        background-color: white;
    }

    /* 3. LA TARJETA (FORMULARIO) MÁS COMPACTA */
    [data-testid="stForm"] {
        background-color: white;
        padding: 25px !important; /* Reducido de 40px a 25px */
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid #e1e4e8;
        max-width: 400px; /* Ancho controlado */
        margin: 0 auto;
    }

    /* 4. Inputs (Cajas de texto) más delgadas */
    .stTextInput input {
        padding: 8px 10px; /* Menos relleno */
        font-size: 14px;
        border: 1px solid #ccc;
        border-radius: 5px;
        background-color: #fff;
        color: #333;
    }
    .stTextInput input:focus {
        border-color: #004d00;
        box-shadow: 0 0 0 1px rgba(0, 77, 0, 0.2);
    }
    /* Reducir espacio entre label e input */
    .stTextInput label {
        margin-bottom: 2px !important;
        font-size: 13px !important;
    }
    /* Reducir espacio entre elementos del form */
    div[data-testid="stForm"] .stMarkdown {
        margin-bottom: -10px !important;
    }

    /* 5. ARREGLO DEL OJO DE LA CONTRASEÑA */
    /* Hace que el botón del ojo sea transparente y se integre bien */
    button[aria-label="Show password"], button[aria-label="Hide password"] {
        background-color: transparent !important;
        border: none !important;
        color: #555 !important;
    }

    /* 6. BOTÓN INGRESAR VERDE (CON PRIORIDAD MÁXIMA) */
    /* Usamos 'div.stButton button' para asegurar que agarre el estilo */
    div.stButton > button {
        background-color: #004d00 !important; /* VERDE CORPORATIVO */
        color: white !important;
        border: none !important;
        width: 100%;
        padding: 10px !important; /* Más delgado */
        font-weight: 700 !important;
        font-size: 15px !important;
        border-radius: 6px !important;
        margin-top: 10px !important;
        box-shadow: 0 4px 6px rgba(0, 77, 0, 0.2);
    }
    div.stButton > button:hover {
        background-color: #006600 !important;
        transform: translateY(-1px);
    }
    div.stButton > button:active {
        background-color: #003300 !important;
        color: white !important;
    }

    /* 7. Footer de Copyright Visible */
    .copyright-text {
        text-align: center;
        margin-top: 15px;
        font-size: 11px;
        color: #999;
    }

    /* Ocultar elementos extra */
    footer, [data-testid="stFooter"] { display: none !important; }
    #MainMenu {visibility: hidden;}
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
# PANTALLA DE LOGIN (COMPACTA)
# ---------------------------------------------------------
if st.session_state.usuario is None:
    
    # Usamos columnas. Ajusté el gap y proporciones para acercar los elementos
    col1, col2 = st.columns([1.1, 1], gap="medium")

    # --- IZQUIERDA: INFORMACIÓN Y LOGO ---
    with col1:
        st.write("") 
        try:
            # Logo más pequeño (160px) para que no ocupe toda la pantalla
            st.image("WhatsApp Image 2026-01-20 at 20.45.54.jpeg", width=160)
        except:
            st.header("🌱 Family Bicons")

        st.markdown("""
        <h1 style="font-size: 38px; margin-top: 5px; margin-bottom: 0px; color: #0f1c3f;">Family Bicons</h1>
        <h3 style="margin-top: 0px; margin-bottom: 20px; font-size: 18px; color: #555;">Banca Web Segura</h3>
        
        <div style="background-color: white; padding: 15px; border-radius: 8px; border-left: 4px solid #004d00; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 16px; margin-right: 8px; color: #004d00;">✅</span>
                <span style="font-size: 13px; color: #555;">Sitio Verificado: Conexión encriptada.</span>
            </div>
            <div style="display: flex; align-items: center;">
                <span style="font-size: 16px; margin-right: 8px; color: #c53030;">🚫</span>
                <span style="font-size: 13px; color: #555;">Nunca compartas tu clave.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- DERECHA: TARJETA DE LOGIN ---
    with col2:
        st.write("") # Un pequeño espacio para alinear verticalmente con el logo
        
        # Inicio del Formulario
        with st.form("frm_login"):
            st.markdown("<h3 style='text-align: center; margin-bottom: 15px; color:#333; font-weight:600; font-size:22px;'>Bienvenido</h3>", unsafe_allow_html=True)
            
            # Inputs muy limpios
            u = st.text_input("Usuario", placeholder="Ingresa tu usuario")
            p = st.text_input("Contraseña", type="password", placeholder="••••••••")
            
            # Espacio pequeño
            st.write("")

            # BOTÓN INGRESAR (Ahora sí debe salir VERDE)
            btn = st.form_submit_button("INGRESAR")
            
            if btn:
                if validar_login(u, p):
                    st.session_state.usuario = u
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
        
        # --- ZONA INFERIOR (Fuera del form para que no apriete los inputs) ---
        
        # 1. Enlace de Olvidaste contraseña (Funcional)
        if st.button("¿Olvidaste tu contraseña?", type="tertiary"):
             st.warning("⚠️ Para restablecer tu clave, contacta a soporte o al administrador.")

        # 2. Copyright (Ahora con clase CSS para asegurar que se vea)
        st.markdown('<div class="copyright-text">© 2026 Family Bicons. Todos los derechos reservados.</div>', unsafe_allow_html=True)

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
        
        st.markdown('<div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
        with st.form("frm_solicitud"):
            monto_req = st.number_input("Monto a solicitar ($)", min_value=10.0, step=5.0)
            motivo_req = st.text_area("Motivo", placeholder="Ej: Compra de mercadería...")
            
            # Botón verde específico para este formulario
            st.markdown("""<style>div[data-testid="stForm"] > .stButton > button {background-color: #004d00 !important; color: white !important;}</style>""", unsafe_allow_html=True)
            
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
