import streamlit as st
import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from io import StringIO
import sys
import time
import json
import pickle
from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Tuple
from ui.components import setup_page_config, create_sidebar, create_login_form, create_register_form, create_login_screen
from ui.pages import (
    render_home_page, render_quiz_page, render_results_page,
    render_student_home_page, render_professor_home_page,
    render_coding_page, render_practice_quiz_page,
    render_developer_users_page, render_developer_home_page,
    render_developer_api_page, render_developer_logs_page,
    render_developer_settings_page, render_professor_analytics_page,
    render_profile_page, render_professor_create_quiz_page,
    render_assigned_quizzes_page, render_professor_rankings_page,
    render_student_rankings_page
)
from services.quiz_service import generate_quiz_prompt, parse_questions, calculate_quiz_score, create_quiz_summary, generate_analysis_prompt, parse_quiz_analysis, generate_practice_quiz
import random
from datetime import datetime

# Load environment variables
load_dotenv()

# Session state persistence functions
def save_session_state():
    """Save session state to a file to persist across sessions"""
    # Keys to save
    keys_to_save = [
        'quizzes', 
        'available_quizzes', 
        'published_quizzes',
        'quiz_results',          # Add quiz results
        'completed_quizzes',     # Add completed quizzes
        'user_answers',          # Save user's answers
        'quiz_analysis',         # Save analysis data
        'coding_test_results'    # Save coding test results
    ]
    
    # Create a dictionary with only the keys we want to save
    state_to_save = {key: st.session_state[key] for key in keys_to_save if key in st.session_state}
    
    # Handle special case for user_code_answers to ensure both integer and string keys work
    if 'user_code_answers' in st.session_state:
        code_answers_copy = {}
        for k, v in st.session_state['user_code_answers'].items():
            code_answers_copy[str(k)] = v  # Convert all keys to strings for consistency
        state_to_save['user_code_answers'] = code_answers_copy
    
    # Handle special case for coding_test_results
    if 'coding_test_results' in st.session_state:
        test_results_copy = {}
        for k, v in st.session_state['coding_test_results'].items():
            test_results_copy[str(k)] = v  # Convert all keys to strings for consistency
        state_to_save['coding_test_results'] = test_results_copy
    
    try:
        # Save to a file
        with open('session_state.pkl', 'wb') as f:
            pickle.dump(state_to_save, f)
        return True
    except Exception as e:
        print(f"Error saving session state: {e}")
        return False

def load_session_state():
    """Load session state from a file"""
    try:
        # Check if file exists
        if os.path.exists('session_state.pkl'):
            with open('session_state.pkl', 'rb') as f:
                state = pickle.load(f)
                
            # Update session state with loaded values
            for key, value in state.items():
                st.session_state[key] = value
            return True
        return False
    except Exception as e:
        print(f"Error loading session state: {e}")
        return False

# Clear cache on startup to force reloading of all components
st.cache_data.clear()
st.cache_resource.clear()

# Define simple Question class
@dataclass
class Question:
    id: int
    question: str
    answers: List[str]
    correct_answer: int

# --- LLM INTEGRATION ---

# Initialize LLM client
@st.cache_resource
def get_llm():
    try:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            st.error("No API key found in .env file. Please add your GROQ_API_KEY to the .env file.")
            return None
        return ChatGroq(model_name="llama3-8b-8192")
    except Exception as e:
        st.error(f"Error initializing LLM: {e}")
        return None

# Generate content using LLM
def generate_content(prompt: str) -> Optional[str]:
    """Generate content using the LLM with proper error handling."""
    llm = get_llm()
    if not llm:
        st.error("LLM initialization failed. Check your API key in the .env file.")
        return None
    
    try:
        with st.spinner("Generating content..."):
            start_time = time.time()
            response = llm.invoke(prompt).content
            elapsed = time.time() - start_time
            st.success(f"Generated in {elapsed:.2f} seconds")
        return response
    except Exception as e:
        st.error(f"Error generating content: {str(e)}")
        return None

# --- QUIZ FUNCTIONS ---

