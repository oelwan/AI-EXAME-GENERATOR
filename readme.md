# Machine Learning Quiz Generator

A powerful educational tool that uses AI to generate personalized quizzes and coding assignments specifically for machine learning courses. Built with Streamlit and powered by Groq's LLM.

## Features

- **ML Quiz Generator**
  - Create customized multiple-choice questions on any machine learning topic
  - Set difficulty level and number of questions
  - Get instant feedback and detailed performance analysis
  - AI-powered recommendations for improvement

- **ML Coding Assignment Generator**
  - Generate interactive machine learning programming challenges
  - Get starter code templates for ML algorithms
  - AI-powered code evaluation
  - Detailed feedback and improvement suggestions

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ml-quiz-generator.git
cd ml-quiz-generator
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your Groq API key:
```
GROQ_API_KEY=your_api_key_here
```

## Usage

1. Start the application:
```bash
streamlit run main.py
```

2. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

3. Choose between ML Quiz Generator or ML Coding Assignment Generator

4. Follow the prompts to create and complete your educational content

## Project Structure

```
project/
├── main.py              # Main application entry point
├── config/             # Configuration files
│   └── __init__.py
├── models/             # Data models
│   └── question.py     # Question model
├── services/           # Business logic
│   ├── llm_service.py  # LLM integration
│   ├── quiz_service.py # Quiz-related functions
│   └── coding_service.py # Coding assignment functions
├── ui/                 # User interface components
│   ├── components.py   # Reusable UI components
│   └── pages.py        # Page layouts
└── utils/             # Utility functions
    └── __init__.py
```

## Technologies Used

- **Frontend**: Streamlit
- **AI**: Groq LLM (LLAMA3-8B-8192)
- **Language**: Python 3.8+
- **Dependencies**: See requirements.txt

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
