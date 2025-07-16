# Niffler Python Tests

Тестовый фреймворк для автоматизации UI тестирования приложения Niffler с использованием **Playwright**.
Проект построен по принципам Page Object Model, с разделением конфигурации и поддержкой разных окружений.

---

## Структура проекта

```
.
├── clients/         # API-клиенты (AuthClient, SpendClient и др.)
├── config/          # Провайдеры и утилиты для работы с конфигами
├── models/          # Pydantic-модели для запросов/ответов API
├── pages/           # Page Object'ы для UI (в т.ч. компоненты)
│   ├── components/  # Вспомогательные компоненты (header, dialog и др.)
│   └── spending/    # Страницы, связанные с расходами
├── tests/           # Тесты, фикстуры
├── config.ini       # Конфиг с URL для разных окружений
├── pyproject.toml   # Зависимости и настройки Poetry
└── README.md        # Этот файл
```

---

## Быстрый старт

### 1. Установка зависимостей

```bash
poetry install
```

### 2. Установка браузеров Playwright

```bash
poetry run playwright install chromium
```

### 3. Настройка переменных окружения

Создайте файл `.env` в корне проекта и добавьте туда секреты:

```
USERNAME=your_test_user
PASSWORD=your_test_password
```

### 4. Конфигурация окружений

В файле `config.ini` задаются URL для разных окружений:

```ini
[dev]
...

[rc]
...

---

## Запуск тестов

```bash
poetry run pytest
```

Для запуска на другом окружении:
```bash
poetry run pytest --env=rc
```

---

## Основные технологии

- **Playwright** — для UI-автотестов
- **pytest** — для запуска тестов и фикстур
- **Pydantic** — для моделей API
- **Poetry** — для управления зависимостями

---

## Page Object Model

- Все страницы и компоненты UI описаны в папке `pages/`.
- Общие элементы (например, диалоги, header) — в `pages/components/`.
- Для форм добавления/редактирования расходов используется базовый класс `SpendingFormPage`.

---

## Пример теста

```python
def test_add_category(profile_page):
    category = "Новая категория"
    profile_page.add_category(category)
    assert category in profile_page.get_categories()
```

---

## Фикстуры

- Фикстуры для браузера, API-клиентов, тестовых пользователей и Page Object'ов определены в `tests/conftest.py`.
- Для каждого теста создаётся новый браузер и контекст.

---

## Советы по написанию тестов

- Используйте методы Page Object для всех действий и проверок.
- Не используйте time.sleep — только Playwright-ожидания!
- Все секреты храните в `.env`, а не в коде или config.ini.