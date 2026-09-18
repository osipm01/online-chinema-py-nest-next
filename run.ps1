# Запуск видеосервиса в новом окне
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd ./videoservice; uvicorn src.main:app --reload"

# Запуск админки в новом окне
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd ./admin; pnpm run dev"

# Запуск mainservice (Django) в новом окне с активацией .venv на порту 9090
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd ./mainservice; .venv\Scripts\Activate.ps1; cd ./mainservice; python manage.py runserver 9090"