# Parse questions from LLM response
def parse_questions(response: str) -> List[Question]:
    """Parse the LLM response into Question objects."""
    if not response:
        return []
    
    questions = []
    lines = response.replace('\r\n', '\n').split('\n')
    
    question_pattern = re.compile(r'^(\d+)[\.\)]\s+(.+)', re.IGNORECASE)
    answer_pattern = re.compile(r'^([A-Z])[\.\)]\s+(.+)', re.IGNORECASE)
    
    current_question = None
    current_answers = []
    correct_answer = -1
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
        
        # Check for a new question
        question_match = question_pattern.match(line)
        if question_match:
            # Save previous question if exists
            if current_question and current_answers:
                if correct_answer == -1:
                    correct_answer = 0
                
                questions.append(Question(
                    id=len(questions) + 1,
                    question=current_question,
                    answers=current_answers,
                    correct_answer=correct_answer
                ))
                
                # Reset
                current_question = None
                current_answers = []
                correct_answer = -1
            
            # Set new question
            current_question = question_match.group(2).strip()
            i += 1
            continue
        
        # Check for an answer
        answer_match = answer_pattern.match(line)
        if answer_match:
            letter = answer_match.group(1).upper()
            text = answer_match.group(2).strip()
            
            # Check if correct (marked with **)
            if "**" in text:
                text = text.replace("**", "")
                correct_answer = ord(letter) - ord('A')
            
            current_answers.append(text)
        
        i += 1
    
    # Add the last question
    if current_question and current_answers:
        if correct_answer == -1:
            correct_answer = 0
        
        questions.append(Question(
            id=len(questions) + 1,
            question=current_question,
            answers=current_answers,
            correct_answer=correct_answer
        ))
    
    return questions

# Note: calculate_quiz_score is now imported from services.quiz_service

# def generate_quiz_prompt(topics: str, num_questions: int, difficulty: str, num_options: int) -> str:
#    """Generate the prompt for quiz creation."""
#    # Focus on machine learning topics
#    ml_topics = f"machine learning topics related to {topics}"
#    return f"""Create a quiz with {num_questions} multiple-choice questions about {ml_topics} at {difficulty} level.
#    Each question should have {num_options} options.
#    Mark the correct answer using bold: **correct answer**
#    
#    Format each question as:
#    1. Question text here?
#    A) First option
#    B) Second option
#    C) Third option
#    D) Fourth option
#    """

def create_quiz_summary(questions: List[Question], user_answers: Dict[int, int]) -> str:
    """Create a summary of the quiz for LLM evaluation."""
    quiz_summary = "QUIZ QUESTIONS AND ANSWERS:\n\n"
    for i, q in enumerate(questions):
        user_answer = user_answers.get(i, -1)
        user_letter = chr(65 + user_answer) if 0 <= user_answer < len(q.answers) else "None"
        correct_letter = chr(65 + q.correct_answer)
        
        quiz_summary += f"Question {i+1}: {q.question}\n"
        for j, ans in enumerate(q.answers):
            quiz_summary += f"{chr(65+j)}) {ans}\n"
        quiz_summary += f"User's answer: {user_letter}) {q.answers[user_answer] if 0 <= user_answer < len(q.answers) else 'Not answered'}\n"
        quiz_summary += f"Correct answer: {correct_letter}) {q.answers[q.correct_answer]}\n\n"
    
    return quiz_summary

def generate_analysis_prompt(quiz_summary: str, correct: int, total: int, score_pct: float) -> str:
    """Generate the prompt for quiz performance analysis."""
    return f"""Based on the following quiz performance, provide a comprehensive analysis:

    {quiz_summary}
    
    The user scored {correct}/{total} ({score_pct:.1f}%).
    
    Please provide:
    1. An assessment of the user's understanding of the subject matter
    2. Identification of knowledge gaps or misconceptions
    3. Specific recommendations for further study
    4. Positive reinforcement for correct answers
    
    Format your response as follows:
    <understanding>
    Assessment of overall understanding
    </understanding>
    
    <knowledge_gaps>
    Identification of specific knowledge gaps
    </knowledge_gaps>
    
    <recommendations>
    Specific recommendations for improvement
    </recommendations>
    
    <strengths>
    Areas where the user demonstrated good understanding
    </strengths>
    """

def parse_quiz_analysis(evaluation: str) -> Dict[str, str]:
    """Parse the LLM response into analysis sections."""
    if not evaluation:
        return {}
        
    sections = {
        "understanding": r'<understanding>(.*?)</understanding>',
        "knowledge_gaps": r'<knowledge_gaps>(.*?)</knowledge_gaps>',
        "recommendations": r'<recommendations>(.*?)</recommendations>',
        "strengths": r'<strengths>(.*?)</strengths>'
    }
    
    result = {}
    for key, pattern in sections.items():
        match = re.search(pattern, evaluation, re.DOTALL)
        result[key] = match.group(1).strip() if match else ""
    
    return result

# --- CODING ASSIGNMENT FUNCTIONS ---

