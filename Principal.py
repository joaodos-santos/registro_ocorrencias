import streamlit as st

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Sistema de Registros TVTOP",
    page_icon="✈️",
    layout="centered"
)


st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

# ==========================================
# CABEÇALHO INFORMATIVO
# ==========================================
st.title("✈️ Sistema de Registros TVTOP PBCS")
st.subheader("CINDACTA III - Seção de Informática Operacional (TIOp)")

st.markdown("---")
st.markdown("""
Bem-vindo ao sistema de relatórios diários de ocorrências. 

Este sistema é composto por três módulos principais de registro:

-   **1. Registro Técnico:** Formulário para registro de anomalias nos indicadores TÉCNICOS do TVTOP e geração do PDF.
-   **2. Registro Operacional:** Formulário para registro de anomalias nos indicadores OPERACIONAIS do TVTOP e geração do PDF.
-   **3. Registro de Segurança:** Formulário para registro de anomalias nos indicadores de SEGURANÇA do TVTOP e geração do PDF.

**Instruções Gerais:**
- Preencha todos os campos obrigatórios de cada formulário antes de gerar os documentos.
- Os relatórios gerados podem ser baixados localmente para assinatura posterior e arquivamento.
""")

st.info("👇 Identifique-se abaixo e selecione o módulo desejado para iniciar o seu turno.")

# ==========================================
# ROTEADOR DE ACESSO (LOGIN DINÂMICO)
# ==========================================
with st.container(border=True):
    nome_preenchedor = st.text_input("Digite Posto/Graduação + nome de guerra")
    st.caption("Ex.: 1S JOSENILDA")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    perfil = st.radio(
        "Selecione o módulo que deseja acessar:",
        ["Técnico", "Operacional", "Segurança", "Acompanhamento"]
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 Iniciar / Acessar", type="primary", use_container_width=True):
        if not nome_preenchedor.strip():
            st.error("⚠️ Por favor, digite seu Posto/Graduação e nome de guerra antes de continuar.")
        else:
            nome_arquivo = nome_preenchedor.strip().lower().replace(" ", "_").replace("/", "_")
            
            st.session_state["usuario_tela"] = nome_preenchedor.strip()
            st.session_state["usuario_arquivo"] = nome_arquivo
            st.session_state["perfil_autorizado"] = perfil  
            
            if perfil == "Técnico":
                st.switch_page("pages/1_Registro_Tecnico.py")
            elif perfil == "Operacional":
                st.switch_page("pages/2_Registro_Operacional.py")
            elif perfil == "Segurança":
                st.switch_page("pages/3_Registro_Seguranca.py")
            elif perfil == "Acompanhamento":
                st.switch_page("pages/4_Acompanhamento_Eventos.py")