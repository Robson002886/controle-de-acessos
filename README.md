# 🏫 Sistema de Controle de Entrada de Alunos Estrangeiros  
Aplicação desenvolvida em **Python + Streamlit** para gerenciar o cadastro, controle de presença e registros de entrada de alunos estrangeiros em escolas de Ensino Fundamental e Médio.

O sistema oferece:
- Cadastro completo de alunos estrangeiros  
- Registro de entradas com data e hora  
- Consulta e edição de dados  
- Exportação para Excel (alunos e presenças)  
- Sistema simples de login  
- Banco de dados local SQLite  
- Interface 100% gráfica via Streamlit  

---

## 📌 Sumário

- [Visão Geral](#-visão-geral)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Funcionalidades](#-funcionalidades)
- [Arquitetura do Projeto](#-arquitetura-do-projeto)
- [Modelagem do Banco de Dados](#-modelagem-do-banco-de-dados)
- [Instalação](#️-instalação)
- [Como Executar](#-como-executar)
- [Exportação para Excel](#-exportação-para-excel)
- [Segurança](#-segurança)
- [Roadmap](#-roadmap)
- [Licença](#-licença)

---

## 🎯 Visão Geral

Este sistema foi criado para ajudar escolas a controlar com eficiência a entrada e informações de alunos estrangeiros. Ele permite um gerenciamento simples e centralizado, com interface amigável e armazenamento seguro em um banco de dados local SQLite.

---

## 🛠 Tecnologias Utilizadas

| Tecnologia | Finalidade |
|-----------|------------|
| **Python 3.10+** | Linguagem principal |
| **Streamlit** | Interface gráfica web |
| **SQLite** | Banco de dados local |
| **SQLAlchemy** | ORM para acessar o banco |
| **Pandas** | Manipulação e exportação de dados |
| **OpenPyXL** | Escrita de arquivos Excel |

---

## ✔ Funcionalidades

### 🔐 Sistema de Login
- Login simples com usuários cadastrados no banco.

### 👤 Gerenciamento de Alunos
- Cadastro de alunos estrangeiros  
- Edição e exclusão  
- Busca por nome ou documento  
- Visualização completa em tabela

### 🕒 Registro de Entradas
- Data e hora automáticas  
- Relatório de entradas por aluno

### 📤 Exportação para Excel
- Exportação separada:
  - `alunos.xlsx`
  - `presencas.xlsx`

### 💾 Banco de Dados
- Tudo armazenado em `SQLite`  
- Dados persistentes mesmo após encerrar o sistema

---

## 📁 Arquitetura do Projeto

