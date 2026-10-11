
## Содержание

1. [Обзор](#1-обзор)
2. [Архитектура](#2-архитектура)
3. [Модели данных](#3-модели-данных)
4. [Слои приложения](#4-слои-приложения)
5. [Обработка ошибок](#5-обработка-ошибок)
6. [Логирование](#6-логирование)
7. [API Reference](#7-api-reference)
   - [Categories](#71-categories)
   - [Media](#72-media)
   - [Seasons](#73-seasons)
   - [Episodes](#74-episodes)
8. [Типичные сценарии](#8-типичные-сценарии)
9. [Правила разработки](#9-правила-разработки)

---

## 1. Обзор

REST API для управления медиатекой: фильмы, сериалы, сезоны, эпизоды и категории. Построено на **FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL**, с разделением на слои **Router → Service → CRUD → Model**.

**Ключевые возможности:**
- CRUD для медиа, категорий, сезонов, эпизодов.
- Many-to-Many связь между медиа и категориями.
- Каскадное удаление категорий (с очисткой связей).
- Поиск, фильтрация, пагинация.
- Ролевой доступ (`ADMIN`, `MANEGER`) на write-операциях.
- Централизованное логирование через `loguru`.
- Единая обработка ошибок БД (`IntegrityError`, `SQLAlchemyError`) с `rollback`.

**Стек:**
| Слой | Технология |
|---|---|
| Web | FastAPI |
| ORM | SQLAlchemy 2.0 (async, `AsyncSession`) |
| БД | PostgreSQL (asyncpg) |
| Валидация | Pydantic v2 |
| Логи | loguru |
| Авторизация | `role_guard` (JWT + роли) |

---

## 2. Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                       HTTP Client                       │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│  Router (src/api/v1/endpoints/*.py)                     │
│  • Валидация Pydantic                                   │
│  • Проверка роли (role_guard)                           │
│  • HTTP-статусы и response_model                        │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│  Service (src/services/*.py)                            │
│  • Бизнес-логика                                        │
│  • Проверка инвариантов (уникальность, существование)   │
│  • Бросает HTTPException                                │
│  • Логирует ключевые операции                           │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│  CRUD (src/crud/*.py)                                   │
│  • Работа с AsyncSession                                │
│  • try/except + rollback + logger                       │
│  • Возвращает ORM-модели                                │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│  Models (src/model/model.py)                            │
│  SQLAlchemy ORM                                         │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│                      PostgreSQL                         │
└─────────────────────────────────────────────────────────┘
```

**Принципы:**
- **Router** не знает про SQLAlchemy — только про сервис.
- **Service** не пишет SQL напрямую — только через CRUD.
- **CRUD** не бросает `HTTPException` — только `SQLAlchemyError`/`IntegrityError` наружу.
- **Model** не знает про HTTP.

---

## 3. Модели данных

### Category
| Поле | Тип | Описание |
|---|---|---|
| `id` | int, PK | Идентификатор |
| `name` | str, unique | Уникальное имя |
| `media` | M2M → Media | Привязанные медиа |

### Media
| Поле | Тип | Описание |
|---|---|---|
| `id` | int, PK | Идентификатор |
| `title` | str | Название |
| `description` | str | Описание |
| `type` | str | `"movie"` или `"tv_show"` |
| `categories` | M2M → Category | Категории |
| `seasons` | 1-to-M → Season | Только для `tv_show` |
| `episodes` | 1-to-M → Episode | Только для `movie` |

### Season
| Поле | Тип | Описание |
|---|---|---|
| `id` | int, PK | Идентификатор |
| `media_id` | FK → Media | Родительский сериал |
| `season_number` | int | Номер сезона (уникален в рамках медиа) |
| `episodes` | 1-to-M → Episode | Эпизоды |

### Episode
| Поле | Тип | Описание |
|---|---|---|
| `id` | int, PK | Идентификатор |
| `season_id` | FK → Season, nullable | Родительский сезон (для сериалов) |
| `media_id` | FK → Media, nullable | Прямой родитель (для фильмов) |

### Связь `media_category`
| Колонка | Описание |
|---|---|
| `media_id` | FK → Media |
| `category_id` | FK → Category |

---

## 4. Слои приложения

### 4.1 Router
**Путь:** `src/api/v1/endpoints/`

Отвечает только за:
- приём HTTP-запроса и его валидацию (Pydantic);
- проверку роли через `role_guard([...])`;
- вызов сервиса;
- возврат ответа согласно `response_model`.

**Не делает:** SQL, бизнес-логику, обработку `SQLAlchemyError`.

### 4.2 Service
**Путь:** `src/services/`

Отвечает за:
- бизнес-правила («нельзя создать две категории с одним именем»);
- проверку существования связанных сущностей;
- бросание `HTTPException` с корректным статусом;
- обёртку write-операций в `try/except` + `rollback` + `logger`.

**Не делает:** прямых SQL-запросов — только через CRUD.

### 4.3 CRUD
**Путь:** `src/crud/`

Отвечает за:
- формирование запросов SQLAlchemy;
- работу с `AsyncSession`;
- `try/except` для `SQLAlchemyError` / `IntegrityError`;
- `rollback` при write-операциях;
- логирование на уровнях `debug` / `info` / `warning` / `error` / `exception`.

**Не бросает** `HTTPException` — только `raise` исходного исключения.

### 4.4 Base
**Путь:** `src/crud/base.py`

Базовый CRUD с дженериками: `CRUDBase[Model, CreateSchema]`. Предоставляет `get`, `create`, `update`, `remove`.

---

## 5. Обработка ошибок

### Уровни ошибок

| Уровень | Где бросается | Пример |
|---|---|---|
| HTTP | Router / Service | `HTTPException(404, "Медиаресурс не найден.")` |
| БД | CRUD | `SQLAlchemyError`, `IntegrityError` |
| Валидация | Pydantic | автоматически FastAPI → 422 |

### Соответствие исключений и HTTP-кодов

| Ситуация | Исключение | HTTP |
|---|---|---|
| Сущность не найдена | `HTTPException` | `404 Not Found` |
| Дубликат имени категории | `HTTPException` | `400 Bad Request` |
| Связь уже существует | `HTTPException` | `400 Bad Request` |
| Некорректный ввод | `RequestValidationError` | `422 Unprocessable Entity` |
| Нет прав | `HTTPException` (role_guard) | `401/403` |
| Ошибка БД (непредвиденная) | `SQLAlchemyError` | `500 Internal Server Error` |
| FK/UNIQUE нарушение | `IntegrityError` | `500` (или `400`, если сервис перехватит) |

### Паттерн обработки в CRUD

```python
try:
    # запрос
    await db.commit()
except IntegrityError as e:
    await db.rollback()
    logger.error(f"...: {e}")
    raise
except SQLAlchemyError as e:
    await db.rollback()
    logger.exception(f"...: {e}")
    raise
```

**Правила:**
- `IntegrityError` — **до** `SQLAlchemyError`, т.к. это подкласс.
- `rollback` — **обязателен** во всех write-операциях.
- `raise` — пробрасываем наверх, чтобы сервис/роутер вернул корректный код.

---

## 6. Логирование

Используется `loguru`. Уровни:

| Уровень | Когда |
|---|---|
| `debug` | Успешные read-операции, метрики (сколько записей, параметры) |
| `info` | Успешные write-операции (создание, обновление, удаление) |
| `warning` | Запись не найдена (не ошибка), связь отсутствует |
| `error` | `IntegrityError` — ожидаемая прикладная ошибка |
| `exception` | `SQLAlchemyError` — с traceback |

**Контекст в логах:** id сущности, параметры пагинации, query, список id.

**Пример:**
```
INFO  | Медиа id=42 добавлено в категорию id=7
DEBUG | Поиск 'matrix' дал 3 результатов (skip=0, limit=100)
WARN  | Связь медиа id=5 с категорией id=9 не найдена — нечего удалять
ERROR | Нарушение целостности при добавлении медиа id=999 в категорию id=1: ...
```

---

## 7. API Reference

Базовый URL: `/api/v1`

### 7.1 Categories

Префикс: `/categories`

#### `POST /categories/create`
Создать категорию.

**Доступ:** `ADMIN`, `MANAGER`

**Body:**
```json
{ "name": "Фантастика" }
```

**Response 201:**
```json
{ "id": 1, "name": "Фантастика" }
```

**Ошибки:**
- `400` — категория с таким именем уже существует.
- `401/403` — нет прав.

---

#### `GET /categories/`
Список всех категорий.

**Response 200:**
```json
[
  { "id": 1, "name": "Фантастика" },
  { "id": 2, "name": "Драма" }
]
```

---

#### `GET /categories/with-count`
Категории с количеством медиа.

**Query:**
| Параметр | Тип | Default | Описание |
|---|---|---|---|
| `skip` | int ≥ 0 | 0 | Пропустить N |
| `limit` | int 1–100 | 100 | Максимум |

**Response 200:**
```json
[
  { "id": 1, "name": "Фантастика", "media_count": 12 },
  { "id": 2, "name": "Драма",      "media_count": 3 }
]
```

---

#### `GET /categories/{category_id}`
Категория по ID.

**Response 200:** `CategoryRead`

**Ошибки:** `404` — категория не найдена.

---

#### `GET /categories/{category_id}/media`
Категория со списком медиа.

**Response 200:** `CategoryWithMediaRead`

**Ошибки:** `404`.

---

#### `PUT /categories/{category_id}`
Обновить категорию.

**Доступ:** `ADMIN`, `MANAGER`

**Body:** `CategoryUpdate` (частичное обновление)

**Response 200:** `CategoryRead`

**Ошибки:**
- `400` — новое имя занято.
- `404` — категория не найдена.

---

#### `DELETE /categories/{category_id}`
Каскадное удаление категории.

**Доступ:** `ADMIN`, `MANAGER`

**Поведение:**
1. Проверяет существование.
2. Удаляет все связи в `media_category`.
3. Удаляет саму категорию.
4. Всё в одной транзакции.

**Response 204:** пустой.

**Ошибки:** если категория не найдена — просто ничего не делает (идемпотентно), логирует warning.

---

#### `POST /categories/{category_id}/media/{media_id}`
Привязать медиа к категории.

**Доступ:** `ADMIN`, `MANAGER`

**Response 200:**
```json
{ "message": "Медиа успешно добавлено в категорию", "success": true }
```

**Ошибки:**
- `404` — категория или медиа не найдены.
- `400` — связь уже существует.

---

#### `DELETE /categories/{category_id}/media/{media_id}`
Отвязать медиа от категории.

**Доступ:** `ADMIN`, `MANAGER`

**Response 200:**
```json
{ "message": "Медиа успешно удалено из категории", "success": true }
```

**Ошибки:** `404` — связь не найдена.

---

### 7.2 Media

Префикс: `/media`

#### `POST /media/create`
Создать медиа (фильм или сериал).

**Доступ:** `ADMIN`, `MANAGER`

**Body:**
```json
{
  "title": "Матрица",
  "description": "Классика научной фантастики",
  "type": "movie",
  "category_ids": [1, 2]
}
```

**Response 201:** `MediaRead`

**Ошибки:**
- `400` — одна или несколько категорий не найдены.
- `422` — невалидный `type`.

---

#### `GET /media/movies`
Список фильмов.

**Query:** `skip` (≥0, default 0), `limit` (1–100, default 100).

**Response 200:** `List[MediaRead]`

---

#### `GET /media/tv-shows`
Список сериалов. Параметры — как у `/movies`.

---

#### `GET /media/category/{category_id}`
Медиа по категории.

**Ошибки:** `404` — категория не найдена.

---

#### `GET /media/search`
Поиск по названию или описанию.

**Query:**
| Параметр | Тип | Обязателен |
|---|---|---|
| `query` | str, ≥1 | да |
| `skip` | int ≥ 0 | нет |
| `limit` | int 1–100 | нет |

**Ошибки:** `400` — пустой query.

---

#### `GET /media/recent`
Последние добавленные медиа.

**Query:** `limit` (1–50, default 10).

---

#### `GET /media/{media_id}`
Детальная информация о медиа.

**Response 200:** `MediaDetailRead`
- для `movie` — привязанные эпизоды;
- для `tv_show` — сезоны с эпизодами;
- всегда — категории.

**Ошибки:** `404`.

---

#### `PUT /media/{media_id}`
Обновить медиа (включая полную замену категорий, если передан `category_ids`).

**Доступ:** `ADMIN`, `MANAGER`

**Response 200:** `MediaRead`

**Ошибки:** `404`.

---

#### `DELETE /media/{media_id}`
Удалить медиа.

**Доступ:** `ADMIN`, `MANAGER`

**Response 204.**

**Ошибки:** `404`.

---

#### `GET /media/{media_id}/seasons`
Все сезоны сериала.

**Response 200:** `List[SeasonRead]`

**Ошибки:** `404` — медиа не найдено.

---

### 7.3 Seasons

Префикс: `/media/seasons`

#### `POST /media/seasons/create`
Создать сезон.

**Доступ:** `ADMIN`, `MANAGER`

**Body:** `SeasonCreate`
```json
{ "media_id": 5, "season_number": 1 }
```

**Response 201:** `SeasonRead`

**Ошибки:**
- `404` — медиа не найдено.
- `400` — медиа не `tv_show`; сезон с таким номером уже существует.

---

#### `GET /media/seasons/{season_id}`
Сезон со всеми эпизодами.

**Response 200:** `SeasonWithEpisodesRead`

**Ошибки:** `404`.

---

#### `PUT /media/seasons/{season_id}`
Обновить сезон.

**Доступ:** `ADMIN`, `MANAGER`

**Response 200:** `SeasonRead`

**Ошибки:** `404`.

---

#### `DELETE /media/seasons/{season_id}`
Удалить сезон.

**Доступ:** `ADMIN`, `MANAGER`

**Response 204.**

**Ошибки:** `404`.

---

#### `GET /media/seasons/{season_id}/episodes`
Все эпизоды сезона.

**Response 200:** `List[EpisodeRead]`

**Ошибки:** `404`.

---

### 7.4 Episodes

Префикс: `/media/episodes`

#### `POST /media/episodes/create`
Создать эпизод.

**Доступ:** `ADMIN`, `MANAGER`

**Body:** `EpisodeCreate`
```json
{ "season_id": 3, "media_id": null, "title": "Пилот" }
```

**Правила:**
- должен быть указан хотя бы один родитель (`season_id` или `media_id`);
- если `media.type == "tv_show"` — обязателен `season_id`.

**Response 201:** `EpisodeRead`

**Ошибки:**
- `400` — оба родителя `None`; сериал без `season_id`.
- `404` — сезон или медиа не найдены.

---

#### `GET /media/episodes/{episode_id}`
Эпизод с информацией о родителях.

**Response 200:** `EpisodeRead`

**Ошибки:** `404`.

---

#### `PUT /media/episodes/{episode_id}`
Обновить эпизод.

**Доступ:** `ADMIN`, `MANAGER`

**Response 200:** `EpisodeRead`

**Ошибки:** `404`.

---

#### `DELETE /media/episodes/{episode_id}`
Удалить эпизод.

**Доступ:** `ADMIN`, `MANAGER`

**Response 204.**

**Ошибки:** `404`.

---

## 8. Типичные сценарии

### Сценарий 1. Создать фильм с категориями

```bash
curl -X POST http://localhost:8000/api/v1/media/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Матрица",
    "description": "Классика",
    "type": "movie",
    "category_ids": [1, 2]
  }'
```

### Сценарий 2. Создать сериал → сезон → эпизод

```bash
# 1. сериал
curl -X POST .../media/create -d '{"title":"Breaking Bad","type":"tv_show"}'
# → {"id": 10, ...}

# 2. сезон
curl -X POST .../media/seasons/create -d '{"media_id":10,"season_number":1}'
# → {"id": 20, ...}

# 3. эпизод
curl -X POST .../media/episodes/create \
  -d '{"season_id":20,"media_id":10,"title":"Pilot"}'
# → {"id": 30, ...}
```

### Сценарий 3. Каскадное удаление категории

```bash
curl -X DELETE .../categories/3 -H "Authorization: Bearer $TOKEN"
# 204
# В логах: "Категория id=3 каскадно удалена (связей удалено: 5)"
```

### Сценарий 4. Привязать/отвязать медиа

```bash
# привязать
curl -X POST .../categories/3/media/42 -H "Authorization: Bearer $TOKEN"
# {"message":"Медиа успешно добавлено в категорию","success":true}

# отвязать
curl -X DELETE .../categories/3/media/42 -H "Authorization: Bearer $TOKEN"
# {"message":"Медиа успешно удалено из категории","success":true}
```

---

## 9. Правила разработки

### 9.1 Где что писать

| Задача | Слой |
|---|---|
| Новый HTTP-эндпоинт | Router |
| Проверка «нельзя создать дубликат» | Service |
| SQL-запрос | CRUD |
| Изменение таблицы | Model + Alembic |

### 9.2 Чек-лист нового метода в CRUD

- [ ] Обёрнут в `try/except`.
- [ ] `IntegrityError` ловится **до** `SQLAlchemyError`.
- [ ] В `except` — `await db.rollback()` (для write).
- [ ] В конце — `raise`.
- [ ] Логи на `debug` (read) / `info` (write) / `warning` (not found) / `error|exception` (errors).
- [ ] Контекст в логе: id, параметры, счётчики.

### 9.3 Чек-лист нового метода в Service

- [ ] Возвращает ORM-модель или бросает `HTTPException`.
- [ ] Проверяет существование всех связанных сущностей.
- [ ] Не пишет SQL напрямую.
- [ ] Не делает `commit` — это делает CRUD.
- [ ] Логирует ключевые бизнес-события (`info`).

### 9.4 Чек-лист нового эндпоинта

- [ ] Указан `response_model`.
- [ ] Указан `status_code`.
- [ ] Указан `summary` и `description`.
- [ ] Write-операции защищены `role_guard(["ADMIN","MANAGER"])`.
- [ ] **Статические пути объявлены выше динамических** (`/movies` выше `/{media_id}`).
- [ ] Query-параметры валидированы (`ge`, `le`, `min_length`).

### 9.5 Соглашения об именовании

| Слой | Префикс / пример |
|---|---|
| CRUD | `get_*`, `add_*`, `remove_*`, `update_*` |
| Service | `create_*`, `get_*`, `update_*`, `delete_*` |
| Router | `create_new_*`, `get_all_*`, `get_*_by_id` |
| Схемы | `*Create`, `*Update`, `*Read`, `*DetailRead` |

### 9.6 Работа с сессией

- `commit`/`rollback` — **внутри CRUD**.
- Service не коммитит, кроме случаев, когда он сам делает `db.add` + `db.commit` (как в `create_media`, `create_season`, `create_episode`) — это допустимое исключение, но лучше унифицировать через `CRUDBase.create`.
- `AsyncSession` инжектится через `Depends(get_async_db)`.

---

## Приложение. Карта эндпоинтов (шпаргалка)

```
CATEGORIES
  POST   /categories/create                      ADMIN, MANAGER
  GET    /categories/
  GET    /categories/with-count
  GET    /categories/{id}
  GET    /categories/{id}/media
  PUT    /categories/{id}                        ADMIN, MANAGER
  DELETE /categories/{id}                        ADMIN, MANAGER  (каскад)
  POST   /categories/{id}/media/{media_id}       ADMIN, MANAGER
  DELETE /categories/{id}/media/{media_id}       ADMIN, MANAGER

MEDIA
  POST   /media/create                           ADMIN, MANAGER
  GET    /media/movies
  GET    /media/tv-shows
  GET    /media/category/{category_id}
  GET    /media/search?query=...
  GET    /media/recent
  GET    /media/{id}
  PUT    /media/{id}                             ADMIN, MANAGER
  DELETE /media/{id}                             ADMIN, MANAGER
  GET    /media/{id}/seasons

SEASONS
  POST   /media/seasons/create                   ADMIN, MANAGER
  GET    /media/seasons/{id}
  PUT    /media/seasons/{id}                     ADMIN, MANAGER
  DELETE /media/seasons/{id}                     ADMIN, MANAGER
  GET    /media/seasons/{id}/episodes

EPISODES
  POST   /media/episodes/create                  ADMIN, MANAGER
  GET    /media/episodes/{id}
  PUT    /media/episodes/{id}                    ADMIN, MANAGER
  DELETE /media/episodes/{id}                    ADMIN, MANAGER
```

---

Готово. Если нужно — могу дополнительно:
- сделать **OpenAPI-описание** (`openapi.yaml`) на основе этого;
- добавить раздел **«Миграции»** (Alembic) с описанием текущих FK и `ondelete`;
- расписать **тесты** (pytest + httpx.AsyncClient) по каждому эндпоинту;
- сделать **README.md** с быстрым стартом (docker-compose, `.env`, миграции).