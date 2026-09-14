# Запуск видеосервиса в новом окне
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd ./videoservice; uvicorn src.main:app --reload"

# Запуск админки в новом окне
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd ./admin; pnpm run dev"
