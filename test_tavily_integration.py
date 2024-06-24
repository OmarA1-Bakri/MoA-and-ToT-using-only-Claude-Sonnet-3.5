import pytest
from agent import Agent
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def agent():
    return Agent("TestAgent", tot_depth=2, tot_branching=2)

def test_tavily_api_key():
    assert os.getenv("TAVILY_API_KEY") is not None, "Tavily API key is not set in the environment"

def test_tavily_client_initialization(agent):
    assert isinstance(agent.tavily_client, TavilyClient), "Tavily client is not properly initialized"

def test_search_internet_success(agent):
    query = "What is the capital of France?"
    result = agent.search_internet(query)
    assert isinstance(result, str), "Search result should be a string"
    assert len(result) > 0, "Search result should not be empty"
    assert "Paris" in result, "Search result should contain the correct answer"

def test_search_internet_error_handling(agent, monkeypatch):
    def mock_get_search_context(*args, **kwargs):
        raise Exception("Mocked API error")
    
    monkeypatch.setattr(agent.tavily_client, "get_search_context", mock_get_search_context)
    
    query = "This query should fail"
    result = agent.search_internet(query)
    assert "Error searching the internet" in result, "Error should be properly handled"

if __name__ == "__main__":
    pytest.main([__file__])