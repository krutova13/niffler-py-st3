# Niffler Python Tests

<div align="center">

**Тестовый фреймворк для приложения Niffler**

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![Poetry](https://img.shields.io/badge/poetry-managed-blue.svg)](https://python-poetry.org/)
[![pytest](https://img.shields.io/badge/testing-pytest-yellow.svg)](https://pytest.org/)
[![Parallel](https://img.shields.io/badge/parallel-xdist-red.svg)](https://github.com/pytest-dev/pytest-xdist)

**100 тестов** | **5 типов тестирования** | **Параллельный запуск** | **Allure отчеты**

</div>

---

## Быстрый старт

```bash
# Установить зависимости
poetry install

# Запустить все API тесты параллельно (рекомендуется)
poetry run pytest tests/api/ -n auto --alluredir=allure-results

# Посмотреть Allure отчет
allure serve allure-results
```

## Структура

```
python-tests/
├── clients/           # 5 API клиентов (Auth, Category, Spends, Kafka, SOAP)
├── tests/             # 100 тестов (REST, gRPC, SOAP, Kafka, UI)
├── fixtures/          # 9 модулей fixtures
├── pages/             # 13 Page Objects для UI
├── models/            # 7 Pydantic моделей
├── databases/         # 2 БД класса (PostgreSQL)
├── utils/             # Helpers (sessions, allure, waiters)
├── internal/          # gRPC (protobuf, interceptors)
├── conftest.py        # Pytest конфигурация
└── config.py          # Settings (Pydantic)
```

---

## Команды запуска

### Базовые

```bash
# Все API + Kafka тесты (быстро)
pytest tests/api/ tests/kafka/ -n auto

# REST API
pytest tests/api/rest/ -v

# gRPC
pytest tests/api/grpc/ -v

# SOAP
pytest tests/api/soap/ -v

# Kafka
pytest tests/kafka/ -v

# UI
pytest tests/ui/ -v
```

### Параллельный запуск

```bash
# Авто-определение CPU (рекомендуется)
pytest -n auto

# 4 воркера
pytest -n 4

# Без параллелизации (отладка)
pytest
```

**Ускорение:** последовательно ~20с → параллельно ~5-7с (**в 3-4 раза быстрее**)

### С Allure отчетами

```bash
# Запустить с генерацией отчета
pytest tests/api/ -n auto --alluredir=allure-results

# Посмотреть отчет (откроется в браузере)
allure serve allure-results
```

### По маркерам

```bash
pytest -m api              # Только API
pytest -m "not ui"         # Все кроме UI
pytest -m boundary         # Граничные тесты
pytest -m "grpc or kafka"  # gRPC или Kafka
```

---

## Ключевые возможности

### Параллельный запуск
- 8 воркеров одновременно (auto CPU)
- Уникальные пользователи для каждого воркера (`test_gw0`, `test_gw1`, etc.)
- Изолированная очистка данных
- Ускорение в 3-4 раза

### Детальные Allure отчеты
- Русский язык
- JSON/XML attachments
- SQL запросы
- Kafka сообщения
- Скриншоты при ошибках
- Метаданные и время выполнения

### GitHub Actions CI/CD
- Автоматический запуск при push/PR
- Matrix strategy (REST, SOAP, gRPC параллельно)
- Публикация отчетов на GitHub Pages
- Комментарии в PR со ссылками

---

## Конфигурация

Создайте `.env` файл (опционально):

```env
# URLs
AUTH_URL=http://auth.niffler.dc:9000
FRONTEND_URL=http://frontend.niffler.dc
GATEWAY_URL=http://gateway.niffler.dc:8090

# Credentials
TEST_USERNAME=test
TEST_PASSWORD=123

# Databases
SPEND_DB_URL=postgresql+psycopg2://postgres:secret@localhost:5432/niffler-spend
USER_DB_URL=postgresql+psycopg2://postgres:secret@localhost:5432/niffler-userdata

# Services
KAFKA_ADDRESS=localhost:9093
GRPC_URL=localhost:8092
AUTH_SECRET=secret
```

> 💡 Все параметры имеют дефолтные значения - работает без `.env`!

---

## Примеры использования

### API тест

```python
@allure.title("Создание категории")
def test_create_category(category_client):
    category = category_client.add_category(name="Еда")
    assert category.name == "Еда"
```

### Kafka тест

```python
@allure.title("Сообщение создает пользователя в БД")
def test_kafka_to_db(kafka, userdata_db):
    kafka.produce_message('users', {'username': 'testuser'})
    user = wait_until_timeout(userdata_db.get_userdata_by_username)('testuser')
    assert user.username == 'testuser'
```

### UI тест (Page Object)

```python
@allure.title("Создание траты")
def test_create_spending(main_page, add_spending_page):
    main_page.create_new_spending()
    add_spending_page.fill_form(amount="1000", category="Еда")
    add_spending_page.submit()
    assert main_page.is_spending_visible("1000")
```


---

## GitHub Actions

### Настройка за 3 шага:

1. **Включить GitHub Pages:** Settings → Pages → Source: `gh-pages`
2. **Настроить права:** Settings → Actions → Read and write permissions
3. **Push:**
   ```bash
   git add .github/workflows/ python-tests/
   git commit -m "ci: добавить автоматизацию"
   git push
   ```

### Workflows:

- **Python Tests** - полный пайплайн (~5-10 мин)
  - Линтинг → API тесты (matrix) → UI тесты → Allure отчет
  - Автоматически при push/PR
  - Публикация отчетов на GitHub Pages

**URL отчета:** `https://<username>.github.io/<repo>/allure-report`

---

## Итоги

- **Полное покрытие:** REST, SOAP, gRPC, Kafka, UI  
- **Параллельный запуск:** ускорение в 3-4 раза  
- **Русские Allure отчеты:** с attachments и steps  
- **GitHub Actions:** автоматический CI/CD  
- **Изоляция данных:** уникальные пользователи для воркеров  
- **Автоматическая очистка:** до и после тестов  
- **100+ тестов:** готовы к использованию  

---

<div align="center">

**Автор:** Артемова Анастасия | **Python:** 3.13+ | **Дата:** 2025-11-08

</div>
