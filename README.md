# Telegram Quiz Bot

Telegram-бот для тестування знань з ролями **студент** і **вчитель**, збереженням даних у **Supabase** (PostgreSQL) та інтерфейсом **українською / англійською**.

Детальний опис функціоналу і вимог — у [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md).

## Можливості

| Роль | Основне |
|------|---------|
| **Вчитель** | Створення тестів (майстер), типи питань (одиночний / множинний вибір, відкрита відповідь), редагування, статистика, результати студентів |
| **Студент** | Публічні тести за предметами, приватний доступ за кодом, проходження з таймером і обмеженням спроб, «Мої результати», пошук (назва / предмет / вчитель) |

**Типи питань у боті:** `single_choice`, `multiple_choice`, `open_answer` (автоперевірка за еталонними відповідями).

**Команди:** `/start`, `/help`, `/cancel`

## Стек

- Python 3.10+
- [aiogram](https://docs.aiogram.dev/) 3.x, FSM (`MemoryStorage`)
- [Supabase](https://supabase.com/) (PostgreSQL + REST API)
- `python-dotenv`, `PyJWT`

## Швидкий старт

### 1. Клонування та залежності

```bash
cd tg_bot
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Змінні середовища

Скопіюйте приклад і заповніть значення:

```bash
cp .env.example .env
```

| Змінна | Опис |
|--------|------|
| `BOT_TOKEN` | Токен від [@BotFather](https://t.me/BotFather) |
| `NEXT_PUBLIC_SUPABASE_URL` | URL проєкту Supabase |
| `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY` | Anon / publishable key |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key (бот працює через admin-клієнт) |
| `SUPABASE_JWT_SECRET` | JWT secret з налаштувань API Supabase |

### 3. База даних

У **SQL Editor** Supabase (або через `psql`) виконайте по черзі:

1. **`db/init_database.sql`** — створення таблиць, індексів і RLS-політик.  
   Увага: скрипт **видаляє** існуючі таблиці (`DROP TABLE …`).

2. **`db/seed_sample_tests.sql`** *(опційно)* — демо-предмети, тести, студенти та сесії. Потрібен хоча б один користувач з роллю `teacher` (зареєструйтесь у боті як вчитель перед seed, або seed підхопить першого вчителя з БД).

3. **`db/cleanup_tests.sql`** *(опційно)* — очищення тестових даних.

### 4. Запуск бота

```bash
python main.py
```

У консолі з’явиться повідомлення на кшталт `Bot online: @your_bot`.

## Структура проєкту

```
main.py                 # Точка входу, polling
config/i18n.py          # Локалізація uk / en
db/
  init_database.sql     # Схема БД
  seed_sample_tests.sql # Демо-дані
  cleanup_tests.sql
  queries.py            # Запити до Supabase
handlers/
  auth.py               # Реєстрація, роль, мова
  common.py             # /start, /help, /cancel, профіль
  teacher.py            # Сценарії вчителя
  student.py            # Сценарії студента
keyboards/
  keyboards.py          # Reply / inline клавіатури
  callbacks.py          # CallbackData
states/states.py        # FSM-стани
```

## База даних (коротко)

| Таблиця | Призначення |
|---------|-------------|
| `users` | Користувачі (`telegram_id`, роль, мова) |
| `subjects` | Предмети |
| `tests` | Тести вчителя (`max_points`, спроби, таймер, код доступу) |
| `questions` / `options` | Питання та варіанти / еталони для відкритих відповідей |
| `test_sessions` | Спроби проходження (`score`, `percentage`, `max_points`) |
| `session_answers` | Відповіді (`option_id` або `answer_text` для `open_answer`) |

Оцінювання: за кожне питання кредит 0–1; підсумок масштабується на `tests.max_points` (див. `complete_session_from_answers` у `db/queries.py`).

## Обмеження

- FSM у пам’яті — стан губиться після перезапуску бота.
- Запити до БД через **service role** (RLS обходиться; політики в `init_database.sql` підготовлені на майбутній перехід на JWT).
- У схемі є типи `matching`, `ordering` — у UI ще не реалізовані.

## Ліцензія

Навчальний / дипломний проєкт. Уточніть умови використання у власника репозиторію.
