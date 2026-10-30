import streamlit as st
from fpdf import FPDF
import datetime
import json
import os

# Dicionário para garantir o mês em português
MESES_PT = {1: 'JAN', 2: 'FEV', 3: 'MAR', 4: 'ABR', 5: 'MAI', 6: 'JUN', 
            7: 'JUL', 8: 'AGO', 9: 'SET', 10: 'OUT', 11: 'NOV', 12: 'DEZ'}

# ==========================================
# CLASSE GERADORA DE PDF (FPDF2)
# ==========================================
class RelatorioSegurancaPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        try:
            self.image("assets/decea.png", x=10, y=8, w=18)
            self.image("assets/cindacta3.png", x=182, y=8, w=18)
        except:
            pass
            
        self.set_y(12)
        self.set_font("helvetica", "B", 10)
        self.set_text_color(0, 51, 102)
        self.cell(0, 5, "CINDACTA III - SEGURANÇA OPERACIONAL", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "B", 12)
        self.cell(0, 6, "RELATÓRIO DIÁRIO DE OCORRÊNCIAS DE SEGURANÇA - TVTOP PBCS", align="C", new_x="LMARGIN", new_y="NEXT")
        
        self.set_y(32)
        self.set_draw_color(0, 51, 102)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Página {self.page_no()}/{{nb}}", align="C")

    def desenhar_secao(self, titulo):
        self.set_font("helvetica", "B", 10)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 6, titulo, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def adicionar_identificacao(self, data, fase, h_inicio, h_fim, sup_tiop, sup_acc, analista_seg):
        self.desenhar_secao("1. IDENTIFICAÇÃO DO TURNO E DA JANELA DE TESTE")
        self.set_font("helvetica", "", 9)
        self.cell(0, 5, f"Data: {data.strftime('%d/%m/%Y')}    |    Fase do TVTOP: {fase}", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, f"Horário Efetivo de Teste: Início: {h_inicio} UTC    |    Término: {h_fim} UTC", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        
        self.set_font("helvetica", "B", 9)
        self.cell(0, 5, "Equipe de Serviço:", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "", 9)
        self.cell(0, 5, f"- Supervisor Técnico (TIOP): {sup_tiop}", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, f"- Supervisor Operacional (ACC-AO): {sup_acc}", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        
        self.set_font("helvetica", "B", 9)
        self.cell(0, 5, "Equipe TVTOP:", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "", 9)
        self.cell(0, 5, f"- Analista de Segurança: {analista_seg}", new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def adicionar_declaracao_normalidade(self, sem_anomalias):
        self.desenhar_secao("2. DECLARAÇÃO DE TURNO SEM ANOMALIAS")
        self.set_font("helvetica", "", 9)
        marcador = "[X]" if sem_anomalias else "[ ]"
        texto = f"{marcador} DECLARO que, durante a janela de aplicação dos testes no presente turno, NÃO HOUVE ocorrência ou observação de qualquer violação dos indicadores de segurança do TVTOP PBCS."
        self.multi_cell(0, 5, texto, new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def adicionar_ficha_ocorrencia(self, num, ind_afetado, dados):
        self.desenhar_secao(f"3. DETALHAMENTO: FICHA DE OCORRÊNCIA N° {num:02d}")
        
        self.set_font("helvetica", "B", 9)
        self.multi_cell(0, 5, f"Questão / Indicador Afetado:\n{ind_afetado}", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        
        self.cell(0, 5, "Constatação, Horários e Criticidade:", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "", 9)
        self.cell(0, 5, f"- Origem da Coleta: {dados['origem']}", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, f"- Horários: Início: {dados['h_inicio']}Z | Término: {dados['h_fim']}Z", new_x="LMARGIN", new_y="NEXT")
        
        self.set_font("helvetica", "B", 9)
        self.cell(0, 5, f"- Classificação: {dados['criticidade']}", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

        self.set_font("helvetica", "B", 9)
        self.cell(0, 5, "Aeronaves e Setores Envolvidos:", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "", 9)
        self.cell(0, 5, f"- Callsign(s) / Matrícula(s): {dados['callsigns']}", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, f"- Posição ATC / Setor: {dados['setor']}", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

        self.set_font("helvetica", "B", 9)
        self.cell(0, 5, "Descrição do Evento:", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "", 9)
        self.multi_cell(0, 5, f"{dados['descricao']}", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

        self.set_font("helvetica", "B", 9)
        self.cell(0, 5, "Ações Adotadas:", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "", 9)
        acoes_texto = ""
        # Usa .get() para evitar quebra caso o JSON carregue um rascunho antigo
        if dados.get("acao_relprev"): acoes_texto += "- [X] Preenchimento de RELPREV\n"
        if dados.get("acao_fno"): acoes_texto += "- [X] Abrir FNO\n"
        if dados.get("acao_avaliar_retorno"): acoes_texto += "- [X] Avaliar retorno\n"
        if dados.get("outras_acoes"): acoes_texto += f"- Outras: {dados['outras_acoes']}"
        
        self.multi_cell(0, 5, acoes_texto if acoes_texto.strip() else "Nenhuma ação pré-definida assinalada.", new_x="LMARGIN", new_y="NEXT")
        
        self.ln(4)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)

    def adicionar_acompanhamento(self, data_registro, texto):
        self.desenhar_secao("4. ACOMPANHAMENTO DE REGISTROS ANTERIORES")
        if texto.strip():
            self.set_font("helvetica", "B", 9)
            self.cell(0, 5, f"Data do registro da ocorrência original: {data_registro.strftime('%d/%m/%Y')}", new_x="LMARGIN", new_y="NEXT")
            self.ln(2)
            self.set_font("helvetica", "", 9)
            self.multi_cell(0, 5, texto, new_x="LMARGIN", new_y="NEXT")
        else:
            self.set_font("helvetica", "I", 9)
            self.cell(0, 5, "Nenhum acompanhamento de registro anterior inserido neste turno.", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def adicionar_outras_ocorrencias(self, texto):
        self.desenhar_secao("5. OUTRAS OCORRÊNCIAS / OBSERVAÇÕES GERAIS")
        if texto.strip():
            self.set_font("helvetica", "", 9)
            self.multi_cell(0, 5, texto, new_x="LMARGIN", new_y="NEXT")
        else:
            self.set_font("helvetica", "I", 9)
            self.cell(0, 5, "Nenhuma ocorrência adicional registrada neste turno.", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def adicionar_assinaturas(self, analista_seg):
        if self.get_y() > (self.h - 80):
            self.add_page()
            
        self.desenhar_secao("6. ASSINATURA E ENCAMINHAMENTO")
        self.set_font("helvetica", "", 9)
        self.multi_cell(0, 5, "O arquivo PDF assinado deverá ser arquivado conforme determinado pelo Gerente do Projeto PBCS.", new_x="LMARGIN", new_y="NEXT")
        self.ln(20)

        y_atual = self.get_y()
        self.set_line_width(0.3)
        self.set_draw_color(0, 0, 0)
        
        largura_linha = 80
        pos_x = (self.w - largura_linha) / 2
        
        # --- PRIMEIRA LINHA: Assinatura Analista (Original) ---
        self.line(pos_x, y_atual, pos_x + largura_linha, y_atual)
        
        self.set_y(y_atual + 2)
        self.set_font("helvetica", "B", 9)
        self.cell(0, 5, analista_seg.upper() if analista_seg else "Analista de Segurança", align="C", new_x="LMARGIN", new_y="NEXT")
        
        self.set_font("helvetica", "", 8)
        self.cell(0, 5, "Analista de Segurança - Equipe TVTOP", align="C", new_x="LMARGIN", new_y="NEXT")
        
        # --- SEGUNDA LINHA: Assinatura Supervisor Local (Nova) ---
        self.ln(20)
        y_atual = self.get_y()
        
        self.line(pos_x, y_atual, pos_x + largura_linha, y_atual)
        
        self.set_y(y_atual + 2)
        self.set_font("helvetica", "B", 9)
        self.cell(0, 5, "SUPERVISOR LOCAL", align="C", new_x="LMARGIN", new_y="NEXT")


# ==========================================
# INTERFACE STREAMLIT DA PÁGINA
# ==========================================
st.set_page_config(page_title="Registro de Segurança", layout="wide")

# ==========================================
# 1. TRAVA DE SEGURANÇA E OCULTAÇÃO DA BARRA LATERAL
# ==========================================
# Esconde a barra lateral visualmente
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="collapsedControl"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# Se tentar acessar sem nem ter passado pelo login, manda pro Início
if "usuario_arquivo" not in st.session_state:
    st.switch_page("Principal.py")

# Se o usuário logou, mas escolheu outro perfil na tela inicial:
if st.session_state.get("perfil_autorizado") != "Segurança":
    st.warning(f"⚠️ **Acesso Restrito.** Você iniciou o turno logado como **{st.session_state.get('perfil_autorizado')}**.")
    st.info("Para acessar o Registro de Segurança, retorne à página inicial e selecione o perfil correto.")
    if st.button("🏠 Voltar para o Início"):
        st.switch_page("Principal.py")
    st.stop() # Freio de mão: impede o Python de ler o resto do arquivo e criar o JSON errado!
# ==========================================
# LÓGICA DE PERSISTÊNCIA DE DADOS (JSON)
# ==========================================
# 2. RASCUNHO DINÂMICO (Usa o nome digitado na Home para criar um arquivo único)
usuario_arq = st.session_state["usuario_arquivo"]
ARQUIVO_RASCUNHO = f"/tiop/dados-containers/tvtop/rascunho_seguranca_{usuario_arq}.json"

class RascunhoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.time, datetime.datetime)):
            return obj.isoformat()
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

agora = datetime.datetime.now()
if agora.hour < 8:
    data_operacional = (agora - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
else:
    data_operacional = agora.strftime("%Y-%m-%d")

if os.path.exists(ARQUIVO_RASCUNHO):
    try:
        with open(ARQUIVO_RASCUNHO, "r") as f:
            conteudo = json.load(f)
            if conteudo.get("data_registro") == data_operacional:
                for chave, valor in conteudo.get("dados", {}).items():
                    if chave not in st.session_state:
                        if isinstance(valor, str):
                            if "hr_" in chave:
                                try: valor = datetime.time.fromisoformat(valor)
                                except: pass
                            elif "data" in chave:
                                try: valor = datetime.date.fromisoformat(valor)
                                except: pass
                        st.session_state[chave] = valor
    except Exception:
        pass

def salvar_tela_inteira():
    dados_tela = {k: v for k, v in st.session_state.items() if k.startswith("seg_") and not k.startswith("FormSubmitter")}
    estado_atual = {
        "data_registro": data_operacional,
        "dados": dados_tela
    }
    try:
        with open(ARQUIVO_RASCUNHO, "w") as f:
            json.dump(estado_atual, f, cls=RascunhoEncoder)
    except Exception as e:
        print(f"Erro ao salvar JSON no arquivo {ARQUIVO_RASCUNHO}: {e}")

def limpar_dados_seguranca():
    if os.path.exists(ARQUIVO_RASCUNHO):
        try:
            os.remove(ARQUIVO_RASCUNHO)
        except:
            pass
            
    for chave in list(st.session_state.keys()):
        if chave.startswith("seg_"):
            del st.session_state[chave]
            
    st.components.v1.html("<script>window.parent.location.reload();</script>", height=0)

#if st.sidebar.button("🗑️ Iniciar Novo Registro de Segurança (Zerar)"):
 #   limpar_dados_seguranca()
# ==========================================


# Função para atualizar horários baseados na fase selecionada
def atualizar_horarios_seg():
    if "Fase 1" in st.session_state.get("seg_fase", ""):
        st.session_state["seg_hr_in"] = datetime.time(13, 0)
        st.session_state["seg_hr_out"] = datetime.time(19, 0)
    else:
        st.session_state["seg_hr_in"] = datetime.time(23, 0)
        st.session_state["seg_hr_out"] = datetime.time(6, 0)

if "seg_hr_in" not in st.session_state:
    st.session_state["seg_hr_in"] = datetime.time(13, 0)
    st.session_state["seg_hr_out"] = datetime.time(19, 0)

st.title("🛡️ TVTOP PBCS - Registro de Segurança")

# --- SEÇÃO 1: Identificação ---
st.markdown("### 1. IDENTIFICAÇÃO DO TURNO E DA JANELA DE TESTE")
with st.container(border=True):
    col_data, col_fase, col_hin, col_hout = st.columns(4)
    data_relatorio = col_data.date_input("Data do Relatório", datetime.date.today(), key="seg_data")
    fase_tvtop = col_fase.selectbox("Fase do TVTOP", ["Fase 1 (13:00-19:00Z)", "Fase 2 (23:00-06:00Z)"], key="seg_fase", on_change=atualizar_horarios_seg)
    hr_inicio = col_hin.time_input("Início (UTC)", key="seg_hr_in")
    hr_fim = col_hout.time_input("Término (UTC)", key="seg_hr_out")
    
    st.markdown("##### Equipe de Serviço")
    c_tiop, c_acc = st.columns(2)
    sup_tiop = c_tiop.text_input("Supervisor Técnico (TIOP)", key="seg_sup_tiop")
    sup_acc = c_acc.text_input("Supervisor Operacional (ACC-AO)", key="seg_sup_acc")
    
    st.markdown("##### Equipe TVTOP")
    analista_seg = st.text_input("Analista de Segurança", key="seg_analista")

# --- SEÇÃO 2: Declaração Geral ---
st.markdown("### 2. DECLARAÇÃO GERAL")
with st.container(border=True):
    plantao_sem_alteracoes = st.toggle("✅ DECLARAÇÃO DE TURNO SEM ANOMALIAS (Marcar se NÃO HOUVE ocorrências de segurança no turno)", value=False, key="seg_toggle")


# --- Dicionário de Perigos, Perguntas e Gatilhos de Anomalia ---
# Formato: "Pergunta": "Resposta que configura Anomalia"
checklist_seguranca = {
    "PERIGO 1: Aplicação incorreta da separação PBCS": [
        ("Foram aplicados os mínimos de separação por performance corretamente?", "Não"),
        ("Os alertas e/ou avisos PBCS foram interpretados corretamente?", "Não"),
        ("O ATCO utilizou adequadamente as ferramentas do SAGITARIO associadas ao PBCS?", "Não"),
        ("O ATCO identificou os desvios laterais de maneira adequada ao cenário?", "Não"),
        ("O Supervisor/Encarregado realizou as setorizações corretamente, de acordo com a carga de trabalho?", "Não"),
        ("Os procedimentos alternativos de comunicação, em situações de falha do meio primário, foram utilizados conforme previsto?", "Não"),
        ("O zoom do SAGITARIO foi utilizado de maneira efetiva, de acordo com o cenário e a evolução dos tráfegos?", "Não"),
        ("A funcionalidade do SAGITARIO 'Nova Janela' foi utilizada de forma adequada?", "Não"),
        ("Em uma situação de degradação do STVD e/ou do enlace de dados, o ATCO identificou a perda das condições necessárias para a separação PBCS?", "Não"),
        ("Em uma situação de degradação do STVD e/ou do enlace de dados, o ATCO adotou os procedimentos previstos para o restabelecimento dos mínimos previstos para a separação convencional?", "Não"),
        ("Em uma situação de degradação do STVD e/ou do enlace de dados, o ATCO demonstrou a manutenção da consciência situacional durante a transição para a separação convencional?", "Não")
    ],
    "PERIGO 2: Aplicação incorreta da separação CDP": [
        ("Separação CDP não avaliada no TVTOP", "N/A") # Placeholder estrutural (conforme manual)
    ],
    "PERIGO 3: Transferência dos tráfegos para as FIR estrangeiras com a separação menor que a prevista": [
        ("As transferências para as FIR adjacentes nacionais foram realizadas conforme previsto?", "Não"),
        ("As transferências para as FIR adjacentes estrangeiras foram realizadas conforme previsto?", "Não"),
        ("Foram observadas dúvidas quanto à aplicação correta da separação prevista durante o recebimento ou a transferência dos tráfegos?", "Sim"),
        ("Foram observadas transferências de tráfegos em condições incompatíveis com a separação prevista?", "Sim"),
        ("Foram observadas intervenções ou coordenação adicionais, devido a necessidade de adequação da separação aplicada durante a transferência dos tráfegos?", "Sim")
    ],
    "PERIGO 4: Aplicação incorreta dos procedimentos operacionais após a perda da capacidade PBCS geral ou parcial, ou após a não conexão datalink de uma aeronave capacitada": [
        ("Em situações de degradação total ou parcial, houve erros de interpretação ou percepção quanto às informações que constam nos planos de voo?", "Sim"),
        ("As ações esperadas do ATCO, relacionadas à degradação total ou parcial do sistema de enlace de dados, foram atendidas?", "Não"),
        ("O ATCO identificou e realizou os procedimentos previstos após a falha na criação das pistas navegadas durante uma situação de degradação total ou parcial do enlace de dados?", "Não"),
        ("O ATCO verificou o status PBCS no plano de voo durante uma situação de degradação total ou parcial do enlace de dados?", "Não"),
        ("O ATCO realizou o procedimento previsto em situações de permanência dos parâmetros PBCS da aeronave declarados em plano de voo após a ausência de conexão datalink para operadores que declaram capacidade PBCS?", "Não"),
        ("O ATCO realizou o procedimento previsto em situações de permanência da indicação de conexão datalink para a aviônica após o SAGITARIO desabilitar as funções datalink para o ATCO?", "Não")
    ],
    "PERIGO 5: Inserção incorreta das capacidades operacionais PBCS da aeronave no plano de voo": [
        ("Houve alguma situação de inserção de dados relativos à capacidade PBCS durante a solicitação de confecção do plano de voo ao operador AIS?", "Sim"),
        ("Houve alguma interação do ATCO com o plano pré-ativo, a fim de modificar o status PBCS da aeronave?", "Sim"),
        ("Houve a solicitação ou a criação de planos de voo a partir de dados anteriores (plano de voo terminados)?", "Sim"),
        ("Houve alguma correção dos dados do plano de voo relacionados a capacidade PBCS?", "Sim"),
        ("Houve alguma situação em que o FPL não foi recebido pelo ACC-AO?", "Sim")
    ],
    "FERRAMENTAS GRSO": [
        ("Foram utilizados, nos casos de desvios horizontais, os formulários LLE/LLD e realizadas as respectivas notificações (SRO/FNO)?", "Não"),
        ("Foram realizadas notificações voluntárias referentes às condições latentes, por meio de RELPREV?", "Não")
    ]
}

ocorrencias_registradas = []
formulario_valido = True

# --- SEÇÃO 3: Triagem e Fichas Múltiplas ---
if not plantao_sem_alteracoes:
    st.markdown("### 3. DETALHAMENTO DO CHECKLIST")
    st.info("Responda as perguntas abaixo. Caso a resposta indique uma anomalia para aquele item, a Ficha de Ocorrência será disponibilizada para preenchimento.")
    
    for perigo, perguntas in checklist_seguranca.items():
        st.markdown(f"#### {perigo}")
        
        # Oculta as perguntas do Perigo 2 conforme a restrição do manual
        if "PERIGO 2" in perigo:
            st.caption("*(Não avaliado no TVTOP)*")
            continue
            
        for idx_p, (pergunta, resposta_anomalia) in enumerate(perguntas):
            # Gera um ID único e seguro baseado no perigo e no index da pergunta
            p_id = f"rad_{perigo[:8].replace(' ', '')}_{idx_p}"
            
            resposta = st.radio(f"**{pergunta}**", ["Sim", "Não", "N/A"], index=2, horizontal=True, key=f"seg_{p_id}")
            
            # Lógica inteligente: se a resposta equivaler a uma anomalia, abre o form
            if resposta == resposta_anomalia:
                qtd_eventos = st.number_input(f"⚠️ Quantidade de ocorrências vinculadas a esta questão", min_value=1, max_value=20, value=1, step=1, key=f"seg_qtd_{p_id}")
                
                for i in range(qtd_eventos):
                    with st.container(border=True):
                        st.markdown(f"📄 **Ficha de Ocorrência (Evento {i+1} de {qtd_eventos}):**")
                        
                        c1, c2, c3 = st.columns(3)
                        origem = c1.selectbox("Método de Coleta", ["Observação direta da operação", "Relatório de Prevenção (RELPREV)", "Outro"], key=f"seg_orig_{p_id}_{i}")
                        h_in = c2.text_input("Horário Início (Z) Ex: 1430", key=f"seg_hin_{p_id}_{i}")
                        h_out = c3.text_input("Horário Término (Z) Opcional", key=f"seg_hout_{p_id}_{i}")
                        
                        criticidade = st.selectbox("Classificação da Ocorrência", 
                                                   ["NÃO CRÍTICO (Escrito no relatório diário)", 
                                                    "CRÍTICO (Comunicar imediatamente ao supervisor local e avaliar suspensão)"], 
                                                   key=f"seg_crit_{p_id}_{i}")
                        
                        ca1, ca2 = st.columns(2)
                        callsigns = ca1.text_input("Callsign(s) / Matrícula(s) da Aeronave", key=f"seg_call_{p_id}_{i}")
                        setor = ca2.text_input("Posição ATC / Setor", key=f"seg_setor_{p_id}_{i}")
                        
                        descricao = st.text_area("Descrição detalhada do Evento", key=f"seg_desc_{p_id}_{i}")
                        
                        st.markdown("**Ações Adotadas pela Equipe/Supervisão:**")
                        cb1, cb2, cb3 = st.columns(3)
                        acao_relprev = cb1.checkbox("Preenchimento de RELPREV", key=f"seg_acao_relprev_{p_id}_{i}")
                        acao_fno = cb2.checkbox("Abrir FNO", key=f"seg_acao_fno_{p_id}_{i}")
                        acao_avaliar_retorno = cb3.checkbox("Avaliar retorno", key=f"seg_acao_retorno_{p_id}_{i}")
                        outras_acoes = st.text_input("Outras providências", key=f"seg_outras_{p_id}_{i}")
                        
                        if not descricao.strip() or not h_in.strip():
                            st.warning(f"⚠️ Preencha pelo menos o 'Horário de Início' e a 'Descrição do Evento' no Evento {i+1}.")
                            formulario_valido = False
                        else:
                            ocorrencias_registradas.append({
                                "indicador": f"[{perigo.split(':')[0]}] {pergunta} (Evento {i+1})",
                                "origem": origem,
                                "h_inicio": h_in,
                                "h_fim": h_out,
                                "criticidade": criticidade.split(" (")[0], 
                                "callsigns": callsigns,
                                "setor": setor,
                                "descricao": descricao,
                                "acao_relprev": acao_relprev,
                                "acao_fno": acao_fno,
                                "acao_avaliar_retorno": acao_avaliar_retorno,
                                "outras_acoes": outras_acoes
                            })
        st.markdown("---") # Linha divisória entre perigos
else:
    st.success("✅ Turno sem ocorrências de segurança. O relatório será gerado contendo a Declaração de Normalidade.")

# --- SEÇÃO 4: Acompanhamento de Registros Anteriores ---
st.markdown("### 4. ACOMPANHAMENTO DE REGISTROS ANTERIORES")
st.info("💡 Utilize este espaço para registrar atualizações de segurança operacional reportadas em plantões anteriores.")
with st.container(border=True):
    col_data_ant, col_vazia = st.columns([1, 2])
    data_registro_ant = col_data_ant.date_input(
        "Data do registro da ocorrência original", 
        value=datetime.date.today(),
        max_value=datetime.date.today(),
        key="seg_data_ant"
    )
    texto_acompanhamento = st.text_area("Acompanhamento / Solução", key="seg_texto_ant")


# --- SEÇÃO 5: Outras Ocorrências ---
st.markdown("### 5. OUTRAS OCORRÊNCIAS / OBSERVAÇÕES GERAIS")
st.info("💡 Utilize este espaço para registrar demais ocorrências não abarcadas pelos itens anteriores.")
with st.container(border=True):
    texto_outras_ocorrencias = st.text_area("Descrição de ocorrências adicionais (Deixe em branco se não houver)", key="seg_texto_outras")


# --- Geração e Download do PDF ---
st.markdown("---")

pode_gerar = formulario_valido and sup_acc.strip() and sup_tiop.strip() and analista_seg.strip()

if pode_gerar:
    pdf = RelatorioSegurancaPDF()
    pdf.add_page()
    
    pdf.adicionar_identificacao(
        data_relatorio, fase_tvtop, 
        hr_inicio.strftime('%H:%M'), hr_fim.strftime('%H:%M'), 
        sup_tiop, sup_acc, analista_seg
    )
    
    sem_anomalias = plantao_sem_alteracoes or not ocorrencias_registradas
    pdf.adicionar_declaracao_normalidade(sem_anomalias)
    
    if not sem_anomalias:
        for idx, ocorrencia in enumerate(ocorrencias_registradas, start=1):
            pdf.adicionar_ficha_ocorrencia(idx, ocorrencia["indicador"], ocorrencia)
    
    pdf.adicionar_acompanhamento(data_registro_ant, texto_acompanhamento)
    
    pdf.adicionar_outras_ocorrencias(texto_outras_ocorrencias)
    
    pdf.adicionar_assinaturas(analista_seg)
            
    pdf_bytes = bytes(pdf.output())
    
    # Nome do arquivo padronizado
    mes_abrev = MESES_PT[data_relatorio.month]
    dia_str = data_relatorio.strftime('%d')
    nome_arquivo = f"REL_GRSO_{dia_str}_{mes_abrev}.pdf"

    st.download_button(
        label="⬇️ Gerar e Baixar PDF de Segurança",
        data=pdf_bytes,
        file_name=nome_arquivo,
        mime="application/pdf",
        type="primary"
    )
else:
    st.button("🚀 Gerar e Baixar PDF de Segurança", type="primary", disabled=True)
    st.error("⚠️ Preencha os 3 nomes da equipe (Sup TIOP, Sup ACC e Analista de Segurança) e corrija os avisos do formulário para liberar o download do PDF.")


if st.button("🗑️ Iniciar Novo Registro de Segurança (Zerar Formulário)"):
    limpar_dados_seguranca()
# Gatilho automático de salvamento JSON
salvar_tela_inteira()