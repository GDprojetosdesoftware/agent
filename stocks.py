import os
from dotenv import load_dotenv
import streamlit as st
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools

load_dotenv()

st.title("- Agente de Ações -")

user_input = st.text_input("Digite o nome da ação ou pergunta:")

if user_input:
    agent = Agent(
        model=OpenAIChat(id="gpt-4.1-mini"),
        tools=[YFinanceTools()],
        instructions="Use tabelas para mostar a informação final. Não inclua nenhum outro texto.",
        markdown=True,
    )
    run_output = agent.run(user_input, markdown=True)
    # Se for um objeto RunOutput, pega o atributo 'content'
    resposta = getattr(run_output, 'content', run_output)
    st.markdown(resposta)