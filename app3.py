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
# NOVA PALETA DE CORES + CSS MODERNO
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
    
    /* HEADER */
    .main-header {
        background: linear-gradient(135deg, #0F172A 0%, #164E63 100%);
        padding: 2.2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 40px rgba(15, 23, 42, 0.25);
        border-bottom: 4px solid #14B8A6;
    }
    .main-header h1 {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .main-header p {
        color: rgba(255,255,255,0.85);
        font-size: 17px;
    }

    /* KPI CARDS */
    .kpi-card {
        background: white;
        padding: 28px 24px;
        border-radius: 22px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.07);
        border: 1px solid #E2E8F0;
        transition: all 0.3s ease;
    }
    .kpi-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 30px rgba(20, 184, 166, 0.15);
        border-color: #14B8A6;
    }
    .kpi-title {
        font-size: 14px;
        color: #64748B;
        font-weight: 500;
    }
    .kpi-value {
        font-size: 36px;
        font-weight: 700;
        color: #0F766E;
        margin: 8px 0;
    }

    /* INSIGHTS */
    .insight-box {
        background: white;
        border-left: 6px solid #14B8A6;
        padding: 22px;
        border-radius: 18px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        margin: 20px 0;
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A, #1E2937);
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* TABS */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        border-radius: 12px;
        padding: 12px 24px;
        transition: all 0.2s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #F1F5F9;
    }

    /* DATAFRAME */
    [data-testid="stDataFrame"] {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }

    /* FOOTER */
    .footer {
        text-align: center;
        color: #64748B;
        margin-top: 50px;
        padding: 25px;
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
# FUNÇÕES (mantidas iguais)
# =========================================================
def fmt_money(v):
    if pd.isna(v):
        return "R$ 0"
    if v >= 1_000_000_000:
        return f"R$ {v/1_000_000_000:.2f}B".replace(".", ",")
    if v >= 1_000_000:
        return f"R$ {v/1_000_000:.2f}M".replace(".", ",")
    return f"R$ {v:,.0f}".replace(",", ".")

def fmt_num(v):
    return f"{int(v):,}".replace(",", ".")

@st.cache_data(ttl=3600)
def load_data(file):
    encodings = ['utf-8', 'latin1', 'cp1252']
    for enc in encodings:
        try:
            file.seek(0)
            df = pd.read_csv(file, sep=';', encoding=enc, low_memory=False)
            df.columns = df.columns.str.lower().str.strip()
            
            if 'valor_pago' in df.columns:
                df['valor_pago'] = (df['valor_pago']
                    .astype(str)
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
            
            mapa = {'SE': 'Sudeste', 'SU': 'Sul', 'NE': 'Nordeste', 'CO': 'Centro-Oeste', 'N': 'Norte', 'NO': 'Norte'}
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
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    st.markdown("---")
    st.markdown("### 📊 Sobre\nDashboard executivo para análise de bolsas, investimentos e tendências científicas do CNPq.")

# =========================================================
# MAIN
# =========================================================
if uploaded:
    with st.spinner("Processando dataset..."):
        df = load_data(uploaded)
    
    if df is not None:
        df_f = df.copy()
        
        # Filtros
        with st.sidebar:
            st.markdown("---")
            st.subheader("🔍 Filtros")
            
            if 'ano' in df.columns:
                anos = sorted(df['ano'].dropna().unique())
                if len(anos) > 1:
                    ano_sel = st.slider("Período", int(min(anos)), int(max(anos)), (int(min(anos)), int(max(anos))))
                    df_f = df_f[(df_f['ano'] >= ano_sel[0]) & (df_f['ano'] <= ano_sel[1])]
            
            if 'regiao_nome' in df.columns:
                regs = sorted(df['regiao_nome'].dropna().unique())
                reg_sel = st.multiselect("Região", regs, default=regs)
                df_f = df_f[df_f['regiao_nome'].isin(reg_sel)]
            
            if 'grande_area' in df.columns:
                areas = sorted(df['grande_area'].dropna().unique())
                area_sel = st.multiselect("Grande Área", areas, default=areas[:5])
                df_f = df_f[df_f['grande_area'].isin(area_sel)]

        # KPIs
        total = df_f['valor_pago'].sum()
        bolsas = len(df_f)
        pesquisadores = df_f['beneficiario'].nunique() if 'beneficiario' in df_f.columns else 0
        instituicoes = df_f['instituicao_destino'].nunique() if 'instituicao_destino' in df_f.columns else 0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-value'>{fmt_money(total)}</div>
                <div class='kpi-title'>💰 Investimento Total</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-value'>{fmt_num(bolsas)}</div>
                <div class='kpi-title'>🎓 Bolsas</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-value'>{fmt_num(pesquisadores)}</div>
                <div class='kpi-title'>👨‍🔬 Pesquisadores</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-value'>{fmt_num(instituicoes)}</div>
                <div class='kpi-title'>🏛️ Instituições</div>
            </div>
            """, unsafe_allow_html=True)

        # Insights
        insights = []
        if 'regiao_nome' in df_f.columns:
            top_reg = df_f.groupby('regiao_nome')['valor_pago'].sum().idxmax()
            insights.append(f"📍 Região líder: <b>{top_reg}</b>")
        if 'grande_area' in df_f.columns:
            top_area = df_f.groupby('grande_area')['valor_pago'].sum().idxmax()
            insights.append(f"🧬 Área mais financiada: <b>{top_area}</b>")

        st.markdown(f"""
        <div class='insight-box'>
            {'<br>'.join(insights)}
        </div>
        """, unsafe_allow_html=True)

        # Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Visão Geral", "🗺️ Regiões", "🧬 Áreas", "🏛️ Instituições", "📈 Tendências"
        ])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                if 'grande_area' in df_f.columns:
                    area_data = df_f.groupby('grande_area')['valor_pago'].sum().sort_values(ascending=False).head(10).reset_index()
                    fig = px.bar(area_data, x='valor_pago', y='grande_area', orientation='h',
                                 color='valor_pago', color_continuous_scale='Teal',
                                 title='Top Áreas Científicas')
                    st.plotly_chart(fig, use_container_width=True)
            with col2:
                if 'regiao_nome' in df_f.columns:
                    reg = df_f.groupby('regiao_nome')['valor_pago'].sum().reset_index()
                    fig2 = px.pie(reg, values='valor_pago', names='regiao_nome', hole=0.55,
                                  color_discrete_sequence=px.colors.sequential.Teal)
                    st.plotly_chart(fig2, use_container_width=True)

        with tab2:
            if 'sigla_uf_destino' in df_f.columns:
                uf_data = df_f.groupby('sigla_uf_destino')['valor_pago'].sum().reset_index()
                fig = px.bar(uf_data.sort_values('valor_pago', ascending=False).head(15),
                             x='sigla_uf_destino', y='valor_pago', color='valor_pago',
                             color_continuous_scale='Tealgrn', title='Top Estados')
                st.plotly_chart(fig, use_container_width=True)

        with tab3:
            if 'grande_area' in df_f.columns and 'regiao_nome' in df_f.columns:
                pivot = pd.pivot_table(df_f, values='valor_pago', index='grande_area',
                                       columns='regiao_nome', aggfunc='sum')
                fig = px.imshow(pivot, text_auto=True, aspect='auto',
                                color_continuous_scale='Teal', title='Heatmap Área × Região')
                st.plotly_chart(fig, use_container_width=True)

        with tab4:
            c1, c2 = st.columns(2)
            with c1:
                if 'instituicao_destino' in df_f.columns:
                    top_inst = df_f.groupby('instituicao_destino')['valor_pago'].sum().sort_values(ascending=False).head(15).reset_index()
                    st.dataframe(top_inst, use_container_width=True)
            with c2:
                if 'beneficiario' in df_f.columns:
                    top_pesq = df_f.groupby('beneficiario')['valor_pago'].sum().sort_values(ascending=False).head(15).reset_index()
                    st.dataframe(top_pesq, use_container_width=True)

        with tab5:
            if 'ano' in df_f.columns:
                ano = df_f.groupby('ano')['valor_pago'].sum().reset_index()
                fig = px.line(ano, x='ano', y='valor_pago', markers=True,
                              title='Evolução dos Investimentos',
                              color_discrete_sequence=['#14B8A6'])
                fig.update_traces(line=dict(width=4))
                st.plotly_chart(fig, use_container_width=True)

        # Export
        st.markdown("---")
        csv = df_f.to_csv(index=False, sep=';')
        st.download_button("📥 Exportar CSV", csv, 
                          file_name=f"cnpq_{datetime.now().strftime('%Y%m%d')}.csv",
                          mime='text/csv')

        with st.expander("🗂️ Visualizar Dados"):
            st.dataframe(df_f.head(1000), use_container_width=True)

        st.markdown(f"""
        <div class='footer'>
            🔬 CNPq Analytics PRO • Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')}
        </div>
        """, unsafe_allow_html=True)

    else:
        st.error("Erro ao carregar o arquivo CSV")
else:
    st.info("👈 Faça upload do dataset CSV para começar a análise")
