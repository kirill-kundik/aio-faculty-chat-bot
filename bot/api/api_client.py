import asyncio
from typing import List

from aiohttp import ClientSession, ClientResponseError

from api.models import User, Answer


class ApiClientError(Exception):
    pass


class ApiClient:
    def __init__(self, api_url, loop=None):
        self._loop = loop or asyncio.get_event_loop()

        self._session = ClientSession(
            loop=self._loop, raise_for_status=True
        )
        self._api_url = api_url

    async def fetch(
            self,
            method: str = "/",
            verb: str = "GET",
            params: dict = None,
            payload: dict = None,
            headers: dict = None
    ) -> dict:
        url = self._api_url + method

        try:
            async with self._session.request(
                    verb, url, json=payload, params=params, headers=headers
            ) as response:
                response = await response.json()

            return response
        except ClientResponseError as e:
            raise ApiClientError from e

    async def add_user(self, user: User) -> bool:
        await self.fetch(
            method="/user/add",
            verb="POST",
            payload={
                "tg_id": user.tg_id,
                "first_name": user.first_name,
                "username": user.username,
            }
        )

        return True

    async def update_answer(self, answer: Answer) -> bool:
        await self.fetch(
            method=f"/answer/{answer.id_}",
            verb="PUT",
            payload={
                "msg_id": answer.msg_id,
                "rating": answer.rating,
            }
        )

        return True

    async def publish_question(
            self,
            query: str,
            predictor: str,
            tg_id: int,
            msg_id: int,
            chat_id: int
    ) -> Answer:
        resp = await self.fetch(
            method="/search",
            params={
                "user_id": tg_id,
                "query": query,
                "predictor": predictor,
                "msg_id": msg_id,
                "chat_id": chat_id,
            }
        )
        return Answer(
            id_=resp["id"],
            text=resp["text"],
            predictor=predictor
        )

    async def get_all_predictors(self) -> List[str]:
        return (await self.fetch(
            method="/predictor/all",
            verb="GET"
        ))["predictors"]
