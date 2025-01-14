import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

# Configuração inicial do Seaborn
sns.set_theme(style="ticks", rc={"axes.spines.right": False, "axes.spines.top": False})

# Função para carregar os dados
@st.cache_data(show_spinner=True)
def load_data(file_data):
    try:
        if file_data.name.endswith('.csv'):
            return pd.read_csv(file_data, sep=';')
        elif file_data.name.endswith('.xlsx'):
            return pd.read_excel(file_data)
        else:
            raise ValueError("Tipo de arquivo não suportado. Suba um arquivo .csv ou .xlsx.")
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()

# Função para filtrar dados
@st.cache_data
def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)

# Função para exportar dados para Excel
@st.cache_data
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    return output.getvalue()

# Função para exportar gráfico como imagem
def save_plot(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return buf

# Função principal
def main():
    st.set_page_config(
        page_title='Telemarketing Analysis',
        page_icon='../img/telmarketing_icon.png',
        layout="wide",
        initial_sidebar_state='expanded'
    )

    st.title('Telemarketing Analysis')
    st.markdown("---")
    image = Image.open("../img/Bank-Branding.jpg")
    st.sidebar.image(image)

    # Upload do arquivo
    st.sidebar.write("## Suba o arquivo")
    data_file_1 = st.sidebar.file_uploader("Bank marketing data", type=['csv', 'xlsx'])

    if data_file_1:
        # Carregar os dados
        bank_raw = load_data(data_file_1)
        if bank_raw.empty:
            st.warning("O arquivo está vazio ou inválido.")
            return

        bank = bank_raw.copy()

        # Filtros
        with st.sidebar.form(key='filters_form'):
            max_age = int(bank.age.max())
            min_age = int(bank.age.min())
            idades = st.slider('Idade', min_age, max_age, (min_age, max_age))
            jobs_selected = st.multiselect("Profissão", bank.job.unique().tolist() + ['all'], ['all'])
            submit_button = st.form_submit_button("Aplicar filtros")

        if submit_button:
            bank = bank.query("age >= @idades[0] and age <= @idades[1]").pipe(multiselect_filter, 'job', jobs_selected)

        st.write("### Dados Filtrados")
        st.dataframe(bank)

        # Exportar dados filtrados
        st.download_button(
            label="📥 Baixar tabela filtrada",
            data=to_excel(bank),
            file_name='dados_filtrados.xlsx'
        )

        # Gerar gráficos
        st.write("### Proporção de Aceite")
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(x=bank_raw['y'].value_counts().index, y=bank_raw['y'].value_counts(normalize=True) * 100, ax=ax)
        ax.set_title("Proporção de Aceite", fontsize=14, fontweight='bold')
        st.pyplot(fig)

        # Download do gráfico
        st.download_button(
            label="📥 Baixar gráfico",
            data=save_plot(fig),
            file_name="grafico_proporcao.png",
            mime="image/png"
        )

if __name__ == '__main__':
    main()
