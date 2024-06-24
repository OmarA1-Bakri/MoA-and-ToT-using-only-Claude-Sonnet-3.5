import os
import logging
import json
from tree_of_thought import TreeOfThought
from api_utils import make_api_call, AnthropicAPIError, CLAUDE_MODEL
from dotenv import load_dotenv
from tavily import TavilyClient
import requests
from ratelimit import limits, sleep_and_retry

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

class Agent:
    def __init__(self, name: str, tot_depth: int = 2, tot_branching: int = 2):
        self.name = name
        self.tot = TreeOfThought(max_depth=tot_depth, branching_factor=tot_branching)
        self.tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

    @sleep_and_retry
    @limits(calls=20, period=60)
    def search_internet(self, query: str) -> str:
        if not self.tavily_client.api_key:
            logger.error("Tavily API key is missing or invalid.")
            return "Error: Tavily API key is missing or invalid."

        try:
            logger.debug(f"Sending request to Tavily API with query: {query}")
            search_result = self.tavily_client.get_search_context(
                query=query,
                search_depth="advanced",
                max_results=3,
            )
            return json.dumps(search_result)
        except requests.exceptions.RequestException as e:
            error_message = f"Error: {str(e)}"
            logging.error(f"Error searching the internet: {str(e)}")
            return error_message
    
    def process(self, input: str) -> str:
        internet_info = self.search_internet(input)
        thoughts, synthesis = self.tot.process(input)
        
        system_prompt = f"""You are AI Agent {self.name} with direct access to internet search results. Use the provided thoughts, synthesis from the Tree of Thought process, and internet information to generate a comprehensive response to the input.
        Include key insights from the thoughts and explain your reasoning. If you need more information, you can request another internet search."""

        user_prompt = f"""Input: {input}

Tree of Thought process:
Thoughts:
{' '.join([str(t) for t in thoughts])}

Synthesis: {synthesis}

Internet Information:
{internet_info}

Based on these thoughts, synthesis, and internet information, provide a comprehensive response. If you need more information, say "SEARCH:" followed by your search query:"""
        
        try:
            response = make_api_call(system=system_prompt, messages=[{"role": "user", "content": user_prompt}], max_tokens=4096)
            
            # Check if the response includes a search request
            if "SEARCH:" in response:
                search_query = response.split("SEARCH:", 1)[1].strip()
                new_info = self.search_internet(search_query)
                
                if "Error" in new_info:
                    logger.warning(f"Error during additional internet search: {new_info}")
                    follow_up_prompt = f"{response}\n\nUnable to perform additional search. Please provide your response based on the available information:"
                else:
                    follow_up_prompt = f"{response}\n\nAdditional Internet Information:\n{new_info}\n\nNow, provide your final response:"
                
                response = make_api_call(system=system_prompt, messages=[{"role": "user", "content": follow_up_prompt}], max_tokens=4096)
            
            return response
        except AnthropicAPIError as e:
            logger.error(f"Error processing input in Agent {self.name}: {str(e)}")
            return f"Error processing input in Agent {self.name}: {str(e)}"

    @staticmethod
    def verify_tavily_api_key():
        if not TAVILY_API_KEY:
            logger.error("Tavily API key is missing. Please add it to your .env file.")
            return False
        
        client = TavilyClient(api_key=TAVILY_API_KEY)
        try:
            client.get_search_context("test query", max_tokens=100)
            logger.info("Tavily API key verified successfully.")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to verify Tavily API key: {str(e)}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Unexpected error verifying Tavily API key: {str(e)}", exc_info=True)
            return False