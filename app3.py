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
    page_title="CNPq Analytics - Dashboard de Pesquisa",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS LINKEDIN PLUS
# ============================================================
st.markdown("""
<style>
/* Cores LinkedIn Plus */
:root {
    --linkedin-blue: #0A66C2;
    --linkedin-blue-light: #E8F4FD;
    --linkedin-gray-bg: #F4F6F9;
    --linkedin-gray-card: #FFFFFF;
    --linkedin-gray-text: #1D2B3E;
    --linkedin-gray-muted: #6B7A8F;
    --linkedin-border: #E4E8ED;
    --linkedin-success: #057642;
    --linkedin-warning: #DF7042;
    --linkedin-purple: #7C3AED;
}

/* Reset */
.stApp {
    background: var(--linkedin-gray-bg) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--linkedin-gray-card) !important;
    border-right: 1px solid var(--linkedin-border);
    box-shadow: none;
}
section[data-testid="stSidebar"] > div {
    padding: 1.5rem 1.2rem;
}
section[data-testid="stSidebar"] * {
    color: var(--linkedin-gray-text) !important;
}

/* Logo Sidebar */
.sidebar-logo {
    text-align: center;
    padding: 20px 0 10px 0;
    border-bottom: 2px solid var(--linkedin-border);
    margin-bottom: 20px;
}
.sidebar-logo h2 {
    color: var(--linkedin-blue) !important;
    font-size: 22px;
    margin: 0;
}
.sidebar-logo p {
    color: var(--linkedin-gray-muted) !important;
    font-size: 12px;
}

/* Cards KPIs */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 20px;
    margin-bottom: 30px;
}
.kpi-card {
    background: var(--linkedin-gray-card);
    border-radius: 16px;
    padding: 20px 15px;
    text-align: center;
    border: 1px solid var(--linkedin-border);
    transition: all 0.2s ease;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    border-color: var(--linkedin-blue);
}
.kpi-icon { font-size: 28px; margin-bottom: 10px; }
.kpi-label { 
    color: var(--linkedin-gray-muted); 
    font-size: 11px; 
    text-transform: uppercase; 
    letter-spacing: 0.8px;
    font-weight: 600;
    margin-bottom: 8px;
}
.kpi-value { 
    color: var(--linkedin-gray-text); 
    font-size: 28px; 
    font-weight: 700; 
    margin: 8px 0 4px;
    line-height: 1.2;
}
.kpi-sub { 
    color: var(--linkedin-gray-muted); 
    font-size: 10px; 
}
.kpi-trend {
    font-size: 11px;
    margin-top: 8px;
    padding: 4px 8px;
    border-radius: 20px;
    display: inline-block;
}
.trend-up { background: #E6F4EA; color: #057642; }
.trend-down { background: #FEF3E8; color: #DF7042; }

/* Cards Insights */
.insight-card {
    background: var(--linkedin-gray-card);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 16px;
    border: 1px solid var(--linkedin-border);
    transition: all 0.2s ease;
}
.insight-card:hover {
    border-color: var(--linkedin-blue);
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.insight-title {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--linkedin-gray-muted);
    margin-bottom: 10px;
}
.insight-value {
    font-size: 28px;
    font-weight: 700;
    color: var(--linkedin-blue);
    margin: 10px 0 5px;
}
.insight-desc {
    font-size: 13px;
    color: var(--linkedin-gray-text);
    line-height: 1.5;
}
.insight-desc strong {
    color: var(--linkedin-gray-text);
}
.insight-icon {
    float: right;
    font-size: 40px;
    opacity: 0.15;
}

/* Headers */
.page-header {
    margin-bottom: 30px;
}
.page-header h1 {
    font-size: 32px;
    font-weight: 700;
    color: var(--linkedin-gray-text);
    margin: 0;
}
.page-header p {
    color: var(--linkedin-gray-muted);
    font-size: 16px;
    margin-top: 8px;
}
.section-header {
    margin: 40px 0 20px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 2px solid var(--linkedin-border);
    padding-bottom: 10px;
}
.section-header h2 {
    font-size: 20px;
    font-weight: 600;
    color: var(--linkedin-gray-text);
    margin: 0;
}
.section-badge {
    background: var(--linkedin-blue-light);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    color: var(--linkedin-blue);
    font-weight: 500;
}

/* Status Bars */
.status-success {
    background: #E6F4EA;
    border-left: 4px solid var(--linkedin-success);
    padding: 12px 18px;
    border-radius: 10px;
    margin-bottom: 20px;
    color: var(--linkedin-success);
    font-size: 13px;
}
.status-info {
    background: var(--linkedin-blue-light);
    border-left: 4px solid var(--linkedin-blue);
    padding: 12px 18px;
    border-radius: 10px;
    margin-bottom: 20px;
    color: var(--linkedin-blue);
    font-size: 13px;
}
.status-warning {
    background: #FEF3E8;
    border-left: 4px solid var(--linkedin-warning);
    padding: 12px 18px;
    border-radius: 10px;
    margin-bottom: 20px;
    color: var(--linkedin-warning);
    font-size: 13px;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    background: var(--linkedin-gray-card);
    border-radius: 12px;
    padding: 10px 28px;
    color: var(--linkedin-gray-muted);
    border: 1px solid var(--linkedin-border);
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: var(--linkedin-blue);
    color: white;
    border: none;
}

/* Botões */
.stDownloadButton button {
    background: var(--linkedin-blue) !important;
    color: white !important;
    border: none !important;
    padding: 10px 24px !important;
    border-radius: 28px !important;
    font-weight: 600 !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}
.stDownloadButton button:hover {
    background: #004182 !important;
    transform: translateY(-1px);
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--linkedin-gray-card);
    border-radius: 12px;
    color: var(--linkedin-gray-text);
    border: 1px solid var(--linkedin-border);
    font-weight: 500;
}
.streamlit-expanderHeader:hover {
    border-color: var(--linkedin-blue);
}

/* Metricas do Plotly */
.metric-container {
    background: var(--linkedin-gray-card);
    border-radius: 12px;
    padding: 10px;
    text-align: center;
    border: 1px solid var(--linkedin-border);
}

/* Footer */
.footer {
    text-align: center;
    padding: 30px 20px 20px;
    margin-top: 50px;
    border-top: 1px solid var(--linkedin-border);
    color: var(--linkedin-gray-muted);
    font-size: 12px;
}

/* Alertas */
.stAlert {
    border-radius: 12px;
}

/* Select e MultiSelect */
.stMultiSelect [data-baseweb="select"] > div,
.stSelectbox [data-baseweb="select"] > div {
    background-color: var(--linkedin-gray-card);
    border-color: var(--linkedin-border);
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNÇÕES
# ============================================================
def fmt_brl(valor):
    if pd.isna(valor) or valor == 0:
        return "R$ 0"
    if abs(valor) >= 1_000_000_000:
        return f"R$ {valor/1_000_000_000:.2f}B".replace(".", ",")
    if abs(valor) >= 1_000_000:
        return f"R$ {valor/1_000_000:.1f}M".replace(".", ",")
    return f"R$ {valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_num(n):
    if pd.isna(n):
        return "0"
    return f"{int(n):,}".replace(",", ".")

@st.cache_data
def carregar_dados(uploaded_file):
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

def calcular_tendencia(serie):
    if len(serie) >= 2:
        ultimo = serie.iloc[-1]
        penultimo = serie.iloc[-2]
        if penultimo > 0:
            var = (ultimo - penultimo) / penultimo * 100
            return var
    return 0

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <h2>🔬 CNPq Analytics</h2>
        <p>Dashboard de Pesquisa e Inovação</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "📄 **Upload do Arquivo CSV**",
        type=["csv"],
        help="Selecione o arquivo bolsa_familia.csv"
    )
    
    st.markdown("---")
    
    st.markdown("### 📊 Dataset")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Registros", "213.735")
        st.metric("Colunas", "26")
    with col2:
        st.metric("Investimento", "R$ 1B+")
        st.metric("Período", "2014-2027")
    
    st.markdown("---")
    st.markdown("📥 **Baixar CSV**")
    st.markdown("[Google Drive](https://drive.google.com/uc?export=download&id=1UXxWqTc6u8_RID_5BbpUI7JLwmgT01ub)")

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="page-header">
    <h1>📊 CNPq Analytics</h1>
    <p>Análise estratégica de investimentos em pesquisa e desenvolvimento no Brasil</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# MAIN
# ============================================================
if uploaded_file is not None:
    with st.spinner("🔄 Processando dados..."):
        df = carregar_dados(uploaded_file)
    
    if df is not None and len(df) > 0:
        
        # ===== FILTROS =====
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎯 Filtros")
        
        df_filtrado = df.copy()
        
        if 'regiao_nome' in df.columns:
            regioes = sorted(df['regiao_nome'].dropna().unique())
            reg_sel = st.sidebar.multiselect("📍 Região", regioes, default=regioes)
            if reg_sel:
                df_filtrado = df_filtrado[df_filtrado['regiao_nome'].isin(reg_sel)]
        
        if 'ano' in df.columns:
            anos = sorted(df['ano'].dropna().unique())
            if len(anos) > 1:
                ano_min, ano_max = int(min(anos)), int(max(anos))
                ano_sel = st.sidebar.slider("📅 Período", ano_min, ano_max, (ano_min, ano_max))
                df_filtrado = df_filtrado[(df_filtrado['ano'] >= ano_sel[0]) & (df_filtrado['ano'] <= ano_sel[1])]
        
        if 'grande_area' in df.columns:
            areas = sorted(df['grande_area'].dropna().unique())
            areas_sel = st.sidebar.multiselect("🧬 Grande Área", areas, default=areas[:5] if len(areas) > 5 else areas)
            if areas_sel:
                df_filtrado = df_filtrado[df_filtrado['grande_area'].isin(areas_sel)]
        
        # Status
        if df_filtrado.shape[0] < df.shape[0]:
            st.markdown(f'<div class="status-info">🔍 <strong>{df_filtrado.shape[0]:,}</strong> de <strong>{df.shape[0]:,}</strong> registros ({100*df_filtrado.shape[0]/df.shape[0]:.1f}%)</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-success">✅ <strong>{df_filtrado.shape[0]:,}</strong> registros carregados</div>', unsafe_allow_html=True)
        
        # ===== KPIs =====
        total_val = df_filtrado['valor_pago'].sum()
        media_val = df_filtrado['valor_pago'].mean()
        n_pesq = df_filtrado['beneficiario'].nunique() if 'beneficiario' in df_filtrado.columns else 0
        n_inst = df_filtrado['instituicao_destino'].nunique() if 'instituicao_destino' in df_filtrado.columns else 0
        n_bolsas = df_filtrado.shape[0]
        
        # Tendências
        if 'ano' in df_filtrado.columns:
            inv_ano = df_filtrado.groupby('ano')['valor_pago'].sum()
            var_total = calcular_tendencia(inv_ano)
        else:
            var_total = 0
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">💰</div>
                <div class="kpi-label">INVESTIMENTO TOTAL</div>
                <div class="kpi-value">{fmt_brl(total_val)}</div>
                <div class="kpi-sub">valor consolidado</div>
                {"<div class='kpi-trend trend-up'>▲ " + f"{var_total:.1f}%" + "</div>" if var_total > 0 else "<div class='kpi-trend trend-down'>▼ " + f"{abs(var_total):.1f}%" + "</div>" if var_total < 0 else ""}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">👥</div>
                <div class="kpi-label">PESQUISADORES</div>
                <div class="kpi-value">{fmt_num(n_pesq)}</div>
                <div class="kpi-sub">beneficiários únicos</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">🏛️</div>
                <div class="kpi-label">INSTITUIÇÕES</div>
                <div class="kpi-value">{fmt_num(n_inst)}</div>
                <div class="kpi-sub">unidades atendidas</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">📊</div>
                <div class="kpi-label">TICKET MÉDIO</div>
                <div class="kpi-value">{fmt_brl(media_val)}</div>
                <div class="kpi-sub">por bolsa</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">🎫</div>
                <div class="kpi-label">TOTAL DE BOLSAS</div>
                <div class="kpi-value">{fmt_num(n_bolsas)}</div>
                <div class="kpi-sub">registros</div>
            </div>
            """, unsafe_allow_html=True)
        
        # ===== TABS =====
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Por Área", "🗺️ Por Região", "📈 Evolução", "🏆 Rankings"])
        
        with tab1:
            if 'grande_area' in df_filtrado.columns:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    area_data = df_filtrado.groupby('grande_area')['valor_pago'].sum().sort_values(ascending=False).head(10).reset_index()
                    area_data.columns = ['Área', 'Valor']
                    
                    fig = px.bar(area_data, x='Valor', y='Área', orientation='h',
                                color='Valor', color_continuous_scale=['#6B7A8F', '#0A66C2'],
                                text='Valor')
                    fig.update_layout(
                        template="plotly_white",
                        height=500,
                        margin=dict(l=20, r=20, t=40, b=20),
                        xaxis_title="Investimento (R$)",
                        yaxis_title=""
                    )
                    fig.update_traces(texttemplate='R$ %{x:,.0f}', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("#### 📋 Detalhamento")
                    area_data['Valor'] = area_data['Valor'].apply(fmt_brl)
                    area_data['%'] = (area_data['Valor'].apply(lambda x: float(x.replace('R$', '').replace('M', '').replace('B', '').replace(',', '.').strip()) if 'M' in x else 0))
                    st.dataframe(area_data[['Área', 'Valor']], use_container_width=True, hide_index=True)
        
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
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    fig2.update_traces(texttemplate='R$ %{y:,.0f}', textposition='outside')
                    st.plotly_chart(fig2, use_container_width=True)
                
                with col2:
                    fig3 = px.pie(reg_data, values='Valor', names='Região', hole=0.35,
                                 color_discrete_sequence=['#0A66C2', '#7C3AED', '#057642', '#DF7042', '#6B7A8F'])
                    fig3.update_layout(
                        template="plotly_white",
                        height=450,
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    fig3.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig3, use_container_width=True)
        
        with tab3:
            if 'ano' in df_filtrado.columns:
                inv_ano = df_filtrado.groupby('ano')['valor_pago'].sum().reset_index()
                inv_ano = inv_ano.dropna()
                
                if len(inv_ano) > 1:
                    fig4 = px.area(inv_ano, x='ano', y='valor_pago', markers=True,
                                  title='Evolução do Investimento Total')
                    fig4.update_layout(
                        template="plotly_white",
                        height=450,
                        margin=dict(l=20, r=20, t=50, b=20)
                    )
                    fig4.update_traces(line=dict(width=2, color='#0A66C2'), 
                                      marker=dict(size=6, color='#0A66C2'),
                                      fillcolor='rgba(10,102,194,0.1)')
                    st.plotly_chart(fig4, use_container_width=True)
        
        with tab4:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🏆 Top 10 Pesquisadores")
                if 'beneficiario' in df_filtrado.columns:
                    top_pesq = df_filtrado.groupby('beneficiario')['valor_pago'].sum().sort_values(ascending=False).head(10).reset_index()
                    top_pesq.columns = ['Pesquisador', 'Total']
                    top_pesq['Total'] = top_pesq['Total'].apply(fmt_brl)
                    st.dataframe(top_pesq, use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("#### 🏛️ Top 10 Instituições")
                if 'instituicao_destino' in df_filtrado.columns:
                    top_inst = df_filtrado.groupby('instituicao_destino')['valor_pago'].sum().sort_values(ascending=False).head(10).reset_index()
                    top_inst.columns = ['Instituição', 'Total']
                    top_inst['Total'] = top_inst['Total'].apply(fmt_brl)
                    st.dataframe(top_inst, use_container_width=True, hide_index=True)
            
            st.markdown("#### 🎓 Top 10 Modalidades")
            if 'modalidade' in df_filtrado.columns:
                top_mod = df_filtrado['modalidade'].value_counts().head(10).reset_index()
                top_mod.columns = ['Modalidade', 'Quantidade']
                st.dataframe(top_mod, use_container_width=True, hide_index=True)
        
        # ===== INSIGHTS =====
        st.markdown("""
        <div class="section-header">
            <h2>🔍 Insights Estratégicos</h2>
            <span class="section-badge">Análise Avançada</span>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'regiao_nome' in df_filtrado.columns:
                inv_reg = df_filtrado.groupby('regiao_nome')['valor_pago'].sum()
                if len(inv_reg) > 0:
                    top_reg = inv_reg.idxmax()
                    pct = 100 * inv_reg.max() / total_val
                    st.markdown(f"""
                    <div class="insight-card">
                        <div class="insight-icon">📍</div>
                        <div class="insight-title">Concentração Regional</div>
                        <div class="insight-value">{top_reg}</div>
                        <div class="insight-desc"><strong>{pct:.1f}%</strong> do investimento total</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            if 'grande_area' in df_filtrado.columns:
                inv_area = df_filtrado.groupby('grande_area')['valor_pago'].sum()
                if len(inv_area) > 0:
                    top_area = inv_area.idxmax()
                    pct = 100 * inv_area.max() / total_val
                    st.markdown(f"""
                    <div class="insight-card">
                        <div class="insight-icon">🧬</div>
                        <div class="insight-title">Área Líder</div>
                        <div class="insight-value">{top_area}</div>
                        <div class="insight-desc"><strong>{pct:.1f}%</strong> dos recursos</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col3:
            if 'ano' in df_filtrado.columns and len(inv_ano) >= 2:
                var = ((inv_ano['valor_pago'].iloc[-1] - inv_ano['valor_pago'].iloc[-2]) / inv_ano['valor_pago'].iloc[-2] * 100)
                st.markdown(f"""
                <div class="insight-card">
                    <div class="insight-icon">📈</div>
                    <div class="insight-title">Variação Anual</div>
                    <div class="insight-value">{var:+.1f}%</div>
                    <div class="insight-desc">de {int(inv_ano['ano'].iloc[-2])} para {int(inv_ano['ano'].iloc[-1])}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # ===== EXPORTAÇÃO =====
        st.markdown("""
        <div class="section-header">
            <h2>📥 Exportar Dados</h2>
            <span class="section-badge">Download</span>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv_data = df_filtrado.to_csv(index=False, sep=';')
            st.download_button("📄 Exportar CSV", csv_data, f"cnpq_dados_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        
        with col2:
            relatorio = f"""
RELATÓRIO CNPq ANALYTICS
Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}

INDICADORES:
- Investimento: {fmt_brl(total_val)}
- Pesquisadores: {fmt_num(n_pesq)}
- Instituições: {fmt_num(n_inst)}
- Ticket Médio: {fmt_brl(media_val)}
- Total de Bolsas: {fmt_num(n_bolsas)}

PERÍODO: {int(df_filtrado['ano'].min()) if 'ano' in df_filtrado.columns else 'N/A'} - {int(df_filtrado['ano'].max()) if 'ano' in df_filtrado.columns else 'N/A'}
            """
            st.download_button("📝 Exportar Relatório", relatorio, f"relatorio_{datetime.now().strftime('%Y%m%d')}.txt", "text/plain")
        
        with col3:
            st.markdown(f"""
            <div style="background:#F4F6F9; padding:12px; border-radius:12px; text-align:center;">
                <span style="color:#6B7A8F; font-size:12px;">📊 Período</span><br>
                <span style="color:#1D2B3E; font-weight:700; font-size:16px;">
                    {int(df_filtrado['ano'].min()) if 'ano' in df_filtrado.columns else 'N/A'} - {int(df_filtrado['ano'].max()) if 'ano' in df_filtrado.columns else 'N/A'}
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        # ===== DADOS DETALHADOS =====
        with st.expander("🗂️ Visualizar Dados Detalhados"):
            cols_to_show = [c for c in df_filtrado.columns if c not in ['ano', 'mes']][:12]
            st.dataframe(df_filtrado[cols_to_show].head(500), use_container_width=True, height=400)
            st.caption(f"Exibindo 500 de {df_filtrado.shape[0]:,} registros")
        
        # ===== FOOTER =====
        st.markdown(f"""
        <div class="footer">
            🔬 CNPq Analytics · Desenvolvido com Streamlit & Plotly · Fonte: CNPq/Governo Federal<br>
            📅 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.error("❌ Erro ao carregar o arquivo. Verifique o formato.")
else:
    st.info("👈 **Faça upload do arquivo CSV no menu lateral para começar**")
    
    st.markdown("""
    <div style="background:#FFFFFF; border-radius:16px; padding:30px; margin-top:20px; border:1px solid #E4E8ED;">
        <h3 style="color:#1D2B3E;">📋 Sobre o Dashboard</h3>
        <p>Este dashboard analisa <strong>213.735 bolsas de pesquisa</strong> do CNPq, totalizando mais de <strong>R$ 1 bilhão</strong> em investimentos.</p>
        
        <h4 style="color:#1D2B3E; margin-top:20px;">🚀 Funcionalidades</h4>
        <ul>
            <li>✅ Filtros interativos por região, período e área</li>
            <li>✅ Gráficos dinâmicos com Plotly</li>
            <li>✅ Rankings de pesquisadores e instituições</li>
            <li>✅ Análise de evolução temporal</li>
            <li>✅ Exportação em CSV e relatório TXT</li>
            <li>✅ Insights automáticos</li>
        </ul>
        
        <h4 style="color:#1D2B3E; margin-top:20px;">📥 Como começar</h4>
        <ol>
            <li>Baixe o CSV original usando o link no menu lateral</li>
            <li>Faça o upload do arquivo</li>
            <li>Explore os filtros e visualizações</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# FIM
# ============================================================
