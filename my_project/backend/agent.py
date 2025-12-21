import asyncio
import logging
from typing import List

from agents import Agent, Runner, AsyncOpenAI
from agents import OpenAIChatCompletionsModel, ModelSettings

from config import Config

# Configure logging
logger = logging.getLogger(__name__)

# Initialize agent with OpenAIChatCompletionsModel using Gemini API
# Using the openai-agents package with custom base_url for Gemini
gemini_agent = Agent(
    name="BookKnowledgeAgent",
    instructions="""
    You are an AI assistant that answers questions based only on the provided book content.
    Your responses must be grounded in the book content provided in the context.
    If the question cannot be answered based on the provided context, politely explain that you don't have the relevant information.
    Do not make up information or go beyond what is provided in the context.
    """,
    model=OpenAIChatCompletionsModel(
        model="gemini-2.5-flash",  # Using Gemini model name
        openai_client=AsyncOpenAI(
            api_key=Config.GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/"  # Using Gemini API base URL
        )
    ),
    model_settings=ModelSettings(
        max_tokens=1000,
        temperature=0.3
    )
)

# Define topics related to the book content for classification
BOOK_TOPICS = [
    "physical ai", "humanoid robotics", "robotics", "ai", "artificial intelligence",
    "machine learning", "neural networks", "computer vision", "natural language processing",
    "reinforcement learning", "embodied ai", "robot learning", "motor control",
    "sensorimotor learning", "robot navigation", "path planning", "manipulation",
    "locomotion", "robot control", "robot perception", "robot cognition"
]


async def classify_content_relevance(query: str) -> bool:
    """
    Determine if the query is related to book content.

    Args:
        query: The user's query string

    Returns:
        True if the query is related to book content, False otherwise
    """
    query_lower = query.lower()

    # Check if the query contains any book-related topics
    for topic in BOOK_TOPICS:
        if topic in query_lower:
            return True

    # Additional check: if query is too general or off-topic
    off_topic_indicators = [
        "weather", "joke", "song", "recipe", "movie", "sports", "gossip",
        "personal advice", "therapy", "relationship advice", "investment advice"
    ]

    for indicator in off_topic_indicators:
        if indicator in query_lower:
            return False

    # If no clear off-topic indicators and some technical terms are present,
    # assume it might be relevant
    technical_indicators = [
        "algorithm", "code", "function", "data", "model", "system", "process",
        "method", "technique", "framework", "architecture", "design", "theory"
    ]

    for indicator in technical_indicators:
        if indicator in query_lower:
            return True

    # Default to being permissive if uncertain
    return True


async def get_agent_response(query: str, context_chunks: List[str]) -> str:
    """
    Generate a response using the OpenAI Agent with provided context.

    Args:
        query: The user's query
        context_chunks: List of relevant text chunks from the book

    Returns:
        Generated response string
    """
    try:
        # First, check if the query is related to book content
        is_relevant = await classify_content_relevance(query)

        if not is_relevant:
            logger.info(f"Off-topic query detected: {query[:50]}...")
            return "I can only answer questions related to the technical book content. Please ask a question about physical AI, humanoid robotics, or related topics."

        # If we have no relevant chunks for the query, explain that
        if not context_chunks:
            logger.warning(f"No relevant context found for query: {query[:50]}...")
            return "I don't have relevant information in the book to answer your question about this topic."

        # Combine the context chunks into a single context string
        context = "\n\n".join(context_chunks)
        logger.info(f"Using {len(context_chunks)} context chunks for query: {query[:50]}...")

        # Create a prompt that includes the context and query
        user_message = f"""
        Context: {context}

        Question: {query}

        Please provide an answer based only on the context provided above.
        """

        # Use the openai-agents Runner to execute the agent with the formatted message
        result = await Runner.run(
            gemini_agent,
            user_message
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
    Initialize the agent with necessary configurations.
    This function can be expanded to include more complex initialization logic if needed.
    """
    # Basic validation to ensure the API key is set
    if not Config.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is required")

    # Additional initialization logic can be added here if needed
    print("Agent initialized successfully with openai-agents package")