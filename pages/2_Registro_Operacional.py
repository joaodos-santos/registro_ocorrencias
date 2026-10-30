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
class RelatorioOperacionalPDF(FPDF):
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
        self.cell(0, 5, "CINDACTA III - CENTRO DE CONTROLE DE ÁREA (ACC-AO)", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "B", 12)
        self.cell(0, 6, "RELATÓRIO DIÁRIO DE OCORRÊNCIAS OPERACIONAIS - TVTOP PBCS", align="C", new_x="LMARGIN", new_y="NEXT")
        
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

    def adicionar_identificacao(self, data, fase, h_inicio, h_fim, sup_acc, sup_tiop, analista_op):
        self.desenhar_secao("1. IDENTIFICAÇÃO DO TURNO E DA JANELA DE TESTE")
        self.set_font("helvetica", "", 9)
        self.cell(0, 5, f"Data: {data.strftime('%d/%m/%Y')}    |    Fase do TVTOP: {fase}", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, f"Horário Efetivo de Teste: Início: {h_inicio} UTC    |    Término: {h_fim} UTC", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        
        self.set_font("helvetica", "B", 9)
        self.cell(0, 5, "Equipe de Serviço:", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "", 9)
        self.cell(0, 5, f"- Supervisor Operacional (ACC-AO): {sup_acc}", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, f"- Supervisor Técnico (TIOP): {sup_tiop}", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        
        self.set_font("helvetica", "B", 9)
        self.cell(0, 5, "Equipe TVTOP:", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "", 9)
        self.cell(0, 5, f"- Analista Operacional: {analista_op}", new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def adicionar_declaracao_normalidade(self, sem_anomalias):
        self.desenhar_secao("2. DECLARAÇÃO DE TURNO SEM ANOMALIAS")
        self.set_font("helvetica", "", 9)
        marcador = "[X]" if sem_anomalias else "[ ]"
        texto = f"{marcador} DECLARO que, durante a janela de aplicação dos testes no presente turno, NÃO HOUVE ocorrência ou observação de qualquer violação dos indicadores operacionais do TVTOP PBCS."
        self.multi_cell(0, 5, texto, new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def adicionar_ficha_ocorrencia(self, num, ind_afetado, dados):
        self.desenhar_secao(f"3. DETALHAMENTO: FICHA DE OCORRÊNCIA N° {num:02d}")
        
        self.set_font("helvetica", "B", 9)
        self.multi_cell(0, 5, f"Indicador Afetado: {ind_afetado}", new_x="LMARGIN", new_y="NEXT")
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
        if dados["acao_instrucao"]: acoes_texto += "- [X] Reforçar instrução ao efetivo (Briefing e correção pontual)\n"
        if dados["acao_fno"]: acoes_texto += "- [X] Abrir FNO e avaliar retorno ao TVTOp\n"
        if dados["acao_sisgtec"]: acoes_texto += "- [X] Acionar SUP Técnico / Abrir chamado SISGTEC\n"
        if dados["outras_acoes"]: acoes_texto += f"- Outras: {dados['outras_acoes']}"
        
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

    def adicionar_assinaturas(self, analista_op):
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
        self.cell(0, 5, analista_op.upper() if analista_op else "Analista Operacional", align="C", new_x="LMARGIN", new_y="NEXT")
        
        self.set_font("helvetica", "", 8)
        self.cell(0, 5, "Analista Operacional - Equipe TVTOP", align="C", new_x="LMARGIN", new_y="NEXT")

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
st.set_page_config(page_title="Registro Operacional", layout="wide")

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
if st.session_state.get("perfil_autorizado") != "Operacional":
    st.warning(f"⚠️ **Acesso Restrito.** Você iniciou o turno logado como **{st.session_state.get('perfil_autorizado')}**.")
    st.info("Para acessar o Registro Operacional, retorne à página inicial e selecione o perfil correto.")
    if st.button("🏠 Voltar para o Início"):
        st.switch_page("Principal.py")
    st.stop() # Freio de mão: impede o Python de ler o resto do arquivo e criar o JSON errado!

# ==========================================
# LÓGICA DE PERSISTÊNCIA DE DADOS (JSON)
# ==========================================
# 2. RASCUNHO DINÂMICO (Usa o nome digitado na Home para criar um arquivo único)
usuario_arq = st.session_state["usuario_arquivo"]
ARQUIVO_RASCUNHO = f"/tiop/dados-containers/tvtop/rascunho_operacional_{usuario_arq}.json"

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

# CARREGAMENTO ISOLADO
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

# SALVAMENTO ISOLADO (COM FILTRO op_)
def salvar_tela_inteira():
    dados_tela = {
        k: v for k, v in st.session_state.items() 
        if k.startswith("op_") and not k.startswith("FormSubmitter")
    }
    estado_atual = {
        "data_registro": data_operacional,
        "dados": dados_tela
    }
    try:
        with open(ARQUIVO_RASCUNHO, "w") as f:
            json.dump(estado_atual, f, cls=RascunhoEncoder)
    except Exception as e:
        print(f"Erro ao salvar JSON no arquivo {ARQUIVO_RASCUNHO}: {e}")

# LIMPEZA ISOLADA
def limpar_dados_operacional():
    if os.path.exists(ARQUIVO_RASCUNHO):
        try:
            os.remove(ARQUIVO_RASCUNHO)
        except:
            pass
            
    for chave in list(st.session_state.keys()):
        if chave.startswith("op_"):
            del st.session_state[chave]
            
    st.components.v1.html("<script>window.parent.location.reload();</script>", height=0)

#if st.sidebar.button("🗑️ Iniciar Novo Registro Operacional (Zerar)"):
#    limpar_dados_operacional()

# ==========================================


# Função para atualizar horários baseados na fase selecionada
def atualizar_horarios_op():
    if "Fase 1" in st.session_state.get("op_fase", ""):
        st.session_state["op_hr_in"] = datetime.time(13, 0)
        st.session_state["op_hr_out"] = datetime.time(19, 0)
    else:
        st.session_state["op_hr_in"] = datetime.time(23, 0)
        st.session_state["op_hr_out"] = datetime.time(6, 0)

# Inicialização padrão para a primeira vez que a página carrega
if "op_hr_in" not in st.session_state:
    st.session_state["op_hr_in"] = datetime.time(13, 0)
    st.session_state["op_hr_out"] = datetime.time(19, 0)

st.title("📡 TVTOP PBCS - Registro Operacional")

# --- SEÇÃO 1: Identificação ---
st.markdown("### 1. IDENTIFICAÇÃO DO TURNO E DA JANELA DE TESTE")
with st.container(border=True):
    col_data, col_fase, col_hin, col_hout = st.columns(4)
    data_relatorio = col_data.date_input("Data do Relatório", datetime.date.today(), key="op_data")
    fase_tvtop = col_fase.selectbox("Fase do TVTOP", ["Fase 1 (13:00-19:00Z)", "Fase 2 (23:00-06:00Z)"], key="op_fase", on_change=atualizar_horarios_op)
    hr_inicio = col_hin.time_input("Início (UTC)", key="op_hr_in")
    hr_fim = col_hout.time_input("Término (UTC)", key="op_hr_out")
    
    st.markdown("##### Equipe de Serviço")
    c_acc, c_tiop = st.columns(2)
    sup_acc = c_acc.text_input("Supervisor Operacional (ACC-AO)", key="op_sup_acc")
    sup_tiop = c_tiop.text_input("Supervisor Técnico (TIOP)", key="op_sup_tiop")
    
    st.markdown("##### Equipe TVTOP")
    analista_op = st.text_input("Analista Operacional", key="op_analista")

# --- SEÇÃO 2: Declaração Geral ---
st.markdown("### 2. DECLARAÇÃO GERAL")
with st.container(border=True):
    plantao_sem_alteracoes = st.toggle("✅ DECLARAÇÃO DE TURNO SEM ANOMALIAS (Marcar se NÃO HOUVE ocorrências operacionais no turno)", value=False, key="op_toggle")

lista_indicadores_op = [
    "IND-OP-01: Aplicação incorreta dos mínimos de separação longitudinal/lateral",
    "IND-OP-02: Aplicação ineficiente da separação longitudinal/lateral",
    "IND-OP-03: Aplicação incorreta dos procedimentos do plano de degradação",
    "IND-OP-04: Inserção incorreta das informações na FPVE e/ou etiqueta eletrônica",
    "IND-OP-05: Interpretação inadequada aos alertas de conflito",
    "IND-OP-06: Inserção manual de capacidade PBCS sem FPL",
    "IND-OP-07: Mudança da capacidade PBCS no FPL com base em reporte do piloto",
    "IND-OP-08: Uso de dados de planos de voo terminados para criação de novo FPL",
    "IND-OP-09: Qualquer outro comportamento inesperado da IHM SAGITARIO PBCS"
]

ocorrencias_registradas = []
formulario_valido = True

# --- SEÇÃO 3: Triagem e Fichas Múltiplas ---
if not plantao_sem_alteracoes:
    st.markdown("### 3. DETALHAMENTO DAS OCORRÊNCIAS OBSERVADAS")
    st.info("Caso um indicador apresente anomalias, marque 'Sim' e informe a quantidade de eventos distintos que ocorreram para ele no turno.")
    
    for ind in lista_indicadores_op:
        observado = st.radio(f"**{ind}** - Observado?", ["Não", "Sim"], horizontal=True, key=f"op_rad_{ind}")
        
        if observado == "Sim":
            qtd_eventos = st.number_input(f"Quantidade de ocorrências registradas para {ind[:9]}", min_value=1, max_value=20, value=1, step=1, key=f"op_qtd_{ind}")
            
            for i in range(qtd_eventos):
                with st.container(border=True):
                    st.markdown(f"📄 **Ficha de Ocorrência (Evento {i+1} de {qtd_eventos}):** {ind}")
                    
                    c1, c2, c3 = st.columns(3)
                    origem = c1.selectbox("Método de Coleta", ["Observação direta da operação", "Registros do C-AIS", "Outro"], key=f"op_orig_{ind}_{i}")
                    h_in = c2.text_input("Horário Início (Z) Ex: 1430", key=f"op_hin_{ind}_{i}")
                    h_out = c3.text_input("Horário Término (Z) Opcional", key=f"op_hout_{ind}_{i}")
                    
                    criticidade = st.selectbox("Classificação da Ocorrência", 
                                               ["NÃO CRÍTICO (Escrito no relatório diário)", 
                                                "CRÍTICO (Comunicar imediatamente ao supervisor local e avaliar suspensão)"], 
                                               key=f"op_crit_{ind}_{i}")
                    
                    ca1, ca2 = st.columns(2)
                    callsigns = ca1.text_input("Callsign(s) / Matrícula(s) da Aeronave", key=f"op_call_{ind}_{i}")
                    setor = ca2.text_input("Posição ATC / Setor", key=f"op_setor_{ind}_{i}")
                    
                    descricao = st.text_area("Descrição detalhada do Evento", key=f"op_desc_{ind}_{i}")
                    
                    st.markdown("**Ações Adotadas pela Equipe/Supervisão:**")
                    cb1, cb2, cb3 = st.columns(3)
                    acao_instrucao = cb1.checkbox("Reforçar instrução (Briefing/Correção)", key=f"op_acao_inst_{ind}_{i}")
                    acao_fno = cb2.checkbox("Abrir FNO / Avaliar retorno", key=f"op_acao_fno_{ind}_{i}")
                    acao_sisgtec = cb3.checkbox("Acionar SUP Téc. / SISGTEC", key=f"op_acao_sisg_{ind}_{i}")
                    outras_acoes = st.text_input("Outras providências", key=f"op_outras_{ind}_{i}")
                    
                    if not descricao.strip() or not h_in.strip():
                        st.warning(f"⚠️ Preencha pelo menos o 'Horário de Início' e a 'Descrição do Evento' no Evento {i+1}.")
                        formulario_valido = False
                    else:
                        ocorrencias_registradas.append({
                            "indicador": f"{ind} (Evento {i+1})",
                            "origem": origem,
                            "h_inicio": h_in,
                            "h_fim": h_out,
                            "criticidade": criticidade.split(" (")[0], 
                            "callsigns": callsigns,
                            "setor": setor,
                            "descricao": descricao,
                            "acao_instrucao": acao_instrucao,
                            "acao_fno": acao_fno,
                            "acao_sisgtec": acao_sisgtec,
                            "outras_acoes": outras_acoes
                        })
else:
    st.success("✅ Turno sem alterações operacionais. O relatório será gerado contendo a Declaração de Normalidade.")

# --- SEÇÃO 4: Acompanhamento de Registros Anteriores ---
st.markdown("### 4. ACOMPANHAMENTO DE REGISTROS ANTERIORES")
st.info("💡 Utilize este espaço para registrar atualizações operacionais ou correções pontuais de plantões anteriores.")
with st.container(border=True):
    col_data_ant, col_vazia = st.columns([1, 2])
    data_registro_ant = col_data_ant.date_input(
        "Data do registro da ocorrência original", 
        value=datetime.date.today(),
        max_value=datetime.date.today(),
        key="op_data_ant"
    )
    texto_acompanhamento = st.text_area("Acompanhamento / Solução", key="op_texto_ant")


# --- SEÇÃO 5: Outras Ocorrências ---
st.markdown("### 5. OUTRAS OCORRÊNCIAS / OBSERVAÇÕES GERAIS")
st.info("💡 Utilize este espaço para registrar demais ocorrências não abarcadas pelos itens anteriores.")
with st.container(border=True):
    texto_outras_ocorrencias = st.text_area("Descrição de ocorrências adicionais (Deixe em branco se não houver)", key="op_texto_outras")


# --- Geração e Download do PDF ---
st.markdown("---")

pode_gerar = formulario_valido and sup_acc.strip() and sup_tiop.strip() and analista_op.strip()

if pode_gerar:
    pdf = RelatorioOperacionalPDF()
    pdf.add_page()
    
    pdf.adicionar_identificacao(
        data_relatorio, fase_tvtop, 
        hr_inicio.strftime('%H:%M'), hr_fim.strftime('%H:%M'), 
        sup_acc, sup_tiop, analista_op
    )
    
    sem_anomalias = plantao_sem_alteracoes or not ocorrencias_registradas
    pdf.adicionar_declaracao_normalidade(sem_anomalias)
    
    if not sem_anomalias:
        for idx, ocorrencia in enumerate(ocorrencias_registradas, start=1):
            pdf.adicionar_ficha_ocorrencia(idx, ocorrencia["indicador"], ocorrencia)
    
    pdf.adicionar_acompanhamento(data_registro_ant, texto_acompanhamento)
    
    pdf.adicionar_outras_ocorrencias(texto_outras_ocorrencias)
    
    pdf.adicionar_assinaturas(analista_op)
            
    pdf_bytes = bytes(pdf.output())
    
    # Nome do arquivo padronizado
    mes_abrev = MESES_PT[data_relatorio.month]
    dia_str = data_relatorio.strftime('%d')
    nome_arquivo = f"REL_OP_{dia_str}_{mes_abrev}.pdf"

    st.download_button(
        label="⬇️ Gerar e Baixar PDF Operacional",
        data=pdf_bytes,
        file_name=nome_arquivo,
        mime="application/pdf",
        type="primary"
    )
else:
    st.button("🚀 Gerar e Baixar PDF Operacional", type="primary", disabled=True)
    st.error("⚠️ Preencha os 3 nomes da equipe (Sup ACC, Sup TIOP e Analista) e corrija os avisos do formulário para liberar o download do PDF.")

if st.button("🗑️ Iniciar Novo Registro Operacional (Zerar Formulário)"):
    limpar_dados_operacional()
# Gatilho automático de salvamento JSON
salvar_tela_inteira()