def generate_assignment_prompt(topic: str, difficulty: str, time_limit: int) -> str:
    """Generate the prompt for coding assignment creation."""
    return f"""Create a high-quality coding assignment about {topic} for a {difficulty.lower()} level student that can be completed in approximately {time_limit} minutes.

    Please format your response EXACTLY as follows:
    
    <title>
    [Provide a concise, descriptive title]
    </title>
    
    <background>
    [Brief background about the topic and why it's important]
    </background>
    
    <requirements>
    [Detailed, numbered list of requirements]
    </requirements>
    
    <hints>
    [1-3 helpful hints without giving away the solution]
    </hints>
    
    <code_template>
    ```python
    # Start with this template
    [Basic code structure to get started]
    ```
    </code_template>
    
    <expected_output>
    ```
    [Example of expected output/behavior]
    ```
    </expected_output>
    
    <evaluation_criteria>
    [How the solution should be evaluated]
    </evaluation_criteria>
    """

def parse_assignment(response: str) -> Dict[str, str]:
    """Parse the LLM response into assignment sections."""
    if not response:
        return {}
    
    sections = {
        "title": r'<title>(.*?)</title>',
        "background": r'<background>(.*?)</background>',
        "requirements": r'<requirements>(.*?)</requirements>',
        "hints": r'<hints>(.*?)</hints>',
        "code_template": r'<code_template>(.*?)</code_template>',
        "expected_output": r'<expected_output>(.*?)</expected_output>',
        "evaluation_criteria": r'<evaluation_criteria>(.*?)</evaluation_criteria>'
    }
    
    parsed_content = {}
    for key, pattern in sections.items():
        match = re.search(pattern, response, re.DOTALL)
        parsed_content[key] = match.group(1).strip() if match else ""
    
    # Extract code template
    if parsed_content.get("code_template"):
        code_match = re.search(r'```python\s+(.*?)\s+```', parsed_content["code_template"], re.DOTALL)
        parsed_content["code_template_content"] = code_match.group(1).strip() if code_match else "# Write your solution here\n"
    
    return parsed_content

def generate_code_evaluation_prompt(code: str, requirements: str, expected_output: str) -> str:
    """Generate the prompt for code evaluation."""
    return f"""Please evaluate the following Python code solution for a coding assignment. 
    
    ASSIGNMENT:
    {requirements}
    
    EXPECTED OUTPUT:
    {expected_output}
    
    CODE TO EVALUATE:
    ```python
    {code}
    ```
    
    Provide a comprehensive review with:
    1. Whether the code will work as expected (Yes/No/Partially)
    2. Any syntax errors or bugs
    3. Correctness of the solution
    4. Suggestions for improvement
    5. Alternative approaches that might be more efficient
    
    Format your response as follows:
    <verdict>Yes/No/Partially</verdict>
    <analysis>
    Your detailed analysis here
    </analysis>
    <improvements>
    Your suggestions for improvement
    </improvements>
    """

def parse_code_evaluation(evaluation: str) -> Dict[str, str]:
    """Parse the LLM response into evaluation sections."""
    if not evaluation:
        return {}
    
    verdict_match = re.search(r'<verdict>(.*?)</verdict>', evaluation, re.DOTALL)
    analysis_match = re.search(r'<analysis>(.*?)</analysis>', evaluation, re.DOTALL)
    improvements_match = re.search(r'<improvements>(.*?)</improvements>', evaluation, re.DOTALL)
    
    return {
        "verdict": verdict_match.group(1).strip() if verdict_match else "Unknown",
        "analysis": analysis_match.group(1).strip() if analysis_match else evaluation,
        "improvements": improvements_match.group(1).strip() if improvements_match else ""
    }

# --- MAIN APPLICATION ---

