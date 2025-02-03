from django.shortcuts import render
from rest_framework import viewsets

from tarot.serializers import TaroChatContentsInitSerializer


# Create your views here.
class TarotInitViewSet(viewsets.GenericViewSet):

    serializer_class = TaroChatContentsInitSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        # gpt 로직
        self.get_serializer(data=request.data)
