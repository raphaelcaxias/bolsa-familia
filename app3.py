import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="CNPq Analytics PRO",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CSS - DESIGN MODERNO 2026
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #F8FAFC;
    }

    /* HEADER / HERO */
    .main-header {
        background: linear-gradient(135deg, #0F172A 0%, #164E63 100%);
        padding: 3rem 2.5rem;
        border-radius: 28px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 15px 50px rgba(15, 23, 42, 0.3);
        text-align: center;
        border-bottom: 5px solid #14B8A6;
    }
    .main-header h1 {
        font-size: 48px;
        font-weight: 700;
        margin-bottom: 12px;
    }
    .main-header p {
        font-size: 18px;
        color: rgba(255,255,255,0.9);
        max-width: 600px;
        margin: 0 auto;
    }

    /* UPLOAD AREA */
    .upload-container {
        background: white;
        border: 3px dashed #14B8A6;
        border-radius: 24px;
        padding: 60px 40px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    }
    .upload-container:hover {
        border-color: #0F766E;
        box-shadow: 0 15px 40px rgba(20, 184, 166, 0.2);
        transform: translateY(-5px);
    }
    .upload-container h3 {
        color: #0F766E;
        margin-bottom: 8px;
    }

    /* KPI CARDS */
    .kpi-card {
        background: white;
        padding: 28px 24px;
        border-radius: 22px;
        box-shadow: 0 6px 25px rgba(0,0,0,0.07);
        border: 1px solid #E2E8F0;
        transition: all 0.3s ease;
    }
    .kpi-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(20, 184, 166, 0.18);
    }
    .kpi-value {
        font-size: 38px;
        font-weight: 700;
        color: #0F766E;
    }
    .kpi-title {
        font-size: 14.5px;
        color: #64748B;
        font-weight: 500;
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A, #1E2937);
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Insight Box */
    .insight-box {
        background: white;
        border-left: 6px solid #14B8A6;
        padding: 24px;
        border-radius: 20px;
        box-shadow: 0 6px 25px rgba(0,0,0,0.06);
    }

    .footer {
        text-align: center;
        color: #64748B;
        margin-top: 60px;
        padding: 30px;
        font-size: 14px;
        border-top: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown("""
<div class="main-header">
    <h1>🔬 CNPq Analytics PRO</h1>
    <p>Plataforma avançada de análise de investimentos científicos no Brasil</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# FUNÇÕES (mantidas)
# =========================================================
def fmt_money(v):
    if pd.isna(v): return "R$ 0"
    if v >= 1_000_000_000:
        return f"R$ {v/1_000_000_000:.2f}B".replace(".", ",")
    if v >= 1_000_000:
        return f"R$ {v/1_000_000:.2f}M".replace(".", ",")
    return f"R$ {v:,.0f}".replace(",", ".")

def fmt_num(v):
    return f"{int(v):,}".replace(",", ".")

@st.cache_data(ttl=3600)
def load_data(file):
    # ... (mesma função anterior)
    encodings = ['utf-8', 'latin1', 'cp1252']
    for enc in encodings:
        try:
            file.seek(0)
            df = pd.read_csv(file, sep=';', encoding=enc, low_memory=False)
            df.columns = df.columns.str.lower().str.strip()
            
            if 'valor_pago' in df.columns:
                df['valor_pago'] = (df['valor_pago'].astype(str)
                    .str.replace('.', '', regex=False)
                    .str.replace(',', '.', regex=False))
                df['valor_pago'] = pd.to_numeric(df['valor_pago'], errors='coerce')
            
            for d in ['data_inicio_processo', 'data_termino_processo']:
                if d in df.columns:
                    df[d] = pd.to_datetime(df[d], errors='coerce', dayfirst=True)
            
            if 'data_inicio_processo' in df.columns:
                df['ano'] = df['data_inicio_processo'].dt.year
            
            if 'data_termino_processo' in df.columns:
                hoje = pd.Timestamp.today()
                df['status_bolsa'] = np.where(df['data_termino_processo'] >= hoje, 'Ativa', 'Encerrada')
            
            mapa = {'SE': 'Sudeste', 'SU': 'Sul', 'NE': 'Nordeste', 'CO': 'Centro-Oeste', 'N': 'Norte'}
            if 'regiao' in df.columns:
                df['regiao_nome'] = df['regiao'].map(mapa).fillna(df['regiao'])
            
            return df
        except:
            pass
    return None

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.title("⚙️ Controle")
    st.markdown("### Upload de Dados")
    
    uploaded = st.file_uploader(
        label="",
        type=["csv"],
        help="Arraste ou clique para selecionar o arquivo CSV",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("""
    ### 📊 Sobre
    Dashboard executivo para análise de bolsas, investimentos e tendências científicas do CNPq.
    """)

# =========================================================
# TELA INICIAL (sem arquivo)
# =========================================================
if not uploaded:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="upload-container">
            <h3>📤 Faça upload do dataset</h3>
            <p style="color:#64748B; margin: 15px 0 25px;">
                Carregue seu arquivo CSV de dados do CNPq para começar a análise
            </p>
            <p style="font-size: 13px; color:#94A3B8;">
                Formato suportado: .csv (separado por ponto e vírgula)
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.info("👈 Use o botão de upload na barra lateral para começar")

else:
    with st.spinner("Processando dataset..."):
        df = load_data(uploaded)
    
    if df is not None:
        # [Restante do código permanece igual - KPIs, tabs, etc.]
        df_f = df.copy()
        
        # Filtros na sidebar
        with st.sidebar:
            st.markdown("---")
            st.subheader("🔍 Filtros")
            # ... (filtros de ano, região, área - mantidos iguais)

        # KPIs, Tabs, etc. (mesmo código anterior)
        total = df_f['valor_pago'].sum()
        bolsas = len(df_f)
        pesquisadores = df_f['beneficiario'].nunique() if 'beneficiario' in df_f.columns else 0
        instituicoes = df_f['instituicao_destino'].nunique() if 'instituicao_destino' in df_f.columns else 0

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f"<div class='kpi-card'><div class='kpi-value'>{fmt_money(total)}</div><div class='kpi-title'>💰 Investimento Total</div></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='kpi-card'><div class='kpi-value'>{fmt_num(bolsas)}</div><div class='kpi-title'>🎓 Bolsas</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='kpi-card'><div class='kpi-value'>{fmt_num(pesquisadores)}</div><div class='kpi-title'>👨‍🔬 Pesquisadores</div></div>", unsafe_allow_html=True)
        with c4: st.markdown(f"<div class='kpi-card'><div class='kpi-value'>{fmt_num(instituicoes)}</div><div class='kpi-title'>🏛️ Instituições</div></div>", unsafe_allow_html=True)

        # ... (o resto do código das tabs pode ser mantido igual ao anterior)

        st.markdown("---")
        csv = df_f.to_csv(index=False, sep=';')
        st.download_button("📥 Exportar CSV Filtrado", csv, 
                          file_name=f"cnpq_{datetime.now().strftime('%Y%m%d')}.csv",
                          mime='text/csv')

        with st.expander("🗂️ Visualizar Dados Brutos"):
            st.dataframe(df_f.head(1000), use_container_width=True)

        st.markdown(f"""
        <div class='footer'>
            🔬 CNPq Analytics PRO • Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')}
        </div>
        """, unsafe_allow_html=True)

    else:
        st.error("❌ Erro ao processar o arquivo CSV")
