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
# CSS
# ============================================================
st.markdown("""
<style>
.stApp { background: #07080d !important; }
html, body, .stApp { color: #f0f4ff !important; font-family: 'DM Sans', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem !important; max-width: 1600px !important; }

/* Sidebar */
section[data-testid="stSidebar"] { background: #0e1018 !important; border-right: 1px solid rgba(255,255,255,0.07) !important; }
section[data-testid="stSidebar"] * { color: #f0f4ff !important; }

/* Header */
.page-header { display: flex; align-items: flex-end; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.07); padding-bottom: 20px; margin-bottom: 28px; }
.page-header-left h1 { font-size: 34px !important; font-weight: 800 !important; color: #f0f4ff !important; margin: 0 0 4px 0 !important; }
.page-header-left p { color: #6b7898; font-size: 14px; }
.badge { background: rgba(99,212,255,0.1); border: 1px solid rgba(99,212,255,0.2); color: #63d4ff; padding: 3px 10px; border-radius: 999px; font-size: 11px; }

/* KPI Cards */
.kpi-grid { display: flex; gap: 16px; margin-bottom: 32px; flex-wrap: wrap; }
.kpi-card { flex: 1; min-width: 180px; background: #141620; border: 1px solid rgba(255,255,255,0.07); border-radius: 16px; padding: 24px 22px; position: relative; }
.kpi-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: #63d4ff; opacity: 0.7; }
.kpi-label { font-size: 11px; text-transform: uppercase; color: #6b7898; margin-bottom: 12px; }
.kpi-value { font-size: 28px; font-weight: 700; color: #f0f4ff; margin-bottom: 8px; }
.kpi-sub { font-size: 12px; color: #6b7898; }
.kpi-icon { position: absolute; top: 20px; right: 20px; font-size: 28px; opacity: 0.15; }

/* Section */
.section-header { display: flex; align-items: center; justify-content: space-between; margin: 32px 0 16px 0; border-bottom: 1px solid rgba(255,255,255,0.07); padding-bottom: 10px; }
.section-header h2 { font-size: 18px !important; font-weight: 700 !important; color: #f0f4ff !important; margin: 0 !important; }
.section-tag { font-size: 11px; color: #6b7898; border: 1px solid rgba(255,255,255,0.07); padding: 2px 8px; border-radius: 4px; }

/* Insight Cards */
.insight-card { background: #141620; border: 1px solid rgba(255,255,255,0.07); border-radius: 16px; padding: 18px 20px; margin-bottom: 15px; border-left: 3px solid #63d4ff; }
.insight-title { font-size: 12px; font-weight: 700; text-transform: uppercase; color: #6b7898; margin-bottom: 8px; }
.insight-value { font-size: 24px; font-weight: 700; color: #63d4ff; margin: 10px 0; }
.insight-body { font-size: 13px; color: #6b7898; }
.highlight-positive { color: #34d399 !important; }
.highlight-negative { color: #f87171 !important; }

/* Status */
.status-bar { background: rgba(52,211,153,0.07); border: 1px solid rgba(52,211,153,0.2); padding: 10px 16px; border-radius: 10px; margin-bottom: 20px; color: #34d399; }
.filter-info { background: rgba(251,191,36,0.07); border: 1px solid rgba(251,191,36,0.2); padding: 10px 16px; border-radius: 10px; margin-bottom: 20px; color: #fbbf24; }

/* Info Cards */
.info-card { background: #141620; border: 1px solid rgba(255,255,255,0.07); border-radius: 16px; padding: 20px; margin-bottom: 16px; border-top: 3px solid #63d4ff; }
.info-icon { font-size: 32px; margin-bottom: 12px; }
.info-title { font-size: 14px; font-weight: 700; color: #f0f4ff; margin-bottom: 8px; }
.info-text { font-size: 13px; color: #6b7898; line-height: 1.5; }

/* Trust Badge */
.trust-badge { display: inline-flex; align-items: center; gap: 8px; background: rgba(52,211,153,0.1); border: 1px solid rgba(52,211,153,0.2); padding: 6px 12px; border-radius: 20px; font-size: 12px; color: #34d399; margin-right: 10px; }

/* Footer */
.page-footer { text-align: center; padding: 30px 0 20px; margin-top: 40px; border-top: 1px solid rgba(255,255,255,0.07); color: #3d4560; font-size: 12px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] { background: #141620; border-radius: 10px; padding: 8px 20px; color: #6b7898; border: 1px solid rgba(255,255,255,0.07); }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #63d4ff, #818cf8); color: #07080d; }

/* Botões */
.stDownloadButton button { width: 100% !important; background: linear-gradient(135deg, #63d4ff, #818cf8) !important; color: #07080d !important; font-weight: 700 !important; border: none !important; border-radius: 10px !important; padding: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CONSTANTES
# ============================================================
REGIOES_MAP = {
    'SE': 'Sudeste', 'SU': 'Sul', 'NE': 'Nordeste',
    'CO': 'Centro-Oeste', 'N': 'Norte', 'NO': 'Norte',
    'EX': 'Exterior', 'NI': 'Não Informado'
}

# ============================================================
# FUNÇÕES
# ============================================================
def fmt_brl(valor):
    if pd.isna(valor) or valor == 0:
        return "R$ 0"
    if abs(valor) >= 1_000_000_000:
        return f"R$ {valor/1_000_000_000:.1f}B".replace(".", ",")
    if abs(valor) >= 1_000_000:
        return f"R$ {valor/1_000_000:.1f}M".replace(".", ",")
    return f"R$ {valor:,.0f}".replace(",", ".")

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
            
            if 'regiao' in df.columns:
                df['regiao_nome'] = df['regiao'].map(REGIOES_MAP).fillna(df['regiao'])
            
            return df
        except:
            continue
    return None

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:20px;">
        <span style="font-size:28px;">🔬</span>
        <span style="font-weight:800; font-size:20px; color:#63d4ff;">CNPq Analytics</span>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("📄 Upload do CSV", type=["csv"])
    
    st.markdown("---")
    st.markdown("### 📊 Dataset")
    st.markdown("- **213.735** registros\n- **26** colunas\n- **R$ 1B+** investimento\n- **2014-2027** período")
    
    st.markdown("---")
    st.markdown("📥 **Baixar CSV original:**")
    st.markdown("[Google Drive](https://drive.google.com/uc?export=download&id=1UXxWqTc6u8_RID_5BbpUI7JLwmgT01ub)")

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="page-header">
    <div class="page-header-left">
        <h1>🔬 CNPq Analytics</h1>
        <p>Análise estratégica de investimentos em pesquisa e desenvolvimento no Brasil</p>
    </div>
    <div class="page-header-right">
        <span class="badge">Dashboard</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# MAIN
# ============================================================
if uploaded_file is not None:
    
    with st.spinner("🔄 Processando 110MB de dados... Isso leva ~30 segundos"):
        df = carregar_dados(uploaded_file)
    
    if df is not None and len(df) > 0:
        
        # FILTROS
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
            areas_sel = st.sidebar.multiselect("🧬 Grande Área", areas, default=areas[:6] if len(areas) > 6 else areas)
            if areas_sel:
                df_filtrado = df_filtrado[df_filtrado['grande_area'].isin(areas_sel)]
        
        # STATUS
        total_r = df_filtrado.shape[0]
        total_o = df.shape[0]
        pct = 100 * total_r / total_o if total_o > 0 else 0
        
        if total_r < total_o:
            st.markdown(f'<div class="filter-info">🔍 Filtros ativos — {total_r:,} de {total_o:,} registros ({pct:.1f}%)</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-bar">✅ {total_r:,} registros carregados</div>', unsafe_allow_html=True)
        
        # ===== KPIs =====
        total_val = df_filtrado['valor_pago'].sum()
        media_val = df_filtrado['valor_pago'].mean()
        n_pesq = df_filtrado['beneficiario'].nunique() if 'beneficiario' in df_filtrado.columns else 0
        n_inst = df_filtrado['instituicao_destino'].nunique() if 'instituicao_destino' in df_filtrado.columns else 0
        n_bolsas = df_filtrado.shape[0]
        
        st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">💰</div>
                <div class="kpi-label">INVESTIMENTO TOTAL</div>
                <div class="kpi-value">{fmt_brl(total_val)}</div>
                <div class="kpi-sub">consolidado</div>
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
                <div class="kpi-icon">🎫</div>
                <div class="kpi-label">BOLSAS</div>
                <div class="kpi-value">{fmt_num(n_bolsas)}</div>
                <div class="kpi-sub">registros</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ===== TABS =====
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Área", "🗺️ Região", "📈 Evolução", "🏆 Rankings"])
        
        with tab1:
            if 'grande_area' in df_filtrado.columns:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    area_data = df_filtrado.groupby('grande_area')['valor_pago'].sum().sort_values(ascending=False).head(10).reset_index()
                    area_data.columns = ['Área', 'Valor']
                    
                    fig = px.bar(area_data, x='Valor', y='Área', orientation='h', color='Valor', 
                                color_continuous_scale=['#6B7898', '#63d4ff'], text='Valor')
                    fig.update_layout(template="plotly_dark", height=500, paper_bgcolor="#0e1018", plot_bgcolor="#0e1018")
                    fig.update_traces(texttemplate='R$ %{x:,.0f}', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    area_show = area_data.copy()
                    area_show['Valor'] = area_show['Valor'].apply(fmt_brl)
                    st.dataframe(area_show[['Área', 'Valor']], use_container_width=True, hide_index=True)
        
        with tab2:
            if 'regiao_nome' in df_filtrado.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    reg_data = df_filtrado.groupby('regiao_nome')['valor_pago'].sum().reset_index()
                    reg_data.columns = ['Região', 'Valor']
                    
                    fig2 = px.bar(reg_data, x='Região', y='Valor', color='Valor', color_continuous_scale='Blues', text='Valor')
                    fig2.update_layout(template="plotly_dark", height=450, paper_bgcolor="#0e1018", plot_bgcolor="#0e1018")
                    fig2.update_traces(texttemplate='R$ %{y:,.0f}', textposition='outside')
                    st.plotly_chart(fig2, use_container_width=True)
                    
                    st.markdown("##### 💰 Ticket Médio por Região")
                    ticket_reg = df_filtrado.groupby('regiao_nome')['valor_pago'].mean().sort_values(ascending=False).reset_index()
                    ticket_reg.columns = ['Região', 'Ticket Médio']
                    ticket_reg['Ticket Médio'] = ticket_reg['Ticket Médio'].apply(fmt_brl)
                    st.dataframe(ticket_reg, use_container_width=True, hide_index=True)
                
                with col2:
                    fig3 = px.pie(reg_data, values='Valor', names='Região', hole=0.35,
                                 color_discrete_sequence=['#63d4ff', '#818cf8', '#34d399', '#fbbf24', '#f87171'])
                    fig3.update_layout(template="plotly_dark", height=450, paper_bgcolor="#0e1018", plot_bgcolor="#0e1018")
                    fig3.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig3, use_container_width=True)
                    
                    if 'Sudeste' in reg_data['Região'].values and 'Norte' in reg_data['Região'].values:
                        sudeste_val = reg_data[reg_data['Região'] == 'Sudeste']['Valor'].values[0]
                        norte_val = reg_data[reg_data['Região'] == 'Norte']['Valor'].values[0]
                        diferenca = sudeste_val / norte_val if norte_val > 0 else 0
                        st.markdown(f"""
                        <div class="insight-card" style="margin-top:20px;">
                            <div class="insight-title">⚖️ SUDESTE VS NORTE</div>
                            <div class="insight-value">{diferenca:.1f}x</div>
                            <div class="insight-body">Sudeste recebe <strong>{diferenca:.1f}x mais</strong> investimento</div>
                        </div>
                        """, unsafe_allow_html=True)
        
        with tab3:
            if 'ano' in df_filtrado.columns:
                inv_ano = df_filtrado.groupby('ano')['valor_pago'].sum().reset_index()
                inv_ano = inv_ano.dropna()
                
                if len(inv_ano) > 1:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig4 = px.area(inv_ano, x='ano', y='valor_pago', markers=True)
                        fig4.update_layout(template="plotly_dark", height=400, paper_bgcolor="#0e1018", plot_bgcolor="#0e1018")
                        fig4.update_traces(line=dict(width=2, color='#63d4ff'), fillcolor='rgba(99,212,255,0.1)')
                        st.plotly_chart(fig4, use_container_width=True)
                    
                    with col2:
                        fig5 = px.bar(inv_ano, x='ano', y='valor_pago', color='valor_pago', color_continuous_scale='Greens')
                        fig5.update_layout(template="plotly_dark", height=400, paper_bgcolor="#0e1018", plot_bgcolor="#0e1018")
                        st.plotly_chart(fig5, use_container_width=True)
                    
                    var = ((inv_ano['valor_pago'].iloc[-1] - inv_ano['valor_pago'].iloc[-2]) / inv_ano['valor_pago'].iloc[-2] * 100)
                    st.metric("📈 Variação Último Ano", f"{var:+.1f}%", delta_color="normal" if var > 0 else "inverse")
        
        with tab4:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🏆 Top 10 Pesquisadores")
                if 'beneficiario' in df_filtrado.columns:
                    top_pesq = df_filtrado.groupby('beneficiario')['valor_pago'].sum().sort_values(ascending=False).head(10).reset_index()
                    top_pesq.columns = ['Pesquisador', 'Total']
                    top_pesq['Total'] = top_pesq['Total'].apply(fmt_brl)
                    st.dataframe(top_pesq, use_container_width=True, hide_index=True)
                else:
                    st.info("Dados não disponíveis")
            
            with col2:
                st.markdown("#### 🏛️ Top 10 Instituições")
                if 'instituicao_destino' in df_filtrado.columns:
                    top_inst = df_filtrado.groupby('instituicao_destino')['valor_pago'].sum().sort_values(ascending=False).head(10).reset_index()
                    top_inst.columns = ['Instituição', 'Total']
                    top_inst['Total'] = top_inst['Total'].apply(fmt_brl)
                    st.dataframe(top_inst, use_container_width=True, hide_index=True)
                else:
                    st.info("Dados não disponíveis")
            
            st.markdown("#### 🎓 Top 10 Modalidades")
            if 'modalidade' in df_filtrado.columns:
                top_mod = df_filtrado['modalidade'].value_counts().head(10).reset_index()
                top_mod.columns = ['Modalidade', 'Quantidade']
                st.dataframe(top_mod, use_container_width=True, hide_index=True)
        
        # ===== INSIGHTS =====
        st.markdown("""
        <div class="section-header">
            <h2>🔍 Insights Estratégicos</h2>
            <span class="section-tag">Análise</span>
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
                        <div class="insight-title">📍 CONCENTRAÇÃO REGIONAL</div>
                        <div class="insight-value">{top_reg}</div>
                        <div class="insight-body"><strong>{pct:.1f}%</strong> do investimento</div>
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
                        <div class="insight-title">🧬 ÁREA LÍDER</div>
                        <div class="insight-value">{top_area}</div>
                        <div class="insight-body"><strong>{pct:.1f}%</strong> dos recursos</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col3:
            if 'ano' in df_filtrado.columns and len(inv_ano) >= 2:
                var = ((inv_ano['valor_pago'].iloc[-1] - inv_ano['valor_pago'].iloc[-2]) / inv_ano['valor_pago'].iloc[-2] * 100)
                st.markdown(f"""
                <div class="insight-card">
                    <div class="insight-title">📈 VARIAÇÃO ANUAL</div>
                    <div class="insight-value">{var:+.1f}%</div>
                    <div class="insight-body">de {int(inv_ano['ano'].iloc[-2])} para {int(inv_ano['ano'].iloc[-1])}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # ===== EXPORTAÇÃO =====
        st.markdown("""
        <div class="section-header">
            <h2>📥 Exportar</h2>
            <span class="section-tag">Download</span>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv_data = df_filtrado.to_csv(index=False, sep=';')
            st.download_button("📄 CSV", csv_data, f"cnpq_dados_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        
        with col2:
            relatorio = f"""RELATÓRIO CNPq - {datetime.now().strftime('%d/%m/%Y %H:%M')}
Investimento: {fmt_brl(total_val)}
Pesquisadores: {fmt_num(n_pesq)}
Instituições: {fmt_num(n_inst)}
Bolsas: {fmt_num(n_bolsas)}"""
            st.download_button("📝 Relatório", relatorio, f"relatorio_{datetime.now().strftime('%Y%m%d')}.txt", "text/plain")
        
        with st.expander("🗂️ Dados Detalhados"):
            cols_show = [c for c in df_filtrado.columns if c not in ['ano']][:10]
            st.dataframe(df_filtrado[cols_show].head(500), use_container_width=True, height=400)
        
        st.markdown(f"""
        <div class="page-footer">
            🔬 CNPq Analytics · Streamlit & Plotly · Fonte: CNPq/Governo Federal<br>
            📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.error("❌ Erro ao carregar o arquivo.")

else:
    # ============================================================
    # TELA INICIAL COM INFORMAÇÕES DA FONTE
    # ============================================================
    
    # Badges de confiabilidade
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <span class="trust-badge">✅ Fonte Oficial</span>
        <span class="trust-badge">🔓 Dados Abertos</span>
        <span class="trust-badge">📊 CGU / MDS</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero
    st.markdown("""
    <div class="info-card">
        <div class="info-icon">🔬</div>
        <div class="info-title">Projeto: Análise Estratégica de Desembolso Federal</div>
        <div class="info-text">
            Este dashboard analisa os pagamentos realizados pelo CNPq (Conselho Nacional de Desenvolvimento Científico e Tecnológico) 
            para beneficiários de bolsas de pesquisa em todo território nacional.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Fonte dos dados
    st.markdown("""
    <div class="section-header">
        <h2>📋 Fonte dos Dados</h2>
        <span class="section-tag">Oficial</span>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card" style="border-top-color: #34d399;">
            <div class="info-icon">🏛️</div>
            <div class="info-title">Origem dos Dados</div>
            <div class="info-text">
                Os dados utilizados nesta análise foram extraídos do <strong>Portal Brasileiro de Dados Abertos</strong>, 
                mantido pela <strong>Controladoria-Geral da União (CGU)</strong> e pelo 
                <strong>Ministério do Desenvolvimento e Assistência Social, Família e Combate à Fome (MDS)</strong>.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card" style="border-top-color: #fbbf24;">
            <div class="info-icon">🔐</div>
            <div class="info-title">Confiabilidade</div>
            <div class="info-text">
                ✅ <strong>Fonte oficial do governo federal</strong><br>
                ✅ <strong>Dados públicos e auditáveis</strong><br>
                ✅ <strong>Atualizados em 27/03/2026</strong><br>
                ✅ <strong>Permite controle social e análise técnica</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Metodologia
    st.markdown("""
    <div class="section-header">
        <h2>🔧 Metodologia</h2>
        <span class="section-tag">Processo</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
        <div class="info-icon">⚙️</div>
        <div class="info-title">Extração e Tratamento</div>
        <div class="info-text">
            <strong>Extação:</strong> Ingestão de dataset bruto (CSV — 110MB) via PostgreSQL com detecção automática de encoding.<br>
            <strong>Período Analisado:</strong> Dados de bolsas de pesquisa entre 2014 e 2027.<br>
            <strong>Filtros Aplicados:</strong> Normalização de tipos de dados, padronização de valores monetários e saneamento de registros.<br>
            <strong>Validação:</strong> Consistência cruzada com fontes oficiais do CNPq.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Link oficial
    st.markdown("""
    <div class="section-header">
        <h2>🔗 Links Oficiais</h2>
        <span class="section-tag">Referência</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card" style="text-align: center;">
        <div class="info-icon">🌐</div>
        <div class="info-title">Portal de Dados Abertos</div>
        <div class="info-text">
            <a href="https://dados.gov.br" target="_blank" style="color:#63d4ff;">dados.gov.br</a> — 
            Bolsas e Auxílios Pagos — Controladoria-Geral da União (CGU)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload area
    st.markdown("""
    <div style="background:#141620; border:2px dashed rgba(99,212,255,0.3); border-radius:20px; padding:40px; text-align: center; margin: 20px 0;">
        <div style="font-size:48px; margin-bottom:16px;">📁</div>
        <div style="font-size:18px; font-weight:600; margin-bottom:8px;">Upload do CSV</div>
        <div style="font-size:13px; color:#6b7898;">Clique no menu lateral → "Browse files" para carregar o arquivo</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Resumo dos dados
    st.markdown("""
    <div class="section-header">
        <h2>📊 O que você vai encontrar</h2>
        <span class="section-tag">Preview</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 30px;">
        <div style="flex:1; min-width:180px; background:#141620; border-radius:16px; padding:20px; text-align:center;">
            <div style="font-size:32px; font-weight:700; color:#63d4ff;">R$ 1,02B</div>
            <div style="font-size:12px; color:#6b7898; margin-top:8px;">Investimento Total</div>
        </div>
        <div style="flex:1; min-width:180px; background:#141620; border-radius:16px; padding:20px; text-align:center;">
            <div style="font-size:32px; font-weight:700; color:#63d4ff;">88.079</div>
            <div style="font-size:12px; color:#6b7898; margin-top:8px;">Pesquisadores</div>
        </div>
        <div style="flex:1; min-width:180px; background:#141620; border-radius:16px; padding:20px; text-align:center;">
            <div style="font-size:32px; font-weight:700; color:#63d4ff;">4.281</div>
            <div style="font-size:12px; color:#6b7898; margin-top:8px;">Instituições</div>
        </div>
        <div style="flex:1; min-width:180px; background:#141620; border-radius:16px; padding:20px; text-align:center;">
            <div style="font-size:32px; font-weight:700; color:#63d4ff;">213.735</div>
            <div style="font-size:12px; color:#6b7898; margin-top:8px;">Bolsas</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="page-footer">
        🔬 CNPq Analytics · Dashboard para portfólio de Analista de Dados<br>
        Fonte: Portal Brasileiro de Dados Abertos (CGU/MDS)
    </div>
    """, unsafe_allow_html=True)
