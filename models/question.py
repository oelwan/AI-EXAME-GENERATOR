"""Model for representing quiz questions."""
from typing import List


class Question:
    """Class representing a quiz question."""
    def __init__(self, question: str, answers: List[str], correct_answer: int):
        """
        Initialize a Question object.
        
        Args:
            question: The question text
            answers: List of answer options
            correct_answer: Index of the correct answer (0-based)
        """
        self.question = question
        self.answers = answers
        self.correct_answer = correct_answer 