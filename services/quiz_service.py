"""
Quiz service module that handles quiz generation, parsing, and evaluation.
"""
import re
from typing import List, Dict, Any, Tuple, Optional
from services.llm_service import generate_content


class Question:
    """Class representing a quiz question."""
    def __init__(self, question, answers=None, correct_answer=None, reference_answer=None, starter_code=None, test_cases=None):
        self.question = question
        self.answers = answers
        self.correct_answer = correct_answer
        self.reference_answer = reference_answer
        self.starter_code = starter_code
        self.test_cases = test_cases


def generate_quiz_prompt(topics: str, num_questions: int, difficulty: str, num_options: int = 4, question_types: List[str] = ["multiple_choice"], type_counts: Dict[str, int] = None) -> str:
    """
    Generate a prompt for the LLM to create a quiz.
    
    Args:
        topics: Topics for the quiz
        num_questions: Number of questions to generate
        difficulty: Difficulty level
        num_options: Number of answer options per question
        question_types: List of question types to include
        type_counts: Dictionary specifying how many of each question type to generate
        
    Returns:
        A formatted prompt string
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
- Each multiple-choice question should have exactly {num_options} options labeled A, B, C, and D.
- Include only one correct answer.
- Make incorrect options plausible but clearly wrong.
- For each question, clearly indicate the correct option with "Correct Answer: [Letter]" at the end.
- Ensure all options are meaningful and directly related to the question.
- Avoid placeholder text or generic options.
- Make sure the correct answer is unambiguous and well-justified.
"""
        type_instructions.append(mc_prompt)
    
    # Instructions for open-ended questions
    if "open_ended" in question_types and type_counts.get("open_ended", 0) > 0:
        oe_count = type_counts.get("open_ended")
        oe_prompt = f"""
- Generate {oe_count} open-ended questions.
- For each open-ended question, provide a reference answer that would be considered correct.
- Make these questions suitable for evaluating deeper understanding of machine learning concepts.
- Ensure questions are specific and focused on the given topics.
- Reference answers should be comprehensive and demonstrate deep understanding.
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
- Ensure starter code is well-documented and includes helpful comments.
- Test cases should be comprehensive and cover edge cases.
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
- Ensure all questions are meaningful and test actual understanding
- Avoid placeholder text or generic content
- Make sure all options and answers are directly relevant to the question

IMPORTANT: Use the following EXACT format for your responses:

For Multiple-Choice Questions:
Question: [Question text]
A. [Option A - must be meaningful and relevant]
B. [Option B - must be meaningful and relevant]
C. [Option C - must be meaningful and relevant]
D. [Option D - must be meaningful and relevant]
Correct Answer: [Letter of correct option - A, B, C, or D]

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

Make sure to provide exactly {num_questions} questions, formatted precisely as specified above.
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
        
        # Validate options
        if len(options) < 2:
            continue  # Skip questions with insufficient options
            
        # Remove any placeholder text from options
        options = [opt for opt in options if not any(placeholder in opt.lower() for placeholder in 
            ["option", "placeholder", "select", "choose", "...", "etc"])]
            
        # If we still don't have enough valid options, skip this question
        if len(options) < 2:
            continue
            
        # Map the letter (A, B, C...) to index (0, 1, 2...)
        correct_letter = match.group(8).strip()
        correct_index = ord(correct_letter) - ord('A')
        
        # Ensure correct_index is within range
        if correct_index >= len(options):
            correct_index = 0
            
        # Validate question text
        if any(placeholder in question_text.lower() for placeholder in 
            ["question", "placeholder", "select", "choose", "...", "etc"]):
            continue
            
        questions.append(Question(
            question=question_text,
            answers=options,
            correct_answer=correct_index
        ))
    
    # Find all open-ended questions
    for match in re.finditer(open_pattern, text, re.DOTALL):
        question_text = match.group(1).strip()
        reference_answer = match.group(2).strip()
        
        # Validate question and answer
        if any(placeholder in question_text.lower() for placeholder in 
            ["question", "placeholder", "select", "choose", "...", "etc"]):
            continue
            
        if any(placeholder in reference_answer.lower() for placeholder in 
            ["answer", "placeholder", "sample", "example", "...", "etc"]):
            continue
            
        questions.append(Question(
            question=question_text,
            reference_answer=reference_answer
        ))
    
    # Find all coding questions
    for match in re.finditer(coding_pattern, text, re.DOTALL):
        question_text = match.group(1).strip()
        starter_code = match.group(2).strip()
        test_cases = match.group(3).strip()
        
        # Validate question and code
        if any(placeholder in question_text.lower() for placeholder in 
            ["question", "placeholder", "select", "choose", "...", "etc"]):
            continue
            
        if any(placeholder in starter_code.lower() for placeholder in 
            ["code", "placeholder", "template", "example", "...", "etc"]):
            continue
            
        if any(placeholder in test_cases.lower() for placeholder in 
            ["test", "placeholder", "example", "sample", "...", "etc"]):
            continue
            
        questions.append(Question(
            question=question_text,
            starter_code=starter_code,
            test_cases=test_cases
        ))
    
    return questions


def calculate_quiz_score(questions: List[Question], user_answers: Dict[int, int], coding_test_results: Dict = None) -> Tuple[int, int, float]:
    """Calculate the score for a quiz.
    
    Args:
        questions: List of Question objects
        user_answers: Dictionary mapping question index to selected answer index
        coding_test_results: Optional dictionary of coding test results
        
    Returns:
        Tuple of (correct_count, total_questions, score_percentage)
    """
    if not questions:
        return 0, 0, 0.0
        
    correct = 0
    total = len(questions)
    answered_questions = 0
    
    for i, question in enumerate(questions):
        # Handle multiple choice questions
        if isinstance(question, dict):
            # Dictionary representation
            question_type = question.get('type', 'multiple_choice')
            
            if question_type == 'multiple_choice':
                if i in user_answers:
                    answered_questions += 1
                    correct_answer = question.get('correct_answer')
                    if correct_answer is None:
                        correct_answer = question.get('correct', 0)
                        if correct_answer is None:
                            correct_answer = question.get('correct_index', 0)
                    
                    if user_answers[i] == correct_answer:
                        correct += 1
            
            elif question_type == 'coding':
                # For coding questions, check if all tests passed
                if coding_test_results:
                    # Look for test results with both integer and string keys
                    test_result = coding_test_results.get(i, coding_test_results.get(str(i), None))
                    if test_result:
                        answered_questions += 1
                        
                        # Validate the test results match this specific question's function
                        test_cases = question.get('test_cases', '')
                        valid_test_results = []
                        
                        # Extract expected function name from test cases
                        func_names = set()
                        if test_cases:
                            for line in test_cases.split('\n'):
                                if 'assert' in line:
                                    func_match = re.search(r'assert\s+(\w+)\(', line)
                                    if func_match:
                                        func_names.add(func_match.group(1))
                        
                        # If we identified function names, filter the test results
                        if func_names:
                            for test in test_result:
                                test_str = test.get('test', '')
                                # Check if this test belongs to this question's function
                                is_valid = False
                                for func in func_names:
                                    if func in test_str:
                                        is_valid = True
                                        break
                                if is_valid:
                                    valid_test_results.append(test)
                        else:
                            # If we couldn't identify function names, use all test results
                            valid_test_results = test_result
                            
                        # A coding question is correct if all valid tests pass
                        if valid_test_results and all(test.get('result', '') == 'PASS' for test in valid_test_results):
                            correct += 1
        
        # Handle object-style questions
        elif hasattr(question, 'correct_answer'):
            # Multiple choice question object
            if i in user_answers:
                answered_questions += 1
                if user_answers[i] == question.correct_answer:
                    correct += 1
        
        elif hasattr(question, 'test_cases'):
            # Coding question object
            if coding_test_results:
                test_result = coding_test_results.get(i, coding_test_results.get(str(i), None))
                if test_result:
                    answered_questions += 1
                    
                    # Validate the test results match this specific question's function
                    test_cases = getattr(question, 'test_cases', '')
                    valid_test_results = []
                    
                    # Extract expected function name from test cases
                    func_names = set()
                    if test_cases:
                        for line in test_cases.split('\n'):
                            if 'assert' in line:
                                func_match = re.search(r'assert\s+(\w+)\(', line)
                                if func_match:
                                    func_names.add(func_match.group(1))
                    
                    # If we identified function names, filter the test results
                    if func_names:
                        for test in test_result:
                            test_str = test.get('test', '')
                            # Check if this test belongs to this question's function
                            is_valid = False
                            for func in func_names:
                                if func in test_str:
                                    is_valid = True
                                    break
                            if is_valid:
                                valid_test_results.append(test)
                    else:
                        # If we couldn't identify function names, use all test results
                        valid_test_results = test_result
                        
                    # A coding question is correct if all valid tests pass
                    if valid_test_results and all(test.get('result', '') == 'PASS' for test in valid_test_results):
                        correct += 1
    
    # If no questions were answered, score is 0
    if total == 0:
        return 0, 0, 0.0
        
    # Calculate score based on total questions, not just answered questions
    score_pct = (correct / total) * 100
    
    return correct, total, score_pct


def create_quiz_summary(questions: List[Any], user_answers: Dict[int, int]) -> str:
    """
    Create a summary of the quiz for LLM analysis.
    
    Args:
        questions: List of Question objects or question dictionaries
        user_answers: Dictionary mapping question index to selected answer index
        
    Returns:
        A formatted string summary
    """
    quiz_summary = "QUIZ QUESTIONS AND ANSWERS:\n\n"
    
    for i, q in enumerate(questions):
        user_answer = user_answers.get(i, -1)
        
        # Handle both dictionary-based questions and Question objects
        if isinstance(q, dict):
            # For dictionary-based questions
            question_text = q.get("question", "")
            options = q.get("options", [])
            correct_index = q.get("correct_index", 0)
            
            # Safety check - ensure correct_index is valid
            if not options:
                # Skip questions with no options
                continue
                
            # Make sure correct_index is within bounds
            correct_index = max(0, min(correct_index, len(options) - 1))
            
            # Get answer letters
            user_letter = chr(65 + user_answer) if 0 <= user_answer < len(options) else "None"
            correct_letter = chr(65 + correct_index)
            
            # Format the summary
            quiz_summary += f"Question {i+1}: {question_text}\n"
            for j, ans in enumerate(options):
                quiz_summary += f"{chr(65+j)}) {ans}\n"
            
            # Safety check for user's answer
            if 0 <= user_answer < len(options):
                user_ans_text = options[user_answer]
            else:
                user_ans_text = "Not answered"
                
            quiz_summary += f"User's answer: {user_letter}) {user_ans_text}\n"
            quiz_summary += f"Correct answer: {correct_letter}) {options[correct_index]}\n\n"
        else:
            # For Question objects (backward compatibility)
            if not hasattr(q, 'answers') or not q.answers:
                # Skip questions with no answers
                continue
                
            # Safety check - ensure correct_answer is valid
            correct_answer = getattr(q, 'correct_answer', 0)
            if not isinstance(correct_answer, int) or correct_answer < 0 or correct_answer >= len(q.answers):
                correct_answer = 0
                
            user_letter = chr(65 + user_answer) if 0 <= user_answer < len(q.answers) else "None"
            correct_letter = chr(65 + correct_answer)
            
            quiz_summary += f"Question {i+1}: {q.question}\n"
            for j, ans in enumerate(q.answers):
                quiz_summary += f"{chr(65+j)}) {ans}\n"
            
            # Safety check for user's answer
            if 0 <= user_answer < len(q.answers):
                user_ans_text = q.answers[user_answer]
            else:
                user_ans_text = "Not answered"
                
            quiz_summary += f"User's answer: {user_letter}) {user_ans_text}\n"
            quiz_summary += f"Correct answer: {correct_letter}) {q.answers[correct_answer]}\n\n"
    
    return quiz_summary


def generate_analysis_prompt(quiz_summary: str, correct: int, total: int, score_pct: float) -> str:
    """
    Generate a prompt for LLM to analyze quiz performance.
    
    Args:
        quiz_summary: Formatted quiz summary
        correct: Number of correct answers
        total: Total number of questions
        score_pct: Percentage score
        
    Returns:
        A formatted prompt string
    """
    return f"""Analyze the following quiz results:

