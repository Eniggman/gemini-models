import google.generativeai as genai
import webbrowser
import os
from datetime import datetime
import re

# API ключ: из переменной окружения (для безопасности)
API_KEY = os.environ.get('GEMINI_API_KEY')
if not API_KEY:
    print("❌ Ошибка: укажи GEMINI_API_KEY в переменных окружения")
    print("   Пример: set GEMINI_API_KEY=твой_ключ_тут")
    exit(1)
genai.configure(api_key=API_KEY)

print("🔄 Загрузка списка моделей...")
models = list(genai.list_models())
models.reverse()

# Официальные даты релизов (из Google changelog и документации)
RELEASE_DATES = {
    # Gemini 3
    'gemini-3-pro-preview': '18.11.2025',
    'gemini-3-pro-image-preview': '20.11.2025',
    'nano-banana-pro-preview': '20.11.2025',
    
    # Gemini 2.5
    'gemini-2.5-pro': '17.06.2025',
    'gemini-2.5-flash': '17.06.2025',
    'gemini-2.5-flash-lite': '17.06.2025',
    'gemini-2.5-pro-preview-06-05': '05.06.2025',
    'gemini-2.5-pro-preview-05-06': '06.05.2025',
    'gemini-2.5-flash-preview-04-17': '17.04.2025',
    'gemini-2.5-pro-exp': '25.03.2025',
    'gemini-2.5-flash-image': '07.05.2025',
    'gemini-2.5-flash-image-preview': '07.05.2025',
    
    # Gemini 2.0
    'gemini-2.0-flash': '30.01.2025',
    'gemini-2.0-flash-001': '30.01.2025',
    'gemini-2.0-flash-exp': '11.12.2024',
    'gemini-2.0-pro-exp': '05.02.2025',
    'gemini-2.0-flash-lite': '05.02.2025',
    'gemini-2.0-flash-lite-001': '05.02.2025',
    'gemini-2.0-flash-live-001': '11.12.2024',
    'gemini-2.0-flash-exp-image-generation': '12.03.2025',
    
    # Gemini 1.5
    'gemini-1.5-pro-002': '24.09.2024',
    'gemini-1.5-flash-002': '24.09.2024',
    'gemini-1.5-flash-8b-001': '03.10.2024',
    'gemini-1.5-pro-latest': '09.04.2024',
    
    # Gemini 1.0
    'gemini-pro-latest': '06.12.2023',
    'gemini-flash-latest': '30.01.2025',
    'gemini-flash-lite-latest': '05.02.2025',
    
    # Veo
    'veo-2.0-generate-001': '16.12.2024',
    'veo-3.0-generate-001': '20.05.2025',
    'veo-3.0-fast-generate-001': '20.05.2025',
    
    # Imagen
    'imagen-4.0-generate-001': '20.05.2025',
    'imagen-4.0-fast-generate-001': '20.05.2025',
    'imagen-4.0-ultra-generate-001': '20.05.2025',
    
    # Embedding
    'text-embedding-004': '09.04.2024',
    'embedding-001': '06.12.2023',
    'gemini-embedding-001': '17.06.2025',
    
    # Gemma
    'gemma-3-27b-it': '12.03.2025',
    'gemma-3-12b-it': '12.03.2025',
    'gemma-3-4b-it': '12.03.2025',
    'gemma-3-1b-it': '12.03.2025',
    
    # Experimental
    'gemini-exp-1206': '06.12.2024',
}

def get_category(name):
    """Определяет категорию модели"""
    name_lower = name.lower()
    if 'veo' in name_lower:
        return 'veo'
    elif 'imagen' in name_lower or 'image' in name_lower:
        return 'imagen'  # Все image-модели включая gemini-3-pro-image
    elif 'gemma' in name_lower:
        return 'gemma'
    elif 'embedding' in name_lower or 'aqa' in name_lower:
        return 'embedding'
    elif 'pro' in name_lower and 'gemini' in name_lower:
        return 'pro'
    elif 'flash' in name_lower:
        return 'flash'
    else:
        return 'other'

