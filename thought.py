class Thought:
    """
    Represents a single thought in the Tree of Thought algorithm.

    Attributes:
        content (str): The content of the thought.
        evaluation (str, optional): The evaluation of the thought ('sure', 'maybe', 'impossible').
    """

    def __init__(self, content: str, evaluation: str = None):
        self.content = content
        self.evaluation = evaluation

    def __str__(self):
        return f"Thought: {self.content} - Evaluation: {self.evaluation}"

    def __repr__(self):
        return self.__str__()