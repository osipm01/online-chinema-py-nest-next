# 1. Запуск видеосервиса (Uvicorn -> порт 8000 по умолчанию, согласно вашему nginx.conf)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd ./videoservice; uvicorn src.main:app --reload"

# 2. Запуск собранной АДМИНКИ (Nuxt -> порт 3400)
# Включает переменные HOST и PORT и запускает готовый .output
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd ./admin; $env:PORT=3400; $env:HOST='127.0.0.1'; node .output/server/index.mjs"

# 3. Запуск mainservice (Django -> порт 9090)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd ./mainservice; .venv\Scripts\Activate.ps1; cd ./mainservice; python manage.py runserver 9090"

# 4. Запуск собранного КЛИЕНТА (Nuxt/Next -> порт 4000)
# Настраивает порт 4000 для главной страницы, как прописано в nginx.conf
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd ./client; $env:PORT=4000; $env:HOST='127.0.0.1'; node .output/server/index.mjs"
