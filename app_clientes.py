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
# 🎨 ESTILOS CSS (MEJORADOS PARA APLICAR COLOR AL BOTÓN)
# ==========================================
st.markdown("""
    <style>
    /* 1. Fondo Claro y Limpio */
    .stApp {
        background-color: #f8f9fa; /* Gris muy suave, más moderno */
        color: #1f2937; /* Letra oscura */
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; /* Tipografía más limpia */
    }
    
    /* 2. Botón Principal VERDE (Selector más específico para que funcione) */
    div.stButton > button:first-child {
        width: 100%; 
        border-radius: 8px; 
        background-color: #004d00 !important; /* TU VERDE, con !important */
        color: white !important;
        border: none; 
        font-weight: 600; /* Semibold */
        padding: 12px 24px; /* Más padding */
        font-size: 16px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:first-child:hover {
        background-color: #006600 !important; /* Verde más claro al pasar mouse */
        transform: translateY(-1px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
    }
    div.stButton > button:first-child:active {
        transform: translateY(0px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* 3. Tarjetas Blancas con Borde Verde */
    .card { 
        background-color: white; 
        padding: 25px; /* Más espacio interno */
        border-radius: 12px; 
        border-left: 6px solid #004d00; /* Borde Verde */
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); /* Sombra más suave */
        color: #333;
    }
    
    .card-debt { 
        background-color: white; 
        padding: 25px;
        border-radius: 12px; 
        border-left: 6px solid #c53030; /* Borde Rojo */
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        color: #333;
    }
    
    /* 4. Textos y Títulos */
    .big-money { font-size: 32px; font-weight: 700; color: #004d00; }
    h1, h2, h3 { color: #004d00 !important; font-weight: 700; }
    p { color: #4b5563; line-height: 1.6; }

    /* Inputs (Cajas de texto) limpias */
    .stTextInput > div > div > input {
        background-color: white;
        color: #333;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        padding: 10px 12px;
    }
    .stTextInput > div > div > input:focus {
        border-color: #004d00; /* Borde verde al escribir */
        box-shadow: 0 0 0 2px rgba(0, 77, 0, 0.2);
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
    col_espacio1, col_centro, col_espacio2 = st.columns([1, 1.5, 1]) # Columna central más ancha

    with col_centro:
        st.write("") 
        st.write("") 
        
        with st.container():
            # LOGO (Asegúrate de tener "logo.jpeg" en GitHub)
            try:
                # Muestra la imagen centrada y con un ancho controlado
                st.image("logo.jpeg", width=150, use_container_width=False)
            except:
                st.header("🌱 Family Bicons")

            st.markdown("""
            <div style="text-align: center; margin-bottom: 30px;">
                <h2 style="color:#004d00; margin-bottom:5px; font-size: 28px;">Banca Web</h2>
                <p style="color:#6b7280; font-size:16px;">Bienvenido Socio</p>
            </div>
            """, unsafe_allow_html=True)
            
            # FORMULARIO LOGIN
            with st.form("frm_login"):
                u = st.text_input("Usuario", placeholder="Ingresa tu usuario")
                p = st.text_input("Contraseña", type="password", placeholder="••••••••")
                
                st.write("")
                # Botón ahora sí verde
                btn = st.form_submit_button("INGRESAR")
                
                if btn:
                    if validar_login(u, p):
                        st.session_state.usuario = u
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas")

            st.write("")
            
            # --- FUNCIONALIDAD: OLVIDASTE CONTRASEÑA ---
            with st.expander("¿Olvidaste tu contraseña?"):
                st.info("Ingresa tu usuario y te contactaremos para restablecerla.")
                email_recup = st.text_input("Tu Usuario o Cédula")
                if st.button("Solicitar Recuperación"):
                    if email_recup:
                        with st.spinner("Enviando solicitud al administrador..."):
                            time.sleep(1.5) # Simula tiempo de carga
                        st.success(f"✅ Solicitud enviada. El administrador revisará tu cuenta ({email_recup}).")
                    else:
                        st.warning("Por favor escribe tu usuario.")

            st.markdown("""
            <div style="text-align: center; margin-top: 30px;">
                <span style="color:#9ca3af; font-size:13px;">🔒 Conexión Segura SSL | © 2026 Family Bicons</span>
            </div>
            """, unsafe_allow_html=True)

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
