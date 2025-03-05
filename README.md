Github Repositories Scraper

## Описание

Эта программа предназначена для асинхронного получения данных о популярных репозиториях на GitHub. Она использует GitHub API для получения информации о репозиториях и их коммитах за последний день. Программа ограничивает количество одновременных запросов и запросов в секунду, чтобы избежать превышения лимитов API.

## Установка

1. Клонируйте репозиторий:
    ```sh
    git clone <URL вашего репозитория>
    cd <название директории>
    ```

2. Создайте виртуальное окружение и активируйте его:
    ```sh
    python -m venv venv
    source venv/bin/activate  # для Windows используйте `venv\Scripts\activate`
    ```

3. Установите зависимости:
    ```sh
    pip install -r requirements.txt
    ```

## Настройка

Создайте файл `.env` в корне проекта и добавьте следующие переменные окружения:

```
GITHUB_ACCESS_TOKEN=<ваш GitHub access token>
MAX_CONCURRENT_REQUESTS=10
REQUESTS_PER_SECOND=5
```

## Использование

Пример использования программы:

```python
import asyncio
import os
from main import GithubReposScrapper

async def main():
    access_token = os.getenv("GITHUB_ACCESS_TOKEN")
    scrapper = GithubReposScrapper(access_token)
    repositories = await scrapper.get_repositories()
    for repo in repositories:
        print(repo)
    await scrapper.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Описание классов и методов

### Класс `GithubReposScrapper`

#### Методы

- `__init__(self, access_token: str)`: Инициализирует объект сессии и семафоры для ограничения запросов.
- `async def _make_request(self, endpoint: str, method: str = "GET", params: dict[str, Any] | None = None) -> Any`: Выполняет асинхронный запрос к GitHub API.
- `async def _get_top_repositories(self, limit: int = 100) -> list[dict[str, Any]]`: Получает список топовых репозиториев.
- `async def _get_repository_commits(self, owner: str, repo: str) -> list[dict[str, Any]]`: Получает список коммитов репозитория за последний день.
- `async def _fetch_repository_data(self, repo_data: dict[str, Any]) -> Repository`: Получает данные о репозитории и его коммитах.
- `async def get_repositories(self) -> list[Repository]`: Возвращает список объектов `Repository` с данными о репозиториях и их коммитах.
- `async def close(self)`: Закрывает сессию.

### Классы данных

- `RepositoryAuthorCommitsNum`: Содержит информацию об авторе и количестве его коммитов.
- `Repository`: Содержит информацию о репозитории и списке авторов с количеством их коммитов за последний день.

## Лицензия

Этот проект лицензирован под лицензией MIT. Подробности см. в файле LICENSE.