def main():
    # Load persisted session state first
    load_session_state()
    
    # Ensure published quizzes are available to students
    # This syncs the quizzes and available_quizzes lists
    if "quizzes" in st.session_state and "available_quizzes" in st.session_state:
        # Find active quizzes that should be visible to students
        for quiz in st.session_state.quizzes:
            if quiz.get('status') == 'active':
                # Check if this quiz is already in available_quizzes
                quiz_id = quiz.get('id')
                if not any(q.get('id') == quiz_id for q in st.session_state.available_quizzes):
                    # Add to available_quizzes
                    st.session_state.available_quizzes.append(quiz)
    
    # Initialize session state
    if "user_type" not in st.session_state:
        st.session_state.user_type = None
    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "show_login_form" not in st.session_state:
        st.session_state.show_login_form = False
    if "show_register_form" not in st.session_state:
        st.session_state.show_register_form = False
    if "login_type" not in st.session_state:
        st.session_state.login_type = None
    if "questions" not in st.session_state:
        st.session_state.questions = []
    
    # Initialize but preserve existing values for quiz-related state
    # This ensures we don't overwrite loaded values from session state
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}
    if "quiz_results" not in st.session_state:
        st.session_state.quiz_results = {}
    if "completed_quizzes" not in st.session_state:
        st.session_state.completed_quizzes = []
    if "quiz_analysis" not in st.session_state:
        st.session_state.quiz_analysis = None
        
    if "assignment" not in st.session_state:
        st.session_state.assignment = None
    if "code_template" not in st.session_state:
        st.session_state.code_template = None
    if "user_code" not in st.session_state:
        st.session_state.user_code = None
    if "language" not in st.session_state:
        st.session_state.language = "en"  # Initialize language to English by default
    if "show_add_user_form" not in st.session_state:
        st.session_state.show_add_user_form = False
    if "show_delete_confirm" not in st.session_state:
        st.session_state.show_delete_confirm = False
    if "user_to_delete" not in st.session_state:
        st.session_state.user_to_delete = None
    if "available_quizzes" not in st.session_state:
        st.session_state.available_quizzes = []
    if "published_quizzes" not in st.session_state:
        st.session_state.published_quizzes = []
    if "quizzes" not in st.session_state:
        st.session_state.quizzes = []
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}
    # New session state variables for practice quiz
    if "quiz_time_taken" not in st.session_state:
        st.session_state.quiz_time_taken = None
    if "coding_test_results" not in st.session_state:
        st.session_state.coding_test_results = {}
        
    # Initialize default users
    try:
        from services.database import Database
        db = Database()
        db.initialize_default_users()
    except Exception as e:
        st.error(f"Error initializing database: {str(e)}")

    # Setup page configuration
    setup_page_config()
    
    # Show login screen if not logged in
    if st.session_state.user_type is None:
        if st.session_state.show_login_form:
            create_login_form()
        elif st.session_state.show_register_form:
            create_register_form()
        else:
            create_login_screen()
        return
    
    # Create sidebar for logged-in users
    create_sidebar()
    
    # Debugger information to help diagnose routing issues
    # We'll remove this after fixing the issue
    debug_info = f"""
    DEBUG INFO:
    user_type: {st.session_state.user_type}
    page: {st.session_state.page}
    quizzes: {len(st.session_state.get('quizzes', []))}
    available_quizzes: {len(st.session_state.get('available_quizzes', []))}
    """
    st.sidebar.markdown(debug_info)
    
    # Render the appropriate page based on session state
    if st.session_state.user_type == "student":
        # STUDENT PAGES
        if st.session_state.page == "student_home":
            render_student_home_page()
        elif st.session_state.page == "student_quiz":
            render_quiz_page()
        elif st.session_state.page == "student_coding":
            render_coding_page()
        elif st.session_state.page == "student_results":
            render_results_page()
        elif st.session_state.page == "profile":
            render_profile_page()
        elif st.session_state.page == "assigned_quizzes":
            render_assigned_quizzes_page()
        elif st.session_state.page == "practice_quiz":
            render_practice_quiz_page()
        elif st.session_state.page == "student_rankings":
            render_student_rankings_page()
        else:
            # Default to student home for unknown pages
            st.session_state.page = "student_home"
            st.rerun()

    elif st.session_state.user_type == "professor":
        # PROFESSOR PAGES
        if st.session_state.page == "professor_home":
            render_professor_home_page()
        elif st.session_state.page == "professor_create_quiz":
            render_professor_create_quiz_page()
        elif st.session_state.page == "professor_analytics":
            render_professor_analytics_page()
        elif st.session_state.page == "professor_rankings":
            render_professor_rankings_page()
        elif st.session_state.page == "profile":
            render_profile_page()
        else:
            # Default to professor home for unknown pages
            st.session_state.page = "professor_home"
            st.rerun()
    
    elif st.session_state.user_type == "developer":
        # DEVELOPER PAGES
        if st.session_state.page == "developer_home":
            render_developer_home_page()
        elif st.session_state.page == "developer_api":
            render_developer_api_page()
        elif st.session_state.page == "developer_logs":
            render_developer_logs_page()
        elif st.session_state.page == "developer_settings":
            render_developer_settings_page()
        elif st.session_state.page == "developer_users":
            render_developer_users_page()
        elif st.session_state.page == "profile":
            render_profile_page()
        else:
            # Default to developer home for unknown pages
            st.session_state.page = "developer_home"
            st.rerun()
    else:
        # If we reach here, there's a serious issue with session state
        st.error(f"Invalid user type in session state: {st.session_state.user_type}")
        # Reset session and go to login
        for key in list(st.session_state.keys()):
            if key != "language":  # Keep language preference
                del st.session_state[key]
        st.session_state.page = "login"
        st.rerun()

