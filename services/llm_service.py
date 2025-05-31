"""
LLM service module that handles interactions with the language model.
"""
import os
import time
import json
import re
import streamlit as st
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from typing import Optional, Dict, List, Any, Union

# Load environment variables
load_dotenv()

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
def generate_content(prompt: str) -> str:
    """
    Generate content using a language model.
    This is a placeholder function that simulates LLM responses.
    
    Args:
        prompt: The input prompt for the language model
        
    Returns:
        Generated text from the language model
    """
    # In a real implementation, this would call an actual LLM API
    # For now, we'll return placeholder responses based on prompt keywords
    
    time.sleep(1)  # Simulate API delay
    
    # Extract topics from prompt for dynamic generation
    topics_str = ""
    topics_match = re.search(r'topics:\s*(.+?)\.', prompt, re.DOTALL)
    if topics_match:
        topics_str = topics_match.group(1).strip()
    
    # Split the topics string into a list
    topics = [t.strip() for t in topics_str.split(',') if t.strip()]
    if not topics:
        topics = ["machine learning"]
    
    # Check if it's for multiple-choice questions
    if "multiple-choice questions" in prompt:
        return _generate_dynamic_question_batch(topics, "multiple_choice")
    elif "open-ended questions" in prompt:
        return _generate_dynamic_question_batch(topics, "open_ended")
    elif "coding questions" in prompt:
        return _generate_dynamic_question_batch(topics, "coding")
    elif "expert Machine Learning educator" in prompt:
        # For practice quiz - extract question counts by type
        mc_count = 0
        oe_count = 0
        coding_count = 0
        
        # Search for the counts in the prompt
        mc_match = re.search(r'Generate (\d+) multiple-choice questions', prompt)
        if mc_match:
            mc_count = int(mc_match.group(1))
        
        oe_match = re.search(r'Generate (\d+) open-ended questions', prompt)
        if oe_match:
            oe_count = int(oe_match.group(1))
            
        coding_match = re.search(r'Generate (\d+) coding questions', prompt)
        if coding_match:
            coding_count = int(coding_match.group(1))
        
        # Generate a mix of questions
        return _generate_mixed_question_set(topics, mc_count, oe_count, coding_count)
    elif "Create a multiple-choice quiz" in prompt:
        return _generate_sample_quiz()
    elif "coding assignment" in prompt:
        return _generate_sample_coding_assignment()
    elif "Evaluate the following Python code" in prompt:
        return _generate_sample_code_evaluation()
    elif "Analyze the following quiz results" in prompt:
        return _generate_sample_quiz_analysis()
    else:
        return "I couldn't generate content for this prompt."

def generate_json_content(prompt: str, max_retries: int = 2) -> Union[List[Dict[str, Any]], None]:
    """
    Generate JSON content using a language model with enhanced retry logic.
    
    Args:
        prompt: The input prompt for the language model
        max_retries: Maximum number of retry attempts if JSON parsing fails
        
    Returns:
        Parsed JSON data as a list of dictionaries, or None if all attempts fail
    """
    # Extract the required number of questions from the prompt
    count_match = re.search(r'Create\s+(\d+)', prompt)
    count = int(count_match.group(1)) if count_match else 5  # Default to 5 if not specified
    
    # Extract topics from the prompt
    topics_match = re.search(r'about\s+(.+?)\s+at', prompt)
    topics = topics_match.group(1) if topics_match else "general topics"
    
    # For simulation purposes, we'll generate dynamic questions based on count
    # In a real implementation, this would make actual API calls to the LLM
    if "multiple-choice questions" in prompt:
        # Always generate 50 questions regardless of what the prompt asked for
        return _generate_dynamic_mc_questions(50, topics)
    elif "open-ended questions" in prompt:
        return _generate_dynamic_open_ended_questions(50, topics)
    elif "coding questions" in prompt:
        return _generate_dynamic_coding_questions(50, topics)
    
    # If we can't determine the type, fall back to normal processing
    
    # First attempt
    response = generate_content(prompt)
    json_data = _extract_and_parse_json(response)
    
    # If the first attempt failed, retry with more explicit instructions
    retries = 0
    while json_data is None and retries < max_retries:
        # Add more explicit instructions for JSON format
        retry_prompt = f"""
I need you to generate ONLY valid JSON and nothing else. 
No explanations, no markdown formatting, just raw JSON.

{prompt}

Remember:
1. The response must be a JSON array of objects
2. Make sure all quotes, brackets, and commas are properly placed
3. Don't include code blocks or any text outside the JSON
"""
        response = generate_content(retry_prompt)
        json_data = _extract_and_parse_json(response)
        retries += 1
    
    # Return all generated questions (don't limit to the count from the prompt)
    return json_data

