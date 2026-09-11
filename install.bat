@echo off
echo Installing AI Text Corrector on Windows...
echo Setting up Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Installation complete!
echo To run the application quietly without a console, double-click run_hidden.vbs
pause
