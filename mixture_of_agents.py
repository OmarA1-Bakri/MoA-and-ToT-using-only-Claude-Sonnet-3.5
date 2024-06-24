from typing import List, Tuple, Dict
from agent import Agent
from api_utils import make_api_call, AnthropicAPIError, chunk_text
import logging

logger = logging.getLogger(__name__)

class MixtureOfAgents:
    def __init__(self, num_layers: int = 2, agents_per_layer: int = 2, tot_depth: int = 2, tot_branching: int = 2):
        self.num_layers = num_layers
        self.agents_per_layer = agents_per_layer
        self.layers = [[Agent(f"L{i}A{j}", tot_depth, tot_branching) for j in range(agents_per_layer)] for i in range(num_layers)]
        self.conversation_history: List[Dict[str, str]] = []

    def process_layer(self, input: str, layer: int) -> List[str]:
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.conversation_history[-5:]])  # Use last 5 messages as context
        return [agent.process(f"Context:\n{context}\n\nCurrent Input: {input}") for agent in self.layers[layer]]

    def synthesize_layer_outputs(self, layer_outputs: List[str]) -> str:
        system_prompt = """You are an AI assistant synthesizing multiple agent outputs. Each agent has access to internet search results and Tree of Thought processes. 
        Combine the following outputs into a coherent response, highlighting key insights and differences. If you need more information, you can request another internet search."""
        user_prompt = "\n".join([f"Agent {i+1} output: {output}" for i, output in enumerate(layer_outputs)])
        user_prompt += "\n\nSynthesize these outputs. If you need more information, say 'SEARCH:' followed by your search query:"
        
        try:
            response = make_api_call(system=system_prompt, messages=[{"role": "user", "content": user_prompt}], max_tokens=4096)
            
            # Check if the response includes a search request
            if "SEARCH:" in response:
                search_query = response.split("SEARCH:", 1)[1].strip()
                new_info = self.layers[0][0].search_internet(search_query)  # Use the first agent to perform the search
                
                if "Error" in new_info:
                    logger.warning(f"Error during internet search: {new_info}")
                    follow_up_prompt = f"{response}\n\nUnable to perform additional search. Please provide your synthesis based on the available information:"
                else:
                    follow_up_prompt = f"{response}\n\nAdditional Internet Information:\n{new_info}\n\nNow, provide your final synthesis:"
                
                response = make_api_call(system=system_prompt, messages=[{"role": "user", "content": follow_up_prompt}], max_tokens=4096)
            
            return response
        except AnthropicAPIError as e:
            logger.error(f"Error in synthesis: {str(e)}")
            return f"Error in synthesis: {str(e)}"

    def process(self, input: str) -> Tuple[str, List[str]]:
        self.conversation_history.append({"role": "user", "content": input})
        all_outputs = []
        current_input = input

        for layer in range(self.num_layers):
            layer_outputs = self.process_layer(current_input, layer)
            all_outputs.extend(layer_outputs)
            current_input = self.synthesize_layer_outputs(layer_outputs)

        self.conversation_history.append({"role": "assistant", "content": current_input})
        return current_input, all_outputs