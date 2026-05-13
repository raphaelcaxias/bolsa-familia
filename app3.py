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
    layout="wide"
)

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
.stApp { background: #0f172a; }
.metric-card {
    background: #1e293b;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    border: 1px solid #334155;
}
.metric-icon { font-size: 32px; margin-bottom: 10px; }
.metric-title { color: #94a3b8; font-size: 12px; text-transform: uppercase; }
.metric-value { color: white; font-size: 28px; font-weight: bold; margin-top: 10px; }
.insight-card {
    background: #1e293b;
    border-left: 4px solid #3b82f6;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 15px;
}
.insight-card h4 { color: white; margin-bottom: 8px; }
.insight-card p { color: #94a3b8; margin: 0; }
.section-header { margin: 30px 0 15px 0; }
.section-header h2 { color: white; font-size: 20px; }
.status-bar {
    background: #1e293b;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 20px;
    color: #10b981;
}
.filter-info {
    background: #1e293b;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 20px;
    color: #fbbf24;
}
.page-footer {
    text-align: center;
    padding: 20px;
    color: #64748b;
    margin-top: 40px;
    border-top: 1px solid #334155;
}
section[data-testid="stSidebar"] { background: #0f172a; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNÇÕES
# ============================================================
def fmt_brl(valor):
    if pd.isna(valor) or valor == 0:
        return "R$ 0,00"
    if abs(valor) >= 1_000_000_000:
        return f"R$ {valor/1_000_000_000:.2f}B".replace(".", ",")
    if abs(valor) >= 1_000_000:
        return f"R$ {valor/1_000_000:.1f}M".replace(".", ",")
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_num(n):
    if pd.isna(n):
        return "0"
    return f"{int(n):,}".replace(",", ".")

@st.cache_data
def carregar_dados(uploaded_file):
    # Tenta diferentes encodings
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
                regioes_map = {'SE': 'Sudeste', 'SU': 'Sul', 'NE': 'Nordeste', 'CO': 'Centro-Oeste', 'N': 'Norte', 'NO': 'Norte', 'EX': 'Exterior', 'NI': 'Não Informado'}
                df['regiao_nome'] = df['regiao'].map(regioes_map).fillna(df['regiao'])
            
            return df
        except:
            continue
    return None

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## 🔬 CNPq Analytics")
    st.markdown("---")
    uploaded_file = st.file_uploader("📤 Envie o arquivo CSV", type=["csv"])
    st.markdown("---")
    st.markdown("📥 **Baixar CSV original:**")
    st.markdown("[Clique aqui](https://drive.google.com/uc?export=download&id=1UXxWqTc6u8_RID_5BbpUI7JLwmgT01ub)")

# ============================================================
# MAIN
# ============================================================
st.markdown("## 📊 CNPq Analytics - Bolsas de Pesquisa")
st.markdown("Análise de investimentos em pesquisa e desenvolvimento no Brasil")

if uploaded_file is not None:
    with st.spinner("Carregando dados..."):
        df = carregar_dados(uploaded_file)
    
    if df is not None and len(df) > 0:
        st.success(f"✅ {len(df):,} registros carregados")
        
        # Filtros
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎯 Filtros")
        
        df_filtrado = df.copy()
        
        if 'regiao_nome' in df.columns:
            regioes = sorted(df['regiao_nome'].dropna().unique())
            if regioes:
                reg_sel = st.sidebar.multiselect("Região", regioes, default=regioes)
                if reg_sel:
                    df_filtrado = df_filtrado[df_filtrado['regiao_nome'].isin(reg_sel)]
        
        if 'ano' in df.columns:
            anos = sorted(df['ano'].dropna().unique())
            if len(anos) > 1:
                ano_min, ano_max = int(min(anos)), int(max(anos))
                ano_sel = st.sidebar.slider("Período", ano_min, ano_max, (ano_min, ano_max))
                df_filtrado = df_filtrado[(df_filtrado['ano'] >= ano_sel[0]) & (df_filtrado['ano'] <= ano_sel[1])]
        
        if 'grande_area' in df.columns:
            areas = sorted(df['grande_area'].dropna().unique())
            if areas:
                areas_sel = st.sidebar.multiselect("Grande Área", areas, default=areas[:5] if len(areas) > 5 else areas)
                if areas_sel:
                    df_filtrado = df_filtrado[df_filtrado['grande_area'].isin(areas_sel)]
        
        # Status
        if df_filtrado.shape[0] < df.shape[0]:
            st.markdown(f'<div class="filter-info">🔍 {df_filtrado.shape[0]:,} de {df.shape[0]:,} registros</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-bar">✓ {df_filtrado.shape[0]:,} registros</div>', unsafe_allow_html=True)
        
        # KPIs
        total_val = df_filtrado['valor_pago'].sum()
        n_pesq = df_filtrado['beneficiario'].nunique() if 'beneficiario' in df_filtrado.columns else 0
        n_inst = df_filtrado['instituicao_destino'].nunique() if 'instituicao_destino' in df_filtrado.columns else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">💰</div>
                <div class="metric-title">Investimento Total</div>
                <div class="metric-value">{fmt_brl(total_val)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">👥</div>
                <div class="metric-title">Pesquisadores</div>
                <div class="metric-value">{fmt_num(n_pesq)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">🏫</div>
                <div class="metric-title">Instituições</div>
                <div class="metric-value">{fmt_num(n_inst)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📊</div>
                <div class="metric-title">Ticket Médio</div>
                <div class="metric-value">{fmt_brl(df_filtrado['valor_pago'].mean())}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # GRÁFICO 1: Áreas
        if 'grande_area' in df_filtrado.columns:
            st.markdown('<div class="section-header"><h2>📌 Investimento por Grande Área</h2></div>', unsafe_allow_html=True)
            
            area_data = df_filtrado.groupby('grande_area')['valor_pago'].sum().sort_values(ascending=False).head(10).reset_index()
            area_data.columns = ['Área', 'Valor']
            
            fig = px.bar(area_data, x='Área', y='Valor', color='Valor', color_continuous_scale=['#3b82f6', '#8b5cf6'])
            fig.update_layout(template="plotly_dark", height=450, paper_bgcolor="#0f172a", plot_bgcolor="#0f172a")
            fig.update_traces(texttemplate='R$ %{y:,.0f}', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        
        # GRÁFICO 2: Regiões
        if 'regiao_nome' in df_filtrado.columns:
            st.markdown('<div class="section-header"><h2>🗺️ Distribuição Regional</h2></div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                reg_data = df_filtrado.groupby('regiao_nome')['valor_pago'].sum().reset_index()
                reg_data.columns = ['Região', 'Valor']
                
                fig2 = px.bar(reg_data, x='Região', y='Valor', color='Valor', color_continuous_scale='Blues')
                fig2.update_layout(template="plotly_dark", height=400, paper_bgcolor="#0f172a", plot_bgcolor="#0f172a")
                st.plotly_chart(fig2, use_container_width=True)
            
            with col2:
                fig3 = px.pie(reg_data, values='Valor', names='Região', hole=0.4)
                fig3.update_layout(template="plotly_dark", height=400, paper_bgcolor="#0f172a", plot_bgcolor="#0f172a")
                fig3.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig3, use_container_width=True)
        
        # GRÁFICO 3: Evolução
        if 'ano' in df_filtrado.columns:
            inv_ano = df_filtrado.groupby('ano')['valor_pago'].sum().reset_index()
            inv_ano = inv_ano.dropna()
            
            if len(inv_ano) > 1:
                st.markdown('<div class="section-header"><h2>📅 Evolução Temporal</h2></div>', unsafe_allow_html=True)
                
                fig4 = px.line(inv_ano, x='ano', y='valor_pago', markers=True)
                fig4.update_layout(template="plotly_dark", height=450, paper_bgcolor="#0f172a", plot_bgcolor="#0f172a")
                fig4.update_traces(line=dict(width=3, color='#3b82f6'), marker=dict(size=8))
                st.plotly_chart(fig4, use_container_width=True)
        
        # INSIGHTS
        st.markdown('<div class="section-header"><h2>🔍 Insights</h2></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
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
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            if 'grande_area' in df_filtrado.columns:
                top_area = df_filtrado.groupby('grande_area')['valor_pago'].sum().idxmax()
                pct_area = 100 * df_filtrado.groupby('grande_area')['valor_pago'].sum().max() / df_filtrado['valor_pago'].sum()
                st.markdown(f"""
                <div class="insight-card">
                    <h4>🧬 Área Líder</h4>
                    <p>A área <b>{top_area}</b> lidera com <b>{pct_area:.1f}%</b> dos recursos.</p>
                </div>
                """, unsafe_allow_html=True)
        
        # EXPORTAÇÃO
        st.markdown('<div class="section-header"><h2>📥 Exportar Dados</h2></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv_data = df_filtrado.to_csv(index=False, sep=';')
            st.download_button("📄 CSV", csv_data, f"dados_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        
        with col2:
            st.info("Excel disponível na versão desktop")
            st.download_button("📊 Excel", csv_data, f"dados.xlsx", disabled=True)
        
        with col3:
            relatorio = f"Total Investido: {fmt_brl(total_val)}\nPesquisadores: {fmt_num(n_pesq)}\nData: {datetime.now().strftime('%d/%m/%Y')}"
            st.download_button("📝 Relatório", relatorio, f"relatorio_{datetime.now().strftime('%Y%m%d')}.txt", "text/plain")
        
        # RODAPÉ
        st.markdown('<div class="page-footer">CNPq Analytics · Streamlit · Plotly · Python</div>', unsafe_allow_html=True)
    
    else:
        st.error("❌ Erro ao carregar o arquivo. Verifique o formato.")
else:
    st.info("👈 **Faça upload do CSV no menu lateral**")

# ============================================================
# FIM
# ============================================================