def _extract_and_parse_json(text: str) -> Union[List[Dict[str, Any]], None]:
    """
    Extract JSON from text and parse it.
    
    Args:
        text: Text that may contain JSON
        
    Returns:
        Parsed JSON data, or None if parsing fails
    """
    try:
        # First try direct parsing
        return json.loads(text)
    except json.JSONDecodeError:
        # If that fails, try to extract JSON using regex
        try:
            # Look for anything that resembles a JSON array
            json_match = re.search(r'\[\s*{.*}\s*\]', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            return None
        except (json.JSONDecodeError, AttributeError):
            return None


def _generate_sample_quiz() -> str:
    """Generate a sample quiz for testing."""
    return """
Q: What is the time complexity of binary search?
A: O(n)
B: O(n log n)
C: O(log n)
D: O(1)
Correct: C

Q: Which of the following is NOT a built-in data type in Python?
A: List
B: Dictionary
C: Set
D: Tree
Correct: D

Q: What does the acronym SQL stand for?
A: Structured Query Language
B: Simple Query Language
C: Standard Question Language
D: Sequence Query Logic
Correct: A

Q: Which sorting algorithm has the best average time complexity?
A: Bubble Sort
B: Quick Sort
C: Insertion Sort
D: Selection Sort
Correct: B

Q: What is the result of 2**3 in Python?
A: 6
B: 5
C: 8
D: 9
Correct: C
"""


def _generate_sample_coding_assignment() -> str:
    """Generate a sample coding assignment for testing."""
    return """
TITLE: Palindrome Checker Function

BACKGROUND:
A palindrome is a word, phrase, number, or other sequence of characters that reads the same forward and backward, ignoring spaces, punctuation, and capitalization. Palindromes are interesting in both linguistics and computer science as they provide examples of pattern recognition.

REQUIREMENTS:
Create a Python function called `is_palindrome` that:
1. Takes a string as input
2. Returns True if the string is a palindrome, and False otherwise
3. Ignores spaces, punctuation, and capitalization
4. Handles empty strings and single characters (both should return True)

EXPECTED_OUTPUT:
```
is_palindrome("racecar") → True
is_palindrome("A man, a plan, a canal: Panama") → True
is_palindrome("hello") → False
is_palindrome("") → True
is_palindrome("a") → True
```

HINTS:
- You may want to remove all non-alphanumeric characters before checking
- Python's string methods like `lower()` and `isalnum()` can be helpful
- Consider comparing the cleaned string with its reverse

EVALUATION_CRITERIA:
1. Correctness: The function should return the expected results for all test cases
2. Efficiency: The solution should be efficient with appropriate time complexity
3. Code quality: The code should be clean, well-commented, and follow Python conventions
4. Edge cases: The solution should handle edge cases like empty strings and single characters

CODE_TEMPLATE:
```python
def is_palindrome(s):
    # TODO: Implement palindrome checking function
    # Remember to ignore spaces, punctuation, and capitalization
    pass

# Test cases
test_cases = [
    "racecar",
    "A man, a plan, a canal: Panama",
    "hello",
    "",
    "a"
]

for test in test_cases:
    print(f'"{test}" → {is_palindrome(test)}')
```
"""


def _generate_sample_code_evaluation() -> str:
    """Generate a sample code evaluation for testing."""
    return """
VERDICT: Partially

ANALYSIS:
The code implements a palindrome checking function that correctly handles basic palindromes like "racecar". The approach used is to compare the string with its reversed version, which is a common and valid strategy for checking palindromes.

However, there are some issues with the implementation:

1. The function doesn't ignore spaces, punctuation, and capitalization as required. Currently, "A man, a plan, a canal: Panama" would return False even though it's a palindrome when ignoring spaces, punctuation, and case.

2. The function does correctly handle edge cases like empty strings and single characters, returning True for both.

3. The code is clean and easy to understand, but lacks comments explaining the logic.

IMPROVEMENTS:
1. Add preprocessing to remove non-alphanumeric characters and convert to lowercase:
   ```python
   def is_palindrome(s):
       # Convert to lowercase and remove non-alphanumeric characters
       clean_s = ''.join(char.lower() for char in s if char.isalnum())
       # Check if the string equals its reverse
       return clean_s == clean_s[::-1]
   ```

2. Add comments to explain the logic and preprocessing steps.

3. Consider adding more test cases to verify the function works with strings containing punctuation, spaces, and mixed case.

4. For very long strings, you could optimize by checking characters from both ends simultaneously instead of creating a reversed string, though this is a minor optimization for most use cases.
"""


def _generate_sample_quiz_analysis() -> str:
    """Generate a sample quiz analysis for testing."""
    return """
UNDERSTANDING: The student demonstrates a basic understanding of the tested concepts, achieving a score of 60%. While they've grasped some fundamental principles, there are significant gaps in their knowledge, particularly in more advanced or nuanced aspects of the subject matter.

STRENGTHS: The student showed good understanding of basic Python syntax and data types, correctly identifying that a Tree is not a built-in data type in Python. They also correctly identified the time complexity of binary search as O(log n), suggesting a solid grasp of algorithm complexity concepts.

KNOWLEDGE_GAPS: The student appears to struggle with SQL terminology, incorrectly identifying what SQL stands for. Additionally, they seem to lack understanding of sorting algorithms' relative performance characteristics, as they incorrectly identified the sorting algorithm with the best average time complexity. The student also had difficulty with basic arithmetic operations in Python, specifically exponentiation.

RECOMMENDATIONS: To improve understanding, the student should:
1. Review basic Python operators, particularly the exponentiation operator.
2. Study database fundamentals, focusing on SQL terminology and concepts.
3. Dedicate time to learning sorting algorithms, comparing their time complexities and use cases.
4. Practice implementing different algorithms and analyze their performance to better understand their characteristics.
5. Use flashcards for terminology and core concepts to reinforce memory.
"""

# Sample JSON responses for testing
def _generate_sample_mc_questions() -> str:
    """Generate sample multiple choice questions in JSON format."""
    return """[
  {
    "type": "multiple_choice",
    "question": "What is the time complexity of binary search?",
    "options": ["O(n)", "O(n log n)", "O(log n)", "O(1)"],
    "correct_index": 2
  },
  {
    "type": "multiple_choice",
    "question": "Which of the following is NOT a built-in data type in Python?",
    "options": ["List", "Dictionary", "Set", "Tree"],
    "correct_index": 3
  },
  {
    "type": "multiple_choice",
    "question": "What does the acronym SQL stand for?",
    "options": ["Structured Query Language", "Simple Query Language", "Standard Question Language", "Sequence Query Logic"],
    "correct_index": 0
  },
  {
    "type": "multiple_choice",
    "question": "Which sorting algorithm has the best average time complexity?",
    "options": ["Bubble Sort", "Quick Sort", "Insertion Sort", "Selection Sort"],
    "correct_index": 1
  },
  {
    "type": "multiple_choice",
    "question": "What is the result of 2**3 in Python?",
    "options": ["6", "5", "8", "9"],
    "correct_index": 2
  }
]"""

def _generate_sample_open_ended_questions() -> str:
    """Generate sample open-ended questions in JSON format."""
    return """[
  {
    "type": "open_ended",
    "question": "Explain the difference between a list and a tuple in Python.",
    "expected_answer": "Lists are mutable, which means they can be changed after creation. Tuples are immutable, meaning they cannot be modified after creation. Lists use square brackets [] while tuples use parentheses ()."
  },
  {
    "type": "open_ended",
    "question": "Describe the principles of object-oriented programming.",
    "expected_answer": "Object-oriented programming is based on four main principles: 1) Encapsulation: bundling data and methods that work on that data. 2) Inheritance: ability to create new classes based on existing ones. 3) Polymorphism: ability to use a common interface for multiple forms. 4) Abstraction: hiding complex implementation details."
  },
  {
    "type": "open_ended",
    "question": "Explain the concept of recursion in programming and provide a simple example.",
    "expected_answer": "Recursion is a technique where a function calls itself to solve a problem. It requires a base case to prevent infinite recursion. Example: A factorial function where factorial(n) = n * factorial(n-1) and factorial(0) = 1."
  }
]"""

def _generate_sample_coding_questions() -> str:
    """Generate sample coding questions in JSON format."""
    return """[
  {
    "type": "coding",
    "question": "Write a function to find the factorial of a number.",
    "starter_code": "def factorial(n):\\n    # Your code here\\n    pass",
    "test_cases": "factorial(5) should return 120\\nfactorial(0) should return 1"
  },
  {
    "type": "coding",
    "question": "Write a function to check if a string is a palindrome.",
    "starter_code": "def is_palindrome(s):\\n    # Your code here\\n    pass",
    "test_cases": "is_palindrome('racecar') should return True\\nis_palindrome('hello') should return False"
  },
  {
    "type": "coding",
    "question": "Write a function to find the nth Fibonacci number.",
    "starter_code": "def fibonacci(n):\\n    # Your code here\\n    pass",
    "test_cases": "fibonacci(0) should return 0\\nfibonacci(1) should return 1\\nfibonacci(6) should return 8"
  }
]"""

# Dynamic question generators
def get_available_topics() -> Dict[str, List[str]]:
    """Return a dictionary of available topics and their descriptions."""
    return {
        "Python Basics": [],
        "Data Structures": [],
        "Functions & Modules": [],
        "Object-Oriented Programming": [],
        "Advanced Python": []
    }

# Define topic_questions dictionary before the function that uses it
topic_questions = {
    "clustering": [
        {
            "type": "multiple_choice",
            "question": "Which of the following algorithms is NOT a clustering algorithm?",
            "options": [
                "K-means", 
                "DBSCAN", 
                "Random Forest", 
                "Hierarchical Clustering"
            ],
            "correct_index": 2
        },
        {
            "type": "multiple_choice",
            "question": "What is the primary objective of K-means clustering?",
            "options": [
                "To minimize the sum of squared distances between data points and their nearest cluster centroid",
                "To maximize the distance between clusters",
                "To create a decision boundary between classes",
                "To identify outliers in the dataset"
            ],
            "correct_index": 0
        },
        {
            "type": "multiple_choice",
            "question": "In hierarchical clustering, what does the dendrogram represent?",
            "options": [
                "The order in which clusters are formed or split",
                "The distribution of data points",
                "The correlation between features",
                "The optimal number of clusters"
            ],
            "correct_index": 0
        },
        {
            "type": "multiple_choice",
            "question": "What is the silhouette coefficient used for in clustering?",
            "options": [
                "Evaluating clustering quality and determining optimal number of clusters",
                "Initializing cluster centroids",
                "Reducing dimensionality of the data",
                "Accelerating the clustering algorithm"
            ],
            "correct_index": 0
        },
        {
            "type": "multiple_choice",
            "question": "Which clustering algorithm is most effective at identifying clusters of arbitrary shapes?",
            "options": [
                "DBSCAN",
                "K-means",
                "K-medoids",
                "Gaussian Mixture Models"
            ],
            "correct_index": 0
        },
        {
            "type": "multiple_choice",
            "question": "What problem does the 'elbow method' help solve in K-means clustering?",
            "options": [
                "Determining the optimal number of clusters",
                "Handling missing values in the dataset",
                "Initializing cluster centroids",
                "Identifying outliers in the dataset"
            ],
            "correct_index": 0
        },
        {
            "type": "multiple_choice",
            "question": "What is a key limitation of K-means clustering?",
            "options": [
                "It struggles with non-spherical clusters",
                "It cannot work with large datasets",
                "It requires labeled data",
                "It can only use categorical features"
            ],
            "correct_index": 0
        },
        {
            "type": "multiple_choice",
            "question": "Which of the following is a density-based clustering algorithm?",
            "options": [
                "DBSCAN",
                "K-means",
                "K-medoids",
                "Expectation-Maximization"
            ],
            "correct_index": 0
        },
        {
            "type": "multiple_choice",
            "question": "What does the 'k' in k-means clustering represent?",
            "options": [
                "The number of clusters to create",
                "The number of iterations to run",
                "The dimensionality of the data",
                "The minimum number of points required to form a cluster"
            ],
            "correct_index": 0
        },
        {
            "type": "multiple_choice",
            "question": "In DBSCAN clustering, what does the parameter 'eps' represent?",
            "options": [
                "The maximum distance between two samples for them to be considered neighbors",
                "The number of clusters to form",
                "The minimum number of points required to form a cluster",
                "The maximum number of iterations"
            ],
            "correct_index": 0
        }
    ],
    "classification": [
        {
            "type": "multiple_choice",
            "question": "Which of the following is NOT a classification algorithm?",
            "options": [
                "Logistic Regression",
                "Random Forest",
                "K-means",
                "Support Vector Machine"
            ],
            "correct_index": 2
        },
        {
            "type": "multiple_choice",
            "question": "What metric is most appropriate for evaluating a highly imbalanced classification problem?",
            "options": [
                "F1 Score",
                "Accuracy",
                "Mean Squared Error",
                "R-squared"
            ],
            "correct_index": 0
        }
    ],
    "regression": [
        {
            "type": "multiple_choice",
            "question": "Which of the following metrics is NOT suitable for evaluating regression models?",
            "options": [
                "Mean Squared Error (MSE)",
                "Root Mean Squared Error (RMSE)",
                "F1 Score",
                "R-squared"
            ],
            "correct_index": 2
        },
        {
            "type": "multiple_choice",
            "question": "What is the purpose of regularization in regression models?",
            "options": [
                "To prevent overfitting by penalizing large coefficients",
                "To increase model complexity",
                "To speed up model training",
                "To normalize the input features"
            ],
            "correct_index": 0
        }
    ],
    "neural networks": [
        {
            "type": "multiple_choice",
            "question": "Which activation function is commonly used in the output layer for binary classification problems?",
            "options": [
                "Sigmoid",
                "ReLU",
                "Tanh",
                "Softmax"
            ],
            "correct_index": 0
        },
        {
            "type": "multiple_choice",
            "question": "What is a key advantage of using the ReLU activation function?",
            "options": [
                "It helps mitigate the vanishing gradient problem",
                "It ensures all neuron outputs are between 0 and 1",
                "It provides probabilistic outputs",
                "It guarantees model convergence"
            ],
            "correct_index": 0
        }
    ],
    "data preprocessing": [
        {
            "type": "multiple_choice",
            "question": "What is the main purpose of feature scaling?",
            "options": [
                "To ensure all features contribute equally to the model",
                "To reduce the number of features",
                "To handle missing values",
                "To remove outliers"
            ],
            "correct_index": 0
        }
    ],
    "feature engineering": [
        {
            "type": "multiple_choice",
            "question": "Which of the following is NOT a common feature engineering technique?",
            "options": [
                "Model training",
                "One-hot encoding",
                "Feature interaction",
                "Polynomial features"
            ],
            "correct_index": 0
        }
    ],
    "dimensionality reduction": [
        {
            "type": "multiple_choice",
            "question": "What is the main advantage of using PCA for dimensionality reduction?",
            "options": [
                "It preserves the maximum variance in the data",
                "It works better with categorical data",
                "It is faster than other methods",
                "It can handle missing values"
            ],
            "correct_index": 0
        }
    ],
    "computer vision": [
        {
            "type": "multiple_choice",
            "question": "What is the purpose of convolutional layers in CNN?",
            "options": [
                "To extract spatial features from images",
                "To reduce image size",
                "To add color to images",
                "To compress image data"
            ],
            "correct_index": 0
        }
    ],
    "natural language processing": [
        {
            "type": "multiple_choice",
            "question": "What is the main purpose of word embeddings?",
            "options": [
                "To represent words as dense vectors that capture semantic meaning",
                "To compress text data",
                "To remove stop words",
                "To count word frequencies"
            ],
            "correct_index": 0
        }
    ],
    "statistical analysis": [
        {
            "type": "multiple_choice",
            "question": "What is the purpose of hypothesis testing?",
            "options": [
                "To make inferences about population parameters",
                "To visualize data distributions",
                "To clean data",
                "To reduce dimensionality"
            ],
            "correct_index": 0
        }
    ],
    "data visualization": [
        {
            "type": "multiple_choice",
            "question": "Which visualization is most appropriate for showing the relationship between two continuous variables?",
            "options": [
                "Scatter plot",
                "Bar chart",
                "Pie chart",
                "Histogram"
            ],
            "correct_index": 0
        }
    ],
    "time series analysis": [
        {
            "type": "multiple_choice",
            "question": "What is the main purpose of differencing in time series analysis?",
            "options": [
                "To make the time series stationary",
                "To remove outliers",
                "To handle missing values",
                "To reduce noise"
            ],
            "correct_index": 0
        }
    ],
    "distributed computing": [
        {
            "type": "multiple_choice",
            "question": "What is the main advantage of using MapReduce?",
            "options": [
                "It enables parallel processing of large datasets",
                "It reduces memory usage",
                "It improves data quality",
                "It handles missing values"
            ],
            "correct_index": 0
        }
    ],
    "data warehousing": [
        {
            "type": "multiple_choice",
            "question": "What is the main purpose of a data warehouse?",
            "options": [
                "To store and analyze historical data for decision making",
                "To process real-time data",
                "To clean raw data",
                "To visualize data"
            ],
            "correct_index": 0
        }
    ],
    "stream processing": [
        {
            "type": "multiple_choice",
            "question": "What is the main challenge in stream processing?",
            "options": [
                "Handling data that arrives continuously in real-time",
                "Storing large amounts of data",
                "Cleaning data",
                "Visualizing data"
            ],
            "correct_index": 0
        }
    ],
    "data lakes": [
        {
            "type": "multiple_choice",
            "question": "What is the main advantage of a data lake over a data warehouse?",
            "options": [
                "It can store raw data in its native format",
                "It is faster for querying",
                "It requires less storage",
                "It is easier to maintain"
            ],
            "correct_index": 0
        }
    ]
}

def _generate_dynamic_mc_questions(count: int, selected_topics: List[str], prompt_prefix: str = None, difficulty: str = "Medium") -> List[Dict[str, Any]]:
    """
    Generate dynamic multiple-choice questions based on the selected topics.
    
    Args:
        count: Number of questions to generate
        selected_topics: List of topics to generate questions for
        prompt_prefix: Optional prefix to add to the prompt for uniqueness
        difficulty: Difficulty level (Easy, Medium, Hard)
        
    Returns:
        List of question dictionaries
    """
    # Ensure we have topics to work with
    if not selected_topics:
        selected_topics = ["machine learning"]
    
    # Import random, time, hashlib and uuid for generating true variety
    import random
    import time
    import hashlib
    import uuid
    
    # Generate a unique identifier for this batch of questions
    batch_id = str(uuid.uuid4())
    timestamp = int(time.time() * 1000)
    
    # Create a seed that varies with each call
    seed_str = f"{batch_id}_{timestamp}_{prompt_prefix or ''}"
    seed_hash = hashlib.md5(seed_str.encode()).hexdigest()
    random.seed(int(seed_hash, 16) % (2**32))
    
    # Create a robust set of question templates for different patterns
    question_templates = [
        "What is a key concept in {difficulty} {topic}?",
        "Which of the following best describes {difficulty} {topic}?",
        "In {difficulty} {topic}, which approach is most effective for solving {problem}?",
        "What distinguishes {topic} from other {category} approaches at a {difficulty} level?",
        "Which technology is most commonly used with {difficulty} {topic} implementations?",
        "What is a primary challenge when implementing {difficulty} {topic}?",
        "Which of the following is NOT a feature of {difficulty} {topic}?",
        "When working with {difficulty} {topic}, what is the recommended best practice?",
        "How does {difficulty} {topic} impact the development of {related_area}?",
        "Which statement about {difficulty} {topic} is correct?",
        "What is the main advantage of using {difficulty} {topic} over traditional methods?",
        "In the context of {difficulty} {topic}, what does the term '{terminology}' refer to?",
        "Which algorithm is most suitable for {topic} problems with {constraint}?",
        "What is the time complexity of {algorithm} when applied to {topic}?",
        "How does changing the {parameter} affect the performance of {topic} models?",
        "Which of these metrics is MOST appropriate for evaluating {topic} models?",
        "What is the relationship between {concept1} and {concept2} in {topic}?",
        "When implementing {topic}, which of these approaches provides the best {quality}?",
        "What is a common pitfall when applying {topic} to {application_area}?",
        "Which tool is best suited for {task} in {topic} workflows?"
    ]
    
    # Sample problems, categories, technologies, etc. for template filling
    problems = ["classification", "regression", "clustering", "anomaly detection", 
               "dimensionality reduction", "feature selection", "optimization",
               "data preprocessing", "model evaluation", "hyperparameter tuning"]
               
    categories = ["supervised learning", "unsupervised learning", "semi-supervised learning",
                 "reinforcement learning", "deep learning", "statistical methods",
                 "probabilistic approaches", "optimization techniques"]
                 
    technologies = ["TensorFlow", "PyTorch", "scikit-learn", "Keras", "XGBoost",
                   "LightGBM", "NLTK", "spaCy", "OpenCV", "Pandas", "NumPy"]
                   
    challenges = ["overfitting", "underfitting", "data scarcity", "class imbalance",
                 "computational complexity", "interpretability", "feature engineering",
                 "hyperparameter optimization", "model deployment", "concept drift"]
                 
    best_practices = ["cross-validation", "feature normalization", "regularization",
                     "ensemble methods", "data augmentation", "transfer learning",
                     "early stopping", "batch normalization", "gradient clipping"]
                     
    related_areas = ["computer vision", "natural language processing", "speech recognition",
                    "recommendation systems", "robotics", "autonomous systems",
                    "medical diagnosis", "financial forecasting", "fraud detection"]
                    
    algorithms = ["k-means", "random forest", "support vector machines", "neural networks",
                 "gradient boosting", "k-nearest neighbors", "decision trees",
                 "linear regression", "logistic regression", "naive Bayes"]
                 
    parameters = ["learning rate", "batch size", "regularization strength", "tree depth",
                 "number of hidden layers", "activation function", "dropout rate",
                 "kernel function", "number of clusters", "embedding dimension"]
                 
    metrics = ["accuracy", "precision", "recall", "F1 score", "AUC-ROC", "mean squared error",
              "R-squared", "log loss", "silhouette score", "perplexity"]
              
    concepts = ["bias-variance tradeoff", "generalization", "backpropagation", "gradient descent",
               "feature importance", "dimensionality reduction", "transfer learning",
               "ensemble learning", "data augmentation", "model calibration"]
               
    qualities = ["scalability", "robustness", "interpretability", "efficiency",
                "accuracy", "generalization", "convergence speed", "memory usage"]
                
    application_areas = ["healthcare", "finance", "autonomous vehicles", "image recognition",
                        "natural language understanding", "recommendation systems",
                        "fraud detection", "predictive maintenance", "genomics"]
                        
    tasks = ["data cleaning", "feature engineering", "model selection", "hyperparameter tuning",
            "visualization", "deployment", "monitoring", "A/B testing", "ensemble creation"]
            
    terminologies = ["backpropagation", "gradient descent", "regularization", "attention mechanism",
                    "embedding", "transfer learning", "batch normalization", "ensemble",
                    "cross-validation", "overfitting", "hyperparameter"]
                    
    constraints = ["limited training data", "high-dimensional features", "real-time requirements",
                  "interpretability needs", "memory constraints", "computational efficiency"]
    
    # Generate a varied set of questions
    all_questions = []
    
    # Ensure we're using all the selected topics
    topics_to_use = list(selected_topics) * (count // len(selected_topics) + 1)
    random.shuffle(topics_to_use)
    
    # Create a bank of ML-related options for different topics
    option_banks = {
        # General ML options
        "machine learning": [
            "Using supervised learning algorithms",
            "Applying unsupervised clustering techniques",
            "Implementing deep neural networks",
            "Leveraging ensemble methods for improved accuracy",
            "Optimizing model hyperparameters automatically",
            "Preprocessing data with normalization and scaling",
            "Creating synthetic features through feature engineering",
            "Building end-to-end pipelines for model deployment",
            "Applying transfer learning from pre-trained models",
            "Implementing cross-validation strategies",
            "Using regularization to prevent overfitting",
            "Creating ensemble models from diverse base learners",
            "Detecting anomalies in high-dimensional data",
            "Extracting latent features through dimensionality reduction",
            "Optimizing objective functions with gradient descent",
            "Validating models with appropriate evaluation metrics",
            "Addressing class imbalance with sampling techniques",
            "Handling missing data through imputation strategies",
            "Selecting relevant features to improve model performance",
            "Implementing early stopping to prevent overfitting"
        ],
        # Neural networks options
        "neural networks": [
            "Using backpropagation to compute gradients",
            "Applying dropout for regularization",
            "Implementing batch normalization",
            "Using convolutional layers for spatial data",
            "Applying recurrent architectures for sequential data",
            "Leveraging attention mechanisms",
            "Using residual connections to train deeper networks",
            "Implementing autoencoder architectures",
            "Applying transfer learning from pre-trained networks",
            "Using different activation functions",
            "Optimizing with adaptive learning rate algorithms",
            "Implementing generative adversarial networks",
            "Using transformer architectures for sequence data",
            "Applying graph neural networks for relational data",
            "Implementing reinforcement learning with neural networks",
            "Using capsule networks for better spatial relationships",
            "Applying neuroevolution for architecture search",
            "Implementing self-supervised learning techniques",
            "Using neural architecture search",
            "Applying quantization for efficient deployment"
        ],
        # Data processing options
        "data preprocessing": [
            "Normalizing numeric features",
            "Encoding categorical variables",
            "Handling missing values through imputation",
            "Removing outliers with statistical methods",
            "Applying feature scaling techniques",
            "Using principal component analysis for dimensionality reduction",
            "Handling imbalanced datasets with resampling",
            "Binning continuous variables",
            "Creating polynomial features",
            "Implementing time series decomposition",
            "Applying text tokenization and vectorization",
            "Using feature hashing to reduce dimensionality",
            "Implementing data augmentation techniques",
            "Applying image preprocessing operations",
            "Creating interaction features between variables",
            "Using domain-specific transformations",
            "Implementing log transformations for skewed distributions",
            "Applying smoothing techniques for noisy data",
            "Creating domain-specific features based on expertise",
            "Implementing pipeline-based preprocessing workflows"
        ]
    }
    
    # Generate diverse questions
    for i in range(count):
        # Use a new random seed for each question to ensure diversity
        question_seed = f"{batch_id}_{i}_{int(time.time() * 1000) % 10000}"
        question_hash = hashlib.md5(question_seed.encode()).hexdigest()
        random.seed(int(question_hash, 16) % (2**32))
        
        # Select a topic for this question
        topic = topics_to_use[i % len(topics_to_use)]
        
        # Modify difficulty for the template
        difficulty_level = ""
        if difficulty == "Easy":
            difficulty_level = "basic"
        elif difficulty == "Medium":
            difficulty_level = "intermediate" 
        elif difficulty == "Hard":
            difficulty_level = "advanced"
            
        # Choose a template and fill it with appropriate values
        template = random.choice(question_templates)
        
        # Prepare placeholders for formatting
        placeholders = {
            "difficulty": difficulty_level,
            "topic": topic,
            "problem": random.choice(problems),
            "category": random.choice(categories),
            "terminology": random.choice(terminologies),
            "related_area": random.choice(related_areas),
            "algorithm": random.choice(algorithms),
            "constraint": random.choice(constraints),
            "parameter": random.choice(parameters),
            "concept1": random.choice(concepts)
        }
        
        # Add concept2 ensuring it's different from concept1
        placeholders["concept2"] = random.choice([c for c in concepts if c != placeholders["concept1"]])
        
        # Add the remaining placeholders
        placeholders["quality"] = random.choice(qualities)
        placeholders["application_area"] = random.choice(application_areas)
        placeholders["task"] = random.choice(tasks)
        
        # Format the question template
        question_text = template
        for key, value in placeholders.items():
            if "{" + key + "}" in question_text:
                question_text = question_text.replace("{" + key + "}", value)
        
        # Generate options - prefer to use option bank if available for the topic
        generic_topic = next((t for t in option_banks.keys() if t in topic.lower()), "machine learning")
        
        # Get a set of options from the bank
        available_options = option_banks.get(generic_topic, option_banks["machine learning"])
        
        # Ensure we select 4 distinct options
        if len(available_options) >= 4:
            options = random.sample(available_options, 4)
        else:
            # Create more meaningful options with real content, not just placeholders
            if "classification" in topic.lower():
                options = [
                    f"Use supervised learning algorithms to classify data",
                    f"Apply decision trees with appropriate feature selection", 
                    f"Implement logistic regression with regularization",
                    f"Use support vector machines with suitable kernels"
                ]
            elif "regression" in topic.lower():
                options = [
                    f"Apply linear regression with appropriate feature scaling",
                    f"Use polynomial regression for non-linear relationships",
                    f"Implement regularization techniques to prevent overfitting",
                    f"Use gradient descent for model optimization"
                ]
            elif "neural" in topic.lower():
                options = [
                    f"Design appropriate network architecture for the problem",
                    f"Apply proper activation functions per layer",
                    f"Implement backpropagation with suitable optimizers",
                    f"Use regularization techniques to prevent overfitting"
                ]
            else:
                # Create more meaningful generic options
                options = [
                    f"Apply established algorithms suitable for the task",
                    f"Implement preprocessing techniques to improve data quality",
                    f"Use appropriate validation methods to evaluate performance",
                    f"Optimize parameters to balance bias and variance"
                ]
        
        # Randomly select the correct answer
        correct_index = random.randint(0, 3)
        
        # Create the question dictionary
        question = {
            "type": "multiple_choice",
            "question": question_text,
            "options": options,
            "correct_index": correct_index,
            "topic": topic,
            "difficulty": difficulty,
            "id": question_hash[:8]  # Add a unique ID for tracking
        }
        
        all_questions.append(question)
    
    # Add timestamp uniqueness by shuffling again with current time
    time_seed = int(time.time() * 1000)
    random.seed(time_seed)
    random.shuffle(all_questions)
    
    return all_questions

def _generate_dynamic_open_ended_questions(count: int, topics: str) -> List[Dict[str, Any]]:
    """Generate dynamic open-ended questions based on count and topics."""
    # Expanded set of diverse open-ended questions
    base_questions = [
        {
            "type": "open_ended",
            "question": f"Explain the key principles of {topics} and how they relate to modern software development.",
            "expected_answer": f"Key principles of {topics} include abstraction, modularity, and scalability. In modern software development, these principles enable faster development cycles, better maintainability, and easier collaboration among teams."
        },
        {
            "type": "open_ended",
            "question": f"Compare and contrast different approaches to implementing {topics} in real-world applications.",
            "expected_answer": f"Different approaches to {topics} implementation include object-oriented, functional, and procedural paradigms. Each has strengths: OO excels at modeling complex systems, functional promotes immutability and pure functions, while procedural offers simplicity for straightforward tasks."
        },
        {
            "type": "open_ended",
            "question": f"What are the ethical considerations when applying {topics} in critical systems?",
            "expected_answer": f"Ethical considerations in {topics} include privacy, security, bias in algorithms, transparency of operation, and accessibility. In critical systems, these concerns are amplified as failures can have serious consequences for users and society."
        },
        {
            "type": "open_ended",
            "question": f"How has the field of {topics} evolved over the past decade, and what future trends do you anticipate?",
            "expected_answer": f"The field of {topics} has evolved through increased automation, cloud integration, and AI capabilities. Future trends likely include more sophisticated AI integration, edge computing applications, and stronger emphasis on security and privacy by design."
        },
        {
            "type": "open_ended",
            "question": f"Describe a situation where {topics} would be preferred over alternative approaches, with justification.",
            "expected_answer": f"{topics} would be preferred in scenarios requiring high flexibility and adaptability, such as rapidly evolving business requirements. The justification lies in its modularity and ability to accommodate changes without extensive reworking of the entire system."
        },
        # Adding more diverse open-ended questions
        {
            "type": "open_ended",
            "question": f"Analyze a recent breakthrough in {topics} and discuss its potential impact on the industry.",
            "expected_answer": f"A comprehensive analysis would identify a significant innovation in {topics}, explain its technical foundations, discuss how it improves upon previous approaches, and evaluate its potential to transform industry practices or enable new capabilities."
        },
        {
            "type": "open_ended",
            "question": f"Design a system architecture that incorporates {topics} to solve a complex business problem.",
            "expected_answer": f"A strong answer would outline a system architecture with clear components, explain how {topics} is integrated, justify design decisions, address scalability and maintenance concerns, and identify potential challenges in implementation."
        },
        {
            "type": "open_ended",
            "question": f"If you were mentoring a junior developer on {topics}, what would be your top three pieces of advice?",
            "expected_answer": f"Key advice might include: 1) Start with fundamentals before tackling complex implementations, 2) Practice building small projects that demonstrate core principles, 3) Study existing codebases to understand real-world applications of {topics}."
        },
        {
            "type": "open_ended",
            "question": f"How would you approach debugging a complex issue in a {topics} environment?",
            "expected_answer": f"An effective debugging approach would include systematic steps like: reproducing the issue consistently, isolating the problem through elimination, using appropriate debugging tools, examining logs and stack traces, and implementing a solution with regression tests to prevent recurrence."
        },
        {
            "type": "open_ended",
            "question": f"Discuss the tradeoffs between performance and maintainability in {topics}.",
            "expected_answer": f"This discussion should cover how optimization techniques in {topics} often increase code complexity, the importance of measuring performance before optimizing, strategies for balancing readable code with efficient operation, and when to prioritize one aspect over the other based on project requirements."
        },
        {
            "type": "open_ended",
            "question": f"Create a comprehensive test strategy for a {topics} project.",
            "expected_answer": f"A comprehensive test strategy would include unit tests for individual components, integration tests for interactions between modules, performance testing to ensure scalability, security testing to identify vulnerabilities, and automated regression testing to maintain stability during development."
        },
        {
            "type": "open_ended",
            "question": f"Evaluate the role of documentation in {topics} projects.",
            "expected_answer": f"Documentation serves multiple critical purposes in {topics} projects: onboarding new team members, preserving institutional knowledge, facilitating maintenance, enabling collaboration, and providing guidance for API consumers. Effective documentation balances comprehensiveness with clarity and is maintained alongside code."
        }
    ]
    
    # Question templates for generating variations
    question_templates = [
        "How would you implement {concept} in {topics} to maximize {quality}?",
        "What are the primary challenges when scaling {topics} for {environment} environments?",
        "Evaluate the impact of {concept} on the development lifecycle of {topics} projects.",
        "How might {topics} evolve in response to changes in {related_field}?",
        "Design a strategy to migrate from {old_approach} to {topics} while minimizing disruption.",
        "Compare how different industries apply {topics} to solve similar problems.",
        "Critique the current best practices in {topics} and propose improvements.",
        "How would you educate non-technical stakeholders about the importance of {topics}?",
        "What metrics would you use to evaluate the success of a {topics} implementation?",
        "Describe how you would integrate {topics} with {complementary_technology}."
    ]
    
    # Related concepts and fields for template questions
    concepts = ["continuous integration", "automated testing", "code reviews", "pair programming", 
                "agile methodologies", "DevOps practices", "cloud deployment", "serverless architecture",
                "microservices", "monolithic architecture", "containerization", "orchestration",
                "infrastructure as code", "configuration management", "version control", "release management"]
    
    qualities = ["scalability", "reliability", "maintainability", "security", "performance", 
                "user experience", "cost efficiency", "cross-platform compatibility"]
    
    environments = ["cloud", "enterprise", "mobile", "edge computing", "IoT", "high-performance computing"]
    
    related_fields = ["artificial intelligence", "machine learning", "blockchain", "internet of things", 
                      "quantum computing", "augmented reality", "data science", "cybersecurity"]
    
    old_approaches = ["legacy systems", "monolithic architecture", "manual testing", 
                     "waterfall methodology", "on-premises infrastructure"]
    
    complementary_technologies = ["databases", "front-end frameworks", "mobile platforms", 
                                 "analytics tools", "authentication systems", "messaging queues"]
    
    # If we have fewer base questions than requested, generate variations
    import random
    
    while len(base_questions) < count:
        # Choose a strategy for generating new questions
        strategy = random.choice(["template", "modify_existing", "combine_concepts"])
        
        if strategy == "template":
            # Create a new question from template
            template = random.choice(question_templates)
            
            # Fill in the template with random concepts
            question_text = template.format(
                concept=random.choice(concepts),
                topics=topics,
                quality=random.choice(qualities),
                environment=random.choice(environments),
                related_field=random.choice(related_fields),
                old_approach=random.choice(old_approaches),
                complementary_technology=random.choice(complementary_technologies)
            )
            
            new_question = {
                "type": "open_ended",
                "question": question_text,
                "expected_answer": f"A thorough response would address key aspects of {topics} including technical implementation, challenges, benefits, and potential drawbacks."
            }
            
            base_questions.append(new_question)
            
        elif strategy == "modify_existing" and base_questions:
            # Take an existing question and modify it
            idx = random.randint(0, len(base_questions) - 1)
            original = base_questions[idx]
            
            # Create specific modifications
            perspectives = ["from a security perspective", "from a performance perspective", 
                           "from a business value perspective", "from a user experience perspective",
                           "considering global deployment challenges", "in resource-constrained environments"]
            
            prefixes = ["Critically analyze:", "From your experience:", "As a technical lead:", 
                       "Using current industry standards:", "In an ideal scenario:"]
            
            # Apply modifications
            if random.random() < 0.5:
                # Add a perspective
                perspective = random.choice(perspectives)
                modified_question = f"{original['question']} Analyze {perspective}."
            else:
                # Add a prefix
                prefix = random.choice(prefixes)
                modified_question = f"{prefix} {original['question']}"
            
            new_question = {
                "type": "open_ended",
                "question": modified_question,
                "expected_answer": original["expected_answer"]
            }
            
            base_questions.append(new_question)
            
        else:  # combine_concepts
            # Combine two concepts into a new question
            concept1 = random.choice(concepts)
            concept2 = random.choice([c for c in concepts if c != concept1])
            
            combined_question = {
                "type": "open_ended",
                "question": f"Discuss how {concept1} and {concept2} can be integrated in {topics} projects to enhance overall quality.",
                "expected_answer": f"An effective response would explain the relationship between {concept1} and {concept2}, identify integration approaches, discuss potential synergies, and address implementation challenges in the context of {topics}."
            }
            
            base_questions.append(combined_question)
    
    # Shuffle and return only the requested number
    random.shuffle(base_questions)
    return base_questions[:count]

def _generate_dynamic_coding_questions(count: int, topics: str) -> List[Dict[str, Any]]:
    """Generate dynamic coding questions based on count and topics."""
    # Expanded base set of diverse coding questions
    base_questions = [
        {
            "type": "coding",
            "question": f"Write a function to find the factorial of a number, a common operation in {topics}.",
            "starter_code": "def factorial(n):\n    # Your code here\n    pass",
            "test_cases": "factorial(5) should return 120\nfactorial(0) should return 1"
        },
        {
            "type": "coding",
            "question": f"Implement a function to check if a string is a palindrome, which is useful in {topics} text processing.",
            "starter_code": "def is_palindrome(s):\n    # Your code here\n    pass",
            "test_cases": "is_palindrome('racecar') should return True\nis_palindrome('hello') should return False"
        },
        {
            "type": "coding",
            "question": f"Create a function to calculate the nth Fibonacci number, demonstrating recursive concepts in {topics}.",
            "starter_code": "def fibonacci(n):\n    # Your code here\n    pass",
            "test_cases": "fibonacci(0) should return 0\nfibonacci(1) should return 1\nfibonacci(6) should return 8"
        },
        {
            "type": "coding",
            "question": f"Write a function that finds all prime numbers up to n, a fundamental algorithm in {topics}.",
            "starter_code": "def find_primes(n):\n    # Your code here\n    pass",
            "test_cases": "find_primes(10) should return [2, 3, 5, 7]\nfind_primes(20) should return [2, 3, 5, 7, 11, 13, 17, 19]"
        },
        {
            "type": "coding",
            "question": f"Implement a function to reverse a linked list, a common operation in {topics} data structures.",
            "starter_code": "class Node:\n    def __init__(self, value, next=None):\n        self.value = value\n        self.next = next\n\ndef reverse_linked_list(head):\n    # Your code here\n    pass",
            "test_cases": "For a linked list 1->2->3, the result should be 3->2->1"
        },
        # Adding more diverse coding questions
        {
            "type": "coding",
            "question": f"Implement a binary search algorithm for finding an element in a sorted array, essential for efficient searching in {topics}.",
            "starter_code": "def binary_search(arr, target):\n    # Your code here\n    pass",
            "test_cases": "binary_search([1, 2, 3, 4, 5], 3) should return 2\nbinary_search([1, 2, 3, 4, 5], 6) should return -1"
        },
        {
            "type": "coding",
            "question": f"Create a function that detects if a directed graph has a cycle, important for dependency resolution in {topics}.",
            "starter_code": "def has_cycle(graph):\n    # graph is represented as an adjacency list\n    # Your code here\n    pass",
            "test_cases": "has_cycle({1: [2], 2: [3], 3: [1]}) should return True\nhas_cycle({1: [2], 2: [3], 3: []}) should return False"
        },
        {
            "type": "coding",
            "question": f"Implement a cache with a Least Recently Used (LRU) eviction policy, commonly used in {topics} for performance optimization.",
            "starter_code": "class LRUCache:\n    def __init__(self, capacity):\n        # Your code here\n        pass\n        \n    def get(self, key):\n        # Your code here\n        pass\n        \n    def put(self, key, value):\n        # Your code here\n        pass",
            "test_cases": "For a cache with capacity 2: put(1, 1), put(2, 2), get(1) returns 1, put(3, 3) evicts key 2, get(2) returns -1"
        },
        {
            "type": "coding",
            "question": f"Write a function to perform deep copying of a complex object with nested references, a challenging task in {topics}.",
            "starter_code": "def deep_copy(obj):\n    # Your code here - handle dictionaries, lists, and primitive types\n    pass",
            "test_cases": "For obj = {'a': 1, 'b': [1, 2, {'c': 3}]}, deep_copy(obj) should return an identical but separate object"
        },
        {
            "type": "coding",
            "question": f"Implement a simple rate limiter to prevent API abuse, a common requirement in {topics} web services.",
            "starter_code": "class RateLimiter:\n    def __init__(self, max_requests, time_window):\n        # max_requests: maximum requests allowed in time_window seconds\n        # Your code here\n        pass\n        \n    def can_process_request(self, client_id):\n        # Return True if request can be processed, False otherwise\n        # Your code here\n        pass",
            "test_cases": "With max_requests=3 and time_window=60, a client should be allowed 3 requests within 60 seconds"
        },
        {
            "type": "coding",
            "question": f"Create a function that implements the merge step of merge sort, fundamental for understanding divide-and-conquer in {topics}.",
            "starter_code": "def merge(left, right):\n    # Merge two sorted arrays into a single sorted array\n    # Your code here\n    pass",
            "test_cases": "merge([1, 3, 5], [2, 4, 6]) should return [1, 2, 3, 4, 5, 6]"
        },
        {
            "type": "coding",
            "question": f"Implement a simple publish-subscribe system, a core pattern in event-driven {topics} architectures.",
            "starter_code": "class PubSub:\n    def __init__(self):\n        # Your code here\n        pass\n        \n    def subscribe(self, topic, callback):\n        # Your code here\n        pass\n        \n    def publish(self, topic, message):\n        # Your code here\n        pass\n        \n    def unsubscribe(self, topic, callback):\n        # Your code here\n        pass",
            "test_cases": "A subscriber should receive messages published to topics they're subscribed to, but not others"
        },
        {
            "type": "coding",
            "question": f"Write a function to serialize and deserialize a binary tree, important for data persistence in {topics}.",
            "starter_code": "class TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\ndef serialize(root):\n    # Your code here\n    pass\n    \ndef deserialize(data):\n    # Your code here\n    pass",
            "test_cases": "For a tree with root 1, left child 2, right child 3, deserialize(serialize(root)) should return an identical tree"
        }
    ]
    
    # Question templates for generating even more variations
    question_templates = [
        "Implement a {data_structure} class with methods for {operation1} and {operation2}, often used in {topics}.",
        "Create a function to solve the {algorithm_problem} problem, which is common in {topics} applications.",
        "Write a {paradigm} implementation of {algorithm} that handles {edge_case} correctly in {topics}.",
        "Develop a utility that converts between {format1} and {format2} formats, useful for data processing in {topics}.",
        "Implement a {pattern} design pattern that would be applicable to a {topics} system.",
        "Write a function that optimizes {operation} for {constraint} constraints in {topics} systems."
    ]
    
    # Data for populating templates
    data_structures = ["Stack", "Queue", "PriorityQueue", "HashMap", "BinarySearchTree", "Graph", "Trie", "Heap"]
    operations = ["insertion", "deletion", "searching", "traversal", "filtering", "sorting", "merging", "partitioning"]
    algorithm_problems = ["Two Sum", "Longest Common Subsequence", "Minimum Spanning Tree", "Shortest Path", 
                          "Knapsack", "Matrix Multiplication", "String Matching", "Topological Sort"]
    paradigms = ["recursive", "iterative", "dynamic programming", "greedy", "divide-and-conquer", "functional"]
    algorithms = ["depth-first search", "breadth-first search", "binary search", "quicksort", "merge sort", 
                 "Dijkstra's algorithm", "A* search", "Boyer-Moore algorithm"]
    edge_cases = ["empty inputs", "large datasets", "duplicate values", "circular references", 
                 "invalid inputs", "boundary conditions", "concurrent access", "timeout scenarios"]
    formats = ["JSON", "XML", "CSV", "binary", "text", "YAML", "Protocol Buffers", "Base64"]
    patterns = ["Singleton", "Factory", "Observer", "Strategy", "Decorator", "Adapter", "Command", "Proxy"]
    constraints = ["time", "memory", "bandwidth", "CPU", "battery life", "storage", "network latency", "security"]
    
    # Import random if not already imported
    import random
    
    # If we have fewer base questions than requested, generate variations
    while len(base_questions) < count:
        # Choose a strategy for generating new questions
        strategy = random.choice(["template", "modify_existing", "combine_concepts"])
        
        if strategy == "template":
            # Use template to create a new question
            template = random.choice(question_templates)
            
            # Randomly select components for the template
            data_structure = random.choice(data_structures)
            operation1, operation2 = random.sample(operations, 2)
            algorithm_problem = random.choice(algorithm_problems)
            paradigm = random.choice(paradigms)
            algorithm = random.choice(algorithms)
            edge_case = random.choice(edge_cases)
            format1, format2 = random.sample(formats, 2)
            pattern = random.choice(patterns)
            constraint = random.choice(constraints)
            
            # Generate the question text
            question_text = template.format(
                data_structure=data_structure,
                operation1=operation1,
                operation2=operation2,
                algorithm_problem=algorithm_problem,
                paradigm=paradigm,
                algorithm=algorithm,
                edge_case=edge_case,
                format1=format1,
                format2=format2,
                pattern=pattern,
                operation=random.choice(operations),
                constraint=constraint,
                topics=topics
            )
            
            # Generate appropriate starter code based on the question
            if "class" in question_text:
                class_name = data_structure if "data_structure" in template else pattern
                starter_code = f"class {class_name}:\n    def __init__(self):\n        # Your code here\n        pass\n        \n    def {operation1}(self, *args):\n        # Your code here\n        pass\n        \n    def {operation2}(self, *args):\n        # Your code here\n        pass"
                test_case = f"Create an instance of {class_name}, call {operation1} and {operation2}, and verify the results"
            else:
                function_name = algorithm.replace("'s algorithm", "").replace(" ", "_").lower()
                if "algorithm_problem" in template:
                    function_name = algorithm_problem.replace(" ", "_").lower()
                starter_code = f"def {function_name}(input_data):\n    # Your code here\n    pass"
                test_case = f"{function_name}(sample_input) should return expected_output\n{function_name}(edge_case_input) should handle {edge_case}"
            
            # Create the new question
            new_question = {
                "type": "coding",
                "question": question_text,
                "starter_code": starter_code,
                "test_cases": test_case
            }
            
            base_questions.append(new_question)
            
        elif strategy == "modify_existing" and base_questions:
            # Modify an existing question
            idx = random.randint(0, len(base_questions) - 1)
            original = base_questions[idx].copy()
            
            # Modifications
            modifications = [
                # Add a constraint
                lambda q: {
                    "question": f"{q['question']} Optimize for {random.choice(constraints)}.",
                    "starter_code": q["starter_code"],
                    "test_cases": q["test_cases"]
                },
                # Change focus to handle edge cases
                lambda q: {
                    "question": f"{q['question']} Make sure to handle {random.choice(edge_cases)}.",
                    "starter_code": q["starter_code"],
                    "test_cases": f"{q['test_cases']}\nAlso test with edge case: {random.choice(edge_cases)}"
                },
                # Add real-world context
                lambda q: {
                    "question": f"In a real-world {topics} application: {q['question']}",
                    "starter_code": q["starter_code"],
                    "test_cases": q["test_cases"]
                }
            ]
            
            # Apply a random modification
            modification = random.choice(modifications)
            modified = modification(original)
            
            original.update(modified)
            base_questions.append(original)
            
        else:  # combine algorithms
            # Combine two algorithms or operations
            algo1 = random.choice(algorithms)
            algo2 = random.choice([a for a in algorithms if a != algo1])
            
            combined_question = {
                "type": "coding",
                "question": f"Implement a hybrid algorithm that combines {algo1} and {algo2} to solve problems in {topics}.",
                "starter_code": f"def hybrid_{algo1.split(' ')[0]}_{algo2.split(' ')[0]}(data):\n    # Implement a solution that uses both approaches\n    # Your code here\n    pass",
                "test_cases": f"Your hybrid algorithm should handle both the strengths of {algo1} and {algo2}"
            }
            
            base_questions.append(combined_question)
    
    # Shuffle and return only the requested number
    random.shuffle(base_questions)
    return base_questions[:count]

def _generate_dynamic_question_batch(topics, question_type, count=10, prompt_prefix=None, difficulty="Medium"):
    """
    Generate a batch of questions of a specified type.
    
    Args:
        topics: List of topics or comma-separated string of topics
        question_type: Type of question to generate (multiple_choice, open_ended, coding)
        count: Number of questions to generate
        prompt_prefix: Optional prefix to add to the prompt for uniqueness
        difficulty: Difficulty level (Easy, Medium, Hard)
        
    Returns:
        A string containing the batch of questions
    """
    # Convert string topics to list if needed
    if isinstance(topics, str):
        topics = [t.strip() for t in topics.split(",") if t.strip()]
    
    # Ensure we have topics
    if not topics:
        topics = ["machine learning"]
    
    # Import modules for randomization
    import random
    import time
    import hashlib
    import uuid
    
    # Generate a unique batch identifier
    batch_uuid = str(uuid.uuid4())
    timestamp = int(time.time() * 1000)
    
    # Create a unique seed that changes for each batch of questions
    seed_base = f"{batch_uuid}_{timestamp}_{prompt_prefix or ''}_{question_type}_{difficulty}"
    seed_hash = hashlib.md5(seed_base.encode()).hexdigest()
    random.seed(int(seed_hash, 16) % (2**32))
    
    # Shuffle and select topics to ensure variety
    shuffled_topics = topics.copy()
    random.shuffle(shuffled_topics)
    
    # Select a subset of topics for this batch if there are many
    if len(shuffled_topics) > 3:
        selected_topics = random.sample(shuffled_topics, min(3, len(shuffled_topics)))
        # Always include at least one topic from the original list
        if set(selected_topics).isdisjoint(set(topics[:1])):
            selected_topics[0] = topics[0]
    else:
        selected_topics = shuffled_topics
    
    # Create a unique identifier for this batch
    batch_id = f"batch_{hashlib.md5((seed_base + str(selected_topics)).encode()).hexdigest()[:8]}"
    
    # Create multiple unique prompts based on question type
    prompt_variations = {
        "multiple_choice": [
            f"Generate {count} unique {difficulty} multiple choice questions about {', '.join(selected_topics)}.",
            f"Create {count} challenging {difficulty} multiple choice quiz items on {', '.join(selected_topics)}.",
            f"Design {count} {difficulty} multiple choice test questions on the topic of {', '.join(selected_topics)}.",
            f"Develop {count} educational {difficulty} MCQs about {', '.join(selected_topics)}.",
            f"Produce {count} diverse {difficulty} multiple choice questions covering {', '.join(selected_topics)}."
        ],
        "open_ended": [
            f"Generate {count} thought-provoking {difficulty} open-ended questions about {', '.join(selected_topics)}.",
            f"Create {count} analytical {difficulty} open-ended questions that explore {', '.join(selected_topics)}.",
            f"Design {count} conceptual {difficulty} open-ended questions on {', '.join(selected_topics)}.",
            f"Develop {count} {difficulty} discussion questions about {', '.join(selected_topics)}.",
            f"Formulate {count} {difficulty} open-ended questions that require deep understanding of {', '.join(selected_topics)}."
        ],
        "coding": [
            f"Generate {count} practical {difficulty} coding exercises about {', '.join(selected_topics)}.",
            f"Create {count} implementation-focused {difficulty} coding challenges on {', '.join(selected_topics)}.",
            f"Design {count} hands-on {difficulty} programming tasks related to {', '.join(selected_topics)}.",
            f"Develop {count} applied {difficulty} coding problems that utilize {', '.join(selected_topics)}.",
            f"Produce {count} realistic {difficulty} coding questions that demonstrate {', '.join(selected_topics)}."
        ]
    }
    
    # Add variation to prompt based on prompt_prefix, timestamp, and batch_id
    unique_prefix = f"Session ID: {batch_uuid}. Timestamp: {timestamp}. Batch: {batch_id}. "
    if prompt_prefix:
        unique_prefix += f"{prompt_prefix} "
    
    # Choose a prompt variation based on the question type
    variations = prompt_variations.get(question_type, prompt_variations["multiple_choice"])
    prompt_variation = random.choice(variations)
    
    # Create the final prompt with uniqueness markers
    final_prompt = f"{unique_prefix}{prompt_variation}"
    
    # Add specific instructions for question format based on question type
    if question_type == "multiple_choice":
        # Create more varied question templates and instructions
        format_instructions = [
            "\nFormat each question with:\n- A clear question statement\n- Four distinct options labeled A through D\n- Mark the correct answer\n- Make sure options are plausible but only one is correct",
            "\nPlease format questions as follows:\nQuestion: [Question text]\nA) [Option A]\nB) [Option B]\nC) [Option C]\nD) [Option D]\nCorrect Answer: [Letter]",
            "\nFollow this format:\nQ: [Question]\nA) [First option]\nB) [Second option]\nC) [Third option]\nD) [Fourth option]\nAnswer: [Correct letter]"
        ]
        final_prompt += random.choice(format_instructions)
        
        # Add specific instruction for diversity and uniqueness
        unique_aspects = [
            f"\nEnsure questions cover different aspects of {', '.join(selected_topics)}.",
            f"\nMake sure each question tests a different concept within {', '.join(selected_topics)}.",
            f"\nVary the difficulty within the {difficulty} level to maintain engagement.",
            f"\nIntroduce some application-based questions that test practical knowledge."
        ]
        final_prompt += random.choice(unique_aspects)
        
        # Generate sample output with variation
        output = ""
        for i in range(count):
            # Create unique seed for each question
            q_seed = f"{batch_id}_{i}_{timestamp % 10000 + i}"
            q_hash = hashlib.md5(q_seed.encode()).hexdigest()[:8]
            
            # Select a topic with rotation
            topic = selected_topics[i % len(selected_topics)]
            
            # Vary question formats
            question_templates = [
                f"What is a key aspect of {topic} in {difficulty.lower()} applications?",
                f"Which approach is most effective for {topic} when dealing with {difficulty.lower()} problems?",
                f"In the context of {topic}, which statement is true at a {difficulty.lower()} level?",
                f"What distinguishes successful implementation of {topic} in {difficulty.lower()} scenarios?"
            ]
            
            # Generate unique question
            question = random.choice(question_templates)
            
            # Ensure more unique questions by appending a subtle identifier
            if random.random() < 0.3:  # Only add to some questions to maintain naturalness
                question += f" (Considering specifically case #{q_hash[:4]})"
            
            # Generate options
            topic_options = {
                "machine learning": [
                    "Using supervised learning algorithms to classify data",
                    "Implementing neural networks for complex pattern recognition",
                    "Applying reinforcement learning for sequential decision making",
                    "Using unsupervised clustering to identify natural groupings",
                    "Employing ensemble methods to improve prediction accuracy",
                    "Implementing transfer learning from pre-trained models",
                    "Using cross-validation for robust model evaluation",
                    "Applying feature selection to improve model performance"
                ],
                "natural language processing": [
                    "Using transformers for contextual word embeddings",
                    "Implementing recurrent neural networks for sequence modeling",
                    "Applying attention mechanisms to focus on relevant parts of input",
                    "Using BERT for bidirectional contextual representations",
                    "Implementing tokenization and lemmatization for text preprocessing",
                    "Applying named entity recognition to extract key information",
                    "Using sentiment analysis to determine emotional tone",
                    "Implementing text summarization for content reduction"
                ],
                "deep learning": [
                    "Using convolutional neural networks for image processing",
                    "Implementing recurrent architectures for sequential data",
                    "Applying gradient descent optimization algorithms",
                    "Using dropout for regularization to prevent overfitting",
                    "Implementing batch normalization to stabilize training",
                    "Applying residual connections to train deeper networks",
                    "Using transfer learning from pre-trained models",
                    "Implementing generative adversarial networks for data generation"
                ],
                "data science": [
                    "Using exploratory data analysis to understand data distributions",
                    "Implementing feature engineering to create meaningful variables",
                    "Applying statistical hypothesis testing to validate assumptions",
                    "Using dimensionality reduction to handle high-dimensional data",
                    "Implementing regression techniques for predictive modeling",
                    "Applying clustering algorithms to find hidden patterns",
                    "Using visualization techniques to communicate insights",
                    "Implementing A/B testing for experimental validation"
                ],
                "computer vision": [
                    "Using convolutional neural networks for image classification",
                    "Implementing object detection algorithms like YOLO or R-CNN",
                    "Applying semantic segmentation for pixel-level classification",
                    "Using image preprocessing techniques like normalization",
                    "Implementing feature extraction with pretrained networks",
                    "Applying optical flow for motion analysis",
                    "Using image augmentation to increase training data",
                    "Implementing facial recognition systems"
                ],
                "neural networks": [
                    "Using backpropagation for gradient calculation",
                    "Implementing various activation functions like ReLU",
                    "Applying weight initialization techniques for better convergence",
                    "Using regularization methods to prevent overfitting",
                    "Implementing various architectures like feed-forward or CNN",
                    "Applying learning rate scheduling for optimization",
                    "Using early stopping to prevent overfitting",
                    "Implementing attention mechanisms for better focus"
                ]
            }
            
            # Find the most relevant topic category
            topic_lower = topic.lower()
            topic_category = "machine learning"  # Default
            
            for category in topic_options.keys():
                if category in topic_lower:
                    topic_category = category
                    break
                    
            available_options = topic_options[topic_category]
            
            # Select 4 unique options
            if len(available_options) >= 4:
                options = random.sample(available_options, 4)
            else:
                # Create more meaningful options with real content, not just placeholders
                if "classification" in topic.lower():
                    options = [
                        f"Use supervised learning algorithms to classify data",
                        f"Apply decision trees with appropriate feature selection", 
                        f"Implement logistic regression with regularization",
                        f"Use support vector machines with suitable kernels"
                    ]
                elif "regression" in topic.lower():
                    options = [
                        f"Apply linear regression with appropriate feature scaling",
                        f"Use polynomial regression for non-linear relationships",
                        f"Implement regularization techniques to prevent overfitting",
                        f"Use gradient descent for model optimization"
                    ]
                elif "neural" in topic.lower():
                    options = [
                        f"Design appropriate network architecture for the problem",
                        f"Apply proper activation functions per layer",
                        f"Implement backpropagation with suitable optimizers",
                        f"Use regularization techniques to prevent overfitting"
                    ]
                else:
                    # Create more meaningful generic options
                    options = [
                        f"Apply established algorithms suitable for the task",
                        f"Implement preprocessing techniques to improve data quality",
                        f"Use appropriate validation methods to evaluate performance",
                        f"Optimize parameters to balance bias and variance"
                    ]
            
            # Determine correct answer
            correct_index = (int(q_hash, 16) % 4)
            correct_letter = chr(65 + correct_index)
            
            # Format the question
            output += f"Question: {question}\n"
            for j, option in enumerate(options):
                letter = chr(65 + j)
                output += f"{letter}) {option}\n"
            output += f"Correct Answer: {correct_letter}\n\n"
    
    elif question_type == "open_ended":
        # Format instructions for open-ended questions
        format_instructions = [
            "\nFormat each question with:\n- A thought-provoking question statement\n- A reference answer that covers key points",
            "\nPlease format questions as follows:\nQuestion: [Question text]\nReference Answer: [Sample correct answer]",
            "\nFollow this format:\nQ: [Open-ended question]\nReference Answer: [Key points to address]"
        ]
        final_prompt += random.choice(format_instructions)
        
        # Add specific instruction for depth and breadth
        unique_aspects = [
            f"\nEnsure questions require critical thinking about {', '.join(selected_topics)}.",
            f"\nInclude questions that compare and contrast different aspects of {', '.join(selected_topics)}.",
            f"\nAsk questions that require analysis of real-world applications.",
            f"\nIncorporate questions that explore theoretical foundations and practical implementations."
        ]
        final_prompt += random.choice(unique_aspects)
        
        # Generate sample output with diversity
        output = ""
        for i in range(count):
            # Create unique seed for each question
            q_seed = f"{batch_id}_{i}_{timestamp % 10000 + i}_open"
            q_hash = hashlib.md5(q_seed.encode()).hexdigest()[:8]
            
            # Select a topic with rotation
            topic = selected_topics[i % len(selected_topics)]
            
            # Create varied open-ended question templates
            question_templates = [
                f"Explain how {topic} is applied in real-world scenarios. Consider case study #{q_hash[:4]}.",
                f"Compare and contrast different approaches to implementing {topic} in {difficulty.lower()} contexts. Specifically situation #{q_hash[:4]}.",
                f"What are the ethical considerations when applying {topic} to sensitive domains? Focus particularly on example #{q_hash[:4]}.",
                f"How might {topic} evolve in the next decade? Consider development path #{q_hash[:4]}."
            ]
            
            # Generate unique question
            question = random.choice(question_templates)
            
            # Generate a reference answer
            reference_answer = f"A comprehensive answer would discuss key aspects of {topic} including theoretical foundations, practical applications, and challenges. For the specific case #{q_hash[:4]}, considerations should include implementation strategies, optimization approaches, and evaluation metrics."
            
            # Format the question
            output += f"Question: {question}\n"
            output += f"Reference Answer: {reference_answer}\n\n"
    
    elif question_type == "coding":
        # Format instructions for coding questions
        format_instructions = [
            "\nFormat each coding question with:\n- A problem statement\n- Starter code in Python\n- Test cases to verify solutions",
            "\nPlease format coding questions as follows:\nQuestion: [Problem statement]\nStarter Code:\n```python\n[Starter code]\n```\nTest Cases:\n```python\n[Test cases]\n```",
            "\nFollow this format:\nQ: [Coding problem]\nStarter Code:\n```python\n[Code template]\n```\nTest Cases:\n```\n[Example inputs and expected outputs]\n```"
        ]
        final_prompt += random.choice(format_instructions)
        
        # Add specific instruction for practical relevance
        unique_aspects = [
            f"\nDesign problems that apply {', '.join(selected_topics)} to solve real-world tasks.",
            f"\nEnsure coding problems test both conceptual understanding and implementation skills.",
            f"\nVary the complexity of problems while maintaining the overall {difficulty} level.",
            f"\nInclude problems that require different programming techniques and approaches."
        ]
        final_prompt += random.choice(unique_aspects)
        
        # Generate sample output with diversity
        output = ""
        for i in range(count):
            # Create unique seed for each question
            q_seed = f"{batch_id}_{i}_{timestamp % 10000 + i}_coding"
            q_hash = hashlib.md5(q_seed.encode()).hexdigest()[:8]
            
            # Select a topic with rotation
            topic = selected_topics[i % len(selected_topics)]
            
            # Create varied function names and problem statements
            function_name = f"implement_{topic.replace(' ', '_')}_{q_hash[:4]}"
            
            problem_templates = [
                f"Implement a function that applies {topic} techniques to solve the following problem (variant #{q_hash[:4]}).",
                f"Create a function that demonstrates {topic} principles to address challenge #{q_hash[:4]}.",
                f"Develop an algorithm using {topic} approaches to solve problem instance #{q_hash[:4]}.",
                f"Write a function implementing {topic} methods to handle the specific use case #{q_hash[:4]}."
            ]
            
            # Generate unique problem statement
            problem = random.choice(problem_templates)
            
            # Generate starter code
            starter_code = f"def {function_name}(data):\n    \"\"\"\n    {problem}\n    \n    Args:\n        data: Input data to process\n        \n    Returns:\n        Processed result based on {topic} principles\n    \"\"\"\n    # Your code here\n    pass"
            
            # Generate test cases
            test_case = f"# Example test case\nimport numpy as np\n\n# Test with unique data for problem #{q_hash[:4]}\ndata = np.array([{q_hash[0]}, {q_hash[1]}, {q_hash[2]}, {q_hash[3]}, {q_hash[4]}])\nresult = {function_name}(data)\n\n# Expected output should match implementation requirements"
            
            # Format the question
            output += f"Question: {problem}\n"
            output += f"Starter Code:\n```python\n{starter_code}\n```\n"
            output += f"Test Cases:\n```python\n{test_case}\n```\n\n"
    
    else:
        return f"Unsupported question type: {question_type} (Batch ID: {batch_id})"
    
    # Add metadata to help with tracking
    output = f"# Batch ID: {batch_id}\n# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n# Question Type: {question_type}\n# Difficulty: {difficulty}\n\n{output}"
    
    return output

def _generate_mixed_question_set(topics, mc_count=3, oe_count=1, coding_count=1):
    """Generate a mixed set of questions with appropriate formatting."""
    result = ""
    
    # Generate multiple choice questions
    if mc_count > 0:
        result += _generate_dynamic_question_batch(topics, "multiple_choice", mc_count)
    
    # Generate open-ended questions
    if oe_count > 0:
        result += _generate_dynamic_question_batch(topics, "open_ended", oe_count)
    
    # Generate coding questions
    if coding_count > 0:
        result += _generate_dynamic_question_batch(topics, "coding", coding_count)
    
    return result 