def get_status(name):
    """Определяет статус модели"""
    name_lower = name.lower()
    if '-001' in name_lower or 'stable' in name_lower:
        return 'stable'
    elif 'preview' in name_lower:
        return 'preview'
    elif 'exp' in name_lower:
        return 'exp'
    elif 'latest' in name_lower:
        return 'latest'
    return ''

def parse_date(name, description=''):
    """Извлекает дату из названия или описания"""
    
    # 0. Сначала проверяем словарь известных дат
    if name in RELEASE_DATES:
        return RELEASE_DATES[name]
    
    # Словарь месяцев
    months = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12',
        'septempber': '09', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12',
        'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'jun': '06', 'jul': '07', 'aug': '08'
    }
    
    desc_lower = description.lower() if description else ''
    
    # 1. Ищем "Month DDth, YYYY" или "Month YYYY" в описании
    for month, num in months.items():
        if month in desc_lower:
            year_match = re.search(r'(\d{4})', description)
            day_match = re.search(r'(\d{1,2})(?:st|nd|rd|th)', description)
            if year_match:
                day = day_match.group(1) if day_match else ''
                if day:
                    return f"{day}.{num}.{year_match.group(1)}"
                return f"{num}/{year_match.group(1)}"
    
    # 2. Ищем MM-YYYY в названии (например: 09-2025)
    match = re.search(r'(\d{2})-(\d{4})(?:$|-)', name)
    if match:
        return f"{match.group(1)}/{match.group(2)}"
    
    # 3. Ищем MM-DD в названии (например: 06-06)
    match = re.search(r'-(\d{2})-(\d{2})$', name)
    if match:
        return f"{match.group(1)}.{match.group(2)}"
    
    return '—'  # Показываем тире вместо пустоты

# Группируем модели
categories = {
    'pro': {'name': '🟣 Gemini Pro', 'models': [], 'color': '#a855f7'},
    'flash': {'name': '⚡ Gemini Flash', 'models': [], 'color': '#22c55e'},
    'imagen': {'name': '🎨 Imagen', 'models': [], 'color': '#f59e0b'},
    'veo': {'name': '🎬 Veo (Video)', 'models': [], 'color': '#ef4444'},
    'embedding': {'name': '📊 Embedding', 'models': [], 'color': '#6366f1'},
    'gemma': {'name': '🤖 Gemma', 'models': [], 'color': '#ec4899'},
    'other': {'name': '📦 Другие', 'models': [], 'color': '#64748b'},
}

for model in models:
    name = model.name.replace('models/', '')
    desc = getattr(model, 'description', '') or ''
    category = get_category(name)
    status = get_status(name)
    date = parse_date(name, desc)
    
    categories[category]['models'].append({
        'name': name,
        'desc': desc[:80],
        'status': status,
        'date': date,
        'category': category
    })

