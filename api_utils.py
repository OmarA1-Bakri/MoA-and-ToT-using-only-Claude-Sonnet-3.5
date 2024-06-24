import anthropic
import os
import logging
from functools import wraps
import time
import random
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from ratelimit import limits, sleep_and_retry
from dotenv import load_dotenv
import tiktoken
from typing import List

load_dotenv()
logger = logging.getLogger(__name__)
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
CLAUDE_MODEL = "claude-3-5-sonnet-20240620"

class AnthropicAPIError(Exception):
    pass

def rate_limited_api_call(func):
    @wraps(func)
    @sleep_and_retry
    @limits(calls=40, period=60)
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type(exception_types=(AnthropicAPIError, anthropic.RateLimitError)),
        before_sleep=lambda retry_state: logger.info(f"Retrying API call, attempt {retry_state.attempt_number}")
    )
    def wrapper(*args, **kwargs):
        try:
            time.sleep(random.uniform(0.5, 1.5))
            return func(*args, **kwargs)
        except anthropic.RateLimitError as e:
            logger.warning(f"Rate limit reached: {str(e)}. Retrying after backoff.")
            raise AnthropicAPIError(f"Rate limit reached: {str(e)}")
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise AnthropicAPIError(f"API call failed: {str(e)}")
    return wrapper

@rate_limited_api_call
def make_api_call(system: str, messages: list, max_tokens: int = 4096):
    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=min(max_tokens, 4096),
            temperature=0.7,
            system=system,
            messages=messages,
            timeout=30
        )
        return response.content[0].text.strip()
    except anthropic.APITimeoutError:
        logger.error("API call timed out")
        raise AnthropicAPIError("API call timed out")
    except Exception as e:
        logger.error(f"Unexpected error in make_api_call: {str(e)}")
        raise AnthropicAPIError(f"Unexpected error: {str(e)}")

def count_tokens(text: str) -> int:
    encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(encoder.encode(text))

def chunk_text(text: str, max_tokens: int = 4000) -> List[str]:
    chunks = []
    current_chunk = ""
    current_tokens = 0

    for sentence in text.split(". "):
        sentence_tokens = count_tokens(sentence)
        if current_tokens + sentence_tokens > max_tokens:
            chunks.append(current_chunk)
            current_chunk = sentence
            current_tokens = sentence_tokens
        else:
            current_chunk += sentence + ". "
            current_tokens += sentence_tokens

    if current_chunk:
        chunks.append(current_chunk)

    return chunks