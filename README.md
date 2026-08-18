```markdown
# StreamReach — парсер и рассылка для стримеров Kick

сервис для сбора информации о стримерах с платформы Kick и автоматической рассылки сообщений через социальные сети

## Структура проекта

```
StreamReach/
├── docker-compose.yml
├── Dockerfile.parser
├── Dockerfile.mailer
├── run.sh
├── run_mailer.sh
├── clean.sh
├── parser/
│   ├── config.json
│   ├── data/
│   │   ├── data_auth.py
│   │   ├── data.json
│   │   └── contacts.json
│   ├── parserService.py
│   └── sender.py
└── mailers/
    ├── templates.json
    └── mailingService.py
```

## Установка

### Через Docker

```bash
git clone <repository>
cd StreamReach
chmod +x *.sh
docker-compose build
```

### Без Docker

```bash
pip install playwright curl_cffi requests
playwright install chromium
```

## Настройка

### 1. Файл `parser/config.json`

Заголовки для запросов к API Kick:

```json
{
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
  "Accept": "application/json",
  "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
}
```

### 2. Файл `parser/data/data_auth.py`

Данные для входа в социальные сети:

```python
instagram_login = "your_email@mail.com"
instagram_password = "your_password"

discord_login = "your_email@mail.com"
discord_password = "your_password"

twitter_login = "your_username"
twitter_password = "your_password"

tiktok_login = "your_email@mail.com"
tiktok_password = "your_password"
```

### 3. Файл `mailers/templates.json`

Шаблоны сообщений для рассылки:

```json
[
  {
    "id": 1,
    "subject": "Предложение о сотрудничестве",
    "body": "Здравствуйте, {streamer_name}!\\n\\nМеня зовут {manager_name}, я представляю {casino_name}.\\n\\nХотим предложить вам сотрудничество."
  }
]
```

**Доступные переменные:**
- `{streamer_name}` — имя стримера
- `{manager_name}` — ваше имя
- `{casino_name}` — название казино

## Проверка данных

```bash
# Посмотреть собранных стримеров
cat parser/data/data.json

# Посмотреть контакты
cat parser/data/contacts.json
```

## Прокси

Прокси-серверы можно взять на [2ip.ru/proxy](https://2ip.ru/proxy/).
Также можно запустить в colab
Настройка прокси в `parserService.py`:
```python
proxy = {
    "http": "http://ip:port",
    "https": "http://ip:port"
}

response = requests.get(
    url,
    headers=headers,
    impersonate="chrome110",
    proxies=proxy,
    timeout=30
)
```

## Как это работает

1. **Парсер** собирает стримеров с Kick (менее 1000 зрителей)
2. Извлекает ссылки на социальные сети со страницы `/about`
3. **Рассылка** логинится в соцсети и отправляет сообщения по шаблону

## Возможные проблемы
сайты постоянно обновляются то что работало вчера может не работать сегодня

## Требования

- Python 3.12+
- Docker (опционально)
- Аккаунты в соцсетях (Instagram, Twitter, TikTok, Discord)

## Предупреждение

Используйте ответственно. Соблюдайте правила платформ. Не злоупотребляйте рассылкой.

```