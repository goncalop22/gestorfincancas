import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(layout="wide")
st.title("🕵️ Modo de Diagnóstico")

# 1. Verificar Credenciais
st.subheader("1. Quem é o Robô?")
try:
    email = st.secrets.connections.gsheets.client_email
    st.info(f"O email configurado nos segredos é:\n\n**{email}**")
    st.warning("👉 VAI AO GOOGLE SHEETS > PARTILHAR e confirma se ESTE email exato está lá como EDITOR.")
except Exception as e:
    st.error(f"Erro a ler segredos: {e}")

# 2. Testar Ligação
st.subheader("2. Teste de Leitura e Escrita")
if st.button("Testar Conexão Agora"):
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    try:
        # Tenta ler
        df = conn.read(worksheet="Folha1", ttl=0)
        st.success(f"✅ Leitura OK! Encontrei {len(df)} linhas.")
        st.dataframe(df.head(2))
        
        # Tenta escrever
        st.write("A tentar escrever uma linha de teste...")
        novo_dado = pd.DataFrame([["Teste", "Teste", "Teste", "Receita", 1.0]], 
                                 columns=["Data", "Descricao", "Categoria", "Tipo", "Valor"])
        df_novo = pd.concat([df, novo_dado], ignore_index=True)
        
        conn.update(worksheet="Folha1", data=df_novo)
        st.success("✅ ESCRITA COM SUCESSO! O problema está resolvido.")
        
    except Exception as e:
        st.error("❌ FALHA NA ESCRITA")
        st.code(str(e))
        st.markdown("""
        **Soluções prováveis para este erro:**
        1. O ficheiro é um **.XLSX** (Converte para Google Sheet nativo).
        2. A aba não se chama **Folha1** (Verifica espaços extra: "Folha 1").
        3. A **Google Drive API** não está ativada na Cloud Console.
        """)