Score: {correct}/{total} ({score_pct:.1f}%)

{quiz_summary}

Please provide an analysis with the following sections:
1. Overall Understanding: Assess the student's overall understanding of the topic.
2. Strengths: Identify areas where the student shows good understanding.
3. Knowledge Gaps: Identify specific areas where the student needs improvement.
4. Recommendations: Suggest specific resources or strategies for improvement.

Format your response as follows:
UNDERSTANDING: [Overall understanding assessment]
STRENGTHS: [Areas of strength]
KNOWLEDGE_GAPS: [Areas needing improvement]
RECOMMENDATIONS: [Specific recommendations]
"""


def parse_quiz_analysis(content: str) -> Dict[str, str]:
    """
    Parse the LLM analysis response into structured sections.
    
    Args:
        content: The raw analysis response from the LLM
        
    Returns:
        A dictionary with analysis sections
    """
    sections = {
        "understanding": "",
        "strengths": "",
        "knowledge_gaps": "",
        "recommendations": ""
    }
    
    current_section = None
    
    for line in content.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('UNDERSTANDING:'):
            current_section = "understanding"
            sections[current_section] = line[13:].strip()
        elif line.startswith('STRENGTHS:'):
            current_section = "strengths"
            sections[current_section] = line[10:].strip()
        elif line.startswith('KNOWLEDGE_GAPS:'):
            current_section = "knowledge_gaps"
            sections[current_section] = line[15:].strip()
        elif line.startswith('RECOMMENDATIONS:'):
            current_section = "recommendations"
            sections[current_section] = line[16:].strip()
        elif current_section:
            sections[current_section] += " " + line
    
    return sections


def generate_practice_quiz(topic: str, num_questions: int, difficulty: str, question_types: list, **kwargs) -> Dict:
    """
    Generate a practice quiz on a specific topic with specified parameters, focusing on Python programming.
    
    Args:
        topic: The topic for the practice quiz (comma-separated topics)
        num_questions: Number of questions to generate
        difficulty: Difficulty level (Easy, Medium, Hard)
        question_types: List of question types to include
        **kwargs: Additional options including:
            - type_counts: Dictionary mapping question types to their counts
            - save_progress: Boolean indicating whether to save quiz progress
            - use_llm: Whether to use LLM to generate questions (default True)
            - use_multiple_methods: Whether to use multiple generation methods (default True)
        
    Returns:
        A dictionary containing the practice quiz data
    """
    import time
    import random
    import uuid
    import hashlib
    import os
    from datetime import datetime
    
    # Clean and validate the question types list
    question_types = [qt for qt in question_types if qt and isinstance(qt, str)]
    
    if not question_types:
        question_types = ["multiple_choice"]  # Default to multiple choice
    
    # Focus on MCQ and coding questions as requested
    if "open_ended" in question_types:
        question_types.remove("open_ended")
    
    if len(question_types) == 0:
        question_types = ["multiple_choice"]
    
    # Create truly unique identifiers for this quiz
    timestamp = int(time.time() * 1000)  # Millisecond precision
    browser_id = kwargs.get('browser_id', '')  # Get browser ID if available
    # Add some entropy from system state
    system_entropy = os.urandom(8).hex()
    
    # Create a unique quiz ID
    quiz_uuid = str(uuid.uuid4())
    quiz_id = f"practice_{timestamp}_{quiz_uuid[:8]}"
    
    # Create a session ID with multiple entropy sources for true randomness
    session_components = [
        quiz_uuid,
        str(timestamp),
        str(random.randint(10000, 99999)),
        system_entropy,
        browser_id
    ]
    session_id = "_".join(session_components)
    
    # Create a hash from the session ID to use as random seed
    # This ensures a consistent but unique set of questions for this quiz
    seed_hash = hashlib.md5(session_id.encode()).hexdigest()
    seed_int = int(seed_hash, 16) % (2**32)  # Convert to integer suitable for random seed
    
    # Set a new random seed based on the hash to ensure diversity
    random.seed(seed_int)
    
    # Get current user ID (default to 1 if not available)
    student_id = kwargs.get('student_id', None)
    if not student_id:
        try:
            import streamlit as st
            student_id = st.session_state.get("user_id", 1)
        except:
            student_id = 1
    
    # Format topic for title display
    display_topic = topic
    if len(display_topic) > 40:
        display_topic = display_topic[:37] + "..."
    
    # Initialize the quiz structure with detailed metadata
    practice_quiz = {
        "id": quiz_id,
        "title": f"Python Practice: {display_topic}",
        "description": f"Python programming practice quiz on {display_topic} with {num_questions} {difficulty.lower()} difficulty questions",
        "course": "Python Programming",
        "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": "No deadline",
        "duration_minutes": 60,
        "status": "active",
        "questions": [],
        "student_id": student_id,
        "session_id": session_id,
        "creation_timestamp": timestamp,
        "difficulty": difficulty,
        "entropy_source": system_entropy[:8]
    }
    
    # Extract optional parameters
    type_counts = kwargs.get('type_counts', None)
    save_progress = kwargs.get('save_progress', True)
    use_llm = kwargs.get('use_llm', True)
    
    # If type_counts is not provided, distribute questions evenly among selected types
    if not type_counts:
        type_counts = {}
        remaining = num_questions
        base_count = remaining // len(question_types)
        remainder = remaining % len(question_types)
        
        for qt in question_types:
            extra = 1 if remainder > 0 else 0
            type_counts[qt] = base_count + extra
            remaining -= (base_count + extra)
            remainder -= extra
    
    # Generate questions using LLM - make multiple attempts if needed
    all_questions = []
    if use_llm:
        max_attempts = 3  # Try up to 3 times with the LLM
        for attempt in range(max_attempts):
            try:
                llm_questions = _generate_from_llm(topic, num_questions, difficulty, question_types, type_counts)
                if llm_questions and len(llm_questions) > 0:
                    all_questions.extend(llm_questions)
                    break  # If we got questions, exit the loop
                else:
                    print(f"LLM attempt {attempt+1} returned no questions, trying again...")
            except Exception as e:
                print(f"Error during LLM attempt {attempt+1}: {str(e)}")
    
    # If we don't have enough questions, use templates
    if len(all_questions) < num_questions:
        try:
            template_questions = _generate_from_templates(topic, num_questions - len(all_questions), difficulty, question_types, type_counts)
            if template_questions:
                all_questions.extend(template_questions)
        except Exception as e:
            print(f"Error using templates for question generation: {str(e)}")
    
    # If we still don't have enough questions, add fallback questions
    if len(all_questions) < num_questions:
        remaining = num_questions - len(all_questions)
        fallback_questions = []
        
        # Python-specific fallback questions
        for q_type, count in type_counts.items():
            if count <= 0:
                continue
                
            if q_type == "multiple_choice":
                # Extended set of Python-specific multiple choice fallback questions
                python_mc_fallbacks = [
                    {
                        "question": "Which of the following is a mutable data type in Python?",
                        "options": ["List", "Tuple", "String", "Integer"],
                        "correct_index": 0
                    },
                    {
                        "question": "What is the output of `print(2 ** 3)` in Python?",
                        "options": ["8", "6", "5", "Error"],
                        "correct_index": 0
                    },
                    {
                        "question": "Which Python keyword is used to define a function?",
                        "options": ["def", "function", "func", "define"],
                        "correct_index": 0
                    },
                    {
                        "question": "What does the `len()` function return when called on a dictionary?",
                        "options": ["Number of key-value pairs", "Number of keys", "Number of values", "Memory size of dictionary"],
                        "correct_index": 0
                    },
                    {
                        "question": "How do you create an empty list in Python?",
                        "options": ["[]", "list()", "Both A and B", "{}"],
                        "correct_index": 2
                    },
                    {
                        "question": "What is the correct way to import a module named 'math' in Python?",
                        "options": ["import math", "include math", "using math", "#include <math>"],
                        "correct_index": 0
                    },
                    {
                        "question": "Which of the following is the correct way to create a set in Python?",
                        "options": ["{1, 2, 3}", "[1, 2, 3]", "(1, 2, 3)", "set[1, 2, 3]"],
                        "correct_index": 0
                    },
                    {
                        "question": "What will `print(3 == 3.0)` output in Python?",
                        "options": ["True", "False", "Error", "None"],
                        "correct_index": 0
                    },
                    {
                        "question": "What is the output of `print('Hello'[1])`?",
                        "options": ["e", "H", "He", "Hello"],
                        "correct_index": 0
                    },
                    {
                        "question": "Which method is used to add an element to a set in Python?",
                        "options": ["add()", "append()", "insert()", "extend()"],
                        "correct_index": 0
                    },
                    {
                        "question": "What is the result of `10 // 3` in Python?",
                        "options": ["3", "3.33", "3.0", "4"],
                        "correct_index": 0
                    },
                    {
                        "question": "Which of the following is a valid way to comment a single line in Python?",
                        "options": ["# This is a comment", "// This is a comment", "/* This is a comment */", "<!-- This is a comment -->"],
                        "correct_index": 0
                    },
                    {
                        "question": "What is the output of `print(bool(''))`?",
                        "options": ["False", "True", "None", "Empty"],
                        "correct_index": 0
                    },
                    {
                        "question": "Which Python function is used to find the maximum value in a list?",
                        "options": ["max()", "maximum()", "largest()", "biggest()"],
                        "correct_index": 0
                    },
                    {
                        "question": "What is the correct syntax for a Python f-string?",
                        "options": [
                            "f\"Value is {x}\"", 
                            "\"Value is {x}\"f", 
                            "\"Value is %s\" % x", 
                            "\"Value is \" + x"
                        ],
                        "correct_index": 0
                    },
                    {
                        "question": "What does the `enumerate()` function do in Python?",
                        "options": [
                            "Returns both index and value in a loop", 
                            "Counts the number of elements", 
                            "Creates an enumerated data type", 
                            "Sorts a collection"
                        ],
                        "correct_index": 0
                    },
                    {
                        "question": "What does the `pass` statement do in Python?",
                        "options": [
                            "Acts as a placeholder (does nothing)", 
                            "Passes control to the next loop iteration", 
                            "Passes a value to a function", 
                            "Terminates the program"
                        ],
                        "correct_index": 0
                    },
                    {
                        "question": "What is the output of `print(type(lambda x: x))`?",
                        "options": [
                            "<class 'function'>", 
                            "<class 'lambda'>", 
                            "<class 'method'>", 
                            "SyntaxError"
                        ],
                        "correct_index": 0
                    },
                    {
                        "question": "How do you check if a key exists in a dictionary?",
                        "options": [
                            "Using the 'in' operator", 
                            "Using haskey()", 
                            "Using exists()", 
                            "Using contains()"
                        ],
                        "correct_index": 0
                    },
                    {
                        "question": "What happens when you execute `list('Python')`?",
                        "options": [
                            "Returns ['P', 'y', 't', 'h', 'o', 'n']", 
                            "Returns ['Python']", 
                            "Error", 
                            "Returns 'Python'"
                        ],
                        "correct_index": 0
                    }
                ]
                
                # Generate a list of indices to use for question selection
                # This ensures we don't repeat questions when we need many
                indices = list(range(len(python_mc_fallbacks)))
                random.shuffle(indices)
                
                for i in range(min(count, remaining, len(python_mc_fallbacks))):
                    question_id = f"fallback_mc_{timestamp}_{random.randint(1000, 9999)}"
                    idx = indices[i % len(indices)]  # Use modulo to avoid index errors
                    fallback_q = python_mc_fallbacks[idx].copy()
                    fallback_q["id"] = question_id
                    fallback_q["type"] = "multiple_choice"
                    
                    fallback_questions.append(fallback_q)
                    remaining -= 1
                
                # If we still need more questions, create topic-specific ones
                if remaining > 0 and count > len(python_mc_fallbacks):
                    python_features = [
                        "List comprehensions", "Dictionary comprehensions", 
                        "Exception handling", "Object-oriented programming",
                        "Context managers", "Generators", "Decorators",
                        "Lambda functions", "Type annotations", "f-strings",
                        "Async/await", "Built-in functions", "Standard library modules"
                    ]
                    
                    for i in range(min(count - len(python_mc_fallbacks), remaining)):
                        question_id = f"fallback_mc_{timestamp}_{random.randint(1000, 9999)}"
                        
                        # Randomize the features for each question
                        random.shuffle(python_features)
                        options = python_features[:4]  # Take first 4 after shuffling
                        correct_index = random.randint(0, 3)
                        
                        fallback_question = {
                            "type": "multiple_choice",
                            "question": f"Which Python feature would be most useful when working with {topic}?",
                            "options": options,
                            "correct_index": correct_index,
                            "id": question_id
                        }
                        
                        fallback_questions.append(fallback_question)
                        remaining -= 1
            
            elif q_type == "coding":
                # Extended set of Python-specific coding fallback questions
                python_code_fallbacks = [
                    {
                        "question": "Write a Python function that reverses a string without using the built-in reverse function.",
                        "starter_code": "def reverse_string(s):\n    \"\"\"\n    Reverse the input string.\n    \n    Args:\n        s: Input string to reverse\n        \n    Returns:\n        The reversed string\n        \n    Example:\n        >>> reverse_string('hello')\n        'olleh'\n    \"\"\"\n    # Your implementation here\n    pass",
                        "test_cases": "assert reverse_string('hello') == 'olleh'\nassert reverse_string('') == ''\nassert reverse_string('a') == 'a'"
                    },
                    {
                        "question": "Implement a function to check if a string is a palindrome in Python.",
                        "starter_code": "def is_palindrome(s):\n    \"\"\"\n    Check if the input string is a palindrome.\n    A palindrome reads the same backward as forward.\n    \n    Args:\n        s: Input string to check\n        \n    Returns:\n        True if the string is a palindrome, False otherwise\n        \n    Example:\n        >>> is_palindrome('racecar')\n        True\n    \"\"\"\n    # Your implementation here\n    pass",
                        "test_cases": "assert is_palindrome('racecar') == True\nassert is_palindrome('hello') == False\nassert is_palindrome('') == True\nassert is_palindrome('A man a plan a canal Panama') == False  # With spaces\nassert is_palindrome('amanaplanacanalpanama') == True  # Without spaces"
                    },
                    {
                        "question": "Write a Python function to find the most frequent element in a list.",
                        "starter_code": "def most_frequent(lst):\n    \"\"\"\n    Find the most frequent element in a list.\n    If there are multiple elements with the same frequency, return any one of them.\n    \n    Args:\n        lst: Input list\n        \n    Returns:\n        The most frequent element\n        \n    Example:\n        >>> most_frequent([1, 2, 3, 2, 2, 4])\n        2\n    \"\"\"\n    # Your implementation here\n    pass",
                        "test_cases": "assert most_frequent([1, 2, 3, 2, 2, 4]) == 2\nassert most_frequent(['a', 'b', 'a']) == 'a'\nassert most_frequent([1]) == 1\nassert most_frequent([1, 2, 3, 1, 2, 3]) in [1, 2, 3]  # Multiple elements with same frequency"
                    },
                    {
                        "question": "Implement a Python function to flatten a nested list.",
                        "starter_code": "def flatten_list(nested_list):\n    \"\"\"\n    Flatten a nested list into a single-level list.\n    \n    Args:\n        nested_list: A list that can contain lists as elements\n        \n    Returns:\n        A flattened list containing all elements\n        \n    Example:\n        >>> flatten_list([1, [2, 3], [4, [5, 6]]])\n        [1, 2, 3, 4, 5, 6]\n    \"\"\"\n    # Your implementation here\n    pass",
                        "test_cases": "assert flatten_list([1, [2, 3], [4, [5, 6]]]) == [1, 2, 3, 4, 5, 6]\nassert flatten_list([]) == []\nassert flatten_list([1, 2, 3]) == [1, 2, 3]\nassert flatten_list([[1, 2], [3, 4]]) == [1, 2, 3, 4]"
                    },
                    {
                        "question": "Write a Python function to find all pairs in a list that sum to a given target.",
                        "starter_code": "def find_pairs(numbers, target):\n    \"\"\"\n    Find all pairs of numbers in the list that add up to the target value.\n    Each pair should be a tuple of two numbers.\n    \n    Args:\n        numbers: List of integers\n        target: Target sum\n        \n    Returns:\n        List of tuples, each containing a pair of numbers\n        \n    Example:\n        >>> find_pairs([1, 2, 3, 4, 5], 6)\n        [(1, 5), (2, 4)]\n    \"\"\"\n    # Your implementation here\n    pass",
                        "test_cases": "assert sorted(find_pairs([1, 2, 3, 4, 5], 6)) == [(1, 5), (2, 4)]\nassert find_pairs([1, 2, 3], 10) == []\nassert sorted(find_pairs([3, 3, 4, 6], 9)) == [(3, 6), (3, 6)]"
                    },
                    {
                        "question": "Implement a function to count the frequency of words in a string.",
                        "starter_code": "def word_frequency(text):\n    \"\"\"\n    Count the frequency of each word in a text string.\n    Ignore case and punctuation.\n    \n    Args:\n        text: Input string\n        \n    Returns:\n        Dictionary mapping each word to its frequency\n        \n    Example:\n        >>> word_frequency('The quick brown fox jumps over the lazy dog.')\n        {'the': 2, 'quick': 1, 'brown': 1, 'fox': 1, 'jumps': 1, 'over': 1, 'lazy': 1, 'dog': 1}\n    \"\"\"\n    # Your implementation here\n    pass",
                        "test_cases": "assert word_frequency('The quick brown fox jumps over the lazy dog.') == {'the': 2, 'quick': 1, 'brown': 1, 'fox': 1, 'jumps': 1, 'over': 1, 'lazy': 1, 'dog': 1}\nassert word_frequency('') == {}\nassert word_frequency('a a a a b b c') == {'a': 4, 'b': 2, 'c': 1}"
                    },
                    {
                        "question": "Write a Python function to find the longest common substring between two strings.",
                        "starter_code": "def longest_common_substring(str1, str2):\n    \"\"\"\n    Find the longest common substring between two strings.\n    \n    Args:\n        str1: First string\n        str2: Second string\n        \n    Returns:\n        The longest common substring\n        \n    Example:\n        >>> longest_common_substring('abcdef', 'bcdefg')\n        'bcdef'\n    \"\"\"\n    # Your implementation here\n    pass",
                        "test_cases": "assert longest_common_substring('abcdef', 'bcdefg') == 'bcdef'\nassert longest_common_substring('python', 'java') == ''\nassert longest_common_substring('', 'abc') == ''\nassert longest_common_substring('programming', 'gaming') == 'gaming'"
                    },
                    {
                        "question": "Implement a simple stack class in Python using a list.",
                        "starter_code": "class Stack:\n    \"\"\"\n    A simple stack implementation using a Python list.\n    \n    Methods:\n        push(item): Add an item to the top of the stack\n        pop(): Remove and return the top item\n        peek(): Return the top item without removing it\n        is_empty(): Return True if the stack is empty\n        size(): Return the number of items in the stack\n    \"\"\"\n    \n    def __init__(self):\n        # Initialize your stack here\n        pass\n    \n    def push(self, item):\n        # Add item to the top of the stack\n        pass\n    \n    def pop(self):\n        # Remove and return the top item\n        pass\n    \n    def peek(self):\n        # Return the top item without removing it\n        pass\n    \n    def is_empty(self):\n        # Return True if the stack is empty\n        pass\n    \n    def size(self):\n        # Return the number of items in the stack\n        pass",
                        "test_cases": "stack = Stack()\nassert stack.is_empty() == True\nstack.push(1)\nstack.push(2)\nstack.push(3)\nassert stack.size() == 3\nassert stack.peek() == 3\nassert stack.pop() == 3\nassert stack.size() == 2\nassert stack.is_empty() == False"
                    }
                ]
                
                # Generate a list of indices to use for question selection
                # This ensures we don't repeat questions when we need many
                indices = list(range(len(python_code_fallbacks)))
                random.shuffle(indices)
                
                for i in range(min(count, remaining, len(python_code_fallbacks))):
                    question_id = f"fallback_coding_{timestamp}_{random.randint(1000, 9999)}"
                    idx = indices[i % len(indices)]  # Use modulo to avoid index errors
                    fallback_q = python_code_fallbacks[idx].copy()
                    fallback_q["id"] = question_id
                    fallback_q["type"] = "coding"
                    
                    fallback_questions.append(fallback_q)
                    remaining -= 1
                
                # If we still need more questions, create topic-specific ones
                if remaining > 0 and count > len(python_code_fallbacks):
                    # Create more specific coding questions instead of generic ones
                    specific_questions = _create_specific_coding_questions(topic, min(count - len(python_code_fallbacks), remaining), difficulty)
                    for q in specific_questions:
                        question_id = f"fallback_coding_{timestamp}_{random.randint(1000, 9999)}"
                        q["id"] = question_id
                        fallback_questions.append(q)
                        remaining -= 1
                        
                    # If we still need more, fall back to the topic-specific template but with better prompts
                    if remaining > 0:
                        for i in range(min(count - len(python_code_fallbacks) - len(specific_questions), remaining)):
                            question_id = f"fallback_coding_{timestamp}_{random.randint(1000, 9999)}"
                            
                            # Make the topic more specific if possible
                            specific_topic = topic
                            if topic.lower() in ["python", "programming", "coding"]:
                                specific_topic = random.choice([
                                    "string manipulation", "file processing", "data structures", 
                                    "algorithms", "object-oriented programming", "functional programming"
                                ])
                            
                            # Create a more specific coding question for the topic
                            topic_safe = specific_topic.lower().replace(' ', '_').replace(',', '')
                            specific_verb = random.choice([
                                "Implement", "Create", "Develop", "Write", "Design", "Build"
                            ])
                            
                            specific_task = random.choice([
                                f"a function that finds all anagrams in a list of words related to {specific_topic}",
                                f"a utility that validates and processes {specific_topic} data",
                                f"a class that represents a {specific_topic} manager with add, remove, and search capabilities",
                                f"a function that efficiently filters and transforms {specific_topic} data",
                                f"a parser for {specific_topic} configuration files",
                                f"a converter between different {specific_topic} formats"
                            ])
                            
                            function_name = f"{topic_safe}_{'processor' if 'process' in specific_task else 'handler'}"
                            
                            fallback_question = {
                                "type": "coding",
                                "question": f"{specific_verb} {specific_task}.",
                                "starter_code": f"def {function_name}(data):\n    \"\"\"\n    {specific_task.capitalize()}.\n    \n    Args:\n        data: Input data to process\n        \n    Returns:\n        Processed result based on the task requirements\n    \"\"\"\n    # Your implementation here\n    pass",
                                "test_cases": f"# Test with example data\ndef test_{function_name}():\n    # Basic functionality test\n    sample_data = [\"example\", \"data\", \"for\", \"testing\"]\n    result = {function_name}(sample_data)\n    assert result is not None\n    \n    # Edge case: empty input\n    assert {function_name}([]) is not None\n    \n    # Additional test case specific to the function\n    # Add more specific tests here\n    \ntest_{function_name}()",
                                "id": question_id
                            }
                            
                            fallback_questions.append(fallback_question)
                            remaining -= 1
        
        all_questions.extend(fallback_questions)
    
    # Ensure we have exactly the requested number of questions
    all_questions = all_questions[:num_questions]
    
    # Shuffle the questions for a better mix
    random.shuffle(all_questions)
    
    # Add questions to the practice quiz
    practice_quiz["questions"] = all_questions
    
    return practice_quiz

def _generate_from_llm(topic: str, num_questions: int, difficulty: str, question_types: list, type_counts: dict = None) -> list:
    """
    Generate quiz questions using the LLM, focused on Python programming topics.
    """
    import time
    import random
    import uuid
    
    # Calculate type counts if not provided
    if not type_counts:
        type_counts = {}
        remaining = num_questions
        base_count = remaining // len(question_types)
        remainder = remaining % len(question_types)
        
        for qt in question_types:
            extra = 1 if remainder > 0 else 0
            type_counts[qt] = base_count + extra
            remaining -= (base_count + extra)
            remainder -= extra
    
    # Parse topics into a list
    topics_list = [t.strip() for t in topic.split(',') if t.strip()]
    if not topics_list:
        topics_list = ["Python programming"]
    
    # Create a unique session ID
    session_id = str(uuid.uuid4())
    timestamp = int(time.time() * 1000)
    
    try:
        from services.llm_service import generate_content
    except ImportError:
        return []
    
    all_questions = []
    
    # Generate each type of question separately
    for q_type, count in type_counts.items():
        if count <= 0:
            continue
        
        # Request more questions than needed to account for duplicates and filtering
        request_count = min(count * 3, 50)  # Request 3x but cap at 50 to avoid prompt size issues
            
        # Build the prompt based on question type
        if q_type == "multiple_choice":
            prompt = f"""
