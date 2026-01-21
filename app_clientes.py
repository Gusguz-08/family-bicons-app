import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURACIÓN DE LA APP
# ==========================================
st.set_page_config(page_title="Family Bicons - Banca Web", page_icon="🌱", layout="wide")

# 👇👇 TU ENLACE SEGURO (Manejo de errores si no hay secrets) 👇👇
try:
    DB_URL = st.secrets["DB_URL"]
except:
    st.error("⚠️ Error crítico: No se configuró el secreto DB_URL.")
    st.stop()

# ==========================================
# 🎨 ESTILOS CSS (AQUÍ ESTÁ LA MAGIA VISUAL)
# ==========================================
st.markdown("""
    <style>
    /* Fondo general más limpio */
    .stApp {
        background-color: #f4f6f9;
    }
    
    /* Estilo del Botón INGRESAR (Parecido al del Banco) */
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        background-color: #ffdd00; /* Amarillo Pichincha (o usa #004d00 para tu verde) */
        color: #0f1c3f; 
        border: none; 
        font-weight: bold; 
        padding: 12px;
        font-size: 16px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton>button:hover { 
        background-color: #ffe64d; 
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
    }

    /* Estilo de las Tarjetas de Datos (Dentro de la app) */
    .card { background-color: white; padding: 20px; border-radius: 12px; border-left: 6px solid #004d00; margin-bottom: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    .card-debt { background-color: white; padding: 20px; border-radius: 12px; border-left: 6px solid #c53030; margin-bottom: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    
    /* Textos grandes */
    .big-money { font-size: 28px; font-weight: 800; color: #004d00; font-family: 'Arial', sans-serif; }
    
    /* Ocultar menú de hamburguesa y footer para que parezca app nativa */
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
    except:
        return False

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
# 🔐 PANTALLA DE LOGIN (CON TU LOGO)
# ==========================================
if st.session_state.usuario is None:
    # Usamos columnas para centrar el contenido como en la foto del banco
    col_espacio1, col_centro, col_espacio2 = st.columns([1, 1, 1])

    with col_centro:
        st.write("") # Espacio arriba
        st.write("") 
        
        # CONTENEDOR VISUAL (LA TARJETA BLANCA)
        with st.container():
            # 👇 AQUÍ ESTÁ TU LOGO 👇
            # Asegúrate de que el archivo en GitHub se llame EXACTAMENTE "logo.jpeg"
            st.image("logo.png", use_container_width=True)

            st.markdown("""
            <div style="text-align: center;">
                <h1 style="color:#0f1c3f; margin-bottom:0;">Banca Web</h1>
                <p style="color:gray; font-size:14px;">Bienvenido a Family Bicons</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("") # Separador
            
            # FORMULARIO
            with st.form("frm_login"):
                u = st.text_input("Usuario", placeholder="Ingresa tu usuario")
                p = st.text_input("Contraseña", type="password", placeholder="••••••••")
                
                st.write("") # Espacio antes del botón
                btn = st.form_submit_button("INGRESAR")
                
                if btn:
                    if validar_login(u, p):
                        st.session_state.usuario = u
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas")

            # Links de ayuda visuales
            st.markdown("""
            <div style="text-align: center; margin-top: 15px;">
                <a href="#" style="color:#004d00; text-decoration:none; font-size:12px;">¿Olvidaste tu contraseña?</a>
                <br>
                <span style="color:gray; font-size:12px;">🔒 Conexión Segura</span>
            </div>
            """, unsafe_allow_html=True)
# ==========================================
# 🏦 DENTRO DE LA APP (DASHBOARD)
# ==========================================
else:
    user = st.session_state.usuario
    inv, deu = obtener_datos_socio(user)
    
    # Header simple dentro de la app
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
                
                # Tarjeta limpia
                st.markdown(f"""
                <div class="card">
                    <div style="color:#666; font-size:14px; text-transform:uppercase; letter-spacing:1px;">Capital Acumulado</div>
                    <div class="big-money">${dinero_total:,.2f}</div>
                    <div style="margin-top:10px; border-top:1px solid #eee; padding-top:10px; font-size:13px; color:#444;">
                        <b>{int(total_acciones)}</b> acciones activas
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.caption("📈 Evolución de tu inversión")
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
                <div class="card-debt">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:bold; color:#333;">PRÉSTAMO ({row['mes']})</span>
                        <span style="background:#ffebee; color:#c53030; padding:4px 10px; border-radius:15px; font-size:11px; font-weight:bold;">POR PAGAR</span>
                    </div>
                    <div style="margin-top:15px; font-size:13px; color:#666;">Cuota mensual:</div>
                    <div style="font-size:22px; font-weight:bold; color:#c53030;">${cuota:,.2f}</div>
                    <div style="margin-top:5px; font-size:12px; color:#888;">
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
