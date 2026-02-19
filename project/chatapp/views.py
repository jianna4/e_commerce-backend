from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .agent import agent_executor


@api_view(["POST"])
def chat_view(request):
    user_message = request.data.get("message")

    if not user_message:
        return Response(
            {"error": "Message is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        result = agent_executor.invoke({
            "messages": [
                {"role": "user", "content": user_message}
            ]
        })

        final_message = result["messages"][-1].content

        return Response({"response": final_message})

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
