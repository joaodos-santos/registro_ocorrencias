import streamlit as st
from fpdf import FPDF
import datetime

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
        self.set_font("helvetica", "B", 10)
        self.set_text_color(0, 51, 102)
        self.cell(0, 5, "CINDACTA III - CÉLULA DE SEGURANÇA OPERACIONAL", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "B", 12)
        self.cell(0, 6, "RELATÓRIO DIÁRIO DE OCORRÊNCIAS DE SEGURANÇA - TVTOP PBCS", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(0, 51, 102)
        self.set_line_width(0.5)
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
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
        if dados["acao_relper"]: acoes_texto += "- [X] Preenchimento de Relatório de Perigo (RELPER)\n"
        if dados["acao_fno"]: acoes_texto += "- [X] Abrir FNO e avaliar retorno ao TVTOp\n"
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

    def adicionar_assinaturas(self, analista_seg):
        if self.get_y() > (self.h - 60):
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
        self.line(pos_x, y_atual, pos_x + largura_linha, y_atual)
        
        self.set_y(y_atual + 2)
        self.set_font("helvetica", "B", 9)
        self.cell(0, 5, analista_seg.upper() if analista_seg else "Analista de Segurança", align="C", new_x="LMARGIN", new_y="NEXT")
        
        self.set_font("helvetica", "", 8)
        self.cell(0, 5, "Analista de Segurança - Equipe TVTOP", align="C", new_x="LMARGIN", new_y="NEXT")


# ==========================================
# INTERFACE STREAMLIT DA PÁGINA
# ==========================================
st.set_page_config(page_title="Registro de Segurança", layout="wide")

# Função para atualizar horários baseados na fase selecionada
def atualizar_horarios_seg():
    if "Fase 1" in st.session_state["fase_seg"]:
        st.session_state["hr_in_seg"] = datetime.time(13, 0)
        st.session_state["hr_out_seg"] = datetime.time(19, 0)
    else:
        st.session_state["hr_in_seg"] = datetime.time(23, 0)
        st.session_state["hr_out_seg"] = datetime.time(6, 0)

# Inicialização padrão para a primeira vez que a página carrega
if "hr_in_seg" not in st.session_state:
    st.session_state["hr_in_seg"] = datetime.time(13, 0)
    st.session_state["hr_out_seg"] = datetime.time(19, 0)

st.title("🛡️ TVTOP PBCS - Registro de Segurança")

# --- SEÇÃO 1: Identificação ---
st.markdown("### 1. IDENTIFICAÇÃO DO TURNO E DA JANELA DE TESTE")
with st.container(border=True):
    col_data, col_fase, col_hin, col_hout = st.columns(4)
    data_relatorio = col_data.date_input("Data do Relatório", datetime.date.today(), key="data_seg")
    fase_tvtop = col_fase.selectbox("Fase do TVTOP", ["Fase 1 (13:00-19:00Z)", "Fase 2 (23:00-06:00Z)"], key="fase_seg", on_change=atualizar_horarios_seg)
    hr_inicio = col_hin.time_input("Início (UTC)", key="hr_in_seg")
    hr_fim = col_hout.time_input("Término (UTC)", key="hr_out_seg")
    
    st.markdown("##### Equipe de Serviço")
    c_tiop, c_acc = st.columns(2)
    sup_tiop = c_tiop.text_input("Supervisor Técnico (TIOP)", key="sup_tiop_seg")
    sup_acc = c_acc.text_input("Supervisor Operacional (ACC-AO)", key="sup_acc_seg")
    
    st.markdown("##### Equipe TVTOP")
    analista_seg = st.text_input("Analista de Segurança", key="analista_seg")

# --- SEÇÃO 2: Declaração Geral ---
st.markdown("### 2. DECLARAÇÃO GERAL")
with st.container(border=True):
    plantao_sem_alteracoes = st.toggle("✅ DECLARAÇÃO DE TURNO SEM ANOMALIAS (Marcar se NÃO HOUVE ocorrências de segurança no turno)", value=False, key="toggle_seg")

lista_indicadores_seg = [
    "P1-01: Aplicação dos mínimos de separação por performance",
    "P1-02: Interpretação dos alertas e/ou avisos PBCS",
    "P1-03: Utilização das ferramentas do SAGITARIO associadas ao PBCS",
    "P1-04: Identificação dos desvios laterais",
    "P1-05: Setorizações em relação à carga de trabalho",
    "P1-06: Procedimentos alternativos de comunicação (falha do meio primário)",
    "P1-07: Utilização do zoom do SAGITARIO",
    "P1-08: Utilização da funcionalidade 'Nova Janela' do SAGITARIO",
    "P1-09: Identificação da perda das condições para separação PBCS (degradação)",
    "P1-10: Procedimentos para o restabelecimento dos mínimos convencionais (degradação)",
    "P1-11: Manutenção da consciência situacional na transição (degradação)",
    "P3-01: Transferências para as FIR adjacentes nacionais",
    "P3-02: Transferências para as FIR adjacentes estrangeiras",
    "P3-03: Dúvidas quanto à aplicação correta da separação",
    "P3-04: Transferências em condições incompatíveis com a separação",
    "P3-05: Intervenções ou coordenação adicionais (adequação da separação)",
    "P4-01: Interpretação ou percepção das informações nos planos de voo",
    "P4-02: Ações esperadas do ATCO na degradação do enlace de dados",
    "P4-03: Procedimentos após falha na criação das pistas navegadas",
    "P4-04: Verificação do status PBCS no plano de voo",
    "P4-05: Procedimentos para permanência dos parâmetros PBCS (ausência de conexão)",
    "P4-06: Procedimentos para permanência da indicação de conexão (após desabilitação)",
    "P5-01: Inserção de dados de capacidade PBCS na confecção do plano de voo",
    "P5-02: Interação do ATCO com o plano pré-ativo para modificar status PBCS",
    "P5-03: Solicitação ou criação de planos de voo a partir de dados anteriores",
    "P5-04: Correção dos dados do plano de voo relacionados à capacidade PBCS",
    "P5-05: FPL não recebido pelo ACC-AO",
    "GRSO-01: Formulários LLE/LLD e notificações (SRO/FNO) para desvios horizontais",
    "GRSO-02: Notificações voluntárias referentes às condições latentes (RELPREV)"
]

ocorrencias_registradas = []
formulario_valido = True

# --- SEÇÃO 3: Triagem e Fichas Múltiplas ---
if not plantao_sem_alteracoes:
    st.markdown("### 3. DETALHAMENTO DAS OCORRÊNCIAS OBSERVADAS")
    st.info("Caso seja observada uma anomalia em algum item do checklist, marque 'Sim' e informe a quantidade de eventos distintos no turno.")
    
    for ind in lista_indicadores_seg:
        observado = st.radio(f"**{ind}** - Observado anomalia?", ["Não", "Sim"], horizontal=True, key=f"rad_seg_{ind}")
        
        if observado == "Sim":
            qtd_eventos = st.number_input(f"Quantidade de ocorrências registradas", min_value=1, max_value=20, value=1, step=1, key=f"qtd_{ind}")
            
            for i in range(qtd_eventos):
                with st.container(border=True):
                    st.markdown(f"📄 **Ficha de Ocorrência (Evento {i+1} de {qtd_eventos}):** {ind}")
                    
                    c1, c2, c3 = st.columns(3)
                    origem = c1.selectbox("Método de Coleta", ["Observação direta da operação", "Relato de Perigo (RELPER)", "Outro"], key=f"orig_seg_{ind}_{i}")
                    h_in = c2.text_input("Horário Início (Z) Ex: 1430", key=f"hin_seg_{ind}_{i}")
                    h_out = c3.text_input("Horário Término (Z) Opcional", key=f"hout_seg_{ind}_{i}")
                    
                    criticidade = st.selectbox("Classificação da Ocorrência", 
                                               ["NÃO CRÍTICO (Escrito no relatório diário)", 
                                                "CRÍTICO (Comunicar imediatamente ao supervisor local e avaliar suspensão)"], 
                                               key=f"crit_seg_{ind}_{i}")
                    
                    ca1, ca2 = st.columns(2)
                    callsigns = ca1.text_input("Callsign(s) / Matrícula(s) da Aeronave", key=f"call_seg_{ind}_{i}")
                    setor = ca2.text_input("Posição ATC / Setor", key=f"setor_seg_{ind}_{i}")
                    
                    descricao = st.text_area("Descrição detalhada do Evento", key=f"desc_seg_{ind}_{i}")
                    
                    st.markdown("**Ações Adotadas pela Equipe/Supervisão:**")
                    cb1, cb2 = st.columns(2)
                    acao_relper = cb1.checkbox("Preenchimento de RELPER", key=f"acao_relper_{ind}_{i}")
                    acao_fno = cb2.checkbox("Abrir FNO / Avaliar retorno", key=f"acao_fno_{ind}_{i}")
                    outras_acoes = st.text_input("Outras providências", key=f"outras_seg_{ind}_{i}")
                    
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
                            "acao_relper": acao_relper,
                            "acao_fno": acao_fno,
                            "outras_acoes": outras_acoes
                        })
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
        key="data_ant_seg"
    )
    texto_acompanhamento = st.text_area("Acompanhamento / Solução", key="texto_ant_seg")


# --- SEÇÃO 5: Outras Ocorrências ---
st.markdown("### 5. OUTRAS OCORRÊNCIAS / OBSERVAÇÕES GERAIS")
st.info("💡 Utilize este espaço para registrar demais ocorrências não abarcadas pelos itens anteriores.")
with st.container(border=True):
    texto_outras_ocorrencias = st.text_area("Descrição de ocorrências adicionais (Deixe em branco se não houver)", key="texto_outras_seg")


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
    
    # Adicionando a nova seção de outras ocorrências no PDF
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