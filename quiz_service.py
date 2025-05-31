import re
from dataclasses import dataclass
from typing import List, Dict, Any, Union, Optional, Tuple

@dataclass
class Question:
    question: str
    answers: List[str] = None
    correct_answer: int = None
    reference_answer: str = None
    starter_code: str = None
    test_cases: str = None

def generate_quiz_prompt(
    topics: str, 
    num_questions: int, 
    difficulty: str, 
    num_options: int = 4,
    question_types: List[str] = ["multiple_choice"],
    type_counts: Dict[str, int] = None
) -> str:
    """
    Generate a prompt for quiz generation with customized question types.
    
    Args:
        topics: The topics for the questions
        num_questions: The number of questions to generate
        difficulty: The difficulty level (Easy, Medium, or Hard)
        num_options: The number of options for multiple-choice questions
        question_types: List of question types to include
        type_counts: Dictionary specifying how many of each question type to generate
        
    Returns:
        A string prompt for the LLM
    """
    # Validate inputs
    valid_types = ["multiple_choice", "open_ended", "coding"]
    question_types = [qt for qt in question_types if qt in valid_types]
    
    if not question_types:
        question_types = ["multiple_choice"]  # Default to multiple choice
        
    # If type_counts is not provided, distribute questions evenly
    if not type_counts:
        type_counts = {}
        remaining = num_questions
        
        for i, q_type in enumerate(question_types):
            if i == len(question_types) - 1:
                # Last type gets all remaining questions
                type_counts[q_type] = remaining
            else:
                # Distribute evenly with at least 1 question per type
                count = max(1, num_questions // len(question_types))
                type_counts[q_type] = count
                remaining -= count
    
    # Build prompt for each question type
    type_instructions = []
    
    # Instructions for multiple choice questions
    if "multiple_choice" in question_types and type_counts.get("multiple_choice", 0) > 0:
        mc_count = type_counts.get("multiple_choice")
        mc_prompt = f"""
- Generate {mc_count} multiple-choice questions.
- Each multiple-choice question should have exactly {num_options} options labeled A, B, C, etc.
- Include only one correct answer.
- Make incorrect options plausible.
- For each question, clearly indicate the correct option.
"""
        type_instructions.append(mc_prompt)
    
    # Instructions for open-ended questions
    if "open_ended" in question_types and type_counts.get("open_ended", 0) > 0:
        oe_count = type_counts.get("open_ended")
        oe_prompt = f"""
- Generate {oe_count} open-ended questions.
- For each open-ended question, provide a reference answer that would be considered correct.
- Make these questions suitable for evaluating deeper understanding of machine learning concepts.
"""
        type_instructions.append(oe_prompt)
    
    # Instructions for coding questions
    if "coding" in question_types and type_counts.get("coding", 0) > 0:
        coding_count = type_counts.get("coding")
        coding_prompt = f"""
- Generate {coding_count} coding questions.
- Each coding question should include:
  - A clear problem statement
  - Starter code template in Python for students to complete
  - Sample test cases to verify solutions
- Focus on ML implementation tasks like creating models, preprocessing data, or evaluating results.
"""
        type_instructions.append(coding_prompt)
    
    # Combine all instructions
    type_instructions_str = "\n".join(type_instructions)
    
    # Main prompt
    prompt = f"""
You are an expert Machine Learning educator. Create a set of {num_questions} {difficulty.lower()}-level machine learning quiz questions on the following topics: {topics}.

Question Requirements:
{type_instructions_str}

General Guidelines:
- Questions must be specifically about machine learning, focusing on {topics}
- Create {difficulty} level questions appropriate for undergraduate/graduate students
- Be clear and concise in your wording
- Avoid ambiguous questions

Response Format:
Return the questions with the following structure:

For Multiple-Choice Questions:
Question: [Question text]
A. [Option A]
B. [Option B]
C. [Option C]
D. [Option D]
Correct Answer: [Letter of correct option]

For Open-Ended Questions:
Question: [Question text]
Reference Answer: [Sample correct answer]

For Coding Questions:
Question: [Problem statement]
Starter Code:
```python
[Starter code template]
```
Test Cases:
```python
[Test cases]
```

Format all questions properly for parsing.
"""
    return prompt

def parse_questions(text: str) -> List[Question]:
    """Parse questions from generated text."""
    questions = []
    
    # Pattern to match multiple-choice questions with labeled options and correct answer
    mc_pattern = r"Question: (.*?)(?:\n|$)(?:(?:A\.|A\)) (.*?)(?:\n|$)(?:B\.|B\)) (.*?)(?:\n|$)(?:C\.|C\)) (.*?)(?:\n|$)(?:D\.|D\)) (.*?)(?:\n|$))?(?:E\.|E\)) (.*?)(?:\n|$))?(?:F\.|F\)) (.*?)(?:\n|$))?Correct Answer: ([A-F])"
    
    # Pattern to match open-ended questions
    open_pattern = r"Question: (.*?)(?:\n|$)Reference Answer: (.*?)(?:\n\n|$)"
    
    # Pattern to match coding questions
    coding_pattern = r"Question: (.*?)(?:\n|$)Starter Code:\s*```(?:python)?\s*(.*?)```(?:\n|$)Test Cases:\s*```(?:python)?\s*(.*?)```"
    
    # Find all multiple-choice questions
    for match in re.finditer(mc_pattern, text, re.DOTALL):
        question_text = match.group(1).strip()
        
        # Get all options that are present
        options = [match.group(i).strip() for i in range(2, 7) if match.group(i) is not None]
        
        # Map the letter (A, B, C...) to index (0, 1, 2...)
        correct_letter = match.group(8).strip()
        correct_index = ord(correct_letter) - ord('A')
        
        # Ensure correct_index is within range
        if correct_index >= len(options):
            correct_index = 0
        
        questions.append(Question(
            question=question_text,
            answers=options,
            correct_answer=correct_index
        ))
    
    # Find all open-ended questions
    for match in re.finditer(open_pattern, text, re.DOTALL):
        question_text = match.group(1).strip()
        reference_answer = match.group(2).strip()
        
        questions.append(Question(
            question=question_text,
            reference_answer=reference_answer
        ))
    
    # Find all coding questions
    for match in re.finditer(coding_pattern, text, re.DOTALL):
        question_text = match.group(1).strip()
        starter_code = match.group(2).strip()
        test_cases = match.group(3).strip()
        
        questions.append(Question(
            question=question_text,
            starter_code=starter_code,
            test_cases=test_cases
        ))
    
    return questions

def calculate_quiz_score(questions: List[Question], user_answers: Dict[int, int]) -> Tuple[int, int, float]:
    """Calculate the score for a quiz."""
    if not questions:
        return 0, 0, 0.0
        
    correct = 0
    total = len(questions)
    answered_questions = 0
    
    for i, question in enumerate(questions):
        if i in user_answers and hasattr(question, 'correct_answer'):
            answered_questions += 1
            if user_answers[i] == question.correct_answer:
                correct += 1
    
    # If no questions were answered, score is 0
    if answered_questions == 0:
        return 0, total, 0.0
        
    # Calculate score based on total questions, not just answered ones
    score_pct = (correct / total) * 100 if total > 0 else 0
    
    return correct, total, score_pct

def create_quiz_summary(questions: List[Question], user_answers: Dict[int, int]) -> str:
    """Create a summary of the quiz results."""
    correct, total, score_pct = calculate_quiz_score(questions, user_answers)
    
    summary = f"You got {correct} out of {total} correct ({score_pct:.1f}%).\n\n"
    
    # Add feedback based on score
    if score_pct >= 90:
        summary += "Excellent! You have a strong understanding of the material.\n\n"
    elif score_pct >= 70:
        summary += "Good job! You've grasped most of the concepts, but there's room for improvement.\n\n"
    elif score_pct >= 50:
        summary += "You have a basic understanding, but should review the material more.\n\n"
    else:
        summary += "You need to spend more time studying this material.\n\n"
    
    # Add question-by-question breakdown
    summary += "Question Breakdown:\n\n"
    
    for i, question in enumerate(questions):
        if hasattr(question, 'correct_answer'):  # Multiple choice
            user_answer_idx = user_answers.get(i, -1)
            correct_answer_idx = question.correct_answer
            
            summary += f"Q{i+1}: {question.question}\n"
            
            for j, answer in enumerate(question.answers):
                if j == correct_answer_idx:
                    if j == user_answer_idx:
                        summary += f"✓ {answer} (Your answer - Correct)\n"
                    else:
                        summary += f"✓ {answer} (Correct answer)\n"
                elif j == user_answer_idx:
                    summary += f"✗ {answer} (Your answer - Incorrect)\n"
                else:
                    summary += f"  {answer}\n"
            
            summary += "\n"
    
    return summary

def generate_analysis_prompt(questions: List[Question], user_answers: Dict[int, int]) -> str:
    """Generate a prompt for analyzing quiz performance."""
    correct, total, score_pct = calculate_quiz_score(questions, user_answers)
    
    # Create a detailed breakdown of the quiz
    question_breakdown = ""
    
    for i, question in enumerate(questions):
        if hasattr(question, 'correct_answer'):  # Multiple choice
            user_answer_idx = user_answers.get(i, -1)
            correct_answer_idx = question.correct_answer
            
            question_breakdown += f"Question {i+1}: {question.question}\n"
            
            # User's answer
            if user_answer_idx >= 0 and user_answer_idx < len(question.answers):
                user_answer = question.answers[user_answer_idx]
                question_breakdown += f"User's answer: {user_answer}\n"
            else:
                question_breakdown += "User's answer: None\n"
            
            # Correct answer
            correct_answer = question.answers[correct_answer_idx]
            question_breakdown += f"Correct answer: {correct_answer}\n"
            
            # Status
            if user_answer_idx == correct_answer_idx:
                question_breakdown += "Status: Correct\n"
            else:
                question_breakdown += "Status: Incorrect\n"
            
            question_breakdown += "\n"
    
    # Create the analysis prompt
    prompt = f"""
You are an expert in education and machine learning. I'd like you to analyze a student's performance on a machine learning quiz.

Quiz Performance Summary:
- Total Questions: {total}
- Correct Answers: {correct}
- Score: {score_pct:.1f}%

Question Breakdown:
{question_breakdown}

Based on this performance, please provide:
1. An analysis of the student's strengths and weaknesses
2. Specific concepts the student should focus on reviewing
3. Recommended resources or study strategies based on their performance
4. Patterns in their misconceptions or errors

Your analysis should be constructive, educational, and aimed at helping the student improve their understanding of machine learning concepts.
"""
    return prompt

def parse_quiz_analysis(text: str) -> Dict[str, str]:
    """Parse the quiz analysis response."""
    # Extract different sections of the analysis
    strengths_pattern = r"(?:Strengths|STRENGTHS):(.*?)(?:Weaknesses|WEAKNESSES|Areas for Improvement|AREAS FOR IMPROVEMENT|$)"
    weaknesses_pattern = r"(?:Weaknesses|WEAKNESSES|Areas for Improvement|AREAS FOR IMPROVEMENT):(.*?)(?:Concepts to Review|CONCEPTS TO REVIEW|Recommended Resources|RECOMMENDED RESOURCES|$)"
    review_pattern = r"(?:Concepts to Review|CONCEPTS TO REVIEW):(.*?)(?:Recommended Resources|RECOMMENDED RESOURCES|$)"
    resources_pattern = r"(?:Recommended Resources|RECOMMENDED RESOURCES):(.*?)(?:Patterns in Misconceptions|PATTERNS IN MISCONCEPTIONS|$)"
    patterns_pattern = r"(?:Patterns in Misconceptions|PATTERNS IN MISCONCEPTIONS):(.*?)$"
    
    # Extract each section using regex
    strengths_match = re.search(strengths_pattern, text, re.DOTALL | re.IGNORECASE)
    weaknesses_match = re.search(weaknesses_pattern, text, re.DOTALL | re.IGNORECASE)
    review_match = re.search(review_pattern, text, re.DOTALL | re.IGNORECASE)
    resources_match = re.search(resources_pattern, text, re.DOTALL | re.IGNORECASE)
    patterns_match = re.search(patterns_pattern, text, re.DOTALL | re.IGNORECASE)
    
    # Create a dictionary with the analysis sections
    analysis = {
        "overview": text.strip(),  # Full analysis
        "strengths": strengths_match.group(1).strip() if strengths_match else "",
        "weaknesses": weaknesses_match.group(1).strip() if weaknesses_match else "",
        "concepts_to_review": review_match.group(1).strip() if review_match else "",
        "recommended_resources": resources_match.group(1).strip() if resources_match else "",
        "misconception_patterns": patterns_match.group(1).strip() if patterns_match else ""
    }
    
    return analysis

def generate_practice_quiz(topics: str, weaknesses: str, num_questions: int = 5, difficulty: str = "Medium") -> str:
    """Generate a practice quiz prompt focused on a student's weak areas."""
    prompt = f"""
You are an expert Machine Learning educator. Create a personalized practice quiz with {num_questions} questions to help a student improve in their areas of weakness.

Focus Topics: {topics}
Areas of Weakness: {weaknesses}
Difficulty: {difficulty}

Requirements:
- Create {num_questions} multiple-choice questions focusing specifically on the weakness areas
- Each question should have 4 options with exactly one correct answer
- Make incorrect options plausible but clearly wrong to someone who understands the concept
- Questions should be slightly challenging but designed to reinforce correct understanding
- Include explanations for why each answer is correct or incorrect

Response Format:
For each question use this format:
Question: [Question text]
A. [Option A]
B. [Option B]
C. [Option C]
D. [Option D]
Correct Answer: [Letter of correct option]
Explanation: [Detailed explanation of why this answer is correct and why others are incorrect]

Remember that these questions are designed to teach, not just test. The explanations are particularly important.
"""
    return prompt 