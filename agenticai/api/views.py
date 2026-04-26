from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from agents.runner import AgentRunner
from .models import AgentSession, ConversationMessage

class AgentQueryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        session_id = data.get("session_id")
        input_text = data.get("input")
        options = data.get("options", {})

        if not input_text:
            return Response({"error": "input required"}, status=status.HTTP_400_BAD_REQUEST)

        if session_id:
            session = get_object_or_404(AgentSession, pk=session_id)
        else:
            session = AgentSession.objects.create(user=request.user)

        ConversationMessage.objects.create(session=session, role="user", content=input_text)

        runner = AgentRunner()
        result = runner.run(session_id=str(session.id), input=input_text, options=options, user=request.user)

        ConversationMessage.objects.create(session=session, role="assistant", content=result.get("response", ""))

        return Response(result, status=status.HTTP_200_OK)
