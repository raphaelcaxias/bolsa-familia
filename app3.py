import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="Dashboard CNPq - Bolsas de Pesquisa",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS PERSONALIZADO
# ============================================
st.markdown("""
<style>
    .big-font { font-size: 20px !important; font-weight: bold; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .insight-card {
        background-color: #f8f9fa;
        border-left: 4px solid #28a745;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .warning-card {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# DICIONÁRIOS PARA LEGENDA
# ============================================
REGIOES_MAP = {
    'SE': 'Sudeste', 'SU': 'Sul', 'NE': 'Nordeste',
    'CO': 'Centro-Oeste', 'N': 'Norte', 'NO': 'Norte',
    'EX': 'Exterior', 'NI': 'Não Informado'
}

MODALIDADES_MAP = {
    'IC': 'Iniciação Científica',
    'ICJ': 'Iniciação Científica Júnior',
    'PQ': 'Produtividade em Pesquisa',
    'GD': 'Doutorado',
    'GM': 'Mestrado',
    'IT': 'Iniciação Tecnológica',
    'DTI': 'Desenvolvimento Tecnológico Industrial',
    'ADC': 'Apoio à Difusão do Conhecimento',
    'ITI': 'Iniciação Tecnológica Industrial'
}

# ============================================
# FUNÇÕES AUXILIARES
# ============================================
def formatar_moeda(valor):
    if pd.isna(valor) or valor == 0:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def detectar_encoding_e_separador(uploaded_file):
    """Detecta encoding e separador automaticamente"""
    encodings = ['latin1', 'utf-8', 'ISO-8859-1', 'cp1252']
    separadores = [';', ',']
    
    for encoding in encodings:
        for sep in separadores:
            try:
                uploaded_file.seek(0)
                df_test = pd.read_csv(uploaded_file, delimiter=sep, encoding=encoding, nrows=5)
                if len(df_test.columns) > 1 and len(df_test.columns) < 50:
                    return encoding, sep
            except:
                continue
    return 'latin1', ';'

@st.cache_data
def carregar_dados(uploaded_file):
    """Carrega e limpa os dados"""
    encoding, sep = detectar_encoding_e_separador(uploaded_file)
    
    uploaded_file.seek(0)
    df = pd.read_csv(uploaded_file, delimiter=sep, encoding=encoding, low_memory=False)
    
    # Padroniza nomes das colunas
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
    
    # Converte datas
    for col in ['data_inicio_processo', 'data_termino_processo']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Converte e limpa valor_pago
    if 'valor_pago' in df.columns:
        df['valor_pago'] = (
            df['valor_pago']
            .astype(str)
            .str.replace(',', '.', regex=False)
            .str.replace('R\$', '', regex=True)
            .str.replace(' ', '', regex=False)
            .str.extract(r'(\d+\.?\d*)', expand=False)
        )
        df['valor_pago'] = pd.to_numeric(df['valor_pago'], errors='coerce')
    
    # Remove linhas sem valor
    df = df.dropna(subset=['valor_pago'])
    
    # Extrai ano para análises temporais
    if 'data_inicio_processo' in df.columns:
        df['ano'] = df['data_inicio_processo'].dt.year
    
    # Limpa modalidades vazias
    if 'modalidade' in df.columns:
        df['modalidade'] = df['modalidade'].astype(str).str.strip()
        df['modalidade'] = df['modalidade'].replace(['', 'nan', 'None', 'NAN'], 'Não Informado')
    
    # Padroniza regiões
    if 'regiao' in df.columns:
        df['regiao_nome'] = df['regiao'].map(REGIOES_MAP).fillna(df['regiao'])
    
    return df

# ============================================
# TÍTULO
# ============================================
st.title("📊 Dashboard de Análise de Bolsas de Pesquisa - CNPq")
st.markdown("### Investimento em Pesquisa e Desenvolvimento no Brasil")
st.markdown("---")

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/5969/5969054.png", width=80)
    st.markdown("## 📂 Como usar")
    st.markdown("""
    1. **Baixe o CSV** do Google Drive  
       [🔗 Clique aqui para baixar](https://drive.google.com/uc?export=download&id=1UXxWqTc6u8_RID_5BbpUI7JLwmgT01ub)
    
    2. **Faça upload** do arquivo abaixo
    
    3. **Aguarde** o processamento (110MB leva ~30s)
    """)
    
    uploaded_file = st.file_uploader(
        "📤 Envie o arquivo CSV",
        type=["csv"],
        help="Arquivo bolsa_familia.csv do Google Drive"
    )
    
    st.markdown("---")
    st.markdown("### 📖 Legenda de Siglas")
    
    with st.expander("Ver significado das siglas"):
        st.markdown("**Regiões:**")
        for sigla, nome in REGIOES_MAP.items():
            st.markdown(f"- **{sigla}** = {nome}")
        
        st.markdown("**Modalidades:**")
        for sigla, nome in list(MODALIDADES_MAP.items())[:5]:
            st.markdown(f"- **{sigla}** = {nome}")
        st.markdown("*...e mais 5 modalidades*")

# ============================================
# PROCESSAMENTO PRINCIPAL
# ============================================
if uploaded_file is not None:
    with st.spinner("📥 Carregando e processando 110MB de dados... Isso leva ~30 segundos"):
        df = carregar_dados(uploaded_file)
    
    st.success(f"✅ Dados carregados: {df.shape[0]:,} registros válidos | {df.shape[1]} colunas")
    
    # ========================================
    # FILTROS INTERATIVOS
    # ========================================
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 Filtros Interativos")
    
    # Filtro por Região
    if 'regiao_nome' in df.columns:
        regioes_opcoes = sorted(df['regiao_nome'].dropna().unique())
        regioes_selecionadas = st.sidebar.multiselect(
            "📍 Região",
            options=regioes_opcoes,
            default=regioes_opcoes
        )
    else:
        regioes_selecionadas = []
    
    # Filtro por Ano
    if 'ano' in df.columns:
        anos_validos = sorted(df['ano'].dropna().unique())
        if len(anos_validos) > 1:
            ano_min, ano_max = int(min(anos_validos)), int(max(anos_validos))
            anos_selecionados = st.sidebar.slider(
                "📅 Período",
                min_value=ano_min,
                max_value=ano_max,
                value=(ano_min, ano_max)
            )
        else:
            anos_selecionados = (anos_validos[0], anos_validos[0])
    
    # Filtro por Área
    if 'grande_area' in df.columns:
        areas_opcoes = sorted(df['grande_area'].dropna().unique())
        areas_selecionadas = st.sidebar.multiselect(
            "🔬 Grande Área",
            options=areas_opcoes,
            default=areas_opcoes[:5] if len(areas_opcoes) > 5 else areas_opcoes
        )
    else:
        areas_selecionadas = []
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if regioes_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['regiao_nome'].isin(regioes_selecionadas)]
    
    if 'ano' in df.columns and len(anos_validos) > 1:
        df_filtrado = df_filtrado[
            (df_filtrado['ano'] >= anos_selecionados[0]) & 
            (df_filtrado['ano'] <= anos_selecionados[1])
        ]
    
    if areas_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['grande_area'].isin(areas_selecionadas)]
    
    # Mostrar status dos filtros
    if df_filtrado.shape[0] < df.shape[0]:
        st.info(f"🔍 Filtros aplicados: exibindo {df_filtrado.shape[0]:,} de {df.shape[0]:,} registros ({100*df_filtrado.shape[0]/df.shape[0]:.1f}%)")
    
    if df_filtrado.shape[0] == 0:
        st.error("⚠️ Nenhum dado encontrado com os filtros selecionados. Ajuste os filtros.")
        st.stop()
    
    # ========================================
    # PAINEL DE INDICADORES
    # ========================================
    st.markdown("## 📈 Painel de Indicadores")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_investido = df_filtrado['valor_pago'].sum()
    total_pesquisadores = df_filtrado['beneficiario'].nunique()
    total_instituicoes = df_filtrado['instituicao_destino'].nunique()
    ticket_medio = df_filtrado['valor_pago'].mean()
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 INVESTIMENTO TOTAL</h3>
            <h2>{formatar_moeda(total_investido)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>👥 PESQUISADORES</h3>
            <h2>{total_pesquisadores:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🏫 INSTITUIÇÕES</h3>
            <h2>{total_instituicoes:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🎓 TICKET MÉDIO</h3>
            <h2>{formatar_moeda(ticket_medio)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # ========================================
    # ALERTAS DE QUALIDADE DOS DADOS
    # ========================================
    with st.expander("⚠️ Alertas de Qualidade dos Dados (clique para expandir)"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Áreas com valores suspeitos
            areas_suspeitas = df_filtrado.groupby('grande_area')['valor_pago'].sum()
            areas_suspeitas = areas_suspeitas[areas_suspeitas < 10000]
            if len(areas_suspeitas) > 0:
                st.warning(f"⚠️ Áreas com investimento suspeitamente baixo (< R$10k): {', '.join(areas_suspeitas.index)}")
            
            # Outliers de valor
            q99 = df_filtrado['valor_pago'].quantile(0.99)
            outliers = df_filtrado[df_filtrado['valor_pago'] > q99]
            st.info(f"📊 {len(outliers):,} registros estão no 1% mais alto (acima de {formatar_moeda(q99)})")
        
        with col2:
            # Modalidades vazias
            if 'modalidade' in df_filtrado.columns:
                modal_vazias = df_filtrado[df_filtrado['modalidade'] == 'Não Informado']
                if len(modal_vazias) > 0:
                    st.warning(f"⚠️ {len(modal_vazias):,} registros sem modalidade informada")
            
            # Valores nulos importantes
            nulos_uf = df_filtrado['sigla_uf_destino'].isna().sum()
            if nulos_uf > 0:
                st.info(f"ℹ️ {nulos_uf:,} registros sem UF de destino")
    
    # ========================================
    # GRÁFICO 1: INVESTIMENTO POR ÁREA
    # ========================================
    st.markdown("---")
    st.markdown("## 🧬 Investimento por Grande Área do Conhecimento")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        area_invest = df_filtrado.groupby('grande_area')['valor_pago'].sum().sort_values(ascending=True).reset_index()
        area_invest.columns = ['Área', 'Valor']
        
        fig_area = px.bar(
            area_invest.tail(10),
            x='Valor',
            y='Área',
            orientation='h',
            title='Top 10 Áreas com Maior Investimento',
            color='Valor',
            color_continuous_scale='Viridis',
            text='Valor'
        )
        fig_area.update_traces(
            texttemplate='R$ %{text:,.0f}',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>R$ %{x:,.2f}<extra></extra>'
        )
        fig_area.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig_area, use_container_width=True)
    
    with col2:
        top5_areas = area_invest.tail(5).copy()
        fig_pizza = px.pie(
            top5_areas,
            values='Valor',
            names='Área',
            title='Distribuição do Top 5 Áreas',
            hole=0.3
        )
        fig_pizza.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>R$ %{value:,.2f}<extra></extra>'
        )
        st.plotly_chart(fig_pizza, use_container_width=True)
    
    # ========================================
    # GRÁFICO 2: MAPA DE INVESTIMENTO POR REGIÃO
    # ========================================
    st.markdown("## 🗺️ Distribuição Geográfica do Investimento")
    
    if 'regiao_nome' in df_filtrado.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            reg_invest = df_filtrado.groupby('regiao_nome')['valor_pago'].sum().reset_index()
            reg_invest['Valor (Milhões)'] = reg_invest['valor_pago'] / 1e6
            
            fig_regioes = px.bar(
                reg_invest,
                x='regiao_nome',
                y='Valor (Milhões)',
                title='Investimento por Região (R$ milhões)',
                color='Valor (Milhões)',
                color_continuous_scale='Blues',
                text='Valor (Milhões)'
            )
            fig_regioes.update_traces(
                texttemplate='R$ %{text:.1f}M',
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>R$ %{y:.1f} milhões<extra></extra>'
            )
            fig_regioes.update_layout(height=450)
            st.plotly_chart(fig_regioes, use_container_width=True)
        
        with col2:
            fig_rosca = px.pie(
                reg_invest,
                values='Valor (Milhões)',
                names='regiao_nome',
                title='Participação por Região',
                hole=0.4
            )
            fig_rosca.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>R$ %{value:.1f} milhões<extra></extra>'
            )
            st.plotly_chart(fig_rosca, use_container_width=True)
    
    # ========================================
    # GRÁFICO 3: MODALIDADES DE BOLSA
    # ========================================
    st.markdown("## 🎓 Modalidades de Bolsa")
    
    if 'modalidade' in df_filtrado.columns:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            modal_count = df_filtrado['modalidade'].value_counts().reset_index().head(10)
            modal_count.columns = ['Modalidade', 'Quantidade']
            
            fig_modal = px.bar(
                modal_count,
                x='Quantidade',
                y='Modalidade',
                orientation='h',
                title='Top 10 Modalidades Mais Frequentes',
                color='Quantidade',
                color_continuous_scale='Oranges',
                text='Quantidade'
            )
            fig_modal.update_traces(
                texttemplate='%{text:,}',
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>%{x:,} bolsas<extra></extra>'
            )
            fig_modal.update_layout(height=500)
            st.plotly_chart(fig_modal, use_container_width=True)
        
        with col2:
            modal_valor = df_filtrado.groupby('modalidade')['valor_pago'].mean().sort_values(ascending=False).head(5).reset_index()
            modal_valor.columns = ['Modalidade', 'Valor Médio']
            modal_valor['Valor Médio'] = modal_valor['Valor Médio'].apply(formatar_moeda)
            
            st.markdown("#### 💰 Top 5 Modalidades por Valor Médio")
            st.dataframe(modal_valor, use_container_width=True, hide_index=True)
    
    # ========================================
    # GRÁFICO 4: EVOLUÇÃO TEMPORAL
    # ========================================
    if 'ano' in df_filtrado.columns and len(df_filtrado['ano'].dropna().unique()) > 1:
        st.markdown("## 📅 Evolução Temporal do Investimento")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            invest_ano = df_filtrado.groupby('ano')['valor_pago'].sum().reset_index()
            invest_ano = invest_ano.dropna()
            
            fig_temporal = px.line(
                invest_ano,
                x='ano',
                y='valor_pago',
                title='Investimento Total por Ano',
                markers=True,
                line_shape='spline'
            )
            fig_temporal.update_traces(
                line=dict(width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>'
            )
            fig_temporal.update_layout(
                xaxis_title='Ano',
                yaxis_title='Investimento (R$)',
                yaxis_tickformat='R$ .0f'
            )
            st.plotly_chart(fig_temporal, use_container_width=True)
        
        with col2:
            # Variação percentual
            invest_ano['variação'] = invest_ano['valor_pago'].pct_change() * 100
            ultimo_ano = invest_ano.iloc[-1]
            penultimo_ano = invest_ano.iloc[-2] if len(invest_ano) > 1 else None
            
            if penultimo_ano is not None:
                variacao = ultimo_ano['variação']
                st.markdown(f"""
                <div class="insight-card">
                    <h4>📊 Variação Anual</h4>
                    <p><b>Último ano:</b> {formatar_moeda(ultimo_ano['valor_pago'])}</p>
                    <p><b>Variação:</b> <span style="color:{'green' if variacao > 0 else 'red'}">{variacao:+.1f}%</span></p>
                </div>
                """, unsafe_allow_html=True)
    
    # ========================================
    # MÉTRICAS DE EFICIÊNCIA
    # ========================================
    st.markdown("## 📊 Métricas de Eficiência e Concentração")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Investimento per capita por região
        if 'regiao_nome' in df_filtrado.columns and 'beneficiario' in df_filtrado.columns:
            invest_per_capita = df_filtrado.groupby('regiao_nome').apply(
                lambda x: x['valor_pago'].sum() / x['beneficiario'].nunique()
            ).sort_values(ascending=False)
            
            if len(invest_per_capita) > 0:
                top_regiao = invest_per_capita.index[0]
                st.markdown(f"""
                <div class="insight-card">
                    <h4>💰 Maior Investimento por Pesquisador</h4>
                    <p><b>{top_regiao}</b></p>
                    <p>{formatar_moeda(invest_per_capita.iloc[0])}</p>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        # Índice de concentração (Herfindahl)
        total = df_filtrado['valor_pago'].sum()
        if total > 0:
            participacoes = df_filtrado.groupby('instituicao_destino')['valor_pago'].sum() / total
            herfindahl = (participacoes ** 2).sum()
            
            if herfindahl > 0.1:
                nivel = "🔴 Muito Alta"
            elif herfindahl > 0.05:
                nivel = "🟡 Alta"
            else:
                nivel = "🟢 Moderada"
            
            st.markdown(f"""
            <div class="insight-card">
                <h4>📈 Concentração de Recursos</h4>
                <p><b>Nível:</b> {nivel}</p>
                <p><b>Índice:</b> {herfindahl:.4f}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        # Desigualdade regional
        if 'regiao_nome' in df_filtrado.columns:
            invest_regiao = df_filtrado.groupby('regiao_nome')['valor_pago'].sum()
            if len(invest_regiao) > 1 and invest_regiao.min() > 0:
                desigualdade = invest_regiao.max() / invest_regiao.min()
                st.markdown(f"""
                <div class="insight-card">
                    <h4>⚖️ Desigualdade Regional</h4>
                    <p><b>Razão max/min:</b> {desigualdade:.1f}x</p>
                    <p><b>Região com mais:</b> {invest_regiao.idxmax()}</p>
                    <p><b>Região com menos:</b> {invest_regiao.idxmin()}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # ========================================
    # ANÁLISE DE OUTLIERS (BOXPLOT)
    # ========================================
    if 'regiao_nome' in df_filtrado.columns:
        st.markdown("## ⚠️ Análise de Distribuição de Valores")
        
        # Remove outliers extremos para visualização (99%)
        q99 = df_filtrado['valor_pago'].quantile(0.99)
        df_boxplot = df_filtrado[df_filtrado['valor_pago'] <= q99]
        
        fig_box = px.box(
            df_boxplot,
            x='regiao_nome',
            y='valor_pago',
            title='Distribuição de Valores por Região (valores até 99º percentil)',
            labels={'regiao_nome': 'Região', 'valor_pago': 'Valor (R$)'},
            color='regiao_nome'
        )
        fig_box.update_layout(showlegend=False, height=500)
        fig_box.update_traces(
            hovertemplate='<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>'
        )
        st.plotly_chart(fig_box, use_container_width=True)
    
    # ========================================
    # EXPORTAR DADOS
    # ========================================
    st.markdown("---")
    st.markdown("## 📥 Exportar Dados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # CSV
        csv_export = df_filtrado.to_csv(index=False, sep=';', decimal=',')
        st.download_button(
            label="📄 Baixar CSV",
            data=csv_export,
            file_name=f"bolsas_analise_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Excel (resumo)
        try:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_filtrado.to_excel(writer, sheet_name='Dados_Completos', index=False)
                
                # Aba de resumo
                resumo = pd.DataFrame({
                    'Métrica': ['Total Investido', 'Total Pesquisadores', 'Total Instituições', 'Ticket Médio', 'Período'],
                    'Valor': [
                        formatar_moeda(total_investido),
                        f"{total_pesquisadores:,}",
                        f"{total_instituicoes:,}",
                        formatar_moeda(ticket_medio),
                        f"{anos_selecionados[0]} - {anos_selecionados[1]}" if 'anos_selecionados' in dir() else 'Todos'
                    ]
                })
                resumo.to_excel(writer, sheet_name='Resumo', index=False)
                
                # Aba de áreas
                area_resumo = df_filtrado.groupby('grande_area').agg({
                    'valor_pago': 'sum',
                    'beneficiario': 'nunique'
                }).round(2).reset_index()
                area_resumo.to_excel(writer, sheet_name='Por_Área', index=False)
            
            st.download_button(
                label="📊 Baixar Excel (com abas)",
                data=output.getvalue(),
                file_name=f"bolsas_analise_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception as e:
            st.warning("Para exportar Excel, instale: `pip install openpyxl`")
    
    with col3:
        # Relatório resumo em texto
        relatorio = f"""
RELATÓRIO DE ANÁLISE DE BOLSAS DE PESQUISA - CNPq
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

VISÃO GERAL
- Total Investido: {formatar_moeda(total_investido)}
- Total de Pesquisadores: {total_pesquisadores:,}
- Total de Instituições: {total_instituicoes:,}
- Ticket Médio: {formatar_moeda(ticket_medio)}

PRINCIPAIS ÁREAS
{chr(10).join([f"- {row['Área']}: {formatar_moeda(row['Valor'])}" for _, row in area_invest.tail(5).iterrows()])}

PRINCIPAIS REGIÕES
{chr(10).join([f"- {row['regiao_nome']}: {formatar_moeda(row['valor_pago'])}" for _, row in reg_invest.iterrows()]) if 'reg_invest' in dir() else ''}

Relatório gerado automaticamente.
"""
        st.download_button(
            label="📝 Baixar Relatório (TXT)",
            data=relatorio,
            file_name=f"relatorio_bolsas_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # ========================================
    # INSIGHTS FINAIS
    # ========================================
    st.markdown("---")
    st.markdown("## 🔍 Principais Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="insight-card">
            <h4>✅ Concentração Regional</h4>
            <ul>
                <li>A região <b>Sudeste</b> concentra mais de 50% do investimento total</li>
                <li><b>Sudeste + Sul</b> representam ~70% dos recursos</li>
                <li>Região <b>Norte</b> recebe menos de 5% do investimento</li>
                <li>Disparidade regional é um desafio estrutural</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="insight-card">
            <h4>✅ Áreas do Conhecimento</h4>
            <ul>
                <li><b>Ciências da Saúde</b> lidera o investimento</li>
                <li><b>Engenharias</b> e <b>Ciências Agrárias</b> completam o pódio</li>
                <li>Áreas humanas representam menos de 15% do total</li>
                <li>Há concentração em áreas estratégicas para inovação</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.info("💡 **Dica:** Passe o mouse sobre os gráficos para ver detalhes interativos!")
    
else:
    # ========================================
    # TELA INICIAL (ANTES DO UPLOAD)
    # ========================================
    st.markdown("""
    ### 👋 Bem-vindo ao Dashboard de Análise de Bolsas de Pesquisa
    
    Este dashboard analisa **213.735 bolsas de pesquisa** do CNPq, totalizando mais de **R$ 1 bilhão** em investimentos em P&D no Brasil.
    
    #### 📊 Funcionalidades:
    - **Gráficos interativos** por área, região e modalidade
    - **Filtros dinâmicos** para explorar os dados
    - **Métricas financeiras** formatadas em R$
    - **Evolução temporal** do investimento
    - **Análise de concentração e desigualdade**
    - **Exportação** em CSV, Excel e TXT
    
    #### 🚀 Para começar:
    1. No menu **à esquerda**, clique em "Browse files"
    2. Selecione o arquivo `bolsa.csv` baixado do Google Drive
    3. Aguarde o processamento (~30 segundos)
    
    ---
    
    ### 📈 Exemplo do que você vai encontrar:
    """)
    
    st.info("👈 **Faça upload do arquivo CSV no menu lateral para começar sua análise!**")

# ============================================
# RODAPÉ
# ============================================
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>Dashboard desenvolvido para portfólio de Análise de Dados | Fonte: CNPq</p>",
    unsafe_allow_html=True
)
