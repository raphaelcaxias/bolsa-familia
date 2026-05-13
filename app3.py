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
# CORES INSTITUCIONAIS
# ============================================================
COR_PRIMARIA = "#003087"      # Azul
COR_SECUNDARIA = "#008000"    # Verde
COR_DESTAQUE = "#FFCC00"      # Amarelo
COR_FUNDO = "#F5F7FA"
COR_TEXTO = "#1A2B4C"

# ============================================================
# CSS
# ============================================================
st.markdown(f"""
<style>
.stApp {{ background: {COR_FUNDO} !important; }}
html, body, .stApp {{ color: {COR_TEXTO} !important; font-family: 'Inter', sans-serif !important; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding: 2rem 2.5rem !important; max-width: 1400px !important; }}

/* Header */
.page-header {{
    background: linear-gradient(135deg, {COR_PRIMARIA}, {COR_SECUNDARIA});
    padding: 1.5rem 2rem;
    border-radius: 16px;
    margin-bottom: 28px;
}}
.page-header h1 {{
    font-size: 28px !important;
    font-weight: 700 !important;
    color: white !important;
    margin: 0 0 8px 0 !important;
}}
.page-header p {{
    color: rgba(255,255,255,0.9);
    font-size: 14px;
    margin: 0;
}}
.update-badge {{
    background: {COR_DESTAQUE};
    color: {COR_PRIMARIA};
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
    margin-top: 12px;
}}

/* KPI Cards */
.kpi-grid {{ display: flex; gap: 20px; margin-bottom: 32px; flex-wrap: wrap; }}
.kpi-card {{
    flex: 1; min-width: 180px; background: white; border-radius: 16px;
    padding: 24px 20px; text-align: center; border: 1px solid #E8ECF0;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    border-top: 4px solid {COR_PRIMARIA};
}}
.kpi-label {{ font-size: 12px; text-transform: uppercase; color: #6B7A8F; margin-bottom: 8px; font-weight: 600; }}
.kpi-value {{ font-size: 32px; font-weight: 700; color: {COR_TEXTO}; margin: 8px 0; }}
.kpi-sub {{ font-size: 11px; color: #6B7A8F; }}

/* Insight */
.insight-card {{
    background: linear-gradient(135deg, #E8F4FD, #FFFFFF);
    border-left: 4px solid {COR_DESTAQUE};
    padding: 16px 20px;
    border-radius: 12px;
    margin-bottom: 20px;
}}
.insight-title {{ font-size: 13px; font-weight: 700; color: {COR_PRIMARIA}; margin-bottom: 8px; }}
.insight-text {{ font-size: 14px; color: {COR_TEXTO}; }}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
.stTabs [data-baseweb="tab"] {{
    background: white; border-radius: 12px; padding: 8px 24px;
    color: #6B7A8F; border: 1px solid #E8ECF0;
}}
.stTabs [aria-selected="true"] {{ background: {COR_PRIMARIA}; color: white; border: none; }}

/* Botões */
.stDownloadButton button {{
    background: {COR_PRIMARIA} !important; color: white !important;
    border-radius: 30px !important; padding: 10px 24px !important;
    font-weight: 600 !important; border: none !important;
}}

/* Footer */
.footer {{
    text-align: center; padding: 30px 0 20px; margin-top: 40px;
    border-top: 1px solid #E8ECF0; color: #6B7A8F; font-size: 12px;
}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
st.markdown(f"""
<div class="page-header">
    <h1>🔬 CNPq Analytics</h1>
    <p>Análise estratégica de investimentos em pesquisa e desenvolvimento no Brasil</p>
    <div class="update-badge">📅 Última atualização: 27/03/2026</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### 🎯 Filtros")
    uploaded_file = st.file_uploader("📄 Upload do CSV", type=["csv"])
    
    st.markdown("---")
    st.markdown("### 📊 Dataset")
    st.markdown("""
    - **213.735** registros
    - **26** colunas
    - **R$ 1B+** investimento
    - **2014-2027** período
    """)
    
    st.markdown("---")
    st.markdown("📥 **Baixar CSV original:**")
    st.markdown("[Google Drive](https://drive.google.com/uc?export=download&id=1UXxWqTc6u8_RID_5BbpUI7JLwmgT01ub)")

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
            
            regioes_map = {'SE': 'Sudeste', 'SU': 'Sul', 'NE': 'Nordeste', 'CO': 'Centro-Oeste', 'N': 'Norte', 'NO': 'Norte', 'EX': 'Exterior', 'NI': 'Não Informado'}
            if 'regiao' in df.columns:
                df['regiao_nome'] = df['regiao'].map(regioes_map).fillna(df['regiao'])
            
            return df
        except:
            continue
    return None

# ============================================================
# MAIN
# ============================================================
if uploaded_file is not None:
    with st.spinner("🔄 Processando 110MB de dados... Isso leva ~30 segundos"):
        df = carregar_dados(uploaded_file)
    
    if df is not None and len(df) > 0:
        st.success(f"✅ {len(df):,} registros carregados com sucesso!")
        
        # FILTROS
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔍 Filtros Avançados")
        
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
        
        # KPIs
        total_val = df_filtrado['valor_pago'].sum()
        media_val = df_filtrado['valor_pago'].mean()
        n_pesq = df_filtrado['beneficiario'].nunique() if 'beneficiario' in df_filtrado.columns else 0
        n_inst = df_filtrado['instituicao_destino'].nunique() if 'instituicao_destino' in df_filtrado.columns else 0
        n_bolsas = df_filtrado.shape[0]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 INVESTIMENTO TOTAL", fmt_brl(total_val), help="Valor total pago em bolsas")
        with col2:
            st.metric("👥 PESQUISADORES", fmt_num(n_pesq), help="Número de beneficiários únicos")
        with col3:
            st.metric("🏛️ INSTITUIÇÕES", fmt_num(n_inst), help="Instituições de destino")
        with col4:
            st.metric("🎫 TOTAL DE BOLSAS", fmt_num(n_bolsas), help="Número total de registros")
        
        # INSIGHTS
        insights = []
        if 'regiao_nome' in df_filtrado.columns:
            top_reg = df_filtrado.groupby('regiao_nome')['valor_pago'].sum().idxmax()
            insights.append(f"📍 <strong>{top_reg}</strong> é a região com maior investimento")
        
        if 'grande_area' in df_filtrado.columns:
            top_area = df_filtrado.groupby('grande_area')['valor_pago'].sum().idxmax()
            insights.append(f"🧬 <strong>{top_area}</strong> lidera o investimento entre as áreas")
        
        if 'ano' in df_filtrado.columns:
            anos_disp = sorted(df_filtrado['ano'].dropna().unique())
            if len(anos_disp) >= 2:
                inv_ano = df_filtrado.groupby('ano')['valor_pago'].sum()
                var = ((inv_ano.iloc[-1] - inv_ano.iloc[-2]) / inv_ano.iloc[-2] * 100)
                sinal = "📈 crescimento" if var > 0 else "📉 queda"
                insights.append(f"📊 {sinal} de {abs(var):.1f}% no último ano")
        
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">🔍 INSIGHTS AUTOMÁTICOS</div>
            <div class="insight-text">{" • ".join(insights)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # TABS
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Por Área", "🗺️ Por Região", "📈 Evolução", "🏆 Rankings"])
        
        with tab1:
            if 'grande_area' in df_filtrado.columns:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    area_data = df_filtrado.groupby('grande_area')['valor_pago'].sum().sort_values(ascending=False).head(10).reset_index()
                    area_data.columns = ['Área', 'Valor']
                    
                    # GRÁFICO MELHORADO
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=area_data['Valor'],
                        y=area_data['Área'],
                        orientation='h',
                        marker=dict(color=area_data['Valor'], colorscale='Blues', showscale=False),
                        text=area_data['Valor'].apply(lambda x: fmt_brl(x)),
                        textposition='outside',
                        hovertemplate='<b>%{y}</b><br>%{customdata}<extra></extra>',
                        customdata=area_data['Valor'].apply(lambda x: fmt_brl(x))
                    ))
                    fig.update_layout(
                        title="Top 10 Áreas do Conhecimento",
                        xaxis_title="Investimento (R$)",
                        height=500, margin=dict(l=20, r=20, t=50, b=20),
                        plot_bgcolor='white', paper_bgcolor='white',
                        font=dict(color='#1A2B4C')
                    )
                    fig.update_xaxis(gridcolor='#E8ECF0', tickformat=',.0f')
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
                    
                    fig2 = px.bar(reg_data, x='Região', y='Valor', color='Valor', 
                                 color_continuous_scale='Blues', text='Valor')
                    fig2.update_layout(template="plotly_white", height=450)
                    fig2.update_traces(texttemplate='R$ %{y:,.0f}', textposition='outside')
                    st.plotly_chart(fig2, use_container_width=True)
                    
                    st.markdown("##### 💰 Ticket Médio por Região")
                    ticket_reg = df_filtrado.groupby('regiao_nome')['valor_pago'].mean().sort_values(ascending=False).reset_index()
                    ticket_reg.columns = ['Região', 'Ticket Médio']
                    ticket_reg['Ticket Médio'] = ticket_reg['Ticket Médio'].apply(fmt_brl)
                    st.dataframe(ticket_reg, use_container_width=True, hide_index=True)
                
                with col2:
                    fig3 = px.pie(reg_data, values='Valor', names='Região', hole=0.35,
                                 color_discrete_sequence=[COR_PRIMARIA, '#7C3AED', COR_SECUNDARIA, COR_DESTAQUE, '#6B7A8F'])
                    fig3.update_layout(template="plotly_white", height=450)
                    fig3.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig3, use_container_width=True)
                    
                    if 'Sudeste' in reg_data['Região'].values and 'Norte' in reg_data['Região'].values:
                        sudeste_val = reg_data[reg_data['Região'] == 'Sudeste']['Valor'].values[0]
                        norte_val = reg_data[reg_data['Região'] == 'Norte']['Valor'].values[0]
                        diferenca = sudeste_val / norte_val if norte_val > 0 else 0
                        st.info(f"⚖️ **Sudeste** recebe **{diferenca:.1f}x mais** investimento que **Norte**")
        
        with tab3:
            if 'ano' in df_filtrado.columns:
                inv_ano = df_filtrado.groupby('ano')['valor_pago'].sum().reset_index()
                inv_ano = inv_ano.dropna()
                
                if len(inv_ano) > 1:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig4 = px.area(inv_ano, x='ano', y='valor_pago', markers=True)
                        fig4.update_layout(template="plotly_white", height=400)
                        fig4.update_traces(line=dict(width=2, color=COR_PRIMARIA), fillcolor='rgba(0,48,135,0.1)')
                        st.plotly_chart(fig4, use_container_width=True)
                    
                    with col2:
                        fig5 = px.bar(inv_ano, x='ano', y='valor_pago', color='valor_pago', color_continuous_scale='Greens')
                        fig5.update_layout(template="plotly_white", height=400)
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
                    
                    if 'instituicao_destino' in df_filtrado.columns:
                        inst_map = df_filtrado.groupby('beneficiario')['instituicao_destino'].first().to_dict()
                        top_pesq['Instituição'] = top_pesq['Pesquisador'].map(inst_map).fillna('-')
                    
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
        
        # EXPORTAÇÃO
        st.markdown("---")
        st.markdown("### 📥 Exportar Dados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv_data = df_filtrado.to_csv(index=False, sep=';')
            st.download_button("📄 Exportar CSV", csv_data, f"cnpq_dados_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        
        with col2:
            relatorio = f"""RELATÓRIO CNPq - {datetime.now().strftime('%d/%m/%Y %H:%M')}
Investimento: {fmt_brl(total_val)}
Pesquisadores: {fmt_num(n_pesq)}
Instituições: {fmt_num(n_inst)}
Bolsas: {fmt_num(n_bolsas)}"""
            st.download_button("📝 Exportar Relatório", relatorio, f"relatorio_{datetime.now().strftime('%Y%m%d')}.txt", "text/plain")
        
        with st.expander("🗂️ Visualizar Dados Detalhados"):
            cols_show = [c for c in df_filtrado.columns if c not in ['ano']][:10]
            st.dataframe(df_filtrado[cols_show].head(500), use_container_width=True, height=400)
        
        st.markdown(f"""
        <div class="footer">
            🔬 CNPq Analytics · Fonte: CNPq/Governo Federal<br>
            📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.error("❌ Erro ao carregar o arquivo.")
else:
    # TELA INICIAL
    st.info("👈 **Faça upload do arquivo CSV no menu lateral para começar**")
    
    st.markdown("""
    <div style="background: white; border-radius: 16px; padding: 24px; margin-bottom: 24px; border: 1px solid #E8ECF0;">
        <h3 style="color: #1A2B4C; margin-bottom: 12px;">📋 Sobre o Dashboard</h3>
        <p style="color: #6B7A8F;">Este dashboard analisa <strong>213.735 bolsas de pesquisa</strong> do CNPq, totalizando mais de <strong>R$ 1 bilhão</strong> em investimentos (2014-2027).</p>
        <p style="color: #6B7A8F; margin-top: 8px;">✅ <strong>Fonte oficial:</strong> Portal Brasileiro de Dados Abertos (CGU/MDS)</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="background: white; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #E8ECF0;">
            <div style="font-size: 28px; font-weight: 700; color: #003087;">213.735</div>
            <div style="font-size: 13px; color: #6B7A8F;">Bolsas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #E8ECF0;">
            <div style="font-size: 28px; font-weight: 700; color: #003087;">R$ 1,02B</div>
            <div style="font-size: 13px; color: #6B7A8F;">Investimento</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: white; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #E8ECF0;">
            <div style="font-size: 28px; font-weight: 700; color: #003087;">88.079</div>
            <div style="font-size: 13px; color: #6B7A8F;">Pesquisadores</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="background: white; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #E8ECF0;">
            <div style="font-size: 28px; font-weight: 700; color: #003087;">4.281</div>
            <div style="font-size: 13px; color: #6B7A8F;">Instituições</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #E8F4FD; border-radius: 12px; padding: 20px; margin-top: 20px;">
        <h4 style="color: #1A2B4C; margin-bottom: 12px;">🚀 Como usar</h4>
        <ol style="color: #6B7A8F; margin: 0; padding-left: 20px;">
            <li>Baixe o CSV original usando o link no menu lateral</li>
            <li>Clique em "Upload do CSV" e selecione o arquivo</li>
            <li>Explore filtros, gráficos e rankings</li>
            <li>Exporte os dados filtrados</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="footer">
        🔬 CNPq Analytics · Dashboard para portfólio<br>
        Fonte: Portal Brasileiro de Dados Abertos (CGU/MDS)
    </div>
    """, unsafe_allow_html=True)
