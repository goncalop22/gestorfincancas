import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Gestor Financeiro", page_icon="💰")

# Título e Introdução
st.title("💰 Gestor de Finanças Pessoais")
st.write("Controlo de receitas e despesas.")

# 1. Estabelecer Ligação ao Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Ler os dados existentes
# ttl=0 garante que não usa cache antiga e vai buscar dados frescos
try:
    df = conn.read(worksheet="Folha1", ttl=0) # Confirma se a tua aba se chama "Folha1"
    # Converter a coluna Data para datetime para evitar erros
    df['Data'] = pd.to_datetime(df['Data'])
except Exception:
    # Se a folha estiver vazia, cria um DataFrame vazio com a estrutura correta
    df = pd.DataFrame(columns=["Data", "Descricao", "Categoria", "Tipo", "Valor"])

# --- DASHBOARD (MÉTRICAS) ---
st.divider()
col1, col2, col3 = st.columns(3)

if not df.empty:
    total_receita = df[df['Tipo'] == "Receita"]['Valor'].sum()
    total_despesa = df[df['Tipo'] == "Despesa"]['Valor'].sum()
    saldo = total_receita - total_despesa
    
    col1.metric("Receita Total", f"{total_receita:.2f} €")
    col2.metric("Despesa Total", f"{total_despesa:.2f} €", delta_color="inverse")
    col3.metric("Saldo Atual", f"{saldo:.2f} €", delta=f"{saldo:.2f} €")
else:
    col1.metric("Receita", "0.00 €")
    col2.metric("Despesa", "0.00 €")
    col3.metric("Saldo", "0.00 €")

st.divider()

# --- FORMULÁRIO PARA ADICIONAR DADOS ---
st.subheader("📝 Adicionar Novo Movimento")

with st.form("entry_form", clear_on_submit=True):
    col_a, col_b = st.columns(2)
    
    with col_a:
        data_movimento = st.date_input("Data", datetime.today())
        tipo = st.selectbox("Tipo", ["Despesa", "Receita"])
        valor = st.number_input("Valor (€)", min_value=0.01, format="%.2f")
    
    with col_b:
        categoria = st.selectbox("Categoria", [
            "Casa (Luz/Água/Net)", 
            "Alimentação", 
            "Transporte", 
            "Saúde", 
            "Educação", 
            "Outros"
        ])
        descricao = st.text_input("Descrição (Ex: Pingo Doce)")

    submitted = st.form_submit_button("Guardar Movimento")

    if submitted:
        # Criar novo registo
        novo_registo = pd.DataFrame([{
            "Data": data_movimento.strftime("%Y-%m-%d"),
            "Descricao": descricao,
            "Categoria": categoria,
            "Tipo": tipo,
            "Valor": valor if tipo == "Receita" else -valor # Opcional: guardar despesa como negativo ou tratar depois
        }])
        
        # Como guardamos o valor absoluto no form, vamos manter positivo na base de dados 
        # e filtrar pelo "Tipo" nas contas, ou podes converter aqui.
        # Vamos manter o valor absoluto para ser mais fácil de ler no Excel.
        novo_registo['Valor'] = valor

        # Atualizar o DataFrame e enviar para o Google Sheets
        df_atualizado = pd.concat([df, novo_registo], ignore_index=True)
        conn.update(worksheet="Folha1", data=df_atualizado)
        
        st.success("Movimento registado com sucesso!")
        st.rerun() # Atualiza a página para mostrar os novos valores logo

# --- MOSTRAR DADOS ---
st.subheader("📊 Histórico de Movimentos")
# Ordenar por data (mais recente primeiro)
if not df.empty:
    st.dataframe(df.sort_values(by="Data", ascending=False), use_container_width=True)
