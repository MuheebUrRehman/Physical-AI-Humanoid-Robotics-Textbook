import asyncio
import logging
from typing import List, Dict, Any

from agents import Agent, Runner, AsyncOpenAI, input_guardrail, GuardrailFunctionOutput, RunContextWrapper
from agents import OpenAIChatCompletionsModel, ModelSettings
from agents import InputGuardrailTripwireTriggered

from config import Config
from models.chat import AgentResponse

logger = logging.getLogger(__name__)


def _build_openai_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=Config.LLM_API_KEY,
        base_url=Config.LLM_BASE_URL,
        default_headers={
            "HTTP-Referer": Config.LLM_SITE_URL,
            "X-Title": Config.LLM_APP_NAME,
        },
    )


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
    book_chunks = ctx.context.get("book_chunks", [])
    chunk_lines = []
    for i, chunk in enumerate(book_chunks):
        if isinstance(chunk, dict):
            source = chunk.get("source", "")
            text = chunk.get("text", str(chunk))
            score = chunk.get("score")
            label = f"Chunk {i+1}" + (f" [from {source}]" if source else "")
            if score is not None:
                label += f" (relevance: {score:.3f})"
            chunk_lines.append(f"{label}:\n{text}")
        else:
            chunk_lines.append(f"Chunk {i+1}:\n{chunk}")
    chunks_text = "\n\n".join(chunk_lines)

    return f"""
    You are an AI assistant that answers questions based ONLY on the provided book content below.
    You must NOT use any external knowledge or training data.

    If the question cannot be answered based on the provided chunks, say:
    "I cannot find this in the textbook."

    Do NOT make up information. Do NOT go beyond what is provided in the context.
    If the context includes page context (URL, title, headings), prioritize information related to that page.

    ### BOOK CONTENT CONTEXT:
    {chunks_text}
    """


book_knowledge_agent = Agent(
    name="BookKnowledgeAgent",
    instructions=book_knowledge_instructions,
    model=OpenAIChatCompletionsModel(
        model=Config.LLM_MODEL,
        openai_client=_build_openai_client(),
    ),
    model_settings=ModelSettings(
        max_tokens=500,
        temperature=0.2
    ),
    input_guardrails=[check_query_relevance]
)