You are an expert Python programming instructor creating a professional quiz for computer science students.

Generate EXACTLY {request_count} high-quality UNIQUE multiple-choice questions about Python programming with a focus on {', '.join(topics_list)}.
Difficulty level: {difficulty}

CRITICAL REQUIREMENTS:
1. Every question MUST be DIFFERENT from the others - DO NOT repeat similar questions
2. Questions MUST focus EXCLUSIVELY on Python programming (version 3.6+)
3. Each question MUST have exactly 4 options (A, B, C, D)
4. Each question MUST test a specific Python concept or skill
5. Never generate questions about machine learning, AI, or data science
6. Focus strictly on Python language features, syntax, and standard library
7. ENSURE variety - cover many different Python topics and concepts

TOPICS TO INCLUDE (cover a wide variety):
- Python syntax and core language features (lists, dictionaries, tuples, sets)
- String manipulation and formatting (f-strings, string methods)
- File handling in Python (read/write operations)
- Python functions, decorators, and functional programming concepts
- Object-oriented programming in Python (classes, inheritance, encapsulation)
- Modules and packages (importing, creating packages)
- Exception handling (try/except/finally)
- Context managers (with statements)
- Iterators and generators (yield, next())
- List/dict comprehensions and generator expressions
- Python standard library (collections, itertools, datetime, etc.)
- Python built-in functions (map, filter, zip, etc.)
- Variable scope and namespaces (local, global, nonlocal)
- Python memory management and optimization
- Python concurrency (threading, multiprocessing, async/await)

