import asyncio
import os
from datetime import datetime, timedelta
from aiohttp import ClientSession, ClientError
from typing import Final, Any, List
from dataclasses import dataclass

GITHUB_API_BASE_URL: Final[str] = "https://api.github.com"
MAX_CONCURRENT_REQUESTS: Final[int] = int(os.getenv("MAX_CONCURRENT_REQUESTS", 10))
REQUESTS_PER_SECOND: Final[int] = int(os.getenv("REQUESTS_PER_SECOND", 5))

@dataclass
class RepositoryAuthorCommitsNum:
    author: str
    commits_num: int

@dataclass
class Repository:
    name: str
    owner: str
    position: int
    stars: int
    watchers: int
    forks: int
    language: str
    authors_commits_num_today: List[RepositoryAuthorCommitsNum]

class GithubReposScrapper:
    def __init__(self, access_token: str):
        self._session = ClientSession(
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Bearer {access_token}",
            }
        )
        self._semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        self._rate_limiter = asyncio.Semaphore(REQUESTS_PER_SECOND)

    async def _make_request(self, endpoint: str, method: str = "GET", params: dict[str, Any] | None = None) -> Any:
        async with self._rate_limiter:
            await asyncio.sleep(1 / REQUESTS_PER_SECOND)
            async with self._session.request(method, f"{GITHUB_API_BASE_URL}/{endpoint}", params=params) as response:
                response.raise_for_status()
                return await response.json()

    async def _get_top_repositories(self, limit: int = 100) -> list[dict[str, Any]]:
        data = await self._make_request(
            endpoint="search/repositories",
            params={"q": "stars:>1", "sort": "stars", "order": "desc", "per_page": limit},
        )
        return data["items"]

    async def _get_repository_commits(self, owner: str, repo: str) -> list[dict[str, Any]]:
        since = (datetime.utcnow() - timedelta(days=1)).isoformat() + 'Z'
        data = await self._make_request(
            endpoint=f"repos/{owner}/{repo}/commits",
            params={"since": since},
        )
        return data

    async def _fetch_repository_data(self, repo_data: dict[str, Any]) -> Repository:
        async with self._semaphore:
            try:
                commits = await self._get_repository_commits(repo_data["owner"]["login"], repo_data["name"])
                authors_commits = {}
                for commit in commits:
                    author = commit["commit"]["author"]["name"]
                    authors_commits[author] = authors_commits.get(author, 0) + 1
                authors_commits_list = [RepositoryAuthorCommitsNum(author, num) for author, num in authors_commits.items()]
                return Repository(
                    name=repo_data["name"],
                    owner=repo_data["owner"]["login"],
                    position=repo_data["stargazers_count"],
                    stars=repo_data["stargazers_count"],
                    watchers=repo_data["watchers_count"],
                    forks=repo_data["forks_count"],
                    language=repo_data["language"],
                    authors_commits_num_today=authors_commits_list,
                )
            except ClientError as e:
                print(f"Failed to fetch data for repository {repo_data['name']}: {e}")
                return None

    async def get_repositories(self) -> list[Repository]:
        top_repos = await self._get_top_repositories()
        tasks = [self._fetch_repository_data(repo) for repo in top_repos]
        repositories = await asyncio.gather(*tasks)
        return [repo for repo in repositories if repo is not None]

    async def close(self):
        await self._session.close()