# Machine Learning Quiz Generator

A powerful educational tool that uses AI to generate personalized quizzes and coding assignments specifically for machine learning courses. Built with Streamlit and powered by Groq's LLM.

## Features
TO TAKE A LOOK ON THE WEBSITE PRESS THIS LINK --> https://ai-exame-generator-9bngyjajgyqwuzuywqcd93.streamlit.app/
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

## 🚀 Deploy to Streamlit Community Cloud

You can deploy this app to Streamlit Community Cloud for free and get a public URL that anyone can access!

### Prerequisites
- A GitHub account
- A Groq API key (get it free at [console.groq.com](https://console.groq.com))

### Step-by-Step Deployment

1. **Push your code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/ai-exam-generator.git
   git push -u origin main
   ```

2. **Go to [share.streamlit.io](https://share.streamlit.io)**

3. **Click "New app"**

4. **Connect your GitHub repository:**
   - Repository: `yourusername/ai-exam-generator`
   - Branch: `main`
   - Main file path: `main.py`

5. **Add your API key in Streamlit Cloud:**
   - Click "Advanced settings"
   - In the "Secrets" section, add:
     ```toml
     GROQ_API_KEY = "your_actual_groq_api_key_here"
     ```

6. **Click "Deploy!"**

Your app will be available at: `https://your-app-name.streamlit.app`

### 🌐 Live Demo
Once deployed, your AI Exam Generator will be accessible 24/7 at your custom Streamlit URL!

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