QUALITY GUIDELINES:
1. Each question must test understanding, not just recall
2. Incorrect options must be plausible but clearly wrong
3. Code examples must be syntactically correct Python 3
4. Questions should test practical knowledge useful for Python developers
5. Don't use placeholder content or generic options
6. Each option must be meaningful and relevant to the question
7. Options should be concise (1-2 lines max)
8. Make questions challenging but fair for {difficulty} level
9. DO NOT repeat similar questions with minor variations

FORMAT:
Question: [Clear, specific question about Python]
A. [First option]
B. [Second option]
C. [Third option]
D. [Fourth option]
Correct Answer: [Letter of correct option - A, B, C, or D]

EXAMPLE 1:
Question: What will be the output of the following Python code?
```python
x = {"a": 1, "b": 2}
y = x.copy()
y["a"] = 10
print(x["a"])
```
A. 1
B. 10
C. KeyError
D. None
Correct Answer: A

EXAMPLE 2:
Question: Which of the following is NOT a valid way to create a list in Python?
A. my_list = list((1, 2, 3))
B. my_list = [x for x in range(3)]
C. my_list = list{1, 2, 3}
D. my_list = [1, 2, 3]
Correct Answer: C

EXAMPLE 3:
Question: What is the time complexity of accessing an element in a Python dictionary by key?
A. O(1)
B. O(n)
C. O(log n)
D. O(n log n)
Correct Answer: A

IMPORTANT: All {request_count} questions MUST be completely different from each other. Ensure maximum variety in topics and concepts.
"""
            
        elif q_type == "coding":
            prompt = f"""
You are an expert Python programming instructor creating coding challenges for a university-level Python course.

Generate EXACTLY {request_count} high-quality UNIQUE Python coding problems with a focus on {', '.join(topics_list)}.
Difficulty level: {difficulty}

CRITICAL REQUIREMENTS:
1. Every problem MUST be DIFFERENT from the others - DO NOT repeat similar problems
2. Problems MUST focus EXCLUSIVELY on Python programming (version 3.6+)
3. Each problem MUST require implementation of a specific Python function or class
4. Never generate problems about machine learning, AI, or data science algorithms
5. Each problem MUST include meaningful starter code and comprehensive test cases
6. Focus strictly on Python language features and standard library
7. ENSURE variety - cover many different Python topics and concepts
8. NEVER create generic problems like "process data" or "implement a utility function"
9. EVERY problem must have a SPECIFIC, CONCRETE task with clear requirements

