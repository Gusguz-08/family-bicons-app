import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURACIÓN DE LA APP (MÓVIL)
# ==========================================
st.set_page_config(page_title="Family Bicons - Socios", page_icon="🌱", layout="centered")

# 👇👇 TU ENLACE DE BASE DE DATOS (Mismo de siempre) 👇👇
DB_URL = st.secrets["DB_URL"]

def get_connection():
    try:
        return psycopg2.connect(DB_URL)
    except Exception as e:
        st.error("⚠️ Sin conexión al sistema.")
        return None

# ==========================================
# 🔐 SEGURIDAD Y DATOS
# ==========================================
def validar_login(usuario, password):
    conn = get_connection()
    if not conn: return False
    query = "SELECT * FROM usuarios WHERE usuario = %s AND password = %s"
    df = pd.read_sql(query, conn, params=(usuario, password))
    conn.close()
    return not df.empty

def obtener_datos_socio(usuario):
    conn = get_connection()
    # Consultas de SOLO LECTURA
    inv = pd.read_sql("SELECT * FROM inversiones WHERE nombre = %s", conn, params=(usuario,))
    deu = pd.read_sql("SELECT * FROM deudores WHERE nombre = %s AND estado = 'Pendiente'", conn, params=(usuario,))
    conn.close()
    return inv, deu

# ==========================================
# 📱 INTERFAZ VISUAL (DISEÑO MÓVIL)
# ==========================================
# Estilos CSS para que parezca una App real
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; background-color: #004d00; color: white; border: none; font-weight: bold;}
    .card { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #004d00; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .card-debt { background-color: #fff5f5; padding: 15px; border-radius: 10px; border-left: 5px solid #c53030; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .big-money { font-size: 24px; font-weight: bold; color: #004d00; }
    .debt-money { font-size: 20px; font-weight: bold; color: #c53030; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌱 Family Bicons")

# --- LOGIN ---
if 'usuario' not in st.session_state: st.session_state.usuario = None

if st.session_state.usuario is None:
    st.markdown("### 🔒 Acceso Socios")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("INGRESAR"):
        if validar_login(u, p):
            st.session_state.usuario = u
            st.rerun()
        else:
            st.error("Credenciales incorrectas")

else:
    # --- DENTRO DE LA APP ---
    user = st.session_state.usuario
    inv, deu = obtener_datos_socio(user)
    
    st.write(f"Hola, **{user}** 👋")
    
    tab1, tab2 = st.tabs(["💎 MIS ACCIONES", "📅 MIS PAGOS"])
    
    # ---------------- PESTAÑA 1: ACCIONES (SOLO VISUALIZAR) ----------------
    with tab1:
        if not inv.empty:
            # Cálculos internos (El usuario NO puede modificar esto)
            valores_texto = inv.iloc[0]['valores_meses']
            valores = [float(x) for x in valores_texto.split(",")]
            total_acciones = sum(valores)
            dinero_total = total_acciones * 5.0 # Valor Acción
            
            # Tarjeta de Resumen
            st.markdown(f"""
            <div class="card">
                <div style="font-size:14px; color:#555;">💰 CAPITAL ACUMULADO</div>
                <div class="big-money">${dinero_total:,.2f}</div>
                <hr>
                <div style="font-size:12px;">Total Acciones: {int(total_acciones)}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Gráfico de evolución
            st.caption("📈 Tu crecimiento mensual")
            df_chart = pd.DataFrame({"Mes": ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"], "Acciones": valores})
            st.area_chart(df_chart.set_index("Mes"), color="#2e7d32")
            
        else:
            st.info("No tienes inversiones activas.")

    # ---------------- PESTAÑA 2: DEUDAS Y PAGOS ----------------
    with tab2:
        if not deu.empty:
            st.subheader("⚠️ Próximos Pagos")
            
            # Recorremos cada deuda para mostrarla como una tarjeta
            for index, row in deu.iterrows():
                monto_total = row['monto']
                plazo = row['plazo']
                mes_registro = row['mes']
                
                # Calculamos la cuota aproximada
                cuota = monto_total / plazo if plazo > 0 else monto_total
                
                st.markdown(f"""
                <div class="card-debt">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="font-weight:bold; color:#888;">PRÉSTAMO ({mes_registro})</span>
                        <span style="background:#ffebee; color:#c53030; padding:2px 8px; border-radius:10px; font-size:12px; font-weight:bold;">PENDIENTE</span>
                    </div>
                    <div style="margin-top:10px; font-size:12px;">Debes pagar una cuota de:</div>
                    <div class="debt-money">${cuota:,.2f} / mes</div>
                    <div style="margin-top:5px; font-size:12px; color:#666;">
                        Deuda Total: ${monto_total:,.2f} • Plazo: {plazo} meses
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
        else:
            st.success("✅ ¡Estás al día! No tienes pagos pendientes.")
            st.balloons()

    st.divider()
    if st.button("Cerrar Sesión"):
        st.session_state.usuario = None

        st.rerun()

