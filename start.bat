@echo off
echo ================================================
echo    DEMARRAGE DU CHATBOT NLP
echo ================================================
echo.

REM Activer l'environnement virtuel
echo [1/3] Activation de l'environnement virtuel...
call venv\Scripts\activate

REM Vérifier si les dépendances sont installées
echo [2/3] Verification des dependances...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Installation des dependances...
    pip install -r requirements.txt
    python -m spacy download fr_core_news_md
)

REM Lancer l'application
echo [3/3] Demarrage du serveur...
echo.
echo ================================================
echo    CHATBOT PRET !
echo    URL: http://localhost:5000
echo ================================================
echo.
echo Appuyez sur Ctrl+C pour arreter le serveur
echo.

python app.py

pause