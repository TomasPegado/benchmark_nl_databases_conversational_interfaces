echo off
echo ...creating the env
call python -m venv .venv
echo ...active the env
call .\.venv\Scripts\activate
echo ...install the requirements
call pip install -r requirements.txt