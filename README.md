# tg-toxic-moderator

Telegram-бот для автоматической модерации сообщений с использованием дообученной модели **RuBERT**.

Бот классифицирует сообщения и удаляет их, если вероятность токсичности превышает заданный порог.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-2CA5E0.svg)](https://docs.aiogram.dev/)
[![transformers](https://img.shields.io/badge/transformers-4.x-yellow.svg)](https://huggingface.co/docs/transformers/)
[![uv](https://img.shields.io/badge/managed%20by-uv-purple.svg)](https://github.com/astral-sh/uv)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Overview

Проект демонстрирует полный цикл интеграции ML-модели в сервис:

* инференс HuggingFace-модели;
* интеграция с Telegram через `aiogram 3`;
* разделение конфигурации и бизнес-логики;
* асинхронная обработка сообщений;
* конфигурация через `.env`, YAML и JSON.

Проект учебный и предназначен для отработки практик **ML Engineering**.

## Model

| Parameter  | Value                                 |
| ---------- | ------------------------------------- |
| Model      | RuBERT (`rubert-base-conversational`) |
| Task       | Binary classification                 |
| Classes    | `toxic / non-toxic`                   |
| Test F1    | **0.8941**                            |
| Threshold  | `0.5`                                 |
| Max length | `128` tokens                          |

Модель обучена отдельно и хранится локально в `models/rubert_base_v1/`.

Веса модели не коммитятся в Git.

Исходный код обучения, сравнение моделей и метрики — в репозитории
[`kvashin-om/toxic-comment-classification`](https://github.com/kvashin-om/toxic-comment-classification).

## Features

* автоматическое удаление токсичных сообщений;
* настраиваемый `threshold`;
* `dry-run` режим;
* логирование результатов классификации;
* конфигурация через `.env`, `config.yaml` и `inference_config.json`;
* команды `/start` и `/ping`.

## Requirements

* Python 3.11+
* [uv](https://github.com/astral-sh/uv)
* Telegram Bot Token
* обученная модель в `models/rubert_base_v1/`
  (см. [toxic-comment-classification](https://github.com/kvashin-om/toxic-comment-classification))

Для запуска через Docker дополнительно:

* Docker
* Docker Compose (плагин `docker compose`)

## Installation

```bash
git clone https://github.com/<your-username>/tg-toxic-moderator.git
cd tg-toxic-moderator
uv sync
```

Создайте `.env`:

```bash
cp .env.example .env
```

Укажите токен:

```ini
BOT_TOKEN=123456789:AA...
```

Добавьте модель:

```text
models/rubert_base_v1/
├── config.json
├── model.safetensors
├── tokenizer.json
├── tokenizer_config.json
└── inference_config.json
```

Запуск:

```bash
uv run python -m app.main
```

## Docker

Для запуска в контейнере есть готовый `Dockerfile` (multi-stage на базе `python:3.13-slim` + `uv`) и `docker-compose.yml`.

### Сборка образа

```bash
docker build -t tg-toxic-moderator:v1.0 .
```

### Запуск через Docker Compose

`docker-compose.yml`:

```yaml
services:
  bot:
    build: .
    image: tg-toxic-moderator:v1.0
    env_file: .env
    volumes:
      - ./models:/app/models:ro
    restart: unless-stopped
```

Команды:

```bash
# сборка и запуск
docker compose up -d --build

# логи
docker compose logs -f bot

# остановка
docker compose down
```

### Как это работает

* `Dockerfile` использует `python:3.13-slim` и устанавливает зависимости через `uv sync --frozen --no-dev` — окружение фиксируется по `uv.lock`, dev-зависимости не попадают в образ.
* Модель **не копируется в образ**, а монтируется с хоста через volume: `./models:/app/models:ro`. Так образ остаётся лёгким, а веса можно обновлять без пересборки.
* `.env` передаётся через `env_file` — секреты (`BOT_TOKEN`) не попадают в образ и в git.
* `restart: unless-stopped` — контейнер поднимается после перезагрузки хоста и после падений.

### Обновление после изменений

```bash
docker compose up -d --build
```

Пересоберёт образ и перезапустит контейнер. Модель и `.env` не затрагиваются.

## Configuration

### `.env`

Секреты:

```ini
BOT_TOKEN=...
```

### `config.yaml`

Настройки приложения:

```yaml
delete_enabled: true
model_dir: models/rubert_base_v1
```

`delete_enabled: false` включает `dry-run` режим.

### `inference_config.json`

Параметры инференса:

```json
{
  "max_len": 128,
  "threshold": 0.5,
  "toxic_class_idx": 1
}
```

| Parameter         | Description                           |
| ----------------- | ------------------------------------- |
| `max_len`         | Максимальная длина последовательности |
| `threshold`       | Порог вероятности токсичности         |
| `toxic_class_idx` | Индекс токсичного класса              |

## Project Structure

```text
tg-toxic-moderator/
├── app/
│   ├── classifier.py
│   ├── config.py
│   ├── logger.py
│   ├── main.py
│   └── handlers/
│       ├── __init__.py
│       ├── common.py
│       ├── messages.py
│       └── moderation.py
├── models/
│   └── rubert_base_v1/
├── config.yaml
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── pyproject.toml
└── uv.lock
```

## Telegram Setup

### Group Privacy

Чтобы бот получал все сообщения группы:

`@BotFather` → `/mybots` → Bot Settings → Group Privacy → **Turn off**

После изменения настройки добавьте бота в группу заново.

### Permissions

Бот должен быть администратором группы с правом:

**Delete messages**

### Check

```text
/ping → pong
neutral message → toxic=False
toxic message → toxic=True
```

## Development

Перед включением удаления рекомендуется использовать `dry-run`:

```yaml
delete_enabled: false
```

После проверки результатов:

```yaml
delete_enabled: true
```

Порог `threshold` подбирается на валидационной выборке с учётом требуемого баланса между **Precision** и **Recall**.

## Roadmap

* [x] ML-модель и инференс
* [x] Telegram-бот
* [x] Разделение слоёв
* [x] Dry-run
* [x] Docker / Docker Compose
* [ ] Структурированное логирование
* [ ] VPS deployment
* [ ] Metrics / monitoring
* [ ] FastAPI inference service
* [ ] Prediction cache
* [ ] Inference batching

## Tech Stack

* **Python 3.11+**
* **aiogram 3**
* **PyTorch**
* **Transformers**
* **Pydantic Settings**
* **uv**
* **Docker / Docker Compose**

## Related Projects

* [`kvashin-om/toxic-comment-classification`](https://github.com/kvashin-om/toxic-comment-classification) — обучение, сравнение моделей и экспорт артефакта `rubert_base_v1`, используемого этим ботом.

## License

MIT. См. [`LICENSE`](LICENSE).

---