TOPICS TO INCLUDE (cover a wide variety):
- String and text processing (string manipulation, regex)
- Data structures implementation (stacks, queues, trees, linked lists)
- Algorithmic problems (sorting, searching, dynamic programming)
- File I/O and data parsing (JSON, CSV, text processing)
- Function and class implementation (inheritance, polymorphism)
- Recursion and iteration challenges
- Working with Python collections (lists, dicts, sets, etc.)
- Using Python's standard library effectively
- Efficiency and optimization in Python
- Iterators, generators, and custom context managers
- Custom decorators and higher-order functions
- Error handling and validation scenarios

QUALITY GUIDELINES:
1. Provide clear, detailed problem descriptions with SPECIFIC requirements
2. Include well-structured starter code with proper Python docstrings
3. Include comprehensive test cases that cover edge cases
4. Problems should be challenging but solvable
5. Problems should teach useful Python concepts and patterns
6. Test cases must be syntactically correct Python 3 code
7. Make sure the function signature is clear and properly typed
8. Starter code should include descriptive comments
9. Problem should be appropriate for {difficulty} level
10. DO NOT repeat similar problems with minor variations
11. AVOID GENERIC PROBLEMS - each must have a specific, concrete task
12. Function names must clearly indicate what the function does (not generic names like "process_data")

FORMAT:
Question: [Clear problem description with specific requirements]
Starter Code:
```python
# Complete, runnable starter code with docstrings and type hints
```
Test Cases:
```python
# Comprehensive test cases that verify the solution
```

EXAMPLES OF SPECIFIC PROBLEMS (generate problems with this level of specificity):

Example 1:
Question: Implement a function that finds all prime numbers up to a given limit using the Sieve of Eratosthenes algorithm.
Starter Code:
```python
def sieve_of_eratosthenes(limit: int) -> list[int]:
    \"\"\"
    Find all prime numbers up to a given limit using the Sieve of Eratosthenes algorithm.
    
    Args:
        limit: The upper limit (inclusive) to find prime numbers up to
        
    Returns:
        A list of all prime numbers up to the limit
        
    Example:
        >>> sieve_of_eratosthenes(10)
        [2, 3, 5, 7]
    \"\"\"
    # Your implementation here
    pass
```

Example 2:
Question: Create a custom context manager called 'Timer' that measures the execution time of a code block and prints it when the block exits.
Starter Code:
```python
import time
from typing import Any

class Timer:
    \"\"\"
    A context manager that measures and prints the execution time of a code block.
    
    Example:
        >>> with Timer() as timer:
        ...     # Some code to measure
        ...     time.sleep(1)
        ... 
        Execution time: 1.001 seconds
    \"\"\"
    def __init__(self, precision: int = 3):
        \"\"\"
        Initialize the Timer.
        
        Args:
            precision: Number of decimal places to display in the time
        \"\"\"
        self.precision = precision
        
    def __enter__(self) -> 'Timer':
        # Your implementation here
        pass
        
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        # Your implementation here
        pass
```

