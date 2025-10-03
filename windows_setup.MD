1) Check Python

PowerShell / CMD

py --version


If that fails:

python --version

2) Create a virtual environment in the current folder

PowerShell / CMD

py -3 -m venv .venv


If py isn’t available:

python -m venv .venv

3) Activate the virtual environment

PowerShell

.\.venv\Scripts\Activate.ps1


CMD

.\.venv\Scripts\activate.bat


Your prompt should now show (.venv).

4) Upgrade pip and install dependencies

Inside the venv (PowerShell / CMD)

python -m pip install --upgrade pip
pip install aiosmtpd

5) Run the server

Inside the venv (PowerShell / CMD)
Run from the folder containing busy_smtp.py:

python busy_smtp.py --bind 127.0.0.1 --port 2526 --helo busy.mx.local --log DEBUG


If Windows Firewall prompts, allow access for local testing.

6) Deactivate when done
deactivate

SWAKS Test (Windows options)
Option A — Use WSL (recommended if available)

Open WSL (Ubuntu).

Install and run:

sudo apt update && sudo apt install -y swaks
swaks -s 127.0.0.1:2526 -f sender@codeffee.com -t rcpt@any.test --ehlo test --quit-after RCPT

Option B — Native Windows via Strawberry Perl

Install Strawberry Perl.

In PowerShell/CMD:

cpan App::swaks
swaks -s 127.0.0.1:2526 -f sender@codeffee.com -t rcpt@any.test --ehlo test --quit-after RCPT

Option C — Quick probe using curl (no RCPT-only quit)

If you just need a minimal SMTP send (goes to DATA), create a file mail.txt:

From: sender@codeffee.com
To: rcpt@any.test
Subject: Test

Hello from curl SMTP!


Then run:

curl --url smtp://127.0.0.1:2526 --mail-from sender@codeffee.com --mail-rcpt rcpt@any.test -T mail.txt -v

Troubleshooting

Activation script blocked
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

Port already in use
Change to another port: --port 2527

Python not found
Use py instead of python, or reinstall Python and add to PATH

SWAKS can’t connect
Ensure the server is running, port 2526 is correct, and Firewall allows local connections

Clean Up

Stop the server (Ctrl+C).

Deactivate: deactivate

(Optional) Remove the venv: delete the .venv folder.