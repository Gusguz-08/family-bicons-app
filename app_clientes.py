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
# 🎨 ESTILOS CSS (REPLICANDO ESTILO BANCARIO PREMIUM)
# ==========================================
st.markdown("""
    <style>
    /* 1. Fondo General (Gris muy suave y limpio) */
    .stApp {
        background-color: #f4f7f6;
        font-family: 'Segoe UI', sans-serif;
    }

    /* 2. TRUCO PARA TU LOGO: Lo recorta en circulo para ocultar el fondo de cuadros */
    /* Esto busca la imagen en la columna izquierda y le aplica el estilo */
    [data-testid="stImage"] img {
        border-radius: 50%;
        border: 4px solid white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        object-fit: cover;
        background-color: white; /* Por si la imagen tiene transparencia real */
    }

    /* 3. Contenedor de la Tarjeta de Login (Derecha) */
    .login-box {
        background-color: white;
        padding: 40px;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); /* Sombra suave y difusa */
        border: 1px solid #eef2f6;
        text-align: center;
        margin-top: 20px;
    }

    /* 4. Inputs (Cajas de texto) más elegantes */
    .stTextInput input {
        border: 1px solid #dfe1e5;
        border-radius: 6px;
        padding: 12px;
        color: #333;
        font-size: 16px;
        background-color: #fafafa;
    }
    .stTextInput input:focus {
        border-color: #ffdd00;
        background-color: white;
        box-shadow: 0 0 0 2px rgba(255, 221, 0, 0.2);
    }

    /* 5. Botón INGRESAR (AMARILLO PICHINCHA EXACTO) */
    div.stButton > button {
        width: 100%;
        background-color: #ffdd00 !important;
        color: #0f1c3f !important; /* Azul oscuro corporativo */
        border: none;
        border-radius: 6px;
        font-weight: 700;
        padding: 14px;
        font-size: 16px;
        margin-top: 15px;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(255, 221, 0, 0.2);
    }
    div.stButton > button:hover {
        background-color: #ffe64d !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(255, 221, 0, 0.3);
    }

    /* 6. Textos y Títulos */
    h1, h2, h3, h4 { color: #0f1c3f !important; font-family: 'Segoe UI', sans-serif; } 
    p, small, span { color: #5f6368; }
    a { color: #004d00 !important; }

    /* Ocultar elementos extra de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Ajuste para móviles: que las columnas se apilen bien */
    @media (max-width: 768px) {
        .login-box { padding: 20px; }
    }
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
# PANTALLA DE LOGIN (ESTILO BANCO PICHINCHA)
# ---------------------------------------------------------
if st.session_state.usuario is None:
    
    st.write("") # Espacio superior
    
    # Columnas asimétricas: Izquierda (Info/Logo) más ancha visualmente, Derecha (Formulario) contenida
    col1, col_space, col2 = st.columns([1.5, 0.2, 1.2])

    # --- IZQUIERDA: INFORMACIÓN Y LOGO ---
    with col1:
        st.markdown("<br>", unsafe_allow_html=True) 
        
        # LOGO (El CSS lo hará redondo automáticamente)
        # Nota: Asegúrate que el nombre del archivo sea EXACTO al que tienes en GitHub
        try:
            st.image("logo.png", width=220)
        except:
            # Si falla la imagen, muestra un icono bonito
            st.markdown("<div style='font-size: 80px;'>🌱</div>", unsafe_allow_html=True)

        st.markdown("""
        <h1 style="font-size: 42px; font-weight: 800; margin-top: 10px; margin-bottom: 10px;">Family Bicons</h1>
        <h3 style="color: #4b5563 !important; font-weight: 400; font-size: 24px;">Banca Web Segura</h3>
        
        <div style="margin-top: 30px; border-left: 4px solid #004d00; padding-left: 20px;">
            <p style="font-size: 16px; margin-bottom: 5px;">✅ <b>Sitio Verificado:</b> Tus datos viajan encriptados.</p>
            <p style="font-size: 16px;">🚫 Nunca compartas tu contraseña con terceros.</p>
        </div>
        """, unsafe_allow_html=True)

    # --- DERECHA: TARJETA DE LOGIN ---
    with col2:
        # Abrimos el contenedor con estilo "login-box" (definido en CSS arriba)
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align: center; margin-bottom: 5px; font-weight: 700;'>Ingresa a tu cuenta</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 14px; margin-bottom: 25px;'>Bienvenido socio</p>", unsafe_allow_html=True)
        
        with st.form("frm_login"):
            # Inputs con diseño limpio
            u = st.text_input("Usuario", placeholder="Escribe tu usuario")
            p = st.text_input("Contraseña", type="password", placeholder="••••••••")
            
            # Link de olvido contraseña
            st.markdown("""
            <div style="text-align: right; margin-top: 5px; margin-bottom: 15px;">
                <a href="#" style="font-size: 13px; text-decoration: none; font-weight: 600;">¿Olvidaste tu usuario?</a>
            </div>
            """, unsafe_allow_html=True)
            
            # Botón Amarillo
            btn = st.form_submit_button("Ingresar")
            
            if btn:
                if validar_login(u, p):
                    st.session_state.usuario = u
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")

        # Footer de la tarjeta con opciones extra
        st.markdown("""
        <div style="margin-top: 25px; display: flex; justify-content: space-between; gap: 10px;">
             <div style="background: #f9fafb; padding: 10px; width: 50%; border-radius: 6px; border: 1px solid #eee; cursor: pointer;">
                <div style="font-size: 20px;">🔒</div>
                <small style="font-weight: 600; display: block; margin-top: 5px;">¿Bloqueada?</small>
             </div>
             <div style="background: #f9fafb; padding: 10px; width: 50%; border-radius: 6px; border: 1px solid #eee; cursor: pointer;">
                <div style="font-size: 20px;">👤</div>
                <small style="font-weight: 600; display: block; margin-top: 5px;">Regístrate</small>
             </div>
        </div>
        <div style="margin-top: 20px; font-size: 11px; color: #aaa;">
            © 2026 Family Bicons. Todos los derechos reservados.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True) # Cierra login-box

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
                
                # Tarjeta de resumen limpia
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
        
        # Formulario estilo tarjeta
        st.markdown('<div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
        with st.form("frm_solicitud"):
            monto_req = st.number_input("Monto a solicitar ($)", min_value=10.0, step=5.0)
            motivo_req = st.text_area("Motivo", placeholder="Ej: Compra de mercadería...")
            
            # Botón verde para acciones dentro de la app
            st.markdown("""
                <style>
                div[data-testid="stForm"] button {
                    background-color: #004d00 !important;
                    color: white !important;
                }
                </style>
            """, unsafe_allow_html=True)
            
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
