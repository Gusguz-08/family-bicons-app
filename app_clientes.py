import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURACIÓN DE LA APP
# ==========================================
st.set_page_config(page_title="Family Bicons - Socios", page_icon="🌱", layout="centered")

# 👇👇 TU ENLACE SEGURO (Ya configurado con Secrets) 👇👇
try:
    DB_URL = st.secrets["DB_URL"]
except:
    st.error("⚠️ Error: No se encontró el secreto DB_URL. Revisa la configuración en Streamlit Cloud.")
    st.stop()

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
    
    # DEFINICIÓN DE PESTAÑAS
    tab1, tab2, tab3, tab4 = st.tabs(["💎 ACCIONES", "📅 PAGOS", "💸 SOLICITAR", "⚙️ PERFIL"])
    
    # ---------------- TAB 1: ACCIONES ----------------
    with tab1:
        # ATENCIÓN: Todo esto debe tener sangría (espacio a la izquierda)
        if not inv.empty:
            valores_texto = inv.iloc[0]['valores_meses']
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
                st.warning("Datos incompletos.")
        else:
            st.info("No tienes inversiones activas.")

    # ---------------- TAB 2: DEUDAS ----------------
    with tab2:
        if not deu.empty:
            st.subheader("⚠️ Próximos Pagos")
            for index, row in deu.iterrows():
                monto_total = row['monto']
                plazo = row['plazo']
                cuota = monto_total / plazo if plazo > 0 else monto_total
                
                st.markdown(f"""
                <div class="card-debt">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="font-weight:bold; color:#888;">PRÉSTAMO ({row['mes']})</span>
                        <span style="background:#ffebee; color:#c53030; padding:2px 8px; border-radius:10px; font-size:12px; font-weight:bold;">PENDIENTE</span>
                    </div>
                    <div style="margin-top:10px; font-size:12px;">Cuota mensual:</div>
                    <div class="debt-money">${cuota:,.2f}</div>
                    <div style="margin-top:5px; font-size:12px; color:#666;">
                        Total: ${monto_total:,.2f} • Plazo: {plazo} m
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ ¡Estás al día! No tienes deudas.")

    # ---------------- TAB 3: SOLICITAR (Aquí estaba el error probable) ----------------
    with tab3:
        st.subheader("Solicitar Nuevo Crédito")
        st.info("Formulario de solicitud.")
        
        with st.form("frm_solicitud"):
            monto_req = st.number_input("Monto a solicitar ($)", min_value=10.0, step=5.0)
            motivo_req = st.text_area("Motivo del préstamo", placeholder="Ej: Compra de materiales...")
            btn_sol = st.form_submit_button("Enviar Solicitud")
            
            if btn_sol:
                if solicitar_prestamo(user, monto_req, motivo_req):
                    st.toast("✅ ¡Solicitud enviada!", icon="🎉")
                else:
                    st.error("Error al enviar.")

    # ---------------- TAB 4: PERFIL ----------------
    with tab4:
        st.subheader("Mi Cuenta")
        
        with st.expander("🔐 Cambiar Contraseña"):
            p1 = st.text_input("Nueva contraseña", type="password", key="p1")
            p2 = st.text_input("Confirmar contraseña", type="password", key="p2")
            if st.button("Actualizar Clave"):
                if p1 == p2 and len(p1) > 0:
                    if cambiar_password(user, p1):
                        st.success("Contraseña cambiada. Reingresa.")
                        st.session_state.usuario = None
                        st.rerun()
                else:
                    st.warning("Las contraseñas no coinciden.")

        st.divider()
        if st.button("Cerrar Sesión"):
            st.session_state.usuario = None
            st.rerun()