# Генерируем HTML
html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini Models</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{ 
            font-family: 'Inter', -apple-system, sans-serif;
            background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
            color: #e2e8f0;
            min-height: 100vh;
            padding: 30px 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        /* Header */
        header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        h1 {{
            font-size: 2.8em;
            font-weight: 700;
            background: linear-gradient(135deg, #00d9ff 0%, #a855f7 50%, #ec4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        
        .stats {{
            color: #64748b;
            font-size: 0.95em;
        }}
        
        .stats span {{
            color: #00d9ff;
            font-weight: 600;
        }}
        
        /* Search & Filters */
        .controls {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 25px;
            align-items: center;
            justify-content: center;
        }}
        
        .search-box {{
            position: relative;
            flex: 1;
            max-width: 400px;
            min-width: 250px;
        }}
        
        .search-box input {{
            width: 100%;
            padding: 12px 20px 12px 45px;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            background: rgba(255,255,255,0.05);
            color: #fff;
            font-size: 1em;
            font-family: inherit;
            transition: all 0.3s;
        }}
        
        .search-box input:focus {{
            outline: none;
            border-color: #00d9ff;
            box-shadow: 0 0 20px rgba(0,217,255,0.2);
        }}
        
        .search-box::before {{
            content: "🔍";
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1.1em;
        }}
        
        .filters {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            justify-content: center;
        }}
        
        .filter-btn {{
            padding: 8px 16px;
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 20px;
            background: rgba(255,255,255,0.05);
            color: #94a3b8;
            cursor: pointer;
            font-size: 0.9em;
            font-family: inherit;
            transition: all 0.3s;
        }}
        
        .filter-btn:hover {{
            background: rgba(255,255,255,0.1);
            color: #fff;
        }}
        
        .filter-btn.active {{
            background: linear-gradient(135deg, #00d9ff, #a855f7);
            border-color: transparent;
            color: #fff;
            font-weight: 500;
        }}
        
        /* Categories */
        .category {{
            margin-bottom: 20px;
            background: rgba(255,255,255,0.03);
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.05);
        }}
        
        .category-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 20px;
            cursor: pointer;
            transition: background 0.3s;
        }}
        
        .category-header:hover {{
            background: rgba(255,255,255,0.05);
        }}
        
        .category-title {{
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 1.1em;
            font-weight: 600;
        }}
        
        .category-count {{
            background: rgba(255,255,255,0.1);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            color: #94a3b8;
        }}
        
        .category-toggle {{
            font-size: 1.2em;
            transition: transform 0.3s;
        }}
        
        .category.collapsed .category-toggle {{
            transform: rotate(-90deg);
        }}
        
        .category.collapsed .category-content {{
            display: none;
        }}
        
        /* Table */
        .category-content {{
            padding: 0 10px 10px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            text-align: left;
            padding: 12px 15px;
            font-weight: 500;
            color: #64748b;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        
        td {{
            padding: 14px 15px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            vertical-align: middle;
        }}
        
        tr:hover {{
            background: rgba(255,255,255,0.03);
        }}
        
        tr:last-child td {{
            border-bottom: none;
        }}
        
        .model-name {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.95em;
            color: #00d9ff;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .copy-btn {{
            opacity: 0;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 0.9em;
            padding: 4px;
            transition: all 0.2s;
        }}
        
        tr:hover .copy-btn {{
            opacity: 0.6;
        }}
        
        .copy-btn:hover {{
            opacity: 1 !important;
            transform: scale(1.1);
        }}
        
        /* Status badges */
        .status {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.8em;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }}
        
        .status-stable {{ background: rgba(34,197,94,0.2); color: #22c55e; }}
        .status-preview {{ background: rgba(245,158,11,0.2); color: #f59e0b; }}
        .status-exp {{ background: rgba(168,85,247,0.2); color: #a855f7; }}
        .status-latest {{ background: rgba(0,217,255,0.2); color: #00d9ff; }}
        
        .date {{
            color: #64748b;
            font-size: 0.9em;
        }}
        
        .desc {{
            color: #94a3b8;
            font-size: 0.9em;
            max-width: 350px;
        }}
        
        /* Toast notification */
        .toast {{
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background: linear-gradient(135deg, #22c55e, #16a34a);
            color: #fff;
            padding: 12px 24px;
            border-radius: 10px;
            font-weight: 500;
            box-shadow: 0 10px 40px rgba(34,197,94,0.3);
            opacity: 0;
            transition: all 0.3s;
            z-index: 1000;
        }}
        
        .toast.show {{
            transform: translateX(-50%) translateY(0);
            opacity: 1;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            h1 {{ font-size: 2em; }}
            table {{ font-size: 0.9em; }}
            .desc {{ display: none; }}
            td, th {{ padding: 10px 8px; }}
        }}
        
        /* Hidden class for filtering */
        .hidden {{ display: none !important; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📋 Gemini Models</h1>
            <p class="stats">
                Обновлено: <span>{datetime.now().strftime("%d.%m.%Y %H:%M")}</span> | 
                Всего: <span>{len(models)}</span> моделей
            </p>
        </header>
        
        <div class="controls">
            <div class="search-box">
                <input type="text" id="search" placeholder="Поиск модели..." autocomplete="off">
            </div>
            <div class="filters">
                <button class="filter-btn active" data-filter="all">Все</button>
                <button class="filter-btn" data-filter="pro">Pro</button>
                <button class="filter-btn" data-filter="flash">Flash</button>
                <button class="filter-btn" data-filter="imagen">Image</button>
                <button class="filter-btn" data-filter="veo">Veo</button>
                <button class="filter-btn" data-filter="embedding">Embed</button>
                <button class="filter-btn" data-filter="gemma">Gemma</button>
            </div>
        </div>
"""

# Генерируем секции для каждой категории
for cat_id, cat_data in categories.items():
    if not cat_data['models']:
        continue
    
    html += f"""
        <div class="category" data-category="{cat_id}">
            <div class="category-header" onclick="toggleCategory(this)">
                <div class="category-title" style="color: {cat_data['color']}">
                    {cat_data['name']}
                    <span class="category-count">{len(cat_data['models'])}</span>
                </div>
                <span class="category-toggle">▼</span>
            </div>
            <div class="category-content">
                <table>
                    <tr>
                        <th>Модель</th>
                        <th>Статус</th>
                        <th>Дата</th>
                        <th>Описание</th>
                    </tr>
"""
    
    for m in cat_data['models']:
        status_class = f"status-{m['status']}" if m['status'] else ""
        status_text = m['status'].upper() if m['status'] else ""
        
        html += f"""                    <tr data-name="{m['name'].lower()}">
                        <td class="model-name">
                            {m['name']}
                            <button class="copy-btn" onclick="copyName('{m['name']}', event)" title="Копировать">📋</button>
                        </td>
                        <td><span class="status {status_class}">{status_text}</span></td>
                        <td class="date">{m['date']}</td>
                        <td class="desc">{m['desc']}</td>
                    </tr>
"""
    
    html += """                </table>
            </div>
        </div>
"""

html += """
        <div class="toast" id="toast">✓ Скопировано!</div>
    </div>
    
    <script>
        // Toggle category collapse
        function toggleCategory(header) {
            header.parentElement.classList.toggle('collapsed');
        }
        
        // Copy model name
        function copyName(name, event) {
            event.stopPropagation();
            navigator.clipboard.writeText(name).then(() => {
                const toast = document.getElementById('toast');
                toast.classList.add('show');
                setTimeout(() => toast.classList.remove('show'), 2000);
            });
        }
        
        // Search functionality
        document.getElementById('search').addEventListener('input', function(e) {
            const query = e.target.value.toLowerCase();
            document.querySelectorAll('tr[data-name]').forEach(row => {
                const name = row.dataset.name;
                row.classList.toggle('hidden', !name.includes(query));
            });
            
            // Hide empty categories
            document.querySelectorAll('.category').forEach(cat => {
                const visibleRows = cat.querySelectorAll('tr[data-name]:not(.hidden)').length;
                cat.classList.toggle('hidden', visibleRows === 0);
            });
        });
        
        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                const filter = this.dataset.filter;
                document.querySelectorAll('.category').forEach(cat => {
                    if (filter === 'all') {
                        cat.classList.remove('hidden');
                    } else {
                        cat.classList.toggle('hidden', cat.dataset.category !== filter);
                    }
                });
            });
        });
    </script>
</body>
</html>"""

# Сохраняем HTML
html_path = os.path.join(os.path.dirname(__file__), 'gemini_models.html')
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ Сохранено: {html_path}")
print(f"📊 Найдено {len(models)} моделей")
for cat_id, cat_data in categories.items():
    if cat_data['models']:
        print(f"   {cat_data['name']}: {len(cat_data['models'])}")

webbrowser.open(f'file:///{html_path}') if not os.environ.get('CI') else None
