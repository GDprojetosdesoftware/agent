import streamlit_authenticator as stauth
import sys

# Usage: python generate_password.py "minha_senha_nova"
if len(sys.argv) > 1:
    password = sys.argv[1]
else:
    password = "admin" # Default if no arg provided

hashed = stauth.Hasher().hash(password)
print(f"\n✅ Senha: '{password}'")
print(f"🔑 Hash para colocar no auth.yaml: {hashed}\n")
