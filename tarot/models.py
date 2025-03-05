from django.db import models

from config.settings.base import env
from tarot.util import CompletionExecutor
from user.models import User


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TaroChatRooms(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ["created_at"]


class TaroCardContents(TimeStampedModel):
    direction = (("upright", "upright"), ("reversed", "reversed"))
    room = models.ForeignKey(TaroChatRooms, on_delete=models.CASCADE)
    card_name = models.CharField()
    card_direction = models.CharField(choices=direction)
    card_content = models.TextField()

    class Meta:
        ordering = ["created_at"]

    @classmethod
    def generate_tarot_prompt(cls, content: str) -> str:
        completion_executor = CompletionExecutor(
            host="https://clovastudio.stream.ntruss.com",
            api_key=env("CLOVA_API_KEY"),
            request_id=env("GENERATE_REQUEST_ID"),
        )

        preset_text = [
            {
                "role": "system",
                "content": env("GENERATE_CONTENTS"),
            },
            {"role": "user", "content": f"{content}"},
        ]

        request_data = {
            "messages": preset_text,
            "topP": 0.92,
            "topK": 40,
            "maxTokens": 800,
            "temperature": 0.7,
            "repeatPenalty": 1.1,
            "stopBefore": [],
            "includeAiFilters": True,
            "seed": 0,
        }

        chat_response = completion_executor.execute(request_data)
        return chat_response


class TaroChatContents(TimeStampedModel):
    room = models.ForeignKey(TaroChatRooms, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        ordering = ["created_at"]

    @classmethod
    def init_tarot_prompt(cls, content: str) -> str:
        completion_executor = CompletionExecutor(
            host="https://clovastudio.stream.ntruss.com",
            api_key=env("CLOVA_API_KEY"),
            request_id=env("INIT_REQUEST_ID"),
        )
        preset_text = [
            {
                "role": "system",
                "content": env("INIT_CONTENTS"),
            },
            {"role": "user", "content": f"{content}"},
        ]

        request_data = {
            "messages": preset_text,
            "topP": 0.92,
            "topK": 40,
            "maxTokens": 800,
            "temperature": 0.7,
            "repeatPenalty": 1.1,
            "stopBefore": [],
            "includeAiFilters": True,
            "seed": 0,
        }
        chat_response = completion_executor.execute(request_data)
        return chat_response