# New functions to handle student pages
# This function has been moved to ui/pages.py
# def render_assigned_quizzes_page():
#     """Render the assigned quizzes page for students."""
#     st.markdown("""
#     <div style="text-align: center; margin-bottom: 30px;">
#         <h1 style="color: #003B70; font-size: 2.5rem; font-weight: 800; margin-bottom: 10px;">
#             Assigned Python Programming Quizzes
#         </h1>
#     </div>
#     """, unsafe_allow_html=True)
#     
#     # Back button
#     if st.button("← Back to Dashboard", key="back_to_dashboard"):
#         st.session_state.page = "student_home"
#         st.rerun()
#     
#     # Get available quizzes from session state
#     if "available_quizzes" not in st.session_state:
#         st.session_state.available_quizzes = []
#         
#     available_quizzes = st.session_state.available_quizzes
#     
#     # Filter out practice quizzes (which have IDs starting with "practice_")
#     professor_quizzes = [q for q in available_quizzes if q.get('status', '') == 'active' and 
#                          not str(q.get('id', '')).startswith('practice_')]
#     
#     if not professor_quizzes:
#         st.markdown("""
#         <div style="background-color: white; border-radius: 10px; padding: 25px; 
#         box-shadow: 0 4px 15px rgba(0, 59, 112, 0.1); margin-bottom: 20px; border: 1px solid rgba(0, 59, 112, 0.1); text-align: center;">
#             <img src="https://img.icons8.com/ios/100/003B70/test-partial-passed.png" width="80" style="margin-bottom: 20px;">
#             <h3 style="color: #003B70; font-weight: 700; margin-bottom: 20px; font-size: 1.5rem;">No Assigned Quizzes Yet</h3>
#             <p style="color: #666; margin-bottom: 20px; font-size: 1.1rem;">
#                 Your professor hasn't published any quizzes that are currently available to take.
#                 <br><br>
#                 Check back later or try creating a practice quiz in the meantime.
#             </p>
#             
#         </div>
#         """, unsafe_allow_html=True)
#         
#         if st.button("Create a Practice Quiz Instead", use_container_width=True, type="primary"):
#             st.session_state.page = "practice_quiz"
#             st.rerun()
#     else:
#         st.subheader("Available Python Programming Quizzes")
#         st.markdown("These quizzes are assigned by your professors and need to be completed by the due date.")
#         
#         for i, quiz in enumerate(professor_quizzes):
#             with st.container():
#                 st.markdown("---")
#                 
#                 # Create a two-column layout
#                 col1, col2 = st.columns([3, 1])
#                 
#                 with col1:
#                     # Quiz title and description
#                     st.markdown(f"### {quiz.get('title', 'Untitled Quiz')}")
#                     st.markdown(f"_{quiz.get('description', 'No description provided')}_")
#                     
#                     # Display quiz metadata in a clean row
#                     metadata_cols = st.columns(3)
#                     with metadata_cols[0]:
#                         st.markdown(f"**Course:** {quiz.get('course', 'N/A')}")
#                     with metadata_cols[1]:
#                         st.markdown(f"**Duration:** {quiz.get('duration_minutes', 60)} minutes")
#                     with metadata_cols[2]:
#                         st.markdown(f"**Due:** {quiz.get('end_time', 'Not set')}")
#                 
#                 with col2:
#                     # Start quiz button
#                     if st.button("Start Quiz", key=f"start_quiz_{quiz.get('id')}", use_container_width=True, type="primary"):
#                         st.session_state.current_quiz_id = quiz.get('id')
#                         
#                         # Get questions from the quiz
#                         if "questions" in quiz:
#                             st.session_state.questions = quiz["questions"]
#                         else:
#                             # If somehow the quiz doesn't have questions, look in available_quizzes
#                             for q in st.session_state.available_quizzes:
#                                 if q.get("id") == quiz.get('id') and "questions" in q:
#                                     st.session_state.questions = q["questions"]
#                                     break
#                         
#                         if "quiz_answers" not in st.session_state:
#                             st.session_state.quiz_answers = {}
#                         
#                         st.session_state.page = "student_quiz"
#                         st.rerun()

