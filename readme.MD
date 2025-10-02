macOS / Linux (bash/zsh)

# 1) Check Python
python3 --version

# 2) Create a venv in the current folder
python3 -m venv .venv

# 3) Activate it
source .venv/bin/activate

# (your prompt now shows (.venv))

# 4) Upgrade pip and install deps
python -m pip install --upgrade pip
pip install aiosmtpd

# 5) Run your server
python busy_smtp.py --bind 127.0.0.1 --port 2526 --helo busy.mx.local --log DEBUG

# 6) Leave the env when done
deactivate

# SWAKS Test

swaks -s 127.0.0.1:2526 \
  -f sender@codeffee.com \
  -t rcpt@any.test \
  --ehlo test \
  --quit-after RCPT