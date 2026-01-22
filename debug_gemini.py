import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    # Try getting from streamlit secrets or just warn
    print("❌ Erro: GOOGLE_API_KEY não encontrada no .env")
else:
    print(f"🔑 Chave encontrada: {api_key[:5]}...{api_key[-3:]}")

try:
    genai.configure(api_key=api_key)
    
    # Candidates to test (based on your list + standard ones)
    candidates = [
        "gemini-flash-latest",
        "gemini-1.5-flash-latest", # sometimes this alias works
        "gemini-2.0-flash-lite-preview-02-05", # Lite might have quota
        "gemini-2.0-flash",
        "gemini-2.0-flash-exp",
        "gemini-2.5-flash"
    ]
    
    print("\n🧪 Testando geração de texto com modelos candidatos...")
    
    working_model = None
    
    for model_name in candidates:
        print(f"\nTentando: {model_name}...", end=" ")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say OK")
            print(f"✅ SUCESSO! Resposta: {response.text.strip()}")
            working_model = model_name
            break # Stop at first working one
        except Exception as e:
            if "429" in str(e):
                print(f"❌ Falha (Cota Excedida/429)")
            elif "404" in str(e):
                print(f"❌ Falha (Não Encontrado/404)")
            else:
                print(f"❌ Falha ({str(e)[:50]}...)")

    if working_model:
        print(f"\n🎉 O modelo '{working_model}' está funcionando! Use este no seu app.")
    else:
        print("\n⚠️ Nenhum dos modelos candidatos funcionou. Verifique seu plano no Google AI Studio.")

except Exception as e:
    print(f"\n❌ Erro geral: {e}")