def render_practice_quiz_page():
    """Render the practice quiz creation page for students."""
    # Add custom CSS for button styling
    st.markdown("""
    <style>
    /* Style for all buttons - general approach */
    .stButton button {
        transition: all 0.3s ease;
    }
    
    /* Primary (selected) state for all buttons */
    .stButton button[data-testid="baseButton-primary"] {
        background-color: #003B70 !important;
        color: white !important;
        border-color: #003B70 !important;
    }
    
    /* Secondary (not selected) state for all buttons */
    .stButton button[data-testid="baseButton-secondary"] {
        background-color: white !important;
        color: #003B70 !important;
        border-color: #003B70 !important;
    }
    
    /* Hover effect for all buttons */
    .stButton button:hover {
        border-color: #003B70 !important;
        color: white !important;
        background-color: #004d8f !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #003B70; font-size: 2.5rem; font-weight: 700; margin-bottom: 15px;">
            Python Programming Practice
        </h1>
        <p style="color: #4B5563; font-size: 1.2rem; margin-bottom: 0;">
            Create professional-grade Python programming quizzes for your practice
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Back button with improved styling
    col_back, col_empty = st.columns([1, 5])
    with col_back:
        if st.button("← Back", key="back_to_dashboard", type="secondary", use_container_width=True):
            st.session_state.page = "student_home"
            st.rerun()
    
    # Custom Practice section with improved styling
    st.markdown("""
    <div style="background-color: white; 
         border-radius: 12px; padding: 25px; 
         box-shadow: 0 4px 12px rgba(0, 59, 112, 0.1); margin-bottom: 30px;
         border: 1px solid rgba(0, 59, 112, 0.1);">
        <h2 style="color: #003B70; margin-bottom: 12px; font-size: 1.6rem; font-weight: 600;">Create Your Practice Quiz</h2>
        <p style="color: #4B5563; font-size: 1.05rem;">
            Select topics and options to create a personalized Python quiz
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Topic selection section
    from services.llm_service import get_available_topics
    available_topics = get_available_topics()
    
    # Initialize session state variables if they don't exist
    if "selected_question_count" not in st.session_state:
        st.session_state.selected_question_count = 10
    
    if "selected_difficulty" not in st.session_state:
        st.session_state.selected_difficulty = "Medium"
    
    if "selected_topics" not in st.session_state:
        st.session_state.selected_topics = []
        
    if "question_types" not in st.session_state:
        st.session_state.question_types = ["multiple_choice"]
    
    # Topic selection outside the form
    st.markdown("<h3 style='color: #003B70; font-size: 1.4rem;'>Select Topics</h3>", unsafe_allow_html=True)
    
    # Create columns for topics
    topic_cols = st.columns(3)
    
    # Get all topic categories
    topic_categories = list(available_topics.keys())
    
    # Create topic buttons outside the form
    for i, category in enumerate(topic_categories):
        col_idx = i % 3
        with topic_cols[col_idx]:
            # Check if this topic was previously selected
            is_selected = category in st.session_state.selected_topics
            
            # Add checkmark for selected button
            button_label = category
            if is_selected:
                button_label = f"✓ {category}"
            
            # Create a button for each topic with primary/secondary styling
            if st.button(
                button_label,
                key=f"topic_{category}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                # Toggle selection
                if category in st.session_state.selected_topics:
                    st.session_state.selected_topics.remove(category)
                else:
                    st.session_state.selected_topics.append(category)
                st.rerun()
    
    # Quiz Options outside the form
    st.markdown("<h3 style='color: #003B70; font-size: 1.4rem; margin-top: 20px;'>Quiz Options</h3>", unsafe_allow_html=True)
    
    # Number of questions with buttons
    st.markdown("<p style='color: #4B5563; font-weight: 500;'>Number of Questions:</p>", unsafe_allow_html=True)
    
    # Create buttons for question counts
    qcount_cols = st.columns(6)
    question_counts = [5, 10, 15, 20, 30, 50]  # Increased max to 50 questions
    
    for i, count in enumerate(question_counts):
        with qcount_cols[i]:
            is_selected = st.session_state.selected_question_count == count
            # Add checkmark for selected button
            button_label = str(count)
            if is_selected:
                button_label = f"✓ {count}"
                
            if st.button(
                button_label,
                key=f"qcount_{count}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                st.session_state.selected_question_count = count
                st.rerun()
    
    # Difficulty level with buttons
    st.markdown("<p style='color: #4B5563; font-weight: 500; margin-top: 15px;'>Difficulty Level:</p>", unsafe_allow_html=True)
    
    # Create buttons for difficulty levels
    diff_cols = st.columns(3)
    difficulty_levels = ["Easy", "Medium", "Hard"]
    
    for i, level in enumerate(difficulty_levels):
        with diff_cols[i]:
            is_selected = st.session_state.selected_difficulty == level
            # Add checkmark for selected button
            button_label = level
            if is_selected:
                button_label = f"✓ {level}"
                
            if st.button(
                button_label,
                key=f"diff_{level}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                st.session_state.selected_difficulty = level
                st.rerun()
    
    # Question Types with buttons
    st.markdown("<h3 style='color: #003B70; font-size: 1.4rem; margin-top: 20px;'>Question Types</h3>", unsafe_allow_html=True)
    
    # Create columns for question types
    qtype_cols = st.columns(3)
    
    # Define question types with icons and descriptions
    question_types = [
        {"id": "multiple_choice", "name": "Multiple Choice", "icon": "📝", "desc": "Select from options"},
        {"id": "open_ended", "name": "Open-Ended", "icon": "📄", "desc": "Write detailed answers"},
        {"id": "coding", "name": "Coding Challenges", "icon": "💻", "desc": "Write Python code"}
    ]
    
    # Create buttons for question types
    for i, qtype in enumerate(question_types):
        with qtype_cols[i]:
            # Check if this type is selected
            is_selected = qtype["id"] in st.session_state.question_types
            
            # Button label with selection indicator
            button_label = f"{qtype['icon']} {qtype['name']}"
            if is_selected:
                button_label = f"✅ {qtype['name']}"
            
            # Create a button with icon and name
            if st.button(
                button_label,
                key=f"qtype_{qtype['id']}",
                use_container_width=True,
                type="primary" if is_selected else "secondary",
                help=qtype["desc"]
            ):
                # Toggle selection
                if qtype["id"] in st.session_state.question_types:
                    if len(st.session_state.question_types) > 1:  # Prevent removing all types
                        st.session_state.question_types.remove(qtype["id"])
                else:
                    st.session_state.question_types.append(qtype["id"])
                st.rerun()
            
            # Show selection status text in addition to button styling
            if is_selected:
                st.markdown(f"<p style='color: #003B70; font-weight: bold; margin-top: 5px;'>✓ {qtype['desc']} (Selected)</p>", unsafe_allow_html=True)
            else:
                st.caption(qtype["desc"])
    
    # Additional Options
    st.markdown("<h3 style='color: #003B70; font-size: 1.4rem; margin-top: 20px;'>Additional Options</h3>", unsafe_allow_html=True)
    
    # Save progress option
    save_progress = st.checkbox("Save my progress and include this quiz in my learning statistics", value=True)
    
    # Now create the form with just the submit button
    with st.form("generate_quiz_form"):
        # Generate button with blue and white styling
        st.markdown("""
        <style>
        div[data-testid="stFormSubmitButton"] > button {
            background-color: #003B70 !important;
            color: white !important;
            border: none !important;
            padding: 0.5rem 1rem !important;
            font-weight: 600 !important;
        }
        div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: #00508F !important;
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button("Generate Practice Quiz", use_container_width=True)
        
        if submitted:
            # Get the selected topics
            selected_topics = st.session_state.selected_topics
            
            # Get the selected question types
            mc_questions = "multiple_choice" in st.session_state.question_types
            open_ended = "open_ended" in st.session_state.question_types
            coding = "coding" in st.session_state.question_types
            
            # Get the selected options
            num_questions = st.session_state.selected_question_count
            difficulty = st.session_state.selected_difficulty
            
            # Validate selections
            if not selected_topics:
                st.error("Please select at least one topic for your practice quiz.")
            elif not any([mc_questions, open_ended, coding]):
                st.error("Please select at least one question type.")
            else:
                # Combine the selected topics into a comma-separated string
                topics_str = ", ".join(selected_topics)
                
                # Show generating message with a spinner
                with st.spinner(f"Generating your practice quiz on {topics_str}..."):
                    try:
                        # Calculate question type distribution
                        selected_types = []
                        if mc_questions:
                            selected_types.append("multiple_choice")
                        if open_ended:
                            selected_types.append("open_ended")
                        if coding:
                            selected_types.append("coding")
                        
                        # Calculate number of questions per type
                        base_count = num_questions // len(selected_types)
                        remainder = num_questions % len(selected_types)
                        
                        type_counts = {}
                        for q_type in selected_types:
                            extra = 1 if remainder > 0 else 0
                            type_counts[q_type] = base_count + extra
                            remainder -= extra
                        
                        # Generate the quiz using the quiz service
                        from services.quiz_service import generate_practice_quiz
                        practice_quiz = generate_practice_quiz(
                            topic=topics_str,
                            num_questions=num_questions,
                            difficulty=difficulty,
                            question_types=selected_types,
                            type_counts=type_counts,
                            save_progress=save_progress
                        )
                        
                        if practice_quiz and practice_quiz.get("questions"):
                            # Store the generated quiz in session state
                            st.session_state.current_quiz_id = practice_quiz["id"]
                            st.session_state.questions = practice_quiz["questions"]
                            
                            # Add to available quizzes if tracking progress
                            if save_progress:
                                if "available_quizzes" not in st.session_state:
                                    st.session_state.available_quizzes = []
                                st.session_state.available_quizzes.append(practice_quiz)
                            
                            # Navigate to quiz page
                            st.session_state.page = "student_quiz"
                            st.rerun()
                        else:
                            st.error("Failed to generate quiz questions. Please try again.")
                            
                    except Exception as e:
                        st.error(f"Error creating practice quiz: {str(e)}")
    
    # Display practice history if available with improved styling
    practice_history = get_practice_history()
    
    if practice_history:
        st.markdown("""
        <div style="background-color: white; 
             border-radius: 12px; padding: 25px; 
             box-shadow: 0 4px 12px rgba(0, 59, 112, 0.1); margin: 30px 0 20px 0;
             border: 1px solid rgba(0, 59, 112, 0.1);">
            <h2 style="color: #003B70; margin-bottom: 10px; font-size: 1.6rem; font-weight: 600;">Your Practice History</h2>
            <p style="color: #4B5563; font-size: 1.05rem;">Track your progress and see how you're improving</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display practice history in a nice table with improved styling
        import pandas as pd
        
        history_df = pd.DataFrame(practice_history)
        st.dataframe(
            history_df, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Quiz": st.column_config.TextColumn("Quiz Title", width="medium"),
                "Date": st.column_config.TextColumn("Date Taken", width="small"),
                "Score": st.column_config.TextColumn("Score", width="small"),
                "Questions": st.column_config.TextColumn("Questions", width="small"),
                "Topics": st.column_config.TextColumn("Topics Covered", width="large")
            }
        )
        
        # Practice analytics with improved metrics
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_practice = len(practice_history)
            st.metric("Total Practice Quizzes", str(total_practice), delta=None, 
                    help="Total number of practice quizzes you've taken")
        
        with col2:
            # Calculate average score - handle string values
            scores = []
            for quiz in practice_history:
                score_str = quiz.get("Score", "")
                if score_str and score_str != "Not completed":
                    try:
                        # Try to extract numeric value
                        score_val = float(''.join(c for c in score_str if c.isdigit() or c == '.'))
                        scores.append(score_val)
                    except:
                        pass
            
            if scores:
                avg_score = sum(scores) / len(scores)
                st.metric("Average Score", f"{avg_score:.1f}%", delta=None,
                        help="Your average score across all practice quizzes")
            else:
                st.metric("Average Score", "N/A")
        
        with col3:
            # Calculate total questions - handle string values
            total_questions = 0
            for quiz in practice_history:
                questions_str = quiz.get("Questions", "0")
                try:
                    questions_count = int(''.join(c for c in questions_str if c.isdigit()))
                    total_questions += questions_count
                except:
                    pass
            
            st.metric("Total Questions Practiced", str(total_questions), delta=None,
                    help="Total number of questions you've practiced")
        
        with col4:
            # Calculate most practiced topic - no changes needed as this works with strings
            topics_count = {}
            for quiz in practice_history:
                quiz_topics = quiz.get("Topics", "").split(", ")
                for topic in quiz_topics:
                    if topic:
                        topics_count[topic] = topics_count.get(topic, 0) + 1
            
            if topics_count:
                most_practiced = max(topics_count.items(), key=lambda x: x[1])[0]
                st.metric("Most Practiced Topic", most_practiced, delta=None,
                        help="The topic you've practiced the most")
            else:
                st.metric("Most Practiced Topic", "N/A")

# Helper function to get practice history
def get_practice_history():
    """Get the practice quiz history for the current user"""
    try:
        # Try to get from database first
        from services.database import Database
        db = Database()
        student_id = "current_user_id"  # Replace with actual student ID
        practice_quizzes = db.get_practice_quizzes(student_id)
        
        # Format data for display
        return [
            {
                "Quiz": str(q.get("title", "Untitled Quiz")),
                "Date": str(q.get("start_time", "Unknown")),
                "Score": str(q.get("score", "Not completed")),
                "Questions": str(len(q.get("questions", []))),
                "Topics": str(q.get("title", "").replace("Practice: ", ""))
            } for q in practice_quizzes
        ]
    except:
        # If database fails, try to get from session state
        if "available_quizzes" in st.session_state:
            # Filter for practice quizzes only
            practice_quizzes = [q for q in st.session_state.available_quizzes 
                               if q.get("id", "").startswith("practice_")]
            
            # Format for display
            return [
                {
                    "Quiz": str(q.get("title", "Untitled Quiz")),
                    "Date": str(q.get("start_time", "Unknown")),
                    "Score": str(q.get("score", "Not completed")),
                    "Questions": str(len(q.get("questions", []))),
                    "Topics": str(q.get("title", "").replace("Practice: ", ""))
                } for q in practice_quizzes
            ]
        return []

if __name__ == "__main__":
    main()
