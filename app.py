# app.py
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime, date
from database import (
    criar_banco,
    inserir_aluno,
    listar_alunos,
    obter_aluno_por_id,
    atualizar_aluno,
    deletar_aluno,
    registrar_presenca_entrada,
    registrar_presenca_saida,
    listar_presencas,
    criar_usuario,
    autenticar_usuario,
)

# Inicializa banco e usuário admin padrão
criar_banco()

st.set_page_config(page_title="Controle de Alunos Estrangeiros", layout="wide")

# --- Helpers de sessão para autenticação ---
if "user" not in st.session_state:
    st.session_state.user = None

def login(username, password):
    user = autenticar_usuario(username, password)
    if user:
        st.session_state.user = {"id": user.id, "username": user.username, "role": user.role}
        return True
    return False

def logout():
    st.session_state.user = None

# ---- Barra lateral: Login / Logout ----
with st.sidebar:
    st.title("🔐 Acesso")
    if st.session_state.user is None:
        with st.form("login_form"):
            user_in = st.text_input("Usuário")
            pass_in = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar")
            if submitted:
                ok = login(user_in, pass_in)
                if ok:
                    st.success(f"Logado como {st.session_state.user['username']}")
                else:
                    st.error("Usuário ou senha incorretos")
        st.write("---")
        st.write("Usuário padrão: `admin` / senha: `admin123` (troque após o primeiro login)")
    else:
        st.write(f"Logado como **{st.session_state.user['username']}** ({st.session_state.user['role']})")
        if st.button("Sair"):
            logout()
            st.experimental_rerun()

# ---- Menu principal ----
menu = st.sidebar.selectbox("Menu", ["Dashboard", "Cadastrar", "Listar / Buscar", "Presença", "Relatórios", "Usuários (admin)"])

# ---- Dashboard ----
if menu == "Dashboard":
    st.title("📊 Dashboard")
    # Resumo rápido
    alunos = listar_alunos()
    total = len(alunos)
    st.metric("Total de alunos cadastrados", total)

    # Alunos por país e por série (tabelas)
    if alunos:
        df = pd.DataFrame([{
            "ID": a.id,
            "Nome": a.nome,
            "País": a.pais or "",
            "Série": a.serie or "",
            "Entrada": a.data_entrada.isoformat() if a.data_entrada else ""
        } for a in alunos])

        st.subheader("Alunos por País")
        pais_count = df["País"].value_counts().rename_axis("País").reset_index(name="Quantidade")
        st.dataframe(pais_count)

        st.subheader("Alunos por Série")
        serie_count = df["Série"].value_counts().rename_axis("Série").reset_index(name="Quantidade")
        st.dataframe(serie_count)
    else:
        st.info("Nenhum aluno cadastrado ainda.")

# ---- Cadastro ----
elif menu == "Cadastrar":
    st.title("➕ Cadastrar Aluno")
    with st.form("form_cadastrar"):
        nome = st.text_input("Nome completo", max_chars=200)
        idade = st.number_input("Idade", min_value=1, max_value=120, value=15)
        pais = st.text_input("País de origem")
        passaporte = st.text_input("Passaporte / Documento")
        serie = st.text_input("Série / Ano")
        data_entrada = st.date_input("Data de entrada", value=date.today())
        responsavel = st.text_input("Responsável")
        observacoes = st.text_area("Observações")
        btn = st.form_submit_button("Salvar")
        if btn:
            aluno = inserir_aluno(
                nome=nome,
                idade=int(idade),
                pais=pais,
                passaporte=passaporte,
                serie=serie,
                data_entrada=data_entrada,
                responsavel=responsavel,
                observacoes=observacoes,
            )
            st.success(f"Aluno '{aluno.nome}' cadastrado (ID {aluno.id}).")

