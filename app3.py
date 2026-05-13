import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime

# ============================================================
# CONFIGURAÇÃO
# ============================================================
st.set_page_config(
    page_title="CNPq Analytics",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS - CORES LINKEDIN
# ============================================================
st.markdown("""
<style>
/* Cores LinkedIn */
:root {
    --linkedin-blue: #0A66C2;
    --linkedin-blue-light: #E8F4FD;
    --linkedin-gray-bg: #F3F6F8;
    --linkedin-gray-card: #FFFFFF;
    --linkedin-gray-text: #1E2A3A;
    --linkedin-gray-muted: #6B7A8A;
    --linkedin-border: #E1E5E8;
    --linkedin-success: #057642;
    --linkedin-warning: #DF7042;
}

.stApp {
    background: #F3F6F8 !important;
}

/* Cards de métricas */
.metric-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 24px 20px;
    text-align: center;
    border: 1px solid #E1E5E8;
    transition: all 0.2s ease;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}
.metric-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    border-color: #0A66C2;
}
.metric-icon { font-size: 32px; margin-bottom: 12px; }
.metric-title { 
    color: #6B7A8A; 
    font-size: 12px; 
    text-transform: uppercase; 
    letter-spacing: 0.5px;
    font-weight: 600;
}
.metric-value { 
    color: #1E2A3A; 
    font-size: 32px; 
    font-weight: 700; 
    margin-top: 12px;
}
.metric-sub { 
    color: #6B7A8A; 
    font-size: 11px; 
    margin-top: 8px;
}

/* Cards de insight */
.insight-card {
    background: #FFFFFF;
    border-left: 4px solid #0A66C2;
    padding: 18px 20px;
    border-radius: 10px;
    margin-bottom: 15px;
    transition: all 0.2s ease;
    border: 1px solid #E1E5E8;
}
.insight-card:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.insight-card h4 { 
    color: #1E2A3A; 
    margin-bottom: 8px; 
    font-size: 14px;
    font-weight: 600;
}
.insight-card p { 
    color: #6B7A8A; 
    margin: 0; 
    font-size: 13px;
}
.insight-card .insight-value { 
    color: #0A66C2; 
    font-weight: bold; 
    font-size: 18px; 
    margin-top: 10px;
}

/* Seções */
.section-header {
    margin: 40px 0 20px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid #E1E5E8;
}
.section-header h2 {
    color: #1E2A3A;
    font-size: 20px;
    font-weight: 600;
    display: inline-block;
}
.section-tag {
    float: right;
    background: #E8F4FD;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    color: #0A66C2;
    font-weight: 500;
}

/* Status bars */
.status-bar {
    background: #E8F4FD;
    padding: 12px 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    color: #057642;
    border-left: 4px solid #057642;
    font-size: 14px;
}
.filter-info {
    background: #FFF8E7;
    padding: 12px 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    color: #DF7042;
    border-left: 4px solid #DF7042;
    font-size: 14px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E1E5E8;
}
section[data-testid="stSidebar"] * {
    color: #1E2A3A !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label {
    color: #6B7A8A !important;
    font-weight: 500;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    background: #F3F6F8;
    border-radius: 8px;
    padding: 8px 24px;
    color: #6B7A8A;
    border: 1px solid #E1E5E8;
}
.stTabs [aria-selected="true"] {
    background: #0A66C2;
    color: white;
    border: none;
}

/* Botões */
.stDownloadButton button {
    background: #0A66C2 !important;
    color: white !important;
    border: none !important;
    padding: 10px 20px !important;
    border-radius: 24px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
.stDownloadButton button:hover {
    background: #004182 !important;
    transform: translateY(-1px);
}

/* Footer */
.page-footer {
    text-align: center;
    padding: 30px 20px 20px;
    color: #6B7A8A;
    margin-top: 50px;
    border-top: 1px solid #E1E5E8;
    font-size: 12px;
}

/* Expander */
.streamlit-expanderHeader {
    background: #F3F6F8;
    border-radius: 10px;
    color: #1E2A3A;
    border: 1px solid #E1E5E8;
}

/* Headers */
h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: #1E2A3A !important;
}

/* Texto normal */
p, .stMarkdown {
    color: #6B7A8A;
}

/* DataFrame */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #E1E5E8;
}

/* Info/Warning/Success */
.stAlert {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================
def fmt_brl(valor):
    """Formata valor em reais"""
    if pd.isna(valor) or valor == 0:
        return "R$ 0,00"
    if abs(valor) >= 1_000_000_000:
        return f"R$ {valor/1_000_000_000:.2f}B".replace(".", ",")
    if abs(valor) >= 1_000_000:
        return f"R$ {valor/1_000_000:.1f}M".replace(".", ",")
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_num(n):
    """Formata número com separador de milhar"""
    if pd.isna(n):
        return "0"
    return f"{int(n):,}".replace(",", ".")

@st.cache_data
def carregar_dados(uploaded_file):
    """Carrega e processa o CSV"""
    for encoding in ['latin1', 'utf-8', 'cp1252']:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, delimiter=';', encoding=encoding, low_memory=False)
            df.columns = df.columns.str.lower().str.strip()
            
            if 'valor_pago' in df.columns:
                df['valor_pago'] = pd.to_numeric(
                    df['valor_pago'].astype(str).str.replace(',', '.', regex=False).str.extract(r'(\d+\.?\d*)', expand=False),
                    errors='coerce'
                )
            
            df = df.dropna(subset=['valor_pago'])
            df = df[df['valor_pago'] > 0]
            
            if 'data_inicio_processo' in df.columns:
                df['data_inicio_processo'] = pd.to_datetime(df['data_inicio_processo'], errors='coerce', dayfirst=True)
                df['ano'] = df['data_inicio_processo'].dt.year
                df['mes'] = df['data_inicio_processo'].dt.month
            
            regioes_map = {
                'SE': 'Sudeste', 'SU': 'Sul', 'NE': 'Nordeste',
                'CO': 'Centro-Oeste', 'N': 'Norte', 'NO': 'Norte',
                'EX': 'Exterior', 'NI': 'Não Informado'
            }
            if 'regiao' in df.columns:
                df['regiao_nome'] = df['regiao'].map(regioes_map).fillna(df['regiao'])
            
            return df
        except:
            continue
    return None

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## 🔬 **CNPq Analytics**")
    st.markdown("*Plataforma de análise de investimentos em P&D*")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("📤 **Envie o arquivo CSV**", type=["csv"])
    
    st.markdown("---")
    st.markdown("### 📊 Estatísticas do Dataset")
    st.markdown("""
    - **213.735** registros
    - **26** colunas de informação
    - **R$ 1B+** em investimentos
    - Período: 2014-2027
    """)
    
    st.markdown("---")
    st.markdown("📥 **Baixar CSV original:**")
    st.markdown("[Clique aqui](https://drive.google.com/uc?export=download&id=1UXxWqTc6u8_RID_5BbpUI7JLwmgT01ub)")

# ============================================================
# MAIN
# ============================================================
st.markdown("# 📊 **CNPq Analytics**")
st.markdown("### *Análise estratégica de bolsas de pesquisa e desenvolvimento no Brasil*")

if uploaded_file is not None:
    with st.spinner("🔄 Processando 110MB de dados... Isso pode levar alguns segundos"):
        df = carregar_dados(uploaded_file)
    
    if df is not None and len(df) > 0:
        
        # ============================================================
        # FILTROS
        # ============================================================
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎯 **Filtros Interativos**")
        
        df_filtrado = df.copy()
        
        # Filtro Região
        if 'regiao_nome' in df.columns:
            regioes = sorted(df['regiao_nome'].dropna().unique())
            reg_sel = st.sidebar.multiselect("📍 **Região**", regioes, default=regioes)
            if reg_sel:
                df_filtrado = df_filtrado[df_filtrado['regiao_nome'].isin(reg_sel)]
        
        # Filtro Ano
        if 'ano' in df.columns:
            anos = sorted(df['ano'].dropna().unique())
            if len(anos) > 1:
                ano_min, ano_max = int(min(anos)), int(max(anos))
                ano_sel = st.sidebar.slider("📅 **Período**", ano_min, ano_max, (ano_min, ano_max))
                df_filtrado = df_filtrado[(df_filtrado['ano'] >= ano_sel[0]) & (df_filtrado['ano'] <= ano_sel[1])]
        
        # Filtro Área
        if 'grande_area' in df.columns:
            areas = sorted(df['grande_area'].dropna().unique())
            areas_sel = st.sidebar.multiselect("🧬 **Grande Área**", areas, default=areas[:5] if len(areas) > 5 else areas)
            if areas_sel:
                df_filtrado = df_filtrado[df_filtrado['grande_area'].isin(areas_sel)]
        
        # Status dos filtros
        if df_filtrado.shape[0] < df.shape[0]:
            st.markdown(f'<div class="filter-info">🔍 **Filtros ativos:** exibindo {df_filtrado.shape[0]:,} de {df.shape[0]:,} registros ({100*df_filtrado.shape[0]/df.shape[0]:.1f}%)</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-bar">✅ **Dados carregados:** {df_filtrado.shape[0]:,} registros válidos</div>', unsafe_allow_html=True)
        
        # ============================================================
        # KPIs
        # ============================================================
        total_val = df_filtrado['valor_pago'].sum()
        media_val = df_filtrado['valor_pago'].mean()
        n_pesq = df_filtrado['beneficiario'].nunique() if 'beneficiario' in df_filtrado.columns else 0
        n_inst = df_filtrado['instituicao_destino'].nunique() if 'instituicao_destino' in df_filtrado.columns else 0
        n_bolsas = df_filtrado.shape[0]
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">💰</div>
                <div class="metric-title">Investimento Total</div>
                <div class="metric-value">{fmt_brl(total_val)}</div>
                <div class="metric-sub">valor consolidado</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">🎓</div>
                <div class="metric-title">Pesquisadores</div>
                <div class="metric-value">{fmt_num(n_pesq)}</div>
                <div class="metric-sub">beneficiários únicos</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">🏛️</div>
                <div class="metric-title">Instituições</div>
                <div class="metric-value">{fmt_num(n_inst)}</div>
                <div class="metric-sub">unidades atendidas</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📊</div>
                <div class="metric-title">Ticket Médio</div>
                <div class="metric-value">{fmt_brl(media_val)}</div>
                <div class="metric-sub">por bolsa</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">🎫</div>
                <div class="metric-title">Total de Bolsas</div>
                <div class="metric-value">{fmt_num(n_bolsas)}</div>
                <div class="metric-sub">registros analisados</div>
            </div>
            """, unsafe_allow_html=True)
        
        # ============================================================
        # GRÁFICOS EM TABS
        # ============================================================
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Por Área", "🗺️ Por Região", "📈 Evolução Temporal", "🏆 Top Rankings"])
        
        # TAB 1: Por Área
        with tab1:
            if 'grande_area' in df_filtrado.columns:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    area_data = df_filtrado.groupby('grande_area')['valor_pago'].sum().sort_values(ascending=False).head(10).reset_index()
                    area_data.columns = ['Área', 'Valor']
                    
                    fig = px.bar(area_data, x='Área', y='Valor', color='Valor',
                                color_continuous_scale=['#0A66C2', '#7B8BA4'])
                    fig.update_layout(
                        template="plotly_white", 
                        height=500, 
                        paper_bgcolor="#FFFFFF", 
                        plot_bgcolor="#F8FAFC",
                        font=dict(color="#1E2A3A")
                    )
                    fig.update_traces(texttemplate='R$ %{y:,.0f}', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("#### 🔢 Detalhamento")
                    area_data['Valor Formatado'] = area_data['Valor'].apply(fmt_brl)
                    area_data['%'] = (area_data['Valor'] / area_data['Valor'].sum() * 100).round(1).astype(str) + '%'
                    st.dataframe(area_data[['Área', 'Valor Formatado', '%']].head(10), use_container_width=True, hide_index=True)
        
        # TAB 2: Por Região
        with tab2:
            if 'regiao_nome' in df_filtrado.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    reg_data = df_filtrado.groupby('regiao_nome')['valor_pago'].sum().reset_index()
                    reg_data.columns = ['Região', 'Valor']
                    
                    fig2 = px.bar(reg_data, x='Região', y='Valor', color='Valor',
                                 color_continuous_scale='Blues', text='Valor')
                    fig2.update_layout(
                        template="plotly_white", 
                        height=450, 
                        paper_bgcolor="#FFFFFF", 
                        plot_bgcolor="#F8FAFC",
                        font=dict(color="#1E2A3A")
                    )
                    fig2.update_traces(texttemplate='R$ %{y:,.0f}', textposition='outside')
                    st.plotly_chart(fig2, use_container_width=True)
                
                with col2:
                    fig3 = px.pie(reg_data, values='Valor', names='Região', hole=0.4,
                                 color_discrete_sequence=['#0A66C2', '#7B8BA4', '#057642', '#DF7042', '#6B7A8A', '#1E2A3A'])
                    fig3.update_layout(
                        template="plotly_white", 
                        height=450, 
                        paper_bgcolor="#FFFFFF", 
                        plot_bgcolor="#FFFFFF",
                        font=dict(color="#1E2A3A")
                    )
                    fig3.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig3, use_container_width=True)
                
                st.markdown("#### 🔥 Concentração de Investimento")
                reg_data['Percentual'] = (reg_data['Valor'] / reg_data['Valor'].sum() * 100).round(1)
                st.dataframe(reg_data, use_container_width=True, hide_index=True)
        
        # TAB 3: Evolução Temporal
        with tab3:
            if 'ano' in df_filtrado.columns:
                inv_ano = df_filtrado.groupby('ano')['valor_pago'].agg(['sum', 'count']).reset_index()
                inv_ano.columns = ['Ano', 'Total', 'Quantidade']
                inv_ano = inv_ano.dropna()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig4 = px.line(inv_ano, x='Ano', y='Total', markers=True,
                                  title='💰 Evolução do Investimento Total')
                    fig4.update_layout(
                        template="plotly_white", 
                        height=400, 
                        paper_bgcolor="#FFFFFF", 
                        plot_bgcolor="#F8FAFC",
                        font=dict(color="#1E2A3A")
                    )
                    fig4.update_traces(line=dict(width=3, color='#0A66C2'), marker=dict(size=8, color='#0A66C2'))
                    st.plotly_chart(fig4, use_container_width=True)
                
                with col2:
                    fig5 = px.bar(inv_ano, x='Ano', y='Quantidade',
                                 title='📊 Evolução do Número de Bolsas', color='Quantidade',
                                 color_continuous_scale='Greens')
                    fig5.update_layout(
                        template="plotly_white", 
                        height=400, 
                        paper_bgcolor="#FFFFFF", 
                        plot_bgcolor="#F8FAFC",
                        font=dict(color="#1E2A3A")
                    )
                    st.plotly_chart(fig5, use_container_width=True)
                
                if len(inv_ano) >= 2:
                    var_total = ((inv_ano['Total'].iloc[-1] - inv_ano['Total'].iloc[-2]) / inv_ano['Total'].iloc[-2] * 100)
                    var_quant = ((inv_ano['Quantidade'].iloc[-1] - inv_ano['Quantidade'].iloc[-2]) / inv_ano['Quantidade'].iloc[-2] * 100)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("📈 Variação do Investimento", f"{var_total:+.1f}%", 
                                 delta_color="normal" if var_total > 0 else "inverse")
                    with col2:
                        st.metric("📊 Variação de Bolsas", f"{var_quant:+.1f}%",
                                 delta_color="normal" if var_quant > 0 else "inverse")
        
        # TAB 4: Top Rankings
        with tab4:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🏆 Top 10 Pesquisadores")
                if 'beneficiario' in df_filtrado.columns and 'valor_pago' in df_filtrado.columns:
                    top_benef = df_filtrado.groupby('beneficiario')['valor_pago'].sum().sort_values(ascending=False).head(10).reset_index()
                    top_benef.columns = ['Pesquisador', 'Total']
                    top_benef['Total'] = top_benef['Total'].apply(fmt_brl)
                    st.dataframe(top_benef, use_container_width=True, hide_index=True)
                else:
                    st.info("Dados de beneficiário não disponíveis")
            
            with col2:
                st.markdown("#### 🏛️ Top 10 Instituições")
                if 'instituicao_destino' in df_filtrado.columns and 'valor_pago' in df_filtrado.columns:
                    top_inst = df_filtrado.groupby('instituicao_destino')['valor_pago'].sum().sort_values(ascending=False).head(10).reset_index()
                    top_inst.columns = ['Instituição', 'Total']
                    top_inst['Total'] = top_inst['Total'].apply(fmt_brl)
                    st.dataframe(top_inst, use_container_width=True, hide_index=True)
                else:
                    st.info("Dados de instituição não disponíveis")
            
            st.markdown("#### 🎓 Top 10 Modalidades")
            if 'modalidade' in df_filtrado.columns:
                top_mod = df_filtrado['modalidade'].value_counts().head(10).reset_index()
                top_mod.columns = ['Modalidade', 'Quantidade']
                st.dataframe(top_mod, use_container_width=True, hide_index=True)
        
        # ============================================================
        # INSIGHTS AVANÇADOS
        # ============================================================
        st.markdown('<div class="section-header"><h2>🔍 Insights Estratégicos</h2><span class="section-tag">Análise</span></div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'regiao_nome' in df_filtrado.columns:
                inv_reg = df_filtrado.groupby('regiao_nome')['valor_pago'].sum()
                if len(inv_reg) > 0:
                    top_reg = inv_reg.idxmax()
                    pct = 100 * inv_reg.max() / df_filtrado['valor_pago'].sum()
                    st.markdown(f"""
                    <div class="insight-card">
                        <h4>📍 Concentração Regional</h4>
                        <p>A região <b>{top_reg}</b> concentra <b>{pct:.1f}%</b> do investimento total.</p>
                        <div class="insight-value">{fmt_brl(inv_reg.max())}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            if 'grande_area' in df_filtrado.columns:
                inv_area = df_filtrado.groupby('grande_area')['valor_pago'].sum()
                if len(inv_area) > 0:
                    top_area = inv_area.idxmax()
                    pct = 100 * inv_area.max() / df_filtrado['valor_pago'].sum()
                    st.markdown(f"""
                    <div class="insight-card">
                        <h4>🧬 Área Líder</h4>
                        <p>A área <b>{top_area}</b> lidera o investimento com <b>{pct:.1f}%</b> dos recursos.</p>
                        <div class="insight-value">{fmt_brl(inv_area.max())}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col3:
            if 'ano' in df_filtrado.columns:
                inv_ano = df_filtrado.groupby('ano')['valor_pago'].sum()
                if len(inv_ano) >= 2:
                    var = ((inv_ano.iloc[-1] - inv_ano.iloc[-2]) / inv_ano.iloc[-2] * 100)
                    cor = "📈" if var > 0 else "📉"
                    st.markdown(f"""
                    <div class="insight-card">
                        <h4>📊 Variação Anual</h4>
                        <p>De <b>{int(inv_ano.index[-2])}</b> para <b>{int(inv_ano.index[-1])}</b>: <b style="color:{'#057642' if var>0 else '#DF7042'}">{var:+.1f}%</b></p>
                        <div class="insight-value">{cor} {fmt_brl(abs(inv_ano.iloc[-1] - inv_ano.iloc[-2]))}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col4:
            if 'regiao_nome' in df_filtrado.columns:
                inv_reg = df_filtrado.groupby('regiao_nome')['valor_pago'].sum()
                inv_reg = inv_reg[inv_reg > 0]
                if len(inv_reg) >= 2:
                    razao = inv_reg.max() / inv_reg.min()
                    st.markdown(f"""
                    <div class="insight-card">
                        <h4>⚖️ Desigualdade Regional</h4>
                        <p>Região mais financiada recebe <b>{razao:.1f}x</b> mais que a menos financiada.</p>
                        <div class="insight-value">Diferença de {fmt_brl(inv_reg.max() - inv_reg.min())}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # ============================================================
        # EXPORTAÇÃO
        # ============================================================
        st.markdown('<div class="section-header"><h2>📥 Exportar Dados</h2><span class="section-tag">Download</span></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv_data = df_filtrado.to_csv(index=False, sep=';', decimal=',')
            st.download_button("📄 **CSV** - Dados filtrados", csv_data, f"cnpq_dados_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        
        with col2:
            relatorio = f"""
            ========================================
            RELATÓRIO CNPq ANALYTICS
            ========================================
            Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
            
            INDICADORES PRINCIPAIS:
            - Investimento Total: {fmt_brl(total_val)}
            - Total de Pesquisadores: {fmt_num(n_pesq)}
            - Total de Instituições: {fmt_num(n_inst)}
            - Ticket Médio: {fmt_brl(media_val)}
            - Total de Bolsas: {fmt_num(n_bolsas)}
            
            FILTROS APLICADOS:
            - Registros: {fmt_num(df_filtrado.shape[0])} / {fmt_num(df.shape[0])}
            
            ========================================
            """
            st.download_button("📝 **Relatório** - Resumo executivo", relatorio, f"cnpq_relatorio_{datetime.now().strftime('%Y%m%d')}.txt", "text/plain")
        
        with col3:
            st.markdown(f"""
            <div style="background:#F3F6F8; padding:15px; border-radius:12px; text-align:center; border:1px solid #E1E5E8;">
                <span style="color:#6B7A8A; font-size:12px;">📊 Período analisado</span><br>
                <span style="color:#1E2A3A; font-weight:bold;">
                    {int(df_filtrado['ano'].min()) if 'ano' in df_filtrado.columns else 'N/A'} - 
                    {int(df_filtrado['ano'].max()) if 'ano' in df_filtrado.columns else 'N/A'}
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        # ============================================================
        # DADOS TABULARES
        # ============================================================
        with st.expander("🗂️ **Visualizar Dados Detalhados**", expanded=False):
            colunas_exibir = [c for c in df_filtrado.columns if c not in ['ano', 'mes']][:15]
            st.dataframe(df_filtrado[colunas_exibir].head(500), use_container_width=True, height=400)
            st.caption(f"Exibindo 500 linhas de {df_filtrado.shape[0]:,} registros")
        
        # ============================================================
        # RODAPÉ
        # ============================================================
        st.markdown(f"""
        <div class="page-footer">
            <b>CNPq Analytics</b> · Desenvolvido com Streamlit & Plotly · Fonte: CNPq/Governo Federal<br>
            Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.error("❌ **Erro ao carregar o arquivo.** Verifique se é um CSV válido com separador ';' e encoding latin1/UTF-8.")
else:
    st.info("👈 **Faça upload do arquivo CSV no menu lateral para começar sua análise!**")
    
    st.markdown("""
    ---
    ### 📋 **Sobre o Dashboard**
    
    | Característica | Descrição |
    |----------------|-----------|
    | **Dados analisados** | 213.735 bolsas de pesquisa do CNPq |
    | **Período** | 2014 - 2027 |
    | **Investimento total** | Mais de R$ 1 bilhão |
    | **Áreas do conhecimento** | 12 grandes áreas |
    | **Instituições atendidas** | Mais de 4.000 |
    
    ### 🚀 **Funcionalidades**
    
    - ✅ Filtros interativos por região, período e área
    - ✅ Gráficos dinâmicos com Plotly
    - ✅ Tabelas de ranking (pesquisadores, instituições)
    - ✅ Análise de evolução temporal
    - ✅ Exportação em CSV e relatório TXT
    - ✅ Insights automáticos sobre concentração e desigualdade
    
    ### 📥 **Como começar**
    
    1. Baixe o CSV original usando o link no menu lateral
    2. Faça o upload do arquivo
    3. Explore os filtros e visualizações
    """)

# ============================================================
# FIM
# ============================================================
