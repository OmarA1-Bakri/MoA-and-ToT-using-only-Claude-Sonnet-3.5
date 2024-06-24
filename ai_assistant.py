from typing import List, Tuple, Dict
from mixture_of_agents import MixtureOfAgents
from api_utils import make_api_call, AnthropicAPIError, chunk_text
import logging

logger = logging.getLogger(__name__)

class AIAssistant:
    def __init__(self, num_layers: int = 2, agents_per_layer: int = 2, tot_depth: int = 2, tot_branching: int = 2):
        self.moa = MixtureOfAgents(num_layers, agents_per_layer, tot_depth, tot_branching)
        self.max_tokens = 4096

    def _process_with_moa(self, input: str) -> str:
        final_output, _ = self.moa.process(input)
        return final_output

    def _synthesize_final_response(self, user_input: str, moa_output: str, concise: bool = False) -> str:
        system_prompt = f"""You are an AI assistant with access to a large context window. Your task is to synthesize the output from a Mixture of Agents (which includes Tree of Thought processes) into a single, {'concise' if concise else 'comprehensive'} response.
        Your goal is to provide a clear, coherent, and complete answer to the original user input.
        Ensure that your response directly addresses the user's question and incorporates all relevant information from the provided input."""

        user_prompt = f"""Original user input: {user_input}

Mixture of Agents output (including Tree of Thought processes):
{moa_output}

Based on this input, provide a {'concise' if concise else 'comprehensive'} response to the original user input. Be sure to incorporate all relevant information and insights:"""
        
        try:
            return make_api_call(system=system_prompt, messages=[{"role": "user", "content": user_prompt}], max_tokens=self.max_tokens)
        except AnthropicAPIError as e:
            logger.error(f"Error in synthesizing final response: {str(e)}")
            return "I apologize, but I'm unable to provide a response at the moment. Please try again later."

    def respond(self, user_input: str, timeout: int = 180, concise: bool = False) -> Tuple[str, List[Dict[str, str]]]:
        try:
            input_chunks = chunk_text(user_input, self.max_tokens)
            moa_outputs = []
            for chunk in input_chunks:
                moa_output = self._process_with_moa(chunk)
                moa_outputs.append(moa_output)

            combined_moa_output = " ".join(moa_outputs)
            final_response_chunks = chunk_text(combined_moa_output, self.max_tokens)
            final_responses = []

            for chunk in final_response_chunks:
                response = self._synthesize_final_response(user_input, chunk, concise)
                final_responses.append(response)

            final_response = " ".join(final_responses)
            return final_response, self.moa.conversation_history
        except Exception as e:
            logger.error(f"Unexpected error in respond method: {str(e)}")
            return "I apologize, but an unexpected error occurred. Please try again later.", []

    def get_conversation_history(self) -> List[Dict[str, str]]:
        return self.moa.conversation_history