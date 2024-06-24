import pytest
from agent import Agent
from dotenv import load_dotenv
import os
import json
import requests

load_dotenv()

@pytest.fixture
def agent():
    return Agent("TestAgent", tot_depth=2, tot_branching=2)

def test_tavily_api_key():
    assert os.getenv("TAVILY_API_KEY") is not None, "Tavily API key is not set in the environment"

def test_search_internet_success(agent):
    query = "What is the capital of France?"
    result = agent.search_internet(query)
    
    assert isinstance(result, str), "Search result should be a string"
    assert len(result) > 0, "Search result should not be empty"
    
    try:
        json_result = json.loads(result)
        assert "Paris" in json.dumps(json_result), "Search result should contain 'Paris'"
    except json.JSONDecodeError:
        pytest.fail("Search result is not a valid JSON string")

def test_search_internet_error_handling(agent, monkeypatch):
    def mock_get_search_context(*args, **kwargs):
        raise requests.exceptions.RequestException("Mocked API error")
    
    monkeypatch.setattr(agent.tavily_client, "get_search_context", mock_get_search_context)
    
    query = "This query should fail"
    result = agent.search_internet(query)
    assert "Error: Mocked API error" in result, "Error should be properly handled"
    assert "Mocked API error" in result, "The specific error message should be included"
def test_search_internet_rate_limiting(agent):
    for _ in range(25):  # Exceeds the rate limit of 20 calls per minute
        agent.search_internet("Test query")
    
    # The 21st call should still succeed due to rate limiting and retrying
    result = agent.search_internet("Final test query")
    assert isinstance(result, str), "Search result should be a string even after exceeding rate limit"
    assert len(result) > 0, "Search result should not be empty even after exceeding rate limit"

if __name__ == "__main__":
    pytest.main([__file__])