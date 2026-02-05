import streamlit_authenticator as stauth
hashed_passwords = stauth.Hasher().hash('admin')
print(f"Hashed password for 'admin': {hashed_passwords}")