# ---- Listar / Buscar / Editar / Deletar ----
elif menu == "Listar / Buscar":
    st.title("🔎 Buscar e Gerenciar Alunos")

    with st.expander("Filtros"):
        nome_f = st.text_input("Nome contém")
        pais_f = st.text_input("País (exato)")
        serie_f = st.text_input("Série (exato)")
        col1, col2 = st.columns(2)
        data_inicio = col1.date_input("Data entrada - início", value=None)
        data_fim = col2.date_input("Data entrada - fim", value=None)
        if data_inicio == date(1970,1,1):
            data_inicio = None
        if data_fim == date(1970,1,1):
            data_fim = None
        if st.button("Aplicar filtros"):
            pass

    filtros = {}
    if nome_f:
        filtros["nome"] = nome_f
    if pais_f:
        filtros["pais"] = pais_f
    if serie_f:
        filtros["serie"] = serie_f
    if data_inicio:
        filtros["data_inicio"] = data_inicio
    if data_fim:
        filtros["data_fim"] = data_fim

    alunos = listar_alunos(filtros=filtros if filtros else None)

    if alunos:
        df = pd.DataFrame([{
            "ID": a.id,
            "Nome": a.nome,
            "Idade": a.idade,
            "País": a.pais,
            "Passaporte": a.passaporte,
            "Série": a.serie,
            "Data Entrada": a.data_entrada,
            "Responsável": a.responsavel
        } for a in alunos])
        st.dataframe(df)

        st.write("---")
        st.subheader("Ações rápidas")
        id_selecionado = st.number_input("ID do aluno para ações", min_value=0, step=1)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Ver detalhes / Editar"):
                if id_selecionado <= 0:
                    st.warning("Informe um ID válido.")
                else:
                    a = obter_aluno_por_id(int(id_selecionado))
                    if not a:
                        st.error("Aluno não encontrado.")
                    else:
                        with st.form("editar_form"):
                            nome_e = st.text_input("Nome", value=a.nome)
                            idade_e = st.number_input("Idade", min_value=1, max_value=120, value=a.idade or 1)
                            pais_e = st.text_input("País", value=a.pais or "")
                            pass_e = st.text_input("Passaporte", value=a.passaporte or "")
                            serie_e = st.text_input("Série", value=a.serie or "")
                            data_e = st.date_input("Data entrada", value=a.data_entrada or date.today())
                            resp_e = st.text_input("Responsável", value=a.responsavel or "")
                            obs_e = st.text_area("Observações", value=a.observacoes or "")
                            btn_ed = st.form_submit_button("Salvar alterações")
                            if btn_ed:
                                atualizado = atualizar_aluno(a.id, {
                                    "nome": nome_e,
                                    "idade": int(idade_e),
                                    "pais": pais_e,
                                    "passaporte": pass_e,
                                    "serie": serie_e,
                                    "data_entrada": data_e,
                                    "responsavel": resp_e,
                                    "observacoes": obs_e
                                })
                                if atualizado:
                                    st.success("Aluno atualizado.")
                                else:
                                    st.error("Erro ao atualizar.")
        with col2:
            if st.button("Deletar aluno"):
                if id_selecionado <= 0:
                    st.warning("Informe um ID válido.")
                else:
                    ok = deletar_aluno(int(id_selecionado))
                    if ok:
                        st.success("Aluno deletado.")
                    else:
                        st.error("Aluno não encontrado ou erro.")
        with col3:
            if st.button("Ver histórico de presenças"):
                if id_selecionado <= 0:
                    st.warning("Informe um ID válido.")
                else:
                    pres = listar_presencas(aluno_id=int(id_selecionado))
                    if pres:
                        dfp = pd.DataFrame([{
                            "ID": p.id,
                            "Data": p.data,
                            "Entrada": p.hora_entrada,
                            "Saída": p.hora_saida,
                            "Observação": p.observacao
                        } for p in pres])
                        st.dataframe(dfp)
                    else:
                        st.info("Nenhuma presença registrada para esse aluno.")
    else:
        st.info("Nenhum aluno encontrado com os filtros informados.")

