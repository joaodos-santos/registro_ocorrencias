import streamlit as st
import json
import os
import datetime
import uuid

# ==========================================
# CONFIGURAÇÃO E TRAVAS DE SEGURANÇA
# ==========================================
st.set_page_config(page_title="Acompanhamento de Eventos", layout="wide")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="collapsedControl"] {display: none;}
    </style>
""", unsafe_allow_html=True)

if "usuario_arquivo" not in st.session_state:
    st.switch_page("Principal.py")

if st.session_state.get("perfil_autorizado") != "Acompanhamento":
    st.warning(f"⚠️ **Acesso Restrito.** Você iniciou o turno logado como **{st.session_state.get('perfil_autorizado')}**.")
    st.info("Para acessar o Acompanhamento, retorne à página inicial e selecione o perfil correto.")
    if st.button("🏠 Voltar para o Início"):
        st.switch_page("Principal.py")
    st.stop()

# ==========================================
# GESTÃO DO BANCO DE DADOS (JSON PERMANENTE)
# ==========================================
DB_PATH = "/tiop/dados-containers/tvtop/banco_acompanhamento.json"

def carregar_db():
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def salvar_db(dados):
    with open(DB_PATH, "w") as f:
        json.dump(dados, f, indent=4)

db = carregar_db()
usuario_atual = st.session_state.get('usuario_tela', 'Desconhecido')

# ==========================================
# INTERFACE PRINCIPAL
# ==========================================
col_titulo, col_sair = st.columns([8, 2])
with col_titulo:
    st.title("📋 Registro de Acompanhamento de Eventos - TVTOP")
    st.markdown(f"**Operador logado:** {usuario_atual}")
with col_sair:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Sair (Logoff)", use_container_width=True):
        st.session_state.clear()
        st.switch_page("Principal.py")
st.markdown("---")

# 1. FORMULÁRIO DE NOVO EVENTO
with st.expander("➕ **ABRIR NOVO CHAMADO / EVENTO**", expanded=False):
    with st.form("form_novo_evento", clear_on_submit=True):
        titulo_novo = st.text_input("Título da Ocorrência *")
        
        c_obs, col1, col2 = st.columns(3)
        data_obs_novo = c_obs.date_input("Data de Observação do Evento *", format="DD/MM/YYYY")
        resp_novo = col1.text_input("Responsável pela avaliação (Opcional)")
        chamado_novo = col2.text_input("Número do chamado (Opcional)")

        submitted = st.form_submit_button("💾 Criar Registro", type="primary")
        if submitted:
            if not titulo_novo.strip():
                st.error("⚠️ O Título da Ocorrência é obrigatório!")
            else:
                novo_registro = {
                    "id": str(uuid.uuid4()),
                    "titulo": titulo_novo.strip(),
                    "data_observacao": data_obs_novo.strftime("%d/%m/%Y"),
                    "responsavel": resp_novo.strip(),
                    "chamado": chamado_novo.strip(),
                    "criador": usuario_atual,
                    "data_criacao": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "status": "analise",
                    "conclusao": "",
                    "data_conclusao": "",
                    "modificado_por": "",
                    "data_modificacao": ""
                }
                db.append(novo_registro)
                salvar_db(db)
                st.success("Evento registrado com sucesso!")
                st.rerun()

# 2. SEPARAÇÃO EM ABAS
aba_analise, aba_concluidos = st.tabs(["❓ Em Análise", "✅ Concluídos"])

# --- ABA: EM ANÁLISE ---
with aba_analise:
    eventos_analise = [e for e in db if e["status"] == "analise"]
    
    if not eventos_analise:
        st.info("🎉 Nenhum evento pendente de análise no momento.")
    else:
        for evento in reversed(eventos_analise):
            # Formatação do cabeçalho com Responsável e Chamado visíveis
            resp_exibicao = evento.get('responsavel') if evento.get('responsavel') else 'Não informado'
            chamado_exibicao = evento.get('chamado') if evento.get('chamado') else 'N/A'
            header = f"❓ {evento['titulo']} | Responsável: {resp_exibicao} | Chamado: {chamado_exibicao}"
            
            with st.expander(header):
                data_obs_exibicao = evento.get('data_observacao', 'Não informada (Registro Antigo)')
                st.caption(f"Criado por **{evento['criador']}** em {evento['data_criacao']} | 📅 Observado em: **{data_obs_exibicao}**")
                
                data_obs_atual_str = evento.get("data_observacao", datetime.date.today().strftime("%d/%m/%Y"))
                try:
                    data_obs_atual_obj = datetime.datetime.strptime(data_obs_atual_str, "%d/%m/%Y").date()
                except ValueError:
                    data_obs_atual_obj = datetime.date.today()

                # Campos de edição
                t_edit = st.text_input("Título", value=evento["titulo"], key=f"t_{evento['id']}")
                
                c0, c1, c2 = st.columns(3)
                d_edit = c0.date_input("Data de Observação", value=data_obs_atual_obj, format="DD/MM/YYYY", key=f"d_{evento['id']}")
                r_edit = c1.text_input("Responsável", value=evento["responsavel"], key=f"r_{evento['id']}")
                ch_edit = c2.text_input("Número do Chamado", value=evento["chamado"], key=f"ch_{evento['id']}")
                
                if evento.get('data_modificacao'):
                    st.caption(f"Última alteração por **{evento['modificado_por']}** em {evento['data_modificacao']}")

                # Botões Salvar e Excluir lado a lado
                b1, b2, _ = st.columns([2, 2, 6])
                if b1.button("✏️ Salvar Alterações", key=f"salvar_{evento['id']}"):
                    evento["titulo"] = t_edit
                    evento["data_observacao"] = d_edit.strftime("%d/%m/%Y")
                    evento["responsavel"] = r_edit
                    evento["chamado"] = ch_edit
                    evento["modificado_por"] = usuario_atual
                    evento["data_modificacao"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                    salvar_db(db)
                    st.success("Alterações salvas!")
                    st.rerun()

                if b2.button("🗑️ Excluir Evento", key=f"del_{evento['id']}"):
                    db = [e for e in db if e["id"] != evento["id"]]
                    salvar_db(db)
                    st.rerun()

                st.markdown("---")
                st.markdown("**Solução / Conclusão:**")
                texto_conclusao = st.text_area("Descreva a solução para finalizar este evento:", key=f"conc_{evento['id']}")
                
                if st.button("✅ Concluir Evento", type="primary", key=f"btn_conc_{evento['id']}"):
                    if not texto_conclusao.strip():
                        st.warning("⚠️ Preencha o campo de solução antes de concluir o evento.")
                    else:
                        evento["conclusao"] = texto_conclusao
                        evento["status"] = "concluido"
                        evento["data_conclusao"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                        evento["modificado_por"] = usuario_atual
                        salvar_db(db)
                        st.rerun()

# --- ABA: CONCLUÍDOS ---
with aba_concluidos:
    eventos_concluidos = [e for e in db if e["status"] == "concluido"]
    
    if not eventos_concluidos:
        st.info("Nenhum evento concluído ainda.")
    else:
        for evento in reversed(eventos_concluidos):
            # Formatação do cabeçalho com Responsável e Chamado visíveis
            resp_exibicao = evento.get('responsavel') if evento.get('responsavel') else 'Não informado'
            chamado_exibicao = evento.get('chamado') if evento.get('chamado') else 'N/A'
            header_conc = f"✅ {evento['titulo']} | Responsável: {resp_exibicao} | Chamado: {chamado_exibicao}"
            
            with st.expander(header_conc):
                st.markdown(f"**📅 Data de Observação:** {evento.get('data_observacao', 'Não informada')}")
                st.markdown(f"**Responsável:** {evento.get('responsavel', 'Não informado')}")
                st.markdown(f"**Criado por:** {evento['criador']} em {evento['data_criacao']}")
                st.markdown(f"**Concluído por:** {evento['modificado_por']} em {evento['data_conclusao']}")
                st.markdown("**Solução Aplicada:**")
                st.success(evento["conclusao"])
                
                col_btn1, col_btn2, _ = st.columns([2, 2, 6])
                if col_btn1.button("🔄 Reabrir (Voltar para Análise)", key=f"reabrir_{evento['id']}"):
                    evento["status"] = "analise"
                    evento["conclusao"] = ""
                    evento["data_conclusao"] = ""
                    evento["modificado_por"] = usuario_atual
                    evento["data_modificacao"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                    salvar_db(db)
                    st.rerun()
                    
                if col_btn2.button("🗑️ Excluir Definitivamente", key=f"del_conc_{evento['id']}"):
                    db = [e for e in db if e["id"] != evento["id"]]
                    salvar_db(db)
                    st.rerun()