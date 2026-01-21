import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURACIÓN DE LA APP
# ==========================================
st.set_page_config(page_title="Family Bicons - Socios", page_icon="🌱", layout="centered")

# 👇👇 TU ENLACE SEGURO (Ya configurado) 👇👇
DB_URL = st.secrets["DB_URL"]

# CSS Estilizado
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; background-color: #004d00; color: white; border: none; font-weight: bold; padding: 10px; }
    .stButton>button:hover { background-color: #006400; color: #e0e0e0; }
    .card { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #004d00; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .card-debt { background-color: #fff5f5; padding: 15px; border-radius: 10px; border-left: 5px solid #c53030; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .big-money { font-size: 24px; font-weight: bold; color: #004d00; }
    .debt-money { font-size: 20px; font-weight: bold; color: #c53030; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🔌 CONEXIÓN OPTIMIZADA (CACHE)
# ==========================================
@st.cache_resource
def get_connection():
    try:
        return psycopg2.connect(DB_URL)
    except Exception as e:
        st.error(f"⚠️ Error de conexión: {e}")
        return None

# ==========================================
# 🧠 LÓGICA DE NEGOCIO
# ==========================================
def validar_login(usuario, password):
    conn = get_connection()
    if not conn: return False
    try:
        # Usamos parameters para evitar SQL Injection
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
    except Exception as e:
        st.error(f"Error actualizando clave: {e}")
        return False

def solicitar_prestamo(usuario, monto, motivo):
    conn = get_connection()
    if not conn: return False
    try:
        cur = conn.cursor()
        # Asegúrate de tener la tabla 'solicitudes' creada en Supabase
        cur.execute("INSERT INTO solicitudes (usuario, monto, motivo, fecha, estado) VALUES (%s, %s, %s, %s, 'Pendiente')", 
                    (usuario, monto, motivo, datetime.now()))
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        st.error(f"Error enviando solicitud: {e}")
        return False

# ==========================================
# 📱 INTERFAZ PRINCIPAL
# ==========================================
st.title("🌱 Family Bicons")

# --- LOGIN ---
if 'usuario' not in st.session_state: st.session_state.usuario = None

if st.session_state.usuario is None:
    st.markdown("### 🔒 Acceso Socios")
    with st.form("frm_login"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        btn = st.form_submit_button("INGRESAR")
        if btn:
            if validar_login(u, p):
                st.session_state.usuario = u
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

else:
    # --- APP DENTRO ---
    user = st.session_state.usuario
    inv, deu = obtener_datos_socio(user)
    
    st.write(f"Hola, **{user}** 👋")
    
    # 4 PESTAÑAS AHORA
    tab1, tab2, tab3, tab4 = st.tabs(["💎 ACCIONES", "📅 PAGOS", "💸 SOLICITAR", "⚙️ PERFIL"])
    
    # ---------------- TAB 1: ACCIONES ----------------
    with tab1:
        if not inv.empty:
            valores_texto = inv.iloc[0]['valores_meses']
            # Manejo de error si la cadena está vacía
            if valores_texto:
                valores = [float(x) for x in valores_texto.split(",")]
                total_acciones = sum(valores)
                dinero_total = total_acciones * 5.0
                
                st.markdown(f"""
                <div class="card">
                    <div style="font-size:14px; color:#555;">💰 CAPITAL ACUMULADO</div>
                    <div class="big-money">${dinero_total:,.2f}</div>
                    <hr>
                    <div style="font-size:12px;">Total Acciones: {int(total_acciones)}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.caption("📈 Tu crecimiento")
                df_chart = pd.DataFrame({"Mes": ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"][:len(valores)], "Acciones": valores})
                st.area_chart(df_chart.set_index("Mes"), color="#2e7d32")
            else:
                st.warning("Datos de acciones incompletos.")
        else:
            st.info("No tienes inversiones activas.")

    # ---------------- TAB 2: DEUDAS ----------------
    with tab2:
        if not deu.empty:
            st