# ---- Presença ----
elif menu == "Presença":
    st.title("🕘 Registro de Presença")

    col1, col2 = st.columns([2,1])
    with col1:
        alunos = listar_alunos()
        options = {a.id: f"{a.id} - {a.nome}" for a in alunos}
        id_sel = st.selectbox("Escolha o aluno", options=[0] + list(options.keys()), format_func=lambda x: "Selecione um aluno" if x==0 else options[x])
        if id_sel and id_sel != 0:
            st.write("Aluno:", options[id_sel])
    with col2:
        now = datetime.now()
        st.write("Agora:", now.strftime("%Y-%m-%d %H:%M:%S"))

    if id_sel and id_sel != 0:
        col_e, col_s = st.columns(2)
        with col_e:
            if st.button("Registrar ENTRADA"):
                p = registrar_presenca_entrada(aluno_id=int(id_sel))
                st.success(f"Entrada registrada (ID pres.: {p.id}) às {p.hora_entrada}")
        with col_s:
            pres_list = listar_presencas(aluno_id=int(id_sel), data_inicio=date.today(), data_fim=date.today())
            # tentar fechar a última com hora_saida vazia
            ultima_aberta = None
            for p in pres_list:
                if p.hora_saida is None:
                    ultima_aberta = p
                    break
            if st.button("Registrar SAÍDA"):
                if ultima_aberta:
                    p2 = registrar_presenca_saida(ultima_aberta.id)
                    st.success(f"Saída registrada: {p2.hora_saida}")
                else:
                    st.warning("Nenhuma entrada aberta encontrada para hoje (não há presenças sem saída).")

    st.write("---")
    st.subheader("Histórico geral de presenças")
    filtro_aluno_hist = st.number_input("Filtrar por ID do aluno (0 para todos)", min_value=0, value=0)
    dt_inicio = st.date_input("Data início", value=date.today())
    dt_fim = st.date_input("Data fim", value=date.today())
    if st.button("Carregar histórico"):
        pres = listar_presencas(aluno_id=(filtro_aluno_hist if filtro_aluno_hist != 0 else None), data_inicio=dt_inicio, data_fim=dt_fim)
        if pres:
            dfp = pd.DataFrame([{
                "ID": p.id,
                "Aluno ID": p.aluno_id,
                "Data": p.data,
                "Entrada": p.hora_entrada,
                "Saída": p.hora_saida,
                "Observação": p.observacao
            } for p in pres])
            st.dataframe(dfp)
        else:
            st.info("Nenhum registro encontrado.")

# ---- Relatórios (export Excel) ----
elif menu == "Relatórios":
    st.title("📥 Exportar Relatórios (Excel)")
    st.write("Escolha filtros e clique em *Gerar Excel* para baixar os dados.")

    nome_f = st.text_input("Nome contém (filtro)")
    pais_f = st.text_input("País (filtro exato)")
    serie_f = st.text_input("Série (filtro exato)")
    col1, col2 = st.columns(2)
    data_inicio = col1.date_input("Data entrada - início", value=None)
    data_fim = col2.date_input("Data entrada - fim", value=None)

    filtros = {}
    if nome_f:
        filtros["nome"] = nome_f
    if pais_f:
        filtros["pais"] = pais_f
    if serie_f:
        filtros["serie"] = serie_f
    if data_inicio:
        filtros["data_inicio"] = data_inicio
    if data_fim:
        filtros["data_fim"] = data_fim

    if st.button("Gerar Excel"):
        alunos = listar_alunos(filtros=filtros if filtros else None)
        if not alunos:
            st.warning("Nenhum aluno com esses filtros.")
        else:
            df = pd.DataFrame([{
                "ID": a.id,
                "Nome": a.nome,
                "Idade": a.idade,
                "País": a.pais,
                "Passaporte": a.passaporte,
                "Série": a.serie,
                "Data Entrada": a.data_entrada,
                "Responsável": a.responsavel,
                "Observações": a.observacoes
            } for a in alunos])

            towrite = BytesIO()
            df.to_excel(towrite, index=False, engine="openpyxl")
            towrite.seek(0)
            today_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(label="Download Excel", data=towrite, file_name=f"alunos_export_{today_str}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ---- Usuários (admin) ----
elif menu == "Usuários (admin)":
    st.title("👥 Gerenciar Usuários")
    if st.session_state.user is None or st.session_state.user.get("role") != "admin":
        st.error("Acesso restrito: somente administradores podem gerenciar usuários.")
    else:
        st.subheader("Criar novo usuário")
        with st.form("form_user"):
            uname = st.text_input("Nome de usuário")
            pwd = st.text_input("Senha", type="password")
            role = st.selectbox("Papel", ["user", "admin"])
            btn = st.form_submit_button("Criar usuário")
            if btn:
                u = criar_usuario(uname, pwd, role=role)
                if u:
                    st.success(f"Usuário '{u.username}' criado.")
                else:
                    st.error("Já existe usuário com esse nome.")

        st.write("---")
        st.subheader("Aviso de segurança")
        st.info("Mude a senha do usuário `admin` retirando o padrão `admin123` após o primeiro login.")

