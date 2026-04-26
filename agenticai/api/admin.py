from django.contrib import admin
from .models import AgentSession, ConversationMessage, LongTermMemory, Document

admin.site.register(AgentSession)
admin.site.register(ConversationMessage)
admin.site.register(LongTermMemory)
admin.site.register(Document)
