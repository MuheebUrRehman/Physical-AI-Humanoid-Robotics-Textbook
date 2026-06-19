import logging
import asyncio
from typing import AsyncIterator, List, Optional, Dict, Any
from datetime import datetime

from agents import Agent, Runner, RunContextWrapper, InputGuardrailTripwireTriggered
from chatkit.server import ChatKitServer, ThreadMetadata, UserMessageItem, ThreadStreamEvent
from chatkit.agents import stream_agent_response
from chatkit.types import ErrorEvent
from store import SQLiteStore

from agent import book_knowledge_agent, book_knowledge_instructions
from retrieval import get_relevant_chunks
from models.chat import RequestContext, PageContext

# Configure logging
logger = logging.getLogger(__name__)

class CustomChatKitServer(ChatKitServer[RequestContext]):
    """
    Custom ChatKit Server that bridges the OpenAI ChatKit protocol
    to the Physical AI & Humanoid Robotics Knowledge Agent.
    """

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """
        Processes a user message and streams the agent response back to ChatKit.
        """
        # Only handle user messages
        if not input_user_message:
            return

        try:
            # 1. Load recent conversation history (last 10 items)
            previous_items = await self.store.load_thread_items(
                thread.id, after=None, limit=10, order="desc", context=context
            )

            # 2. Build history string for prompt (CarFixer pattern)
            # Reversing because order="desc" gives newest first
            def extract_text(content_items: list) -> str:
                texts = []
                for c in content_items:
                    if hasattr(c, 'text') and c.text:
                        texts.append(c.text)
                return "\n".join(texts) if texts else str(content_items)

            role_map = {
                "user_message": "User",
                "assistant_message": "Assistant",
                "client_tool_call": "Tool",
                "widget": "Widget",
            }
            history_lines = []
            for item in reversed(previous_items.data):
                role = role_map.get(getattr(item, 'type', ''), "Unknown")
                text = extract_text(getattr(item, 'content', []))
                if text:
                    history_lines.append(f"{role}: {text}")
            history_str = "\n".join(history_lines)

            # 3. Extract and format Page Context
            page_context_obj = context.page_context
            page_context_str = ""
            if page_context_obj:
                page_context_str = f"\nSTUDENT CONTEXT:\nViewing page: {page_context_obj.title} ({page_context_obj.url})\n"
                if page_context_obj.headings:
                    page_context_str += f"Headings: {', '.join(page_context_obj.headings)}\n"

            # Extract user query text from content items
            user_query = extract_text(input_user_message.content)

            # 4. Perform RAG retrieval
            # Ground the search in both user message and page title for better relevance
            search_query = user_query
            if page_context_obj:
                search_query = f"{page_context_obj.title}: {search_query}"
            
            relevant_chunks = await get_relevant_chunks(search_query)

            # 5. Prepare runtime context for the agent
            agent_run_context = {
                "book_chunks": relevant_chunks,
                "page_context": page_context_obj.model_dump() if page_context_obj else None,
                "user_id": context.user_id,
                "thread_id": thread.id
            }

            # 6. Create a dynamic instruction wrapper
            # This prepends history and page context to the existing book knowledge instructions
            def dynamic_instructions(ctx: RunContextWrapper, agent: Agent) -> str:
                base_instructions = book_knowledge_instructions(ctx, agent)
                return f"{history_str}\n{page_context_str}\n{base_instructions}"

            # 7. Execute the agent with streaming
            # We use a transient agent clone to avoid modifying the global singleton
            run_agent = Agent(
                name=book_knowledge_agent.name,
                instructions=dynamic_instructions,
                model=book_knowledge_agent.model,
                model_settings=book_knowledge_agent.model_settings,
                input_guardrails=book_knowledge_agent.input_guardrails
            )

            # Stream results through the ChatKit SSE bridge
            result = Runner.run_streamed(
                run_agent, 
                user_query, 
                context=agent_run_context
            )

            # 8. Yield events to ChatKit using AgentContext
            from chatkit.agents import AgentContext as ChatKitAgentContext
            agent_ctx = ChatKitAgentContext(
                thread=thread,
                store=self.store,
                request_context=context,
            )
            sent_any_event = False
            async for event in stream_agent_response(agent_ctx, result):
                yield event
                sent_any_event = True

        except asyncio.CancelledError:
            raise
        except InputGuardrailTripwireTriggered:
            logger.info("Guardrail triggered (InputGuardrailTripwireTriggered) in ChatKit respond")
            if not sent_any_event:
                yield ErrorEvent(
                    code="custom",
                    message="I can only answer questions related to Physical AI and Robotics.",
                    allow_retry=False,
                )
        except Exception as e:
            logger.error(f"Error in ChatKit respond loop: {str(e)}")
            # Only yield ErrorEvent if no response tokens were streamed yet.
            # If events were already sent, the client has partial output and
            # an ErrorEvent would corrupt the conversation state.
            if not sent_any_event:
                yield ErrorEvent(
                    code="custom",
                    message=f"Sorry, something went wrong: {str(e)[:200]}",
                    allow_retry=True,
                )

async def initialize_chatkit_server(db_path: str = "chatkit.db") -> CustomChatKitServer:
    """
    Initializes the SQLite store and ChatKit server.
    """
    store = SQLiteStore(db_path)
    await store.initialize()
    return CustomChatKitServer(store=store)
