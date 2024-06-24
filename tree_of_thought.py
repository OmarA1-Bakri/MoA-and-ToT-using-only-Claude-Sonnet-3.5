import logging
from typing import List, Tuple
from thought import Thought
from api_utils import make_api_call, AnthropicAPIError, chunk_text

logger = logging.getLogger(__name__)

class TreeOfThought:
    def __init__(self, max_depth: int = 2, branching_factor: int = 2):
        self.max_depth = max_depth
        self.branching_factor = branching_factor

    def generate_and_evaluate_thoughts(self, prompt: str, depth: int) -> List[Thought]:
        system_prompt = f"""Generate and evaluate {self.branching_factor} thoughts as next steps for the given prompt.
        For each thought, provide an evaluation of 'sure', 'maybe', or 'impossible'.
        Format your response as follows:
        Thought 1: [content] - Evaluation: [evaluation]
        Thought 2: [content] - Evaluation: [evaluation]
        Synthesis: [A brief synthesis of the thoughts, directly addressing the prompt]"""

        user_prompt = f"Depth: {depth}\nPrompt: {prompt}\n\nGenerate and evaluate {self.branching_factor} thoughts:"
        
        try:
            response = make_api_call(system=system_prompt, messages=[{"role": "user", "content": user_prompt}])
            thoughts = []
            for line in response.split('\n'):
                if 'Thought' in line and 'Evaluation:' in line:
                    content, evaluation = line.split(' - Evaluation:')
                    content = content.split(':', 1)[1].strip()
                    thoughts.append(Thought(content.strip(), evaluation.strip()))
            return thoughts[:self.branching_factor]
        except AnthropicAPIError as e:
            logger.error(f"Error generating and evaluating thoughts: {str(e)}")
            return []

    def search(self, initial_prompt: str) -> List[Thought]:
        frontier = [(Thought(initial_prompt), 0)]
        solution = []

        while frontier and len(solution) < self.branching_factor:
            current_thought, depth = frontier.pop(0)
            
            if depth == self.max_depth or current_thought.evaluation == 'sure':
                solution.append(current_thought)
                continue

            if depth < self.max_depth:
                children = self.generate_and_evaluate_thoughts(current_thought.content, depth + 1)
                frontier.extend((child, depth + 1) for child in children if child.evaluation != "impossible")

        return solution

    def process(self, input: str) -> Tuple[List[Thought], str]:
        thoughts = self.search(input)
        synthesis = self.synthesize_thoughts(thoughts)
        return thoughts, synthesis

    def synthesize_thoughts(self, thoughts: List[Thought]) -> str:
        thought_contents = [t.content for t in thoughts]
        system_prompt = "Synthesize the following thoughts into a brief, coherent response:"
        user_prompt = "\n".join(f"Thought {i+1}: {content}" for i, content in enumerate(thought_contents))
        
        try:
            return make_api_call(system=system_prompt, messages=[{"role": "user", "content": user_prompt}], max_tokens=500)
        except AnthropicAPIError as e:
            logger.error(f"Error synthesizing thoughts: {str(e)}")
            return "Unable to synthesize thoughts due to an error."