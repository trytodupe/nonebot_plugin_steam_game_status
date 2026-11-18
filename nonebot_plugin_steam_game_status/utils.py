from contextlib import asynccontextmanager
from typing import AsyncIterator

from nonebot import get_driver
from nonebot.internal.driver import HTTPClientMixin, HTTPClientSession
from nonebot_plugin_alconna.uniseg import SupportAdapter

from .config import config_steam, get_steam_api_domain
from .model import ModTarget
from .source import group_list

driver = get_driver()
_shared_session: HTTPClientSession | None = None


def _build_headers() -> dict[str, str]:
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": f"https://{get_steam_api_domain()}/ISteamUser/GetPlayerSummaries/v0002/",
        "TE": "trailers",
    }


@driver.on_shutdown
async def close_shared_http_client() -> None:
    global _shared_session
    if _shared_session is not None:
        try:
            await _shared_session.__aexit__(None, None, None)
        except Exception:
            pass
        _shared_session = None


@asynccontextmanager
async def http_client(**kwargs) -> AsyncIterator[HTTPClientSession]:
    global _shared_session
    if not isinstance(driver, HTTPClientMixin):
        raise TypeError("Current driver does not support http client")

    if not kwargs:
        if _shared_session is None:
            session = driver.get_session(
                headers=_build_headers(),
                proxy=config_steam.steam_proxy,
            )
            await session.__aenter__()
            _shared_session = session
        yield _shared_session
        return

    session = driver.get_session(
        headers=_build_headers(),
        proxy=config_steam.steam_proxy,
        **kwargs,
    )
    try:
        await session.__aenter__()
        yield session
    finally:
        await session.__aexit__(None, None, None)


def to_enum(s: str) -> SupportAdapter:
    for member in SupportAdapter:
        if member.value == s:
            return member
    try:
        return SupportAdapter(s)
    except ValueError:
        return SupportAdapter.onebot11


def get_target(group_id: str) -> ModTarget:
    adapter_name = group_list[group_id]["adapter"]
    return ModTarget(
        id=group_id,
        adapter=to_enum(adapter_name),
    )
