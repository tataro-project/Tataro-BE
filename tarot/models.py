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


class TaroCardContents(TimeStampedModel):
    room = models.ForeignKey(TaroChatRooms, on_delete=models.CASCADE)
    card_id = models.IntegerField()
    card_content = models.TextField()

    @classmethod
    def generate_tarot_prompt(cls, content: str) -> str:
        completion_executor = CompletionExecutor(
            host="https://clovastudio.stream.ntruss.com",
            api_key=env("API_KEY"),
            request_id=env("GENERATE_REQUEST_ID"),
        )

        preset_text = [
            {
                "role": "system",
                "content": env("GENERATE_CONTENTS"),
            },
            {"role": "user", "content": f"{content}"},
            {
                "role": "assistant",
                "content": "🔮 카드:44번 -Eight of Cups (컵 8번) 역방향🔮\n역방향의 Eight of Cups는 과거와의 연결을 끊고 새로운 시작을 향해 나아가는 것을 의미해요. 🪐\n지금까지의 관계 패턴이 반복되는 것에 지친 두 사람에게는 잠시 떨어져 있는 시간이 필요할 수도 있어요. 어쩌면 이번 싸움이 서로의 솔직한 마음을 털어놓고 진짜 문제를 해결할 기회가 될지도 몰라요. 💊\n여자친구분께 먼저 연락하기 전에, 이 갈등이 어디서 시작되었는지, 각자 어떤 감정을 느끼고 있는지 천천히 생각해 보세요. 그리고 그 마음을 담아 조심스럽게 이야기를 건네보는 거예요. 📝\n타로 카드는 두 분이 이 어려움을 함께 이겨내고 더욱 단단한 관계로 나아갈 수 있다고 말하고 있어요. 🌟 지금은 조금 힘들더라도, 포기하지 않고 서로를 이해하려 노력해 봐요. 분명 더 행복한 미래가 기다리고 있을 테니까요! 😊",
            },
        ]

        request_data = {
            "messages": preset_text,
            "topP": 0.8,
            "topK": 0,
            "maxTokens": 498,
            "temperature": 0.5,
            "repeatPenalty": 5.0,
            "stopBefore": [],
            "includeAiFilters": True,
            "seed": 0,
        }

        chat_response = completion_executor.execute(request_data)
        return chat_response


class TaroChatContents(TimeStampedModel):
    room = models.ForeignKey(TaroChatRooms, on_delete=models.CASCADE)
    content = models.TextField()

    @classmethod
    def init_tarot_prompt(cls, content: str) -> str:
        completion_executor = CompletionExecutor(
            host="https://clovastudio.stream.ntruss.com",
            api_key=env("API_KEY"),
            request_id=env("INIT_REQUEST_ID"),
        )

        preset_text = [
            {
                "role": "system",
                "content": env("INIT_CONTENTS"),
            },
            {"role": "user", "content": f"{content}"},
            {"role": "assistant", "content": "연애운이 궁금하구나? 솔로탈출을 위해 카드를 뽑아 볼까?"},
        ]

        request_data = {
            "messages": preset_text,
            "topP": 0.8,
            "topK": 0,
            "maxTokens": 256,
            "temperature": 0.5,
            "repeatPenalty": 5.0,
            "stopBefore": [],
            "includeAiFilters": True,
            "seed": 0,
        }
        chat_response = completion_executor.execute(request_data)
        return chat_response