IMPORTANT: All {request_count} problems MUST be completely different from each other. Ensure maximum variety in topics and concepts.
"""
        
        elif q_type == "open_ended":
            # Skip open-ended questions as requested to focus on MCQ and coding
            continue
        
        # Try to generate questions multiple times to get a good set
        max_attempts = 3
        questions_for_type = []
        
        for attempt in range(max_attempts):
            try:
                # Generate questions using the prompt
                response = generate_content(prompt)
                if not response:
                    continue
                
                # Process the response
                items = _generate_question_batch_items(response)
                
                if q_type == "multiple_choice":
                    for item in items:
                        question, options, correct_index = _parse_mc_question(item)
                        if question and options and len(options) >= 2:
                            questions_for_type.append({
                                "type": "multiple_choice",
                                "question": question,
                                "options": options,
                                "correct_index": correct_index,
                                "id": f"mc_{timestamp}_{random.randint(1000, 9999)}"
                            })
                
                elif q_type == "coding":
                    for item in items:
                        question, starter_code, test_cases = _parse_coding_question(item)
                        if question and starter_code and test_cases:
                            # Create question dictionary
                            coding_question = {
                                "type": "coding",
                                "question": question,
                                "starter_code": starter_code,
                                "test_cases": test_cases,
                                "id": f"code_{timestamp}_{random.randint(1000, 9999)}"
                            }
                            
                            # Filter out generic questions
                            if not _is_generic_coding_question(coding_question):
                                questions_for_type.append(coding_question)
                
                # If we got enough questions, we can stop trying
                if len(questions_for_type) >= count:
                    break
                    
            except Exception as e:
                print(f"Error during LLM attempt {attempt+1} for {q_type}: {str(e)}")
        
        # Filter for uniqueness based on question text to avoid duplicates
        unique_questions = {}
        for q in questions_for_type:
            question_text = q["question"]
            # Only add if we haven't seen this question text before
            if question_text not in unique_questions:
                unique_questions[question_text] = q
        
        # Take up to the requested count
        all_questions.extend(list(unique_questions.values())[:count])
    
    # Ensure we have exactly the requested number of questions
    all_questions = all_questions[:num_questions]
    
    # Shuffle the questions for a better mix
    random.shuffle(all_questions)
    
    return all_questions

def _generate_from_templates(topic: str, num_questions: int, difficulty: str, question_types: list, type_counts: dict = None) -> list:
    """
    Generate quiz questions from templates.
    
    Args:
        topic: The topic to generate questions about
        num_questions: The total number of questions to generate
        difficulty: The difficulty level (Easy, Medium, Hard)
        question_types: List of question types to include
        type_counts: Dictionary mapping question types to their counts
        
    Returns:
        A list of generated questions in dictionary format
    """
    import time
    import random
    import uuid
    
    # Calculate type counts if not provided
    if not type_counts:
        type_counts = {}
        remaining = num_questions
        
        # Distribute questions evenly across selected question types
        base_count = remaining // len(question_types) if question_types else 0
        remainder = remaining % len(question_types) if question_types else 0
        
        for qt in question_types:
            # Add an extra question for the first few types if there's a remainder
            extra = 1 if remainder > 0 else 0
            type_counts[qt] = base_count + extra
            remaining -= (base_count + extra)
            remainder -= extra
    
    # Parse topics into a list
    topics_list = [t.strip() for t in topic.split(',') if t.strip()]
    
    # If no topics, use a default one
    if not topics_list:
        topics_list = ["machine learning"]
    
    timestamp = int(time.time() * 1000)  # Millisecond precision
    
    # Template questions for different topics and types
    template_questions = []
    
    # Multiple choice templates
    mc_templates = [
        {
            "template": "Which of the following best describes {concept} in {topic}?",
            "options": [
                "{correct_definition}",
                "{incorrect_definition_1}",
                "{incorrect_definition_2}",
                "{incorrect_definition_3}"
            ],
            "concepts": {
                "machine learning": [
                    {"concept": "supervised learning", 
                     "correct": "Learning from labeled data to make predictions", 
                     "incorrect": ["Discovering patterns in unlabeled data", "Learning through trial and error", "Making decisions without human input"]},
                    {"concept": "clustering", 
                     "correct": "Grouping similar data points without prior labels", 
                     "incorrect": ["Predicting numeric values", "Classifying data into predefined categories", "Finding the best features for a model"]},
                    {"concept": "neural networks", 
                     "correct": "Models inspired by the human brain with layers of neurons", 
                     "incorrect": ["Tree-based models that partition the feature space", "Algorithms that use distance metrics", "Statistical techniques for dimension reduction"]}
                ],
                "data science": [
                    {"concept": "feature engineering", 
                     "correct": "Creating new variables from existing data", 
                     "incorrect": ["Removing irrelevant variables", "Automating model selection", "Converting categorical variables to numeric"]},
                    {"concept": "data preprocessing", 
                     "correct": "Cleaning and transforming raw data for analysis", 
                     "incorrect": ["Collecting data from various sources", "Interpreting model outputs", "Publishing analytical findings"]},
                    {"concept": "model evaluation", 
                     "correct": "Assessing how well a model performs on data", 
                     "incorrect": ["Optimizing model parameters", "Creating data visualizations", "Implementing production systems"]}
                ],
                "programming": [
                    {"concept": "object-oriented programming", 
                     "correct": "A paradigm based on objects containing data and methods", 
                     "incorrect": ["A paradigm based on function composition", "A style that avoids side effects", "A technique for optimizing code"]},
                    {"concept": "recursion", 
                     "correct": "A technique where a function calls itself", 
                     "incorrect": ["A loop that iterates a fixed number of times", "A method to optimize memory usage", "A way to handle exceptions"]},
                    {"concept": "data structures", 
                     "correct": "Specialized formats for organizing and storing data", 
                     "incorrect": ["Tools for cleaning input data", "Frameworks for building user interfaces", "Methods for securing applications"]}
                ],
                # Add a default category for any topic
                "default": [
                    {"concept": "fundamental principles", 
                     "correct": "Core ideas that form the foundation of the field", 
                     "incorrect": ["Optional guidelines rarely used in practice", "Historical approaches no longer relevant", "Hypothetical concepts not yet implemented"]},
                    {"concept": "best practices", 
                     "correct": "Recommended approaches based on industry experience", 
                     "incorrect": ["Theoretical concepts with no practical use", "Outdated methods from early development", "Experimental techniques not widely adopted"]},
                    {"concept": "key terminology", 
                     "correct": "Standard vocabulary used by professionals in the field", 
                     "incorrect": ["Slang terms used informally", "Technical jargon from other fields", "Deprecated terms no longer in use"]}
                ]
            }
        },
        {
            "template": "What is the main advantage of using {technique} for {task}?",
            "options": [
                "{correct_advantage}",
                "{incorrect_advantage_1}",
                "{incorrect_advantage_2}",
                "{incorrect_advantage_3}"
            ],
            "techniques": {
                "machine learning": [
                    {"technique": "random forests", "task": "classification",
                     "correct": "They are resistant to overfitting",
                     "incorrect": ["They train faster than any other algorithm", "They work with very small datasets", "They require no parameter tuning"]},
                    {"technique": "deep learning", "task": "image recognition",
                     "correct": "It can automatically learn hierarchical features",
                     "incorrect": ["It requires less data than other methods", "It always provides explainable results", "It uses less computational resources"]},
                    {"technique": "regularization", "task": "regression models",
                     "correct": "It helps prevent overfitting by penalizing complexity",
                     "incorrect": ["It speeds up the training process", "It allows for perfect fitting of training data", "It eliminates the need for feature selection"]}
                ],
                "data science": [
                    {"technique": "cross-validation", "task": "model evaluation",
                     "correct": "It provides a more reliable estimate of model performance",
                     "incorrect": ["It speeds up model training", "It automatically handles missing values", "It eliminates the need for a test set"]},
                    {"technique": "dimensionality reduction", "task": "data preprocessing",
                     "correct": "It helps mitigate the curse of dimensionality",
                     "incorrect": ["It always improves model accuracy", "It makes models more interpretable", "It eliminates the need for normalization"]},
                    {"technique": "ensemble methods", "task": "predictive modeling",
                     "correct": "They often perform better than any single model",
                     "incorrect": ["They require less computational resources", "They are easier to interpret", "They eliminate the need for feature selection"]}
                ],
                "programming": [
                    {"technique": "version control", "task": "software development",
                     "correct": "It allows tracking changes and collaborating effectively",
                     "incorrect": ["It automatically optimizes code", "It prevents all bugs", "It eliminates the need for documentation"]},
                    {"technique": "unit testing", "task": "code quality assurance",
                     "correct": "It helps catch bugs early in the development process",
                     "incorrect": ["It makes the code run faster", "It generates documentation automatically", "It optimizes memory usage"]},
                    {"technique": "object-oriented design", "task": "large-scale applications",
                     "correct": "It improves code organization and reusability",
                     "incorrect": ["It always leads to faster execution", "It eliminates the need for debugging", "It automatically handles memory management"]}
                ],
                # Add a default category
                "default": [
                    {"technique": "modern approaches", "task": "solving complex problems",
                     "correct": "They can handle more diverse and challenging scenarios",
                     "incorrect": ["They always run faster than traditional methods", "They require no specialized knowledge", "They automatically adapt to any situation"]},
                    {"technique": "systematic methodology", "task": "project planning",
                     "correct": "It provides a structured framework for organizing work",
                     "incorrect": ["It eliminates the need for creativity", "It guarantees successful outcomes", "It requires no adjustments once implemented"]},
                    {"technique": "specialized tools", "task": "professional work",
                     "correct": "They are designed for specific challenges in the field",
                     "incorrect": ["They are universally applicable to any problem", "They require no training to use effectively", "They make human expertise unnecessary"]}
                ]
            }
        }
    ]
    
    # Open-ended templates with more generic questions
    open_ended_templates = [
        {
            "template": "Explain the concept of {concept} in {topic} and discuss its practical applications.",
            "concepts": {
                "machine learning": ["neural networks", "supervised learning", "feature selection", "transfer learning"],
                "data science": ["data preprocessing", "exploratory data analysis", "feature engineering", "model evaluation"],
                "programming": ["recursion", "object-oriented design", "functional programming", "concurrent programming"],
                # Add default concepts for any topic
                "default": ["fundamental principles", "key methodologies", "best practices", "recent innovations"]
            }
        },
        {
            "template": "Compare and contrast {technique1} and {technique2} in {topic}, highlighting their strengths and weaknesses.",
            "technique_pairs": {
                "machine learning": [
                    {"t1": "decision trees", "t2": "neural networks"},
                    {"t1": "supervised learning", "t2": "unsupervised learning"},
                    {"t1": "batch learning", "t2": "online learning"}
                ],
                "data science": [
                    {"t1": "linear regression", "t2": "logistic regression"},
                    {"t1": "principal component analysis", "t2": "factor analysis"},
                    {"t1": "parametric models", "t2": "non-parametric models"}
                ],
                "programming": [
                    {"t1": "object-oriented programming", "t2": "functional programming"},
                    {"t1": "imperative programming", "t2": "declarative programming"},
                    {"t1": "static typing", "t2": "dynamic typing"}
                ],
                # Add default pairs for any topic
                "default": [
                    {"t1": "traditional approaches", "t2": "modern techniques"},
                    {"t1": "theoretical frameworks", "t2": "practical implementations"},
                    {"t1": "specialized methods", "t2": "general-purpose solutions"}
                ]
            }
        }
    ]
    
    # Coding task templates with more robust options
    coding_templates = [
        {
            "template": "Implement a function to {task} for {application}.",
            "starter_code": "def {function_name}({parameters}):\n    # Your code here\n    pass",
            "test_cases": "# Test cases\nassert {function_name}({test_input}) == {expected_output}",
            "tasks": {
                "machine learning": [
                    {"task": "calculate precision and recall", "application": "a binary classifier",
                     "function": "calculate_metrics", "params": "y_true, y_pred", 
                     "test": "[1, 0, 1, 1, 0], [1, 1, 1, 0, 0]", "output": "{'precision': 0.67, 'recall': 0.67}"},
                    {"task": "implement k-means clustering", "application": "data segmentation",
                     "function": "kmeans_cluster", "params": "data, k, max_iterations=100", 
                     "test": "np.array([[1,2], [5,6], [9,10], [2,1]]), 2", "output": "np.array([0, 1, 1, 0])"},
                    {"task": "implement a simple neural network forward pass", "application": "binary classification",
                     "function": "forward_pass", "params": "inputs, weights, bias", 
                     "test": "np.array([0.5, 0.3]), np.array([[0.2, 0.8], [0.5, 0.2]]), np.array([0.1, -0.1])", "output": "np.array([0.24, 0.28])"}
                ],
                "data science": [
                    {"task": "preprocess text data", "application": "natural language processing",
                     "function": "preprocess_text", "params": "text", 
                     "test": "'Hello, World! This is an Example.'", "output": "['hello', 'world', 'example']"},
                    {"task": "calculate correlation matrix", "application": "feature selection",
                     "function": "correlation_matrix", "params": "dataframe", 
                     "test": "pd.DataFrame({'A': [1, 2, 3], 'B': [2, 4, 6]})", "output": "pd.DataFrame([[1.0, 1.0], [1.0, 1.0]], index=['A', 'B'], columns=['A', 'B'])"},
                    {"task": "detect outliers", "application": "data cleaning",
                     "function": "detect_outliers", "params": "data, threshold=1.5", 
                     "test": "[1, 2, 3, 100, 2, 3]", "output": "[3]"}
                ],
                "programming": [
                    {"task": "implement a queue data structure", "application": "algorithm implementation",
                     "function": "Queue", "params": "", 
                     "test": "q = Queue(); q.enqueue(1); q.enqueue(2); q.dequeue()", "output": "1"},
                    {"task": "implement a binary search algorithm", "application": "efficient data retrieval",
                     "function": "binary_search", "params": "sorted_array, target", 
                     "test": "[1, 3, 5, 7, 9], 5", "output": "2"},
                    {"task": "implement a memoization decorator", "application": "optimization",
                     "function": "memoize", "params": "func", 
                     "test": "@memoize\\ndef fib(n): return 1 if n <= 1 else fib(n-1) + fib(n-2); fib(10)", "output": "55"}
                ],
                # Add default tasks for any topic
                "default": [
                    {"task": "implement a basic algorithm", "application": "solving a common problem",
                     "function": "solve_problem", "params": "input_data", 
                     "test": "[5, 3, 8, 1, 9, 2]", "output": "[1, 2, 3, 5, 8, 9]"},
                    {"task": "create a utility function", "application": "data processing",
                     "function": "process_data", "params": "data", 
                     "test": "[1, 2, 3, 4, 5]", "output": "[2, 4, 6, 8, 10]"},
                    {"task": "build a simple data structure", "application": "efficient data management",
                     "function": "DataStructure", "params": "", 
                     "test": "ds = DataStructure(); ds.add(5); ds.add(10); ds.contains(5)", "output": "True"}
                ]
            }
        }
    ]
    
    # Generate questions based on the type counts
    for q_type, count in type_counts.items():
        if count <= 0:
            continue
            
        if q_type == "multiple_choice":
            # Generate multiple choice questions from templates
            for _ in range(count):
                # Select a random template
                template = random.choice(mc_templates)
                
                # Choose a topic from the topics list
                selected_topic = random.choice(topics_list)
                
                # Find the closest matching topic category
                topic_category = "default"  # Default category
                for category in template.get("concepts", {}).keys() or template.get("techniques", {}).keys():
                    if category in selected_topic.lower():
                        topic_category = category
                        break
                
                try:
                    # Get concept data
                    if "concepts" in template and topic_category in template["concepts"]:
                        # Choose a random concept from the available ones
                        concept_data = random.choice(template["concepts"][topic_category])
                        
                        # Format the question based on the template
                        question_text = template["template"].format(
                            concept=concept_data["concept"],
                            topic=selected_topic
                        )
                        
                                                                        # Create options                        options = []                                                # Add all options first (correct and incorrect)                        options.append(concept_data["correct"])                        for incorrect in concept_data["incorrect"]:                            options.append(incorrect)                                                    # Shuffle options to randomize the position of the correct answer                        correct_option = concept_data["correct"]                        random.shuffle(options)                        correct_index = options.index(correct_option)
                            
                    elif "techniques" in template and topic_category in template["techniques"]:
                        # Choose a random technique from the available ones
                        technique_data = random.choice(template["techniques"][topic_category])
                        
                        # Format the question based on the template
                        question_text = template["template"].format(
                            technique=technique_data["technique"],
                            task=technique_data["task"]
                        )
                        
                                                                        # Create options                        options = []                                                # Add all options first (correct and incorrect)                        options.append(technique_data["correct"])                        incorrect_options = technique_data["incorrect"]                        for incorrect in incorrect_options:                            options.append(incorrect)                                                    # Shuffle options to randomize the position of the correct answer                        correct_option = technique_data["correct"]                        random.shuffle(options)                        correct_index = options.index(correct_option)
                    else:
                        # Skip this template if it doesn't have concepts or techniques for the topic
                        continue
                        
                    # Create unique question ID combining timestamp and random number
                    question_id = f"mc_template_{timestamp}_{random.randint(1000, 9999)}"
                    
                    # Create the question dictionary
                    question = {
                        "type": "multiple_choice",
                        "question": question_text,
                        "options": options,
                        "correct_index": correct_index,
                        "id": question_id
                    }
                    
                    template_questions.append(question)
                except (KeyError, IndexError) as e:
                    # Skip this question if there's an error and try the next one
                    print(f"Error creating multiple choice question: {str(e)}")
                    continue
        elif q_type == "open_ended":
            # Generate open-ended questions from templates
            for _ in range(count):
                try:
                    # Select a random template
                    template = random.choice(open_ended_templates)
                    
                    # Choose a topic from the topics list
                    selected_topic = random.choice(topics_list)
                    
                    # Find the closest matching topic category
                    topic_category = "default"  # Default category
                    for category in template.get("concepts", {}).keys() or template.get("technique_pairs", {}).keys():
                        if category in selected_topic.lower():
                            topic_category = category
                            break
                    
                    question_text = ""
                    
                    if "concepts" in template and topic_category in template["concepts"]:
                        # Choose a random concept
                        concept = random.choice(template["concepts"][topic_category])
                        
                        # Format the question
                        question_text = template["template"].format(
                            concept=concept,
                            topic=selected_topic
                        )
                        
                    elif "technique_pairs" in template and topic_category in template["technique_pairs"]:
                        # Choose a random technique pair
                        pair = random.choice(template["technique_pairs"][topic_category])
                        
                        # Format the question
                        question_text = template["template"].format(
                            technique1=pair["t1"],
                            technique2=pair["t2"],
                            topic=selected_topic
                        )
                    else:
                        # Skip this template if it doesn't apply
                        continue
                    
                    # Create unique question ID
                    question_id = f"oe_template_{timestamp}_{random.randint(1000, 9999)}"
                    
                    # Create the question dictionary
                    question = {
                        "type": "open_ended",
                        "question": question_text,
                        "reference_answer": f"A comprehensive answer would discuss key aspects of {selected_topic} in relation to the question.",
                        "id": question_id
                    }
                    
                    template_questions.append(question)
                except (KeyError, IndexError) as e:
                    # Skip this question if there's an error and try the next one
                    print(f"Error creating open-ended question: {str(e)}")
                    continue
                
        elif q_type == "coding":
            # Generate coding questions from templates
            for _ in range(count):
                try:
                    # Select a random template
                    template = random.choice(coding_templates)
                    
                    # Choose a topic from the topics list
                    selected_topic = random.choice(topics_list)
                    
                    # Find the closest matching topic category
                    topic_category = "default"  # Default category
                    for category in template["tasks"].keys():
                        if category in selected_topic.lower():
                            topic_category = category
                            break
                    
                    if topic_category in template["tasks"]:
                        # Choose a random task
                        task_data = random.choice(template["tasks"][topic_category])
                        
                        # Format the question
                        question_text = template["template"].format(
                            task=task_data["task"],
                            application=task_data["application"]
                        )
                        
                        # Format the starter code
                        starter_code = template["starter_code"].format(
                            function_name=task_data["function"],
                            parameters=task_data["params"]
                        )
                        
                        # Format the test cases
                        test_cases = template["test_cases"].format(
                            function_name=task_data["function"],
                            test_input=task_data["test"],
                            expected_output=task_data["output"]
                        )
                        
                        # Create unique question ID
                        question_id = f"code_template_{timestamp}_{random.randint(1000, 9999)}"
                        
                        # Create the question dictionary
                        question = {
                            "type": "coding",
                            "question": question_text,
                            "starter_code": starter_code,
                            "test_cases": test_cases,
                            "id": question_id
                        }
                        
                        template_questions.append(question)
                except (KeyError, IndexError) as e:
                    # Skip this question if there's an error and try the next one
                    print(f"Error creating coding question: {str(e)}")
                    continue
    
    # If we didn't generate enough questions, add generic ones
    if len(template_questions) < num_questions:
        remaining = num_questions - len(template_questions)
        
        for i in range(remaining):
            question_id = f"generic_{timestamp}_{i}_{random.randint(1000, 9999)}"
            
            if question_types and "multiple_choice" in question_types:
                                                # Generic multiple choice question with random correct answer                options = [                    "Understanding the fundamental principles",                    "Applying advanced techniques",                    "Analyzing patterns in data",                    "Implementing efficient algorithms"                ]                # Randomly shuffle the options                random.shuffle(options)                # Randomly select which option is correct                correct_index = random.randint(0, 3)                                generic_question = {                    "type": "multiple_choice",                    "question": f"Which of the following is a key concept in {random.choice(topics_list)}?",                    "options": options,                    "correct_index": correct_index,                    "id": question_id                }
                template_questions.append(generic_question)
            
            elif question_types and "open_ended" in question_types:
                # Generic open-ended question
                generic_question = {
                    "type": "open_ended",
                    "question": f"Explain the importance of {random.choice(['methodology', 'theory', 'practical application', 'innovation'])} in {random.choice(topics_list)}.",
                    "reference_answer": f"A comprehensive answer would discuss key aspects of the topic in relation to the question.",
                    "id": question_id
                }
                template_questions.append(generic_question)
            
            elif question_types and "coding" in question_types:
                # Generic coding question
                generic_question = {
                    "type": "coding",
                    "question": f"Write a function to implement a basic algorithm related to {random.choice(topics_list)}.",
                    "starter_code": "def solution(data):\n    # Your implementation here\n    pass",
                    "test_cases": "# Test cases\nassert solution([1, 2, 3]) is not None",
                    "id": question_id
                }
                template_questions.append(generic_question)
            else:
                                                # Default to multiple choice if no types specified                options = [                    "Theoretical foundations",                    "Practical applications",                    "Historical development",                    "Current research trends"                ]                # Randomly shuffle the options                random.shuffle(options)                # Randomly select which option is correct                correct_index = random.randint(0, 3)                                generic_question = {                    "type": "multiple_choice",                    "question": f"Which aspect is most important when studying {random.choice(topics_list)}?",                    "options": options,                    "correct_index": correct_index,                    "id": question_id                }
                template_questions.append(generic_question)
    
    # Randomize the order of questions to avoid repeated patterns
    random.shuffle(template_questions)
    
    # Return only the number of questions requested
    return template_questions[:num_questions]

def _generate_question_batch_items(response: str) -> list:
    """
    Parse the LLM response to extract individual question items.
    
    Args:
        response: The raw text response from the LLM containing multiple questions
        
    Returns:
        A list of individual question items as strings
    """
    if not response:
        return []
        
    # Clean up the response text
    cleaned_text = response.strip()
    
    # Different patterns to try for separating questions
    patterns = [
        # Pattern for questions starting with "Question: "
        r"Question:\s*(.+?)(?=Question:\s*|\Z)",
        # Pattern for questions starting with numbered format "1. " or "1) "
        r"(?:^|\n)\s*(?:\d+[\.\)]\s*)(.+?)(?=(?:^|\n)\s*\d+[\.\)]\s*|\Z)",
        # Pattern for questions separated by double newlines
        r"(.+?)(?:\n\n+|\Z)"
    ]
    
    # Try each pattern until we find items
    items = []
    for pattern in patterns:
        items = [m.group(0).strip() for m in re.finditer(pattern, cleaned_text, re.DOTALL)]
        if items and len(items) > 0:
            break
            
    # If no items were found with the patterns, split by double newlines
    if not items:
        items = [item.strip() for item in cleaned_text.split("\n\n") if item.strip()]
        
    # Final filtering - ensure items have relevant content
    filtered_items = []
    for item in items:
        # Check if item contains any question indicators
        if ("Question:" in item or 
            re.search(r"\b[A-D]\.|\b[A-D]\)", item) or 
            "Reference Answer:" in item or 
            "Starter Code:" in item or
            "Test Cases:" in item):
            filtered_items.append(item)
            
    return filtered_items

def _parse_mc_question(item: str) -> tuple:
    """
    Parse a multiple-choice question item to extract the question, options, and correct answer.
    
    Args:
        item: A string containing a multiple-choice question
        
    Returns:
        A tuple of (question, options_list, correct_answer_index)
    """
    # Extract the question
    question_match = re.search(r"Question:\s*(.+?)(?=\n[A-D]\.|\n[A-D]\)|\Z)", item, re.DOTALL)
    if not question_match:
        return None, [], -1
    
    question_text = question_match.group(1).strip()
    
    # Extract the options (both A. and A) formats)
    options = []
    option_matches = re.finditer(r"([A-D])[\.\)]\s*(.+?)(?=\n[A-D][\.\)]|\nCorrect Answer:|\Z)", item, re.DOTALL)
    
    option_dict = {}
    for match in option_matches:
        letter = match.group(1)
        text = match.group(2).strip()
        option_dict[letter] = text
    
    # Ensure options are in order A, B, C, D
    for letter in ['A', 'B', 'C', 'D']:
        if letter in option_dict:
            options.append(option_dict[letter])
    
    # Extract the correct answer
    correct_letter = None
    correct_match = re.search(r"Correct Answer:\s*([A-D])", item)
    if not correct_match:
        # Try alternate format with comma
        correct_match = re.search(r"Correct Answer:\s*\[?([A-D])[,\]]?", item)
    
    if correct_match:
        correct_letter = correct_match.group(1)
    
    # Convert letter to index
    correct_index = -1
    if correct_letter:
        correct_index = ord(correct_letter) - ord('A')
        if correct_index < 0 or correct_index >= len(options):
            correct_index = 0
    elif options:
        correct_index = 0  # Default to first option if not specified
    
    return question_text, options, correct_index

def _parse_open_ended_question(item: str) -> tuple:
    """
    Parse an open-ended question item to extract the question and reference answer.
    
    Args:
        item: A string containing an open-ended question
        
    Returns:
        A tuple of (question, reference_answer)
    """
    # Extract the question
    question_match = re.search(r"Question:\s*(.+?)(?=\nReference Answer:|\Z)", item, re.DOTALL)
    if not question_match:
        return None, None
    
    question_text = question_match.group(1).strip()
    
    # Extract the reference answer
    reference_match = re.search(r"Reference Answer:\s*(.+?)(?=\n\n|\Z)", item, re.DOTALL)
    reference_answer = reference_match.group(1).strip() if reference_match else None
    
    return question_text, reference_answer

def _parse_coding_question(item: str) -> tuple:
    """
    Parse a coding question item to extract the question, starter code, and test cases.
    
    Args:
        item: A string containing a coding question
        
    Returns:
        A tuple of (question, starter_code, test_cases)
    """
    # Extract the question
    question_match = re.search(r"Question:\s*(.+?)(?=\nStarter Code:|\Z)", item, re.DOTALL)
    if not question_match:
        return None, None, None
    
    question_text = question_match.group(1).strip()
    
    # Extract the starter code
    code_match = re.search(r"Starter Code:\s*```(?:python)?\s*(.*?)```(?=\n|\Z)", item, re.DOTALL)
    starter_code = code_match.group(1).strip() if code_match else None
    
    # Extract the test cases
    test_cases = re.search(r"Test Cases:\s*```(?:python)?\s*(.*?)```(?=\n|\Z)", item, re.DOTALL)
    test_cases = test_cases.group(1).strip() if test_cases else None
    
    return question_text, starter_code, test_cases 

def _is_generic_coding_question(question: dict) -> bool:
    """
    Check if a coding question is too generic.
    
    Args:
        question: The question dictionary to check
        
    Returns:
        True if the question is generic, False otherwise
    """
    # Generic question detection based on question text
    generic_patterns = [
        r"implement a( simple)? (function|utility|method) to process",
        r"create a (function|utility|method) for data processing",
        r"implement a utility function",
        r"write a function to (process|handle) data",
        r"implement a generic",
        r"create a basic function",
        r"write a function for general",
    ]
    
    question_text = question.get("question", "").lower()
    
    # Check for generic patterns in the question text
    for pattern in generic_patterns:
        if re.search(pattern, question_text, re.IGNORECASE):
            return True
    
    # Check for generic function names in starter code
    starter_code = question.get("starter_code", "")
    generic_function_names = [
        "process_data", 
        "handle_data", 
        "utility_function", 
        "helper_function",
        "process_input",
        "analyze_data",
        "general_function",
        "basic_function"
    ]
    
    for name in generic_function_names:
        if f"def {name}" in starter_code:
            return True
    
    # Check if the question is too short (likely generic)
    if len(question_text.split()) < 5:
        return True
    
    # Check if test cases are too generic
    test_cases = question.get("test_cases", "")
    if not test_cases or test_cases == "# Test cases" or "is not None" in test_cases and len(test_cases) < 100:
        return True
    
    return False

def _create_specific_coding_questions(topic: str, count: int, difficulty: str) -> list:
    """
    Create specific coding questions for a given topic.
    
    Args:
        topic: The topic to create questions for
        count: Number of questions to create
        difficulty: Difficulty level
        
    Returns:
        A list of coding questions
    """
    import time
    import random
    
    timestamp = int(time.time() * 1000)
    
    # Create a variety of specific Python topics if the main topic is general
    python_topics = [
        "string manipulation", "file processing", "data structures", 
        "algorithms", "object-oriented programming", "functional programming",
        "error handling", "regular expressions", "network programming", 
        "database integration", "web scraping", "text processing",
        "concurrency", "context managers", "decorators"
    ]
    
    # Additional specific algorithms for algorithmic questions
    algorithms = [
        "binary search", "merge sort", "depth-first search", "breadth-first search",
        "dynamic programming", "greedy algorithms", "backtracking", "recursion",
        "divide and conquer", "graph traversal", "tree traversal", "heap operations"
    ]
    
    # Specific data structures
    data_structures = [
        "linked lists", "trees", "graphs", "heaps", "stacks", "queues",
        "dictionaries", "sets", "priority queues", "hash tables", "tries",
        "binary search trees", "AVL trees", "B-trees", "deques"
    ]
    
    # Python standard library modules
    std_libraries = [
        "collections", "itertools", "functools", "os", "sys", "datetime",
        "json", "csv", "re", "math", "random", "pathlib", "argparse",
        "logging", "unittest", "threading", "multiprocessing", "asyncio"
    ]
    
    questions = []
    
    # Specific coding question templates
    specific_templates = [
        # String processing templates
        {
            "topic": "string manipulation",
            "question": f"Implement a function that converts snake_case text to camelCase while preserving word boundaries.",
            "function_name": "snake_to_camel",
            "params": "text: str",
            "return_type": "str",
            "description": "Convert snake_case text to camelCase",
            "example_input": "'user_name_field'",
            "example_output": "'userNameField'",
            "test_cases": [
                ("'user_name_field'", "'userNameField'"),
                ("'snake_case'", "'snakeCase'"),
                ("'already_camel_case'", "'alreadyCamelCase'"),
                ("''", "''"),
                ("'single'", "'single'")
            ]
        },
        # Data structure template
        {
            "topic": "data structures",
            "question": f"Implement a custom Priority Queue class that maintains elements in priority order (highest priority first).",
            "class_name": "PriorityQueue",
            "methods": [
                {"name": "__init__", "params": "", "description": "Initialize an empty priority queue"},
                {"name": "enqueue", "params": "item, priority: int", "description": "Add an item with priority (higher values = higher priority)"},
                {"name": "dequeue", "params": "", "description": "Remove and return highest priority item"},
                {"name": "peek", "params": "", "description": "Return highest priority item without removing it"},
                {"name": "is_empty", "params": "", "description": "Check if queue is empty"}
            ],
            "test_cases_text": "pq = PriorityQueue()\nassert pq.is_empty() == True\npq.enqueue('task1', 1)\npq.enqueue('task2', 3)\npq.enqueue('task3', 2)\nassert pq.peek() == 'task2'  # Highest priority\nassert pq.dequeue() == 'task2'\nassert pq.dequeue() == 'task3'\nassert pq.dequeue() == 'task1'\nassert pq.is_empty() == True"
        },
        # Algorithm template
        {
            "topic": "algorithms",
            "question": f"Implement a function that finds the longest increasing subsequence in a list of numbers.",
            "function_name": "longest_increasing_subsequence",
            "params": "numbers: list[int]",
            "return_type": "list[int]",
            "description": "Find the longest increasing subsequence in a list",
            "example_input": "[10, 22, 9, 33, 21, 50, 41, 60]",
            "example_output": "[10, 22, 33, 50, 60]",
            "test_cases": [
                ("[10, 22, 9, 33, 21, 50, 41, 60]", "[10, 22, 33, 50, 60]"),
                ("[3, 2, 1]", "[3]"),
                ("[5, 6, 7, 8]", "[5, 6, 7, 8]"),
                ("[]", "[]"),
                ("[1]", "[1]")
            ]
        },
        # File processing template
        {
            "topic": "file processing",
            "question": f"Create a function that reads a CSV file and returns the data grouped by a specified column.",
            "function_name": "group_csv_data",
            "params": "file_path: str, group_by_column: str",
            "return_type": "dict",
            "description": "Group CSV data by a specified column",
            "test_cases_text": "import tempfile\nimport csv\n\n# Create a temporary CSV file for testing\nwith tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv') as temp:\n    writer = csv.writer(temp)\n    writer.writerow(['name', 'department', 'salary'])\n    writer.writerow(['Alice', 'Engineering', '90000'])\n    writer.writerow(['Bob', 'Marketing', '85000'])\n    writer.writerow(['Charlie', 'Engineering', '95000'])\n    temp_path = temp.name\n\n# Test the function\nresult = group_csv_data(temp_path, 'department')\nassert 'Engineering' in result\nassert 'Marketing' in result\nassert len(result['Engineering']) == 2\nassert len(result['Marketing']) == 1\nassert result['Engineering'][0]['name'] == 'Alice'\nassert result['Engineering'][1]['name'] == 'Charlie'\nassert result['Marketing'][0]['name'] == 'Bob'\n\nimport os\nos.unlink(temp_path)  # Clean up the temporary file"
        }
    ]
    
    # Generate specific questions based on templates and the topic
    for i in range(count):
        # Select a Python subtopic that might match the user's topic
        selected_topic = topic
        if "python" in topic.lower() or topic.lower() in ["programming", "coding", "development"]:
            selected_topic = random.choice(python_topics)
        
        # Find a suitable template based on the topic
        matching_templates = [t for t in specific_templates if t["topic"] in selected_topic.lower()]
        if not matching_templates:
            # If no direct match, use a random template
            template = random.choice(specific_templates)
        else:
            template = random.choice(matching_templates)
        
        question_id = f"specific_coding_{timestamp}_{random.randint(1000, 9999)}"
        
        # Generate the question based on the template
        if "class_name" in template:
            # Class-based question
            class_template = f"""class {template['class_name']}:
    \"\"\"
    {template.get('description', 'A custom class implementation')}
    \"\"\"
    
