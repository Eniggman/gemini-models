# 📋 Gemini Models List

Интерактивная страница со списком всех доступных моделей Google Gemini API.

## 🌐 Онлайн версия

👉 **[Открыть список моделей](https://YOUR_USERNAME.github.io/gemini-models/gemini_models.html)**

## ✨ Возможности

- 📂 Группировка по категориям (Pro, Flash, Image, Video, Embedding, Gemma)
- 🔍 Поиск по названию
- 🏷️ Фильтры по типу модели
- 📅 Даты релизов
- 📋 Копирование названия модели в один клик
- 🔄 Автообновление каждый день

## 🚀 Локальный запуск

```bash
pip install google-generativeai
python list_models.py
```

## ⚙️ Настройка автообновления

1. Создай секрет `GEMINI_API_KEY` в настройках репозитория:
   - Settings → Secrets and variables → Actions → New repository secret
   - Name: `GEMINI_API_KEY`
   - Value: твой API ключ

2. Включи GitHub Pages:
   - Settings → Pages → Source: GitHub Actions

3. Готово! Список будет обновляться автоматически каждый день в 8:00 по Киеву.

## 📄 Лицензия

MIT
