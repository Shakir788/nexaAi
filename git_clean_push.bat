@echo off
echo ======================================
echo Cleaning old Git repo and pushing fresh code
echo ======================================

REM Project directory change kar
cd /d "C:\Users\mohammmad shakir\OneDrive\Desktop\nexa_streamlit_app"

REM Purana .git hatao
rmdir /s /q .git

REM Naya repo init
git init

REM Branch ko main set karo
git branch -M main

REM Remote repo set karo
git remote add origin https://github.com/Shakir788/nexaAi.git

REM .gitignore file banao agar exist nahi hai
if not exist .gitignore (
    echo # Ignore files > .gitignore
    echo .venv/>>.gitignore
    echo __pycache__/>>.gitignore
    echo *.env>>.gitignore
    echo *.wav>>.gitignore
    echo *.mp3>>.gitignore
    echo *.zip>>.gitignore
    echo *.tar.gz>>.gitignore
    echo *.pkl>>.gitignore
    echo *.pt>>.gitignore
    echo *.onnx>>.gitignore
    echo .streamlit/>>.gitignore
    echo .vscode/>>.gitignore
    echo .idea/>>.gitignore
)

REM Files add and commit
git add .
git commit -m "Clean repo push (without heavy files)"

REM Push forcefully
git push origin main --force

echo ======================================
echo DONE ✅
echo ======================================
pause
