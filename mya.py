import sys
import os

if not os.path.exists("client_secret.json"):
    print("No client_secret.json found. Follow this guide: https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred and put it in the current directory.")
    exit()