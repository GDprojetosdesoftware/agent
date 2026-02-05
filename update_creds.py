import yaml
import streamlit_authenticator as stauth
import sys

# Usage: python update_creds.py <new_username> <new_password>

if len(sys.argv) < 3:
    print("❌ Usage: python update_creds.py <username> <password>")
    sys.exit(1)

new_user = sys.argv[1]
new_pass = sys.argv[2]

print(f"🔄 Updating credentials for user: {new_user}...")

# 1. Generate hash
hashed_pw = stauth.Hasher().hash(new_pass)

# 2. Load existing yaml
with open('auth.yaml', 'r') as f:
    config = yaml.safe_load(f)

# 3. Update cookie name slightly to force re-login for everyone
config['cookie']['name'] = 'agent_auth_cookie_v3'

# 4. Rebuild credentials structure
# We replace the entire 'usernames' block to ensure old users (like 'admin' if you change the name) are removed
config['credentials']['usernames'] = {
    new_user: {
        'email': f'{new_user}@example.com',
        'name': new_user.capitalize(),
        'password': hashed_pw
    }
}

# 5. Save back to yaml
with open('auth.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)

print(f"✅ Success! User '{new_user}' created/updated.")
print(f"🔑 Password hash stored safely.")
print(f"🍪 Cookie name updated to force re-login.")
