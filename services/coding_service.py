"""
Coding service module that handles coding assignment generation, parsing, and evaluation.
"""
from typing import Dict, Any
import re
from services.llm_service import generate_content

def generate_assignment_prompt(topic: str, difficulty: str, time_limit: int) -> str:
    """
    Generate a prompt for the LLM to create a coding assignment.
    
    Args:
        topic: Topic for the coding assignment
        difficulty: Difficulty level
        time_limit: Estimated time to complete in minutes
        
    Returns:
        A formatted prompt string
    """
    return f"""Create a Python coding assignment on the topic: {topic}
    Difficulty level: {difficulty}
    Estimated completion time: {time_limit} minutes
    
    Please format your response with the following sections:
    
    TITLE: A descriptive title for the assignment
    
    BACKGROUND: Brief explanation of the topic and relevant concepts
    
    REQUIREMENTS: Clear statement of what the program should do
    
    EXPECTED_OUTPUT: Examples of expected input/output behavior
    
    HINTS: Helpful hints or tips for solving the problem
    
    EVALUATION_CRITERIA: Criteria for evaluating the solution
    
    CODE_TEMPLATE:
    ```python
    # Include starter code here that the student can use
    ```
    
    Make the assignment challenging but achievable for a {difficulty} level student.
    The assignment should be completable within {time_limit} minutes.
    """

def parse_assignment(content: str) -> Dict[str, Any]:
    """
    Parse the LLM response into structured assignment data.
    
    Args:
        content: The raw response from the LLM
        
    Returns:
        A dictionary with assignment sections
    """
    sections = {
        "title": "",
        "background": "",
        "requirements": "",
        "expected_output": "",
        "hints": "",
        "evaluation_criteria": "",
        "code_template_content": ""
    }
    
    # Extract the code template
    code_template_match = re.search(r'```python(.*?)```', content, re.DOTALL)
    if code_template_match:
        sections["code_template_content"] = code_template_match.group(1).strip()
    
    # Extract other sections
    patterns = {
        "title": r'TITLE:(.*?)(?=BACKGROUND:|$)',
        "background": r'BACKGROUND:(.*?)(?=REQUIREMENTS:|$)',
        "requirements": r'REQUIREMENTS:(.*?)(?=EXPECTED_OUTPUT:|$)',
        "expected_output": r'EXPECTED_OUTPUT:(.*?)(?=HINTS:|$)',
        "hints": r'HINTS:(.*?)(?=EVALUATION_CRITERIA:|$)',
        "evaluation_criteria": r'EVALUATION_CRITERIA:(.*?)(?=CODE_TEMPLATE:|$)'
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, content, re.DOTALL)
        if match:
            sections[key] = match.group(1).strip()
    
    return sections

def generate_code_evaluation_prompt(code: str, requirements: str, expected_output: str) -> str:
    """
    Generate a prompt for LLM to evaluate student code.
    
    Args:
        code: The student's code submission
        requirements: The original requirements
        expected_output: The expected output description
        
    Returns:
        A formatted prompt string
    """
    return f"""Evaluate the following Python code based on the requirements:

REQUIREMENTS:
{requirements}

EXPECTED OUTPUT:
{expected_output}

CODE TO EVALUATE:
```python
{code}
```

Provide a detailed analysis of the code with the following sections:
1. Verdict (Yes/Partially/No): Does the code meet the requirements?
2. Analysis: Detailed review of the code's functionality, correctness, and quality.
3. Improvements: Suggestions for how the code could be improved.

Format your response as follows:
VERDICT: [Yes/Partially/No]
ANALYSIS: [Detailed analysis]
IMPROVEMENTS: [Specific improvement suggestions]
"""

def parse_code_evaluation(content: str) -> Dict[str, str]:
    """
    Parse the LLM evaluation response into structured sections.
    
    Args:
        content: The raw evaluation response from the LLM
        
    Returns:
        A dictionary with evaluation sections
    """
    sections = {
        "verdict": "",
        "analysis": "",
        "improvements": ""
    }
    
    current_section = None
    
    for line in content.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('VERDICT:'):
            current_section = "verdict"
            sections[current_section] = line[8:].strip()
        elif line.startswith('ANALYSIS:'):
            current_section = "analysis"
            sections[current_section] = line[9:].strip()
        elif line.startswith('IMPROVEMENTS:'):
            current_section = "improvements"
            sections[current_section] = line[13:].strip()
        elif current_section:
            sections[current_section] += " " + line
    
    return sections 