# app.py
import streamlit as st

st.set_page_config(
    page_title="Sistema de Registros TVTOP",
    page_icon="✈️",
    layout="centered"
)

st.title("✈️ Sistema de Registros TVTOP PBCS")
st.subheader("CINDACTA III - Seção de Informática Operacional (TIOp)")

st.markdown("---")
st.markdown("""
Bem-vindo ao sistema de relatórios diários de ocorrências. 

Utilize o **menu lateral esquerdo** para navegar entre os módulos disponíveis:

*   **1. Registro Técnico:** Formulário para registro de anomalias nos indicadores TÉCNICOS do TVTOP e geração do PDF.
*   **2. Registro Operacional:** Formulário para registro de anomalias nos indicadores OPERACIONAIS do TVTOP e geração do PDF.
*   **3. Registro de Segurança:** Formulário para registro de anomalias nos indicadores se Segurança do TVTOP e geração do PDF.

**Instruções Gerais:**
- Preencha todos os campos obrigatórios de cada formulário antes de gerar os documentos.
- Os relatórios gerados podem ser baixados localmente para assinatura posterior.
""")

st.info("👈 Selecione um módulo no menu ao lado para iniciar o preenchimento do turno.")