import asyncio
import logging
from typing import List, Dict, Any

from agents import Agent, Runner, AsyncOpenAI, AgentOutputSchema, input_guardrail, GuardrailFunctionOutput, RunContextWrapper
from agents import OpenAIChatCompletionsModel, ModelSettings

from config import Config
from models.chat import AgentResponse

# Configure logging
logger = logging.getLogger(__name__)

# Initialize the Judge Agent as a singleton to avoid per-request overhead
# Using the lightweight flash-lite model for fast classification
judge_agent = Agent(
    name="Judge",
    instructions="Determine if the input is related to physical AI, robotics, or technical topics. Respond with 'yes' or 'no'.",
    model=OpenAIChatCompletionsModel(
        model=Config.GEMINI_31_LITE_MODEL,
        openai_client=AsyncOpenAI(
            api_key=Config.GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/"
        )
    )
)


@input_guardrail
async def check_query_relevance(
    ctx: RunContextWrapper, agent: Agent, input_text: str
) -> GuardrailFunctionOutput:
    """
    Native Input Guardrail using the global judge_agent singleton.
    """
    try:
        # Reuse the pre-initialized judge_agent instance
        result = await Runner.run(judge_agent, f"Analyze: {input_text}")
        response = result.final_output.lower().strip()
        is_relevant = 'yes' in response
        
        return GuardrailFunctionOutput(
            tripwire_triggered=not is_relevant,
            output_info="Off-topic query detected" if not is_relevant else None
        )
    except Exception as e:
        logger.error(f"Error in native guardrail: {e}")
        # Fail open for safety if guardrail fails technical execution
        return GuardrailFunctionOutput(tripwire_triggered=False)


def book_knowledge_instructions(ctx: RunContextWrapper, agent: Agent) -> str:
    """
    Dynamic instructions that inject book chunks into the system prompt.
    """
    book_chunks = ctx.context.get("book_chunks", [])
    chunks_text = "\n\n".join([f"Chunk {i+1}:\n{chunk}" for i, chunk in enumerate(book_chunks)])
    
    return f"""
    You are an AI assistant that answers questions based only on the provided book content.
    Your responses must be grounded in the book content provided in the context.
    If the question cannot be answered based on the provided context, politely explain that you don't have the relevant information.
    Do not make up information or go beyond what is provided in the context.
    
    ### BOOK CONTENT CONTEXT:
    {chunks_text}
    """


# Initialize the main BookKnowledgeAgent using openai-agents==0.6 as per specification
book_knowledge_agent = Agent(
    name="BookKnowledgeAgent",
    instructions=book_knowledge_instructions,
    model=OpenAIChatCompletionsModel(
        model="gemini-3.5-flash",
        openai_client=AsyncOpenAI(
            api_key=Config.GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/"
        )
    ),
    model_settings=ModelSettings(
        max_tokens=1000,
        temperature=0.3
    ),
    input_guardrails=[check_query_relevance]
)


async def initialize_agent():
    """
    Initialize the agents with necessary configurations.
    This follows the official OpenAI Agents SDK v0.6 documentation.
    """
    # Basic validation to ensure the API key is set
    if not Config.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is required")

    logger.info("Agents initialized successfully with openai-agents v0.6")