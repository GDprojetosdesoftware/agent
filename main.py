import os
import yaml
from yaml.loader import SafeLoader
import streamlit as st
import streamlit_authenticator as stauth
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
from agno.tools.yfinance import YFinanceTools
from tools.weather import get_current_weather
from storage import ChatStorage

# --- Load Environment Variables ---
load_dotenv()

# --- Page Config ---
st.set_page_config(
    page_title="AI Pro Assistant",
    page_icon="🧠",
    layout="wide",
)

# --- Authenticator Setup ---
def load_auth_config():
    with open('auth.yaml') as file:
        return yaml.load(file, Loader=SafeLoader)

config = load_auth_config()

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# --- Load Custom CSS ---
@st.cache_data
def load_css(file_name):
    with open(file_name) as f:
        return f.read()

try:
    css_content = load_css("branding.css")
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# --- Login System (Streamlit Authenticator) ---
try:
    # Use columns to center and constrain the width of the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        authenticator.login()
except Exception as e:
    st.error(e)

if st.session_state["authentication_status"] is False:
    st.error("Username/password is incorrect")
    st.stop()
elif st.session_state["authentication_status"] is None:
    # Just show the login form without checking for errors
    st.stop()
    
# --- Main Application (Only runs if authenticated) ---

# --- Main Application (Only runs if authenticated) ---

# --- Session State & Persistence Initialization ---
if "storage" not in st.session_state:
    st.session_state.storage = ChatStorage()

if "messages" not in st.session_state:
    st.session_state.messages = st.session_state.storage.load_history()

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "GPT-4o"

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Painel de Controle")
    st.write(f"Bem-vindo, *{st.session_state['name']}*") # Show user name
    
    # Model Selection
    st.subheader("🤖 Modelo de IA")
    model_choice = st.selectbox(
        "Selecione o Cérebro:",
        ["GPT-4o", "Gemini Flash Latest"],
        index=0 if st.session_state.selected_model == "GPT-4o" else 1
    )
    
    # Update session state if changed
    if model_choice != st.session_state.selected_model:
        st.session_state.selected_model = model_choice
        # st.session_state.messages = [] # Don't clear history on switch anymore!
        st.rerun()

    st.markdown("---")
    
    if st.button("Limpar Conversa"):
        st.session_state.storage.clear_history()
        st.session_state.messages = []
        st.rerun()
        
    authenticator.logout() # Built-in logout button
    
    st.markdown("---")
    st.caption("v2.2.1 | Powered by Agno")

# --- Header ---
st.markdown("<h1 class='gradient-text'>🧠 Assistente Senior Full-Stack</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #a29bfe'>Rodando com <b>{st.session_state.selected_model}</b> | Programação, Finanças e Clima.</p>", unsafe_allow_html=True)


# --- Agent Configuration ---
@st.cache_resource(hash_funcs={"agno.agent.Agent": lambda _: None}) # Simple hash fix if needed
def get_agent(model_name):
    
    # Select the underlying LLM
    if model_name == "GPT-4o":
        llm = OpenAIChat(id="gpt-4o-mini") # Keeping mini for speed/cost as per original
    elif model_name == "Gemini Flash Latest":
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("A chave GOOGLE_API_KEY não foi encontrada no arquivo .env ou nas variáveis de ambiente.")
        
        # Use the verified working model ID
        llm = Gemini(id="gemini-flash-latest", api_key=api_key)
    else:
        llm = OpenAIChat(id="gpt-4o-mini")

    return Agent(
        model=llm,
        tools=[
            YFinanceTools(),
            get_current_weather
        ],
        instructions=[
            "Você é um Engenheiro de Software Sênior e Mentor Técnico Sênior.",
            "Responda sempre em Português do Brasil.",
            "Para perguntas de programação: Siga Clean Code, SOLID e boas práticas.",
            "Para perguntas de Clima: Use a ferramenta get_current_weather.",
            "Para perguntas de Ações: Use o YFinanceTools.",
            "Para Cotação de Moedas: Use YFinanceTools com o ticker 'BRL=X' para Dólar e 'EURBRL=X' para Euro.",
            "Seja direto e profissional, mas amigável.",
            "Use tabelas e markdows para formatar suas respostas de forma bonita."
        ],
        markdown=True,
    )

# Instantiate agent based on selection
try:
    agent = get_agent(st.session_state.selected_model)
except Exception as e:
    st.error(f"Erro ao inicializar o modelo {st.session_state.selected_model}: {e}")
    st.stop()

# --- Chat Interface ---

# 1. Display existing history
for message in st.session_state.messages:
    avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 2. Suggestion Chips (Only if history is empty)
if not st.session_state.messages:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #a29bfe;'>Sugestões Rápidas:</h4>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    suggestion = None
    if col1.button("🌦️ Clima em SP", use_container_width=True):
        suggestion = "Como está o clima em São Paulo agora?"
    if col2.button("💻 Criar Componente", use_container_width=True):
        suggestion = "Crie um componente de Botão em React usando Tailwind."
    if col3.button("📈 Dólar Hoje", use_container_width=True):
        suggestion = "Qual a cotação do Dólar hoje?"
        
    if suggestion:
        # Add to state and rerun to process immediately
        st.session_state.messages.append({"role": "user", "content": suggestion})
        st.rerun()

# 3. Chat Input
if prompt := st.chat_input("Em que posso ajudar hoje, Sr. Engenheiro?"):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Show user message immediately
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner(f"Processando com {st.session_state.selected_model}..."):
            try:
                # Build context from history
                # Use storage to get recent context directly ensuring consistency
                recent_history = st.session_state.storage.load_history(limit=10)
                history_text = "\n".join(
                    [f"{msg['role'].title()}: {msg['content']}" for msg in recent_history]
                )
                
                full_prompt = f"""
                Histórico da Conversa:
                {history_text}
                
                Nova Instrução do Usuário:
                {prompt}
                
                Responda considerando o histórico acima e sua persona de Engenheiro Sênior.
                """

                # Run the agent
                response_obj = agent.run(full_prompt)
                
                # Extract content
                response_text = getattr(response_obj, 'content', str(response_obj))
                
                st.markdown(response_text)
                
                # Save assistant response to state
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                # Persist to DB
                st.session_state.storage.save_message("user", prompt) # Save user prompt late to ensure both are saved ONLY if success, or save early? Better save early but simple here.
                # Actually, better to save user prompt before run, but if run fails we have orphan. 
                # Let's save both after success for now to keep pairs, or save user before.
                
                # Re-saving user here might duplicate if we logic change, but for now standard flow:
                # We appended to session_state above for UI. Now commit to DB.
                # Wait, we appended user to session_state at line 161.
                st.session_state.storage.save_message("user", prompt)
                st.session_state.storage.save_message("assistant", response_text)
                
            except Exception as e:
                error_msg = f"Erro: {str(e)}. Verifique se a API Key do {st.session_state.selected_model} está configurada."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
