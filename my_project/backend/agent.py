import asyncio
import logging
from typing import List, Dict, Any
from dataclasses import dataclass

from agents import Agent, Runner, AsyncOpenAI
from agents import OpenAIChatCompletionsModel, ModelSettings

from config import Config

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class Context:
    """
    Context class for the OpenAI Agents SDK to manage context injection.
    This follows the official SDK documentation for context management.
    """
    book_chunks: List[str]
    query: str
    metadata: Dict[str, Any]


# Initialize the main BookKnowledgeAgent using openai-agents==0.6 as per specification
book_knowledge_agent = Agent(
    name="BookKnowledgeAgent",
    instructions="""
    You are an AI assistant that answers questions based only on the provided book content.
    Your responses must be grounded in the book content provided in the context.
    If the question cannot be answered based on the provided context, politely explain that you don't have the relevant information.
    Do not make up information or go beyond what is provided in the context.
    """,
    model=OpenAIChatCompletionsModel(
        model="gemini-2.5-flash",
        openai_client=AsyncOpenAI(
            api_key=Config.GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/"
        )
    ),
    model_settings=ModelSettings(
        max_tokens=1000,
        temperature=0.3
    )
)


# Initialize the Input Guardrail agent that checks query relevance
input_guardrail_agent = Agent(
    name="InputGuardrailAgent",
    instructions="""
    You are an Input Guardrail agent that determines if a user's query is relevant to book content.
    Your task is to analyze the query and determine if it's related to physical AI, humanoid robotics, or related technical topics.
    Return a simple yes/no decision about whether the query should be processed by the main agent.
    """,
    model=OpenAIChatCompletionsModel(
        model="gemini-2.5-flash",
        openai_client=AsyncOpenAI(
            api_key=Config.GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/"
        )
    ),
    model_settings=ModelSettings(
        max_tokens=100,
        temperature=0.1
    )
)

async def check_query_relevance(query: str) -> bool:
    """
    Use the Input Guardrail agent to check if the query is relevant to book content.

    Args:
        query: The user's query string

    Returns:
        True if the query is relevant to book content, False otherwise
    """
    try:
        guardrail_message = f"""
        Analyze this query: '{query}'

        Determine if this query is related to physical AI, humanoid robotics,
        or other technical topics covered in the book. Respond with 'yes' if
        it's relevant and should be processed, 'no' if it's off-topic.
        """

        result = await Runner.run(
            input_guardrail_agent,
            guardrail_message
        )

        response = result.final_output.lower().strip()
        is_relevant = 'yes' in response or 'relevant' in response

        logger.info(f"Guardrail decision for query '{query[:50]}...': {'relevant' if is_relevant else 'not relevant'}")
        return is_relevant

    except Exception as e:
        logger.error(f"Error in query relevance check: {e}", exc_info=True)
        # Default to allowing the query if guardrail fails
        return True


async def get_agent_response(query: str, context_chunks: List[str]) -> str:
    """
    Generate a response using the OpenAI Agent with provided context.
    Implements the Input Guardrail agent and context management as specified.

    Args:
        query: The user's query
        context_chunks: List of relevant text chunks from the book

    Returns:
        Generated response string
    """
    try:
        # First, use the Input Guardrail agent to check if the query is relevant to book content
        is_relevant = await check_query_relevance(query)

        if not is_relevant:
            logger.info(f"Off-topic query detected by guardrail: {query[:50]}...")
            return "I can only answer questions related to the technical book content. Please ask a question about physical AI, humanoid robotics, or related topics."

        # If we have no relevant chunks for the query, explain that
        if not context_chunks:
            logger.warning(f"No relevant context found for query: {query[:50]}...")
            return "I don't have relevant information in the book to answer your question about this topic."

        # Create a context object using OpenAI Agents SDK context management
        context = Context(
            book_chunks=context_chunks,
            query=query,
            metadata={"timestamp": asyncio.get_event_loop().time()}
        )

        # Use the BookKnowledgeAgent via the documented runner class with context property
        # Pass the query via the documented runner class as specified in requirements
        result = await Runner.run(
            book_knowledge_agent,
            query,  # Pass the query via the documented runner class
            context=context  # Pass context through the separate 'context' property as required
        )

        response = result.final_output
        if not response:
            logger.warning("Empty response from agent")
            return "I couldn't generate a response based on the provided context."

        logger.info("Successfully generated agent response")
        return response

    except Exception as e:
        logger.error(f"Error in get_agent_response: {e}", exc_info=True)
        return "Sorry, I encountered an error while processing your request. Please try again later."


async def initialize_agent():
    """
    Initialize the agents with necessary configurations.
    This follows the official OpenAI Agents SDK v0.6 documentation.
    """
    # Basic validation to ensure the API key is set
    if not Config.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is required")

    logger.info("Agents initialized successfully with openai-agents v0.6")