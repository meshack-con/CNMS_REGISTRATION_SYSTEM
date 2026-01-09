import streamlit as st
import pandas as pd
import datetime

# --- CONFIGURATION YA UKURASA ---
st.set_page_config(page_title="PesaTrack Dashboard", layout="wide")

# --- CSS ILIYOBORESHA MUONEKANO (STYLING) ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-left: 5px solid #2ecc71;
    }
    .summary-title {
        color: #2c3e50;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .highlight {
        color: #27ae60;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALIZATION YA DATA (SESSION STATE) ---
if 'income_data' not in st.session_state:
    st.session_state.income_data = []
if 'expense_data' not in st.session_state:
    st.session_state.expense_data = []
if 'lengo_la_mwaka' not in st.session_state:
    st.session_state.lengo_la_mwaka = 0.0

# --- SIDEBAR: PEMBENI ---
st.sidebar.title("💰 PesaTrack v1.0")
st.sidebar.subheader("Ingiza Taarifa")

menu = st.sidebar.selectbox("Chagua Hatua:", ["Dashboard", "Ingiza Kipato", "Rekodi Matumizi", "Malengo & Makadirio"])

# --- LOGIC ZA MAREKODI ---
if menu == "Ingiza Kipato":
    st.header("💵 Ingiza Kipato Kipya")
    with st.form("income_form"):
        kiasi = st.number_input("Kiasi cha Shilingi (TSh):", min_value=0.0, step=500.0)
        maelezo = st.text_input("Maelezo (mf. Mshahara, Biashara):")
        submit = st.form_submit_button("Hifadhi Kipato")
        
        if submit and kiasi > 0:
            sadaka = kiasi * 0.10
            uwekezaji = kiasi * 0.10
            st.session_state.income_data.append({
                "tarehe": datetime.date.today(),
                "kiasi": kiasi,
                "sadaka": sadaka,
                "uwekezaji": uwekezaji,
                "maelezo": maelezo
            })
            st.success(f"Umefanikiwa! Sadaka yako ni {sadaka:,} na Uwekezaji ni {uwekezaji:,}")

elif menu == "Rekodi Matumizi":
    st.header("💸 Rekodi Matumizi ya Siku")
    with st.form("expense_form"):
        kiasi_m = st.number_input("Kiasi ulichotumia (TSh):", min_value=0.0, step=500.0)
        aina = st.selectbox("Aina ya Matumizi:", ["Lazima (Chakula/Nauli/Tiba)", "Sio Lazima (Anasa)", "Uwekezaji wa Ziada"])
        submit_m = st.form_submit_button("Hifadhi Matumizi")
        
        if submit_m and kiasi_m > 0:
            st.session_state.expense_data.append({
                "tarehe": datetime.date.today(),
                "kiasi": kiasi_m,
                "aina": aina
            })
            st.info(f"Matumizi ya {kiasi_m:,} yamerekodiwa kwenye kundi la {aina}.")

elif menu == "Malengo & Makadirio":
    st.header("🎯 Malengo na Makadirio ya Baadaye")
    st.session_state.lengo_la_mwaka = st.number_input("Weka Lengo la Uwekezaji kwa Mwaka (TSh):", 
                                                      value=st.session_state.lengo_la_mwaka, step=100000.0)
    st.write("---")
    st.subheader("🔮 Makadirio ya Utajiri (Projections)")
    st.info("Hapa mfumo unapiga hesabu kulingana na wastani wa vipato vyako.")

# --- DASHBOARD (HOME) ---
if menu == "Dashboard":
    st.title("📊 Ripoti ya Jumla ya Fedha")
    
    # Mahesabu ya haraka
    df_inc = pd.DataFrame(st.session_state.income_data)
    df_exp = pd.DataFrame(st.session_state.expense_data)
    
    total_inc = df_inc['kiasi'].sum() if not df_inc.empty else 0
    total_sadaka = df_inc['sadaka'].sum() if not df_inc.empty else 0
    total_inv = (df_inc['uwekezaji'].sum() if not df_inc.empty else 0) + \
                (df_exp[df_exp['aina'] == "Uwekezaji wa Ziada"]['kiasi'].sum() if not df_exp.empty else 0)
    
    # 1. KADI ZA VIPATIO (Metrics)
    col1, col2, col3 = st.columns(3)
    col1.metric("Jumla ya Kipato", f"{total_inc:,.0f} TSh")
    col2.metric("Sadaka (10%)", f"{total_sadaka:,.0f} TSh", delta_color="normal")
    col3.metric("Jumla ya Uwekezaji", f"{total_inv:,.0f} TSh")

    st.markdown("---")

    # 2. MALENGO YA MWAKA
    if st.session_state.lengo_la_mwaka > 0:
        percent = (total_inv / st.session_state.lengo_la_mwaka) * 100
        st.subheader(f"🎯 Maendeleo ya Lengo la Mwaka: {percent:.1f}%")
        st.progress(min(percent/100, 1.0))
        st.write(f"Umefikia TSh {total_inv:,.0f} kati ya TSh {st.session_state.lengo_la_mwaka:,.0f}")

    # 3. MAKADIRIO (PROJECTIONS)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 📈 Makadirio ya Miaka 10 Ijayo")
    
    # Tunachukua wastani (rahisi: jumla / idadi ya siku tangu kuanza au miezi)
    wastani_mwezi = total_inc if total_inc > 0 else 0 # Hapa unaweza kurekebisha logic kulingana na muda
    kwa_mwaka = wastani_mwezi * 12
    baada_ya_miaka_10 = kwa_mwaka * 10
    
    c1, c2 = st.columns(2)
    c1.write(f"**Makadirio kwa Mwaka:** TSh {kwa_mwaka:,.0f}")
    c1.write(f"**Baada ya Miaka 10:** TSh {baada_ya_miaka_10:,.0f}")
    
    # Grafu ya Makadirio ya Uwekezaji
    years = list(range(1, 11))
    growth = [total_inv + (total_inv * 0.1 * y) for y in years] # Mfano wa ongezeko la 10% kila mwaka
    st.line_chart(pd.DataFrame({"Miaka": years, "Uwekezaji": growth}).set_index("Miaka"))
    st.markdown("</div>", unsafe_allow_html=True)

    # 4. TAFSIRI YA MATUMIZI
    if not df_exp.empty:
        st.subheader("📉 Uchambuzi wa Matumizi")
        fig_data = df_exp.groupby('aina')['kiasi'].sum()
        st.bar_chart(fig_data)
    else:
        st.write("Ingiza matumizi ili kuona ripoti hapa.")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.write("© 2026 PesaTrack System")
