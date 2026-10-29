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
class RelatorioTVTOpPDF(FPDF):
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
        self.cell(0, 5, "CINDACTA III - SEÇÃO DE INFORMÁTICA OPERACIONAL (TIOP)", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "B", 12)
        self.cell(0, 6, "RELATÓRIO DIÁRIO DE OCORRÊNCIAS TÉCNICAS - TVTOP PBCS", align="C", new_x="LMARGIN", new_y="NEXT")
        
        # Força a linha a ser desenhada abaixo do limite inferior das imagens
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

    def adicionar_identificacao(self, data, fase, h_inicio, h_fim, sup_tiop, sup_acc, analista_tec):
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
        self.cell(0, 5, f"- Analista Técnico: {analista_tec}", new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def adicionar_declaracao_normalidade(self, sem_anomalias):
        self.desenhar_secao("2. DECLARAÇÃO DE TURNO SEM ANOMALIAS")
        self.set_font("helvetica", "", 9)
        marcador = "[X]" if sem_anomalias else "[ ]"
        texto = f"{marcador} DECLARO que, durante a janela de aplicação dos testes no presente turno, NÃO HOUVE ocorrência ou observação de qualquer violação dos indicadores técnicos do TVTOP PBCS."
        self.multi_cell(0, 5, texto, new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def adicionar_ficha_ocorrencia(self, num, ind_afetado, dados):
        self.desenhar_secao(f"3. DETALHAMENTO: FICHA DE OCORRÊNCIA N° {num:02d}")
        
        self.set_font("helvetica", "B", 9)
        self.cell(0, 5, f"Indicador Afetado: {ind_afetado}", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        
        self.cell(0, 5, "Constatação e Horários:", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "", 9)
        origem_str = dados["origem"]
        if dados["origem"] == "Reporte ACC-AO" and dados.get("militar_acc"):
            origem_str += f" (Militar: {dados['militar_acc']})"
        self.cell(0, 5, f"- Origem: {origem_str}", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, f"- Horários: Início: {dados['h_inicio']}Z | Término: {dados['h_fim']}Z | Duração: {dados['duracao']} min", new_x="LMARGIN", new_y="NEXT")
        
        self.set_font("helvetica", "B", 9)
        self.cell(0, 5, f"Criticidade Atribuída: {dados['criticidade']}", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

        self.set_font("helvetica", "B", 9)
        self.cell(0, 5, "Aeronaves / Setores / Servidores:", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "", 9)
        self.cell(0, 5, f"- Callsign(s) / Matrícula(s): {dados['callsigns']}", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, f"- Posição ATC / Setor: {dados['setor']}", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, f"- Servidor / Equipamento: {dados['servidor']}", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

        self.set_font("helvetica", "B", 9)
        self.cell(0, 5, "Descrição & Ações / Chamados:", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "", 9)
        self.multi_cell(0, 5, f"Descrição do Evento:\n{dados['descricao']}", new_x="LMARGIN", new_y="NEXT")
        
        acoes_texto = "Ações Tomadas:\n"
        if dados["log_24h"]: acoes_texto += "- [X] Análise de logs 24h\n"
        if dados["chamado_atech"]: acoes_texto += f"- [X] Chamado ATECH N°: {dados['num_atech']}\n"
        if dados["chamado_sita"]: acoes_texto += f"- [X] Chamado SITA N°: {dados['num_sita']}\n"
        if dados["outras_acoes"]: acoes_texto += f"- Outras providências: {dados['outras_acoes']}"
        
        self.multi_cell(0, 5, acoes_texto, new_x="LMARGIN", new_y="NEXT")
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

    def adicionar_assinaturas(self, sup_tiop, analista_tec):
        if self.get_y() > (self.h - 60):
            self.add_page()
            
        self.desenhar_secao("6. ASSINATURA E ENCAMINHAMENTO")
        self.set_font("helvetica", "", 9)
        self.multi_cell(0, 5, "O arquivo PDF assinado deverá ser arquivado conforme determinado pelo Gerente do Projeto PBCS.", new_x="LMARGIN", new_y="NEXT")
        self.ln(20)

        y_atual = self.get_y()
        self.set_line_width(0.3)
        self.set_draw_color(0, 0, 0)
        
        self.line(20, y_atual, 90, y_atual)
        self.line(120, y_atual, 190, y_atual)
        
        self.set_y(y_atual + 2)
        self.set_font("helvetica", "B", 9)
        self.cell(90, 5, sup_tiop.upper() if sup_tiop else "Supervisor Técnico da TIOp", align="C")
        self.cell(10, 5, "")
        self.cell(90, 5, analista_tec.upper() if analista_tec else "Analista Técnico", align="C", new_x="LMARGIN", new_y="NEXT")
        
        self.set_font("helvetica", "", 8)
        self.cell(90, 5, "Supervisor Técnico - TIOp", align="C")
        self.cell(10, 5, "")
        self.cell(90, 5, "Analista Técnico - Equipe TVTOP", align="C", new_x="LMARGIN", new_y="NEXT")


# ==========================================
# INTERFACE STREAMLIT DA PÁGINA
# ==========================================
st.set_page_config(page_title="Registro Técnico", layout="wide")

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
if st.session_state.get("perfil_autorizado") != "Técnico":
    st.warning(f"⚠️ **Acesso Restrito.** Você iniciou o turno logado como **{st.session_state.get('perfil_autorizado')}**.")
    st.info("Para acessar o Registro Técnico, retorne à página inicial e selecione o perfil correto.")
    if st.button("🏠 Voltar para o Início"):
        st.switch_page("Principal.py")
    st.stop() # Freio de mão: impede o Python de ler o resto do arquivo e criar o JSON errado!

# ==========================================
# LÓGICA DE PERSISTÊNCIA DE DADOS (JSON)
# ==========================================
# 2. RASCUNHO DINÂMICO (Usa o nome digitado na Home para criar um arquivo único)
usuario_arq = st.session_state["usuario_arquivo"]
ARQUIVO_RASCUNHO = f"/tiop/dados-containers/tvtop/rascunho_tecnico_{usuario_arq}.json"

class RascunhoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.time, datetime.datetime)):
            return obj.isoformat()
        # Blindagem: se for algo desconhecido, converte para string em vez de crashar
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

# SALVAMENTO ISOLADO (COM FILTRO tec_)
def salvar_tela_inteira():
    dados_tela = {
        k: v for k, v in st.session_state.items() 
        if k.startswith("tec_") and not k.startswith("FormSubmitter")
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
def limpar_dados_tecnico():
    if os.path.exists(ARQUIVO_RASCUNHO):
        try:
            os.remove(ARQUIVO_RASCUNHO)
        except:
            pass
            
    for chave in list(st.session_state.keys()):
        if chave.startswith("tec_"):
            del st.session_state[chave]
            
    st.components.v1.html("<script>window.parent.location.reload();</script>", height=0)

#if st.sidebar.button("🗑️ Iniciar Novo Registro Técnico (Zerar)"):
 #   limpar_dados_tecnico()

# ==========================================

# Função para atualizar horários baseados na fase selecionada
def atualizar_horarios_tec():
    # Agora procura pela chave com prefixo tec_
    if "Fase 1" in st.session_state.get("tec_fase", ""):
        st.session_state["tec_hr_in"] = datetime.time(13, 0)
        st.session_state["tec_hr_out"] = datetime.time(19, 0)
    else:
        st.session_state["tec_hr_in"] = datetime.time(23, 0)
        st.session_state["tec_hr_out"] = datetime.time(6, 0)

# Inicialização padrão para a primeira vez que a página carrega
if "tec_hr_in" not in st.session_state:
    st.session_state["tec_hr_in"] = datetime.time(13, 0)
    st.session_state["tec_hr_out"] = datetime.time(19, 0)

st.title("🔧 TVTOP PBCS - Registro Técnico")

# --- SEÇÃO 1: Identificação ---
st.markdown("### 1. IDENTIFICAÇÃO DO TURNO E DA JANELA DE TESTE")
with st.container(border=True):
    col_data, col_fase, col_hin, col_hout = st.columns(4)
    data_relatorio = col_data.date_input("Data do Relatório", datetime.date.today(), key="tec_data")
    fase_tvtop = col_fase.selectbox("Fase do TVTOP", ["Fase 1 (13:00-19:00Z)", "Fase 2 (23:00-06:00Z)"], key="tec_fase", on_change=atualizar_horarios_tec)
    hr_inicio = col_hin.time_input("Início (UTC)", key="tec_hr_in")
    hr_fim = col_hout.time_input("Término (UTC)", key="tec_hr_out")
    
    st.markdown("##### Equipe de Serviço")
    c_tiop, c_acc = st.columns(2)
    sup_tiop = c_tiop.text_input("Supervisor Técnico (TIOP)", key="tec_sup_tiop")
    sup_acc = c_acc.text_input("Supervisor Operacional (ACC-AO)", key="tec_sup_acc")
    
    st.markdown("##### Equipe TVTOP")
    analista_tec = st.text_input("Analista Técnico", key="tec_analista")

# --- SEÇÃO 2: Declaração Geral ---
st.markdown("### 2. DECLARAÇÃO GERAL")
with st.container(border=True):
    plantao_sem_alteracoes = st.toggle("✅ DECLARAÇÃO DE TURNO SEM ANOMALIAS (Marcar se NÃO HOUVE ocorrências no turno)", value=False, key="tec_toggle")

lista_indicadores = [
    "IND-01: Desconexões CPDLC/ADS-C por aeronave",
    "IND-02: Perda de Continuidade ACP no sistema",
    "IND-03: Perda de Continuidade ASP no sistema",
    "IND-04: Retirada de Capacidade PBCS pelo ATCO",
    "IND-05: Indisponibilidade DATALINK (>10 min)",
    "IND-06: Chaveamento não programado Servidor STA",
    "IND-07: Divergência de Capacidade (FPL vs SAGITARIO)",
    "IND-08: Inconsistência em Extração de Relatórios (PER)",
    "IND-09: Atendimento Semanal RCP 240 (<99%)",
    "IND-10: Atendimento Semanal RSP 180 (<99%)"
]

ocorrencias_registradas = []
formulario_valido = True

# --- SEÇÃO 3: Triagem e Fichas Múltiplas ---
if not plantao_sem_alteracoes:
    st.markdown("### 3. DETALHAMENTO DAS OCORRÊNCIAS OBSERVADAS")
    st.info("Caso um indicador apresente anomalias, marque 'Sim' e informe a quantidade de eventos distintos que ocorreram para ele no turno.")
    
    for ind in lista_indicadores:
        observado = st.radio(f"**{ind}** - Observado?", ["Não", "Sim"], horizontal=True, key=f"tec_rad_{ind}")
        
        if observado == "Sim":
            qtd_eventos = st.number_input(f"Quantidade de ocorrências registradas para {ind[:6]}", min_value=1, max_value=20, value=1, step=1, key=f"tec_qtd_{ind}")
            
            for i in range(qtd_eventos):
                with st.container(border=True):
                    st.markdown(f"📄 **Ficha de Ocorrência (Evento {i+1} de {qtd_eventos}):** {ind}")
                    
                    c1, c2, c3 = st.columns(3)
                    origem = c1.selectbox("Origem", ["Observação TIOp (Alertas/Logs)", "Reporte ACC-AO"], key=f"tec_orig_{ind}_{i}")
                    militar_acc = ""
                    if origem == "Reporte ACC-AO":
                        militar_acc = c1.text_input("Nome do Militar (ACC-AO)", key=f"tec_mil_{ind}_{i}")
                    
                    h_in = c2.text_input("Horário Início (Z) Ex: 1430", key=f"tec_hin_{ind}_{i}")
                    h_out = c2.text_input("Horário Término (Z)", key=f"tec_hout_{ind}_{i}")
                    duracao = c3.text_input("Duração (min)", key=f"tec_dur_{ind}_{i}")
                    
                    criticidade = st.selectbox("Criticidade Atribuída", 
                                               ["BAIXA/MÉDIA (Registro em relatório diário)", 
                                                "ALTA (Análise técnica imediata + acionamento ATECH/SITA)", 
                                                "CRÍTICO (Aviso imediato Coordenador TVTOP / Supervisor ACC-AO)"], 
                                               key=f"tec_crit_{ind}_{i}")
                    
                    ca1, ca2, ca3 = st.columns(3)
                    callsigns = ca1.text_input("Callsign(s) / Matrícula(s)", key=f"tec_call_{ind}_{i}")
                    setor = ca2.text_input("Posição ATC / Setor", key=f"tec_setor_{ind}_{i}")
                    servidor = ca3.text_input("Servidor / Equipamento", key=f"tec_serv_{ind}_{i}")
                    
                    descricao = st.text_area("Descrição do Evento", key=f"tec_desc_{ind}_{i}")
                    
                    st.markdown("**Ações Tomadas / Chamados:**")
                    cb1, cb2, cb3 = st.columns(3)
                    log_24h = cb1.checkbox("Análise de logs 24h", key=f"tec_log_{ind}_{i}")
                    chamado_atech = cb2.checkbox("Chamado ATECH", key=f"tec_chk_at_{ind}_{i}")
                    num_atech = cb2.text_input("Nº Chamado ATECH", key=f"tec_num_at_{ind}_{i}") if chamado_atech else ""
                    chamado_sita = cb3.checkbox("Chamado SITA", key=f"tec_chk_st_{ind}_{i}")
                    num_sita = cb3.text_input("Nº Chamado SITA", key=f"tec_num_st_{ind}_{i}") if chamado_sita else ""
                    
                    outras_acoes = st.text_input("Outras providências", key=f"tec_outras_{ind}_{i}")
                    
                    if not descricao.strip() or not h_in.strip():
                        st.warning(f"⚠️ Preencha pelo menos o 'Horário de Início' e a 'Descrição do Evento' no Evento {i+1}.")
                        formulario_valido = False
                    else:
                        ocorrencias_registradas.append({
                            "indicador": f"{ind} (Evento {i+1})",
                            "origem": origem,
                            "militar_acc": militar_acc,
                            "h_inicio": h_in,
                            "h_fim": h_out,
                            "duracao": duracao,
                            "criticidade": criticidade.split(" (")[0],
                            "callsigns": callsigns,
                            "setor": setor,
                            "servidor": servidor,
                            "descricao": descricao,
                            "log_24h": log_24h,
                            "chamado_atech": chamado_atech,
                            "num_atech": num_atech,
                            "chamado_sita": chamado_sita,
                            "num_sita": num_sita,
                            "outras_acoes": outras_acoes
                        })
else:
    st.success("✅ Turno sem alterações. O relatório será gerado contendo a Declaração de Normalidade.")

# --- SEÇÃO 4: Acompanhamento de Registros Anteriores ---
st.markdown("### 4. ACOMPANHAMENTO DE REGISTROS ANTERIORES")
st.info("💡 Utilize este espaço para registrar atualizações, soluções ou monitoramento de panes reportadas em plantões anteriores.")
with st.container(border=True):
    col_data_ant, col_vazia = st.columns([1, 2])
    data_registro_ant = col_data_ant.date_input(
        "Data do registro da ocorrência original", 
        value=datetime.date.today(),
        max_value=datetime.date.today(),
        key="tec_data_ant"
    )
    texto_acompanhamento = st.text_area("Acompanhamento / Solução", key="tec_texto_ant")

# --- SEÇÃO 5: Outras Ocorrências ---
st.markdown("### 5. OUTRAS OCORRÊNCIAS / OBSERVAÇÕES GERAIS")
st.info("💡 Utilize este espaço para registrar demais ocorrências não abarcadas pelos itens anteriores.")
with st.container(border=True):
    texto_outras_ocorrencias = st.text_area("Descrição de ocorrências adicionais (Deixe em branco se não houver)", key="tec_texto_outras")


# --- Geração e Download do PDF ---
st.markdown("---")

pode_gerar = formulario_valido and sup_tiop.strip() and sup_acc.strip() and analista_tec.strip()

if pode_gerar:
    pdf = RelatorioTVTOpPDF()
    pdf.add_page()
    
    pdf.adicionar_identificacao(
        data_relatorio, fase_tvtop, 
        hr_inicio.strftime('%H:%M'), hr_fim.strftime('%H:%M'), 
        sup_tiop, sup_acc, analista_tec
    )
    
    sem_anomalias = plantao_sem_alteracoes or not ocorrencias_registradas
    pdf.adicionar_declaracao_normalidade(sem_anomalias)
    
    if not sem_anomalias:
        for idx, ocorrencia in enumerate(ocorrencias_registradas, start=1):
            pdf.adicionar_ficha_ocorrencia(idx, ocorrencia["indicador"], ocorrencia)
    
    pdf.adicionar_acompanhamento(data_registro_ant, texto_acompanhamento)
    
    pdf.adicionar_outras_ocorrencias(texto_outras_ocorrencias)
    
    pdf.adicionar_assinaturas(sup_tiop, analista_tec)
            
    pdf_bytes = bytes(pdf.output())
    
    # Nome do arquivo padronizado
    mes_abrev = MESES_PT[data_relatorio.month]
    dia_str = data_relatorio.strftime('%d')
    nome_arquivo = f"REL_TEC_{dia_str}_{mes_abrev}.pdf"

    st.download_button(
        label="⬇️ Gerar e Baixar PDF Oficial",
        data=pdf_bytes,
        file_name=nome_arquivo,
        mime="application/pdf",
        type="primary"
    )
else:
    st.button("🚀 Gerar e Baixar PDF Oficial", type="primary", disabled=True)
    st.error("⚠️ Preencha os 3 nomes da equipe (Sup TIOP, Sup ACC e Analista) e corrija os avisos do formulário para liberar o download do PDF.")

if st.button("🗑️ Iniciar Novo Registro Técnico (Zerar Formulário)"):
    limpar_dados_tecnico()
# Gatilho automático de salvamento JSON
salvar_tela_inteira()