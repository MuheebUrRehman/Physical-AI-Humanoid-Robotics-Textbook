import asyncio
import logging
from typing import List, Dict, Any

from agents import Agent, Runner, AsyncOpenAI, AgentOutputSchema, input_guardrail, GuardrailFunctionOutput, RunContextWrapper
from agents import OpenAIChatCompletionsModel, ModelSettings

from config import Config
from models.chat import AgentResponse

# Configure logging
logger = logging.getLogger(__name__)


def _build_openai_client() -> AsyncOpenAI:
    """Build an OpenAI-compatible client pointing at OpenRouter (or any provider).

    Injects identity headers required by OpenRouter. Works with any
    OpenAI-compatible endpoint by changing LLM_BASE_URL / LLM_API_KEY.
    """
    return AsyncOpenAI(
        api_key=Config.LLM_API_KEY,
        base_url=Config.LLM_BASE_URL,
        default_headers={
            "HTTP-Referer": Config.LLM_SITE_URL,
            "X-Title": Config.LLM_APP_NAME,
        },
    )


# Judge Agent — singleton for fast off-topic detection
judge_agent = Agent(
    name="Judge",
    instructions="Determine if the input is related to physical AI, robotics, or technical topics. Respond with 'yes' or 'no'.",
    model=OpenAIChatCompletionsModel(
        model=Config.LLM_MODEL,
        openai_client=_build_openai_client(),
    ),
)


@input_guardrail
async def check_query_relevance(
    ctx: RunContextWrapper, agent: Agent, input_text: str
) -> GuardrailFunctionOutput:
    """
    Native Input Guardrail using the global judge_agent singleton.
    """
    try:
        result = await Runner.run(judge_agent, f"Analyze: {input_text}")
        response = result.final_output.lower().strip()
        is_relevant = 'yes' in response

        return GuardrailFunctionOutput(
            tripwire_triggered=not is_relevant,
            output_info="Off-topic query detected" if not is_relevant else None
        )
    except Exception as e:
        logger.error(f"Error in native guardrail: {e}")
        return GuardrailFunctionOutput(
            output_info=None,
            tripwire_triggered=False,
        )


def book_knowledge_instructions(ctx: RunContextWrapper, agent: Agent) -> str:
    """
    Dynamic instructions that inject book chunks into the system prompt.
    """
    book_chunks = ctx.context.get("book_chunks", [])
    chunk_lines = []
    for i, chunk in enumerate(book_chunks):
        if isinstance(chunk, dict):
            source = chunk.get("source", "")
            text = chunk.get("text", str(chunk))
            label = f"Chunk {i+1}" + (f" [from {source}]" if source else "")
            chunk_lines.append(f"{label}:\n{text}")
        else:
            chunk_lines.append(f"Chunk {i+1}:\n{chunk}")
    chunks_text = "\n\n".join(chunk_lines)

    return f"""
    You are an AI assistant that answers questions based only on the provided book content.
    Your responses must be grounded in the book content provided in the context.

    If the context provided includes information about what the student is currently viewing (URL, title, or headings),
    prioritize answering using information related to that page while still remaining grounded in the provided chunks.

    If the question cannot be answered based on the provided context, politely explain that you don't have the relevant information.
    Do not make up information or go beyond what is provided in the context.

    ### BOOK CONTENT CONTEXT:
    {chunks_text}
    """


# Main BookKnowledgeAgent — routes through OpenRouter (or configured provider)
book_knowledge_agent = Agent(
    name="BookKnowledgeAgent",
    instructions=book_knowledge_instructions,
    model=OpenAIChatCompletionsModel(
        model=Config.LLM_MODEL,
        openai_client=_build_openai_client(),
    ),
    model_settings=ModelSettings(
        max_tokens=1000,
        temperature=0.3
    ),
    input_guardrails=[check_query_relevance]
)