"""
            for method in template["methods"]:
                class_template += f"    def {method['name']}({method['params']}):\n        \"\"\"\n        {method.get('description', '')}\n        \"\"\"\n        # Your implementation here\n        pass\n    \n"
            
            question_dict = {
                "type": "coding",
                "question": template["question"],
                "starter_code": class_template,
                "test_cases": template["test_cases_text"],
                "id": question_id
            }
        else:
            # Function-based question
            function_template = f"""def {template['function_name']}({template['params']}) -> {template.get('return_type', 'Any')}:
    \"\"\"
    {template.get('description', 'Implementation of a specific function')}
    
    Args:
        {template['params'].replace(': ', ': Description of ')}
        
    Returns:
        {template.get('return_type', 'Any')}: {template.get('description', 'Result of the function')}
        
    Example:
        >>> {template['function_name']}({template.get('example_input', '')})
        {template.get('example_output', '')}
    \"\"\"
    # Your implementation here
    pass"""
            
            # Generate test cases
            if "test_cases" in template:
                test_cases_text = ""
                for test_input, test_output in template["test_cases"]:
                    test_cases_text += f"assert {template['function_name']}({test_input}) == {test_output}\n"
            else:
                test_cases_text = template.get("test_cases_text", "# Test cases\nassert True")
            
            question_dict = {
                "type": "coding",
                "question": template["question"],
                "starter_code": function_template,
                "test_cases": test_cases_text,
                "id": question_id
            }
        
        questions.append(question_dict)
    
    # Ensure we create unique questions
    unique_questions = {}
    for q in questions:
        if q["question"] not in unique_questions:
            unique_questions[q["question"]] = q
    
    return list(unique_questions.values())