import streamlit as st
import os
from datetime import datetime

def setup_page_config():
    """Set up the page configuration and styling."""
    st.set_page_config(
        page_title="Machine Learning Quiz Generator",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom styling
    st.markdown("""
    <style>
    /* Modern design system */
    * {
        font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    }
    
    /* New vibrant color palette */
    :root {
        --primary: #003B70;
        --primary-dark: #002B54;
        --secondary: #0056A4;
        --success: #4CAF50;
        --warning: #FFC107;
        --danger: #F44336;
        --info: #00BCD4;
        --dark: #212121;
        --light: #FAFAFA;
        --gray: #9E9E9E;
    }
    
    /* Page background */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Bold modern headers */
    .main-header {
        font-size: 3.5rem;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        background: linear-gradient(90deg, #003B70 0%, #0056A4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.1);
        text-transform: uppercase;
    }
    
    .sub-header {
        font-size: 2.2rem;
        color: var(--primary);
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 900;
        letter-spacing: -0.02em;
        text-transform: uppercase;
    }
    
    /* Card with shadow and border */
    .card {
        background-color: white;
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 8px 32px rgba(0, 59, 112, 0.15);
        margin-bottom: 30px;
        color: var(--dark);
        border: 1px solid rgba(0, 59, 112, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 36px rgba(0, 59, 112, 0.2);
    }
    
    /* Modern footer */
    .footer {
        text-align: center;
        color: var(--dark);
        font-size: 1.1rem;
        margin-top: 4rem;
        padding: 2rem;
        background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(0, 59, 112, 0.1) 100%);
        border-radius: 16px;
        font-weight: 600;
    }
    
    /* Bold button styling */
    .stButton button {
        border-radius: 50px !important;
        font-weight: 900 !important;
        padding: 0.7rem 1.5rem !important;
        font-size: 1.1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        box-shadow: 0 6px 15px rgba(0, 59, 112, 0.4) !important;
        border: none !important;
        transition: all 0.3s ease !important;
        color: white !important;
        background-color: #003B70 !important;
    }
    
    .stButton button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 20px rgba(0, 59, 112, 0.5) !important;
    }
    
    /* Text styling */
    p {
        color: #333333;
        font-size: 1.2rem;
        line-height: 1.7;
        font-weight: 500;
        margin-bottom: 1.2rem;
    }
    
    li {
        color: #333333;
        line-height: 1.8;
        font-weight: 500;
        margin-bottom: 0.8rem;
        font-size: 1.1rem;
    }
    
    h1, h2, h3 {
        color: var(--primary);
        font-weight: 900;
        letter-spacing: -0.01em;
        text-transform: uppercase;
    }
    
    h4, h5, h6 {
        color: var(--primary);
        font-weight: 800;
    }
    
    /* List styling */
    ul {
        padding-left: 1.5rem;
    }
    
    ul li::marker {
        color: var(--primary);
        font-size: 1.2em;
    }
    
    /* Radio buttons for quiz - CLEAN STYLING */
    .stRadio > div {
        padding: 12px 0;
    }
    
    .stRadio label {
        font-weight: 600;
        color: #333333;
        font-size: 1.1rem;
    }
    
    /* Much cleaner quiz radio buttons */
    .stRadio > div > div {
        background-color: white !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
        padding: 12px 15px !important;
        margin-bottom: 8px !important;
        transition: all 0.2s ease !important;
    }
    
    .stRadio > div > div:hover {
        background-color: #f9f9f9 !important;
        border-color: #003B70 !important;
    }
    
    .stRadio > div > div[data-baseweb="radio"] > div {
        margin-right: 12px !important;
    }
    
    .stRadio > div > div[aria-checked="true"] {
        background-color: #E6F0FF !important;
        border-color: #003B70 !important;
        border-left: 4px solid #003B70 !important;
    }
    
    /* Bold expander styling - CLEANER VERSION */
    .st-expander {
        border: 1px solid #e0e0e0 !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important;
        margin-bottom: 15px !important;
        background-color: white !important;
    }
    
    .st-expander:hover {
        border-color: #003B70 !important;
    }
    
    .st-expander > details > summary {
        background-color: white !important;
        font-weight: 700 !important;
        padding: 15px 20px !important;
        color: #333333 !important;
    }
    
    .st-expander > details[open] > summary {
        border-bottom: 1px solid #e0e0e0 !important;
        margin-bottom: 10px !important;
    }
    
    /* Analysis sections */
    .analysis-section {
        padding: 25px;
        border-radius: 16px;
        height: 100%;
        color: #333333;
        border: 1px solid rgba(0, 59, 112, 0.1);
        box-shadow: 0 8px 20px rgba(0, 59, 112, 0.1);
        transition: transform 0.2s;
    }
    
    .analysis-section:hover {
        transform: translateY(-4px);
    }
    
    /* Strong elements */
    strong {
        font-weight: 800;
        color: #333333;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background-color: var(--primary) !important;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-image: linear-gradient(180deg, #f0f8ff 0%, #e6f0ff 100%);
    }
    
    /* Alerts and messages */
    .stAlert {
        border-radius: 16px !important;
        border-width: 2px !important;
    }
    
    .stAlert > div {
        padding: 18px 24px !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    
    /* Code blocks */
    pre {
        border-radius: 16px !important;
    }
    
    code {
        font-family: 'Fira Code', 'Roboto Mono', monospace !important;
        font-size: 0.95rem !important;
        padding: 0.2em 0.4em !important;
        border-radius: 6px !important;
    }
    
    /* Fix the background color of the main page */
    div.appview-container {
        background-color: #f9f9f9;
    }

    /* Input field styling */
    .stTextInput > div > div > input {
        border-radius: 8px !important;
        border: 2px solid #e0e0e0 !important;
        padding: 12px 16px !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: #003B70 !important;
        transition: all 0.3s ease !important;
        background-color: white !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #666666 !important;
        font-weight: 600 !important;
        opacity: 0.9 !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #003B70 !important;
        box-shadow: 0 0 0 3px rgba(0, 59, 112, 0.1) !important;
        outline: none !important;
        color: #003B70 !important;
        font-weight: 800 !important;
    }

    .stTextInput > div > div > input:hover {
        border-color: #003B70 !important;
    }

    /* Password input field styling */
    .stTextInput > div > div > input[type="password"] {
        letter-spacing: 2px !important;
        font-weight: 800 !important;
    }

    /* Label styling */
    .stTextInput > div > div > label {
        color: #003B70 !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        margin-bottom: 8px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    /* Blue box text styling */
    .bau-header {
        background-color: #003B70 !important;
        padding: 40px 20px !important;
        text-align: center !important;
        border-radius: 5px !important;
        margin-bottom: 40px !important;
        box-shadow: 0 4px 10px rgba(0, 59, 112, 0.3) !important;
    }

    .bau-text {
        color: white !important;
        font-size: 80px !important;
        font-weight: 900 !important;
        letter-spacing: -2px !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2) !important;
    }

    .user-type-text {
        color: #003B70 !important;
        font-size: 24px !important;
        font-weight: 800 !important;
        margin-bottom: 20px !important;
        text-align: center !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }

    /* Form field labels */
    .stTextInput > div > div > div {
        color: #003B70 !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        margin-bottom: 8px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    /* Radio button styling */
    .stRadio > div > div {
        background-color: white !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 8px !important;
        padding: 12px 15px !important;
        margin-bottom: 8px !important;
        transition: all 0.2s ease !important;
    }

    .stRadio > div > div:hover {
        background-color: #f9f9f9 !important;
        border-color: #003B70 !important;
    }

    .stRadio > div > div[aria-checked="true"] {
        background-color: #E6F0FF !important;
        border-color: #003B70 !important;
        border-left: 4px solid #003B70 !important;
    }

    .stRadio > div > div > label {
        color: #003B70 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    .stRadio > div > div[aria-checked="true"] > label {
        color: #003B70 !important;
        font-weight: 800 !important;
    }

    /* Language selector buttons */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 800 !important;
        padding: 12px 24px !important;
        font-size: 1.1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        box-shadow: 0 4px 8px rgba(0, 59, 112, 0.2) !important;
        border: 2px solid #003B70 !important;
        transition: all 0.3s ease !important;
        color: #003B70 !important;
        background-color: white !important;
        width: 100% !important;
        margin: 5px 0 !important;
    }

    .stButton > button:hover {
        background-color: #003B70 !important;
        color: white !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(0, 59, 112, 0.3) !important;
    }

    /* Register button specific styling */
    .register-btn > button {
        background-color: #003B70 !important;
        color: white !important;
        border: none !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        padding: 15px 30px !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 8px rgba(0, 59, 112, 0.3) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }

    .register-btn > button:hover {
        background-color: #002B54 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(0, 59, 112, 0.4) !important;
    }

    /* Language selector container */
    .language-selector {
        text-align: center !important;
        margin-top: 40px !important;
        padding: 20px !important;
        background-color: white !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 8px rgba(0, 59, 112, 0.1) !important;
        border: 1px solid rgba(0, 59, 112, 0.1) !important;
    }

    .language-button {
        background-color: white !important;
        color: #003B70 !important;
        border: 2px solid #003B70 !important;
        font-size: 1.1rem !important;
        font-weight: 800 !important;
        padding: 12px 24px !important;
        margin: 5px !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }

    .language-button:hover, .language-button.active {
        background-color: #003B70 !important;
        color: white !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0, 59, 112, 0.3) !important;
    }
    </style>
    """,
    unsafe_allow_html=True)

def create_login_screen():
    """Create the initial login/registration screen."""
    # Custom CSS for styling
    st.markdown("""
        <style>
            .main {
                background-color: white !important;
            }
            .block-container {
                max-width: 1000px;
                padding: 2rem;
            }
            .login-container {
                width: 100%;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }
            .bau-header {
                background-color: #003B70;
                padding: 40px 20px;
                text-align: center;
                border-radius: 5px;
                margin-bottom: 40px;
                box-shadow: 0 4px 10px rgba(0, 59, 112, 0.3);
            }
            .bau-text {
                color: white;
                font-size: 80px;
                font-weight: 900;
                letter-spacing: -2px;
            }
            .user-type-text {
                color: #003B70;
                font-size: 24px;
                font-weight: 600;
                margin-bottom: 20px;
                text-align: center;
            }
            .stButton button {
                width: 100%;
                height: 50px;
                background-color: white !important;
                color: #003B70 !important;
                font-size: 16px !important;
                font-weight: 500 !important;
                border-radius: 5px !important;
                border: 1px solid #003B70 !important;
                margin: 10px 0 !important;
                box-shadow: none !important;
            }
            .stButton button:hover {
                background-color: #f5f5f5 !important;
                transform: none !important;
                box-shadow: none !important;
            }
            .register-btn button {
                background-color: white !important;
                color: #003B70 !important;
                border: 1px solid #003B70 !important;
            }
            .register-btn button:hover {
                background-color: #f5f5f5 !important;
            }
            .developer-btn button {
                background-color: #f0f0f0 !important;
                color: #555 !important;
                border: 1px dashed #999 !important;
                font-size: 14px !important;
            }
            .developer-btn button:hover {
                background-color: #e5e5e5 !important;
            }
            .divider {
                margin: 30px 0;
                border-top: 1px solid #ddd;
            }
            .language-selector {
                text-align: center;
                margin-top: 40px;
                color: #666;
                font-size: 14px;
            }
            .language-button {
                background: none;
                border: none;
                color: #666;
                font-size: 14px;
                cursor: pointer;
                padding: 5px 10px;
                margin: 0 5px;
            }
            .language-button:hover, .language-button.active {
                color: #003B70;
                font-weight: bold;
                text-decoration: underline;
            }
        </style>
    """, unsafe_allow_html=True)

    # Center content
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Large BAU text with blue background
    st.markdown('<div class="bau-header"><div class="bau-text">BAU</div></div>', unsafe_allow_html=True)
    
    # Get text based on language
    if st.session_state.language == "tr":
        user_type_text = "Kullanıcı Tipi Seçin"
        student_login = "Öğrenci Olarak Giriş Yap"
        professor_login = "Profesör Olarak Giriş Yap"
        developer_login = "Geliştirici Olarak Giriş Yap"
        register_text = "Yeni Hesap Oluştur"
        english_text = "İNGİLİZCE"
        turkish_text = "TÜRKÇE"
    else:
        user_type_text = "Select User Type"
        student_login = "Login as Student"
        professor_login = "Login as Professor"
        developer_login = "Login as Developer"
        register_text = "Register New Account"
        english_text = "ENGLISH"
        turkish_text = "TÜRKÇE"
    
    # User Type Selection
    st.markdown(f'<p class="user-type-text">{user_type_text}</p>', unsafe_allow_html=True)
    
    # Student Login Button
    if st.button(student_login, key="student-login"):
        st.session_state.show_login_form = True
        st.session_state.login_type = "student"
        st.rerun()

    # Professor Login Button
    if st.button(professor_login, key="professor-login"):
        st.session_state.show_login_form = True
        st.session_state.login_type = "professor"
        st.rerun()
        
    # Developer Login Button
    st.markdown('<div class="developer-btn">', unsafe_allow_html=True)
    if st.button(developer_login, key="developer-login"):
        st.session_state.show_login_form = True
        st.session_state.login_type = "developer"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Register Section
    st.markdown('<div class="register-btn">', unsafe_allow_html=True)
    if st.button(register_text, key="register"):
        st.session_state.show_register_form = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Language selector at the bottom
    st.markdown('<div class="language-selector">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(english_text, key="lang_en"):
            st.session_state.language = "en"
            st.rerun()
    with col2:
        if st.button(turkish_text, key="lang_tr"):
            st.session_state.language = "tr"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)

def create_login_form():
    """Create the login form with validation."""
    # Center content
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Large BAU text with blue background
    st.markdown('<div class="bau-header"><div class="bau-text">BAU</div></div>', unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back", key="back_to_login_screen"):
        st.session_state.show_login_form = False
        st.rerun()
    
    # Get page text based on language
    if st.session_state.language == "tr":
        login_title = f"{st.session_state.login_type.title()} Girişi"
        email_label = "E-Posta"
        password_label = "Şifre"
        login_button = "GİRİŞ"
        forgot_password = "ŞİFREMİ UNUTTUM"
        email_placeholder = "BAU e-posta adresinizi girin"
        password_placeholder = "Şifrenizi girin"
        email_error = "Lütfen BAU e-posta adresinizi kullanın (@bahcesehir.edu.tr)"
        invalid_credentials = "Geçersiz e-posta veya şifre"
    else:
        login_title = f"Login as {st.session_state.login_type.title()}"
        email_label = "E-Mail"
        password_label = "Password"
        login_button = "LOGIN"
        forgot_password = "I FORGOT MY PASSWORD"
        email_placeholder = "Enter your BAU email address"
        password_placeholder = "Enter your password"
        email_error = "Please use your BAU email address (@bahcesehir.edu.tr)"
        invalid_credentials = "Invalid email or password"
    
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #003B70; font-size: 24px; font-weight: 600;">
                {login_title}
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        # Email field
        st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
        st.markdown(f'<div style="color: #666; font-size: 14px; margin-bottom: 5px;">{email_label}</div>', unsafe_allow_html=True)
        email = st.text_input("Email Address", placeholder=email_placeholder, key="email_input", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Password field
        st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
        st.markdown(f'<div style="color: #666; font-size: 14px; margin-bottom: 5px;">{password_label}</div>', unsafe_allow_html=True)
        password = st.text_input("Password", type="password", placeholder=password_placeholder, key="password_input", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        submit = st.form_submit_button(login_button)
        
        if submit:
            if not email or not password:
                st.error("Please fill in all fields" if st.session_state.language == "en" else "Lütfen tüm alanları doldurun")
            elif not email.endswith("@bahcesehir.edu.tr"):
                st.error(email_error)
            else:
                # Special check for developer login
                if st.session_state.login_type == "developer":
                    if email == "omar@bahcesehir.edu.tr" and password == "1234":
                        st.session_state.user_type = "developer"
                        st.session_state.page = "developer_home"
                        st.session_state.show_login_form = False
                        st.rerun()
                    else:
                        st.error(invalid_credentials)
                # Special check for professor login - direct login without database check
                elif st.session_state.login_type == "professor":
                    # For testing/demo purposes, allow direct professor login
                    # You can replace this with proper DB checks later
                    st.session_state.user_type = "professor"
                    st.session_state.page = "professor_home"
                    st.session_state.show_login_form = False
                    st.rerun()
                else:
                    try:
                        from services.database import Database
                        db = Database()
                        user = db.verify_user(email, password)
                        
                        if user:
                            st.session_state.user_type = user["user_type"]
                            st.session_state.page = f"{user['user_type']}_home"
                            st.session_state.show_login_form = False
                            st.rerun()
                        else:
                            st.error(invalid_credentials)
                    except Exception as e:
                        st.error(f"Error during login: {str(e)}" if st.session_state.language == "en" else f"Giriş sırasında hata: {str(e)}")
    
    # Forgot password link
    st.markdown(f'<div style="text-align: center; margin-top: 15px; color: #666; font-size: 14px; cursor: pointer;">{forgot_password}</div>', unsafe_allow_html=True)
    
    # Language selector
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("ENGLISH", key="login_lang_en"):
            st.session_state.language = "en"
            st.rerun()
    with col2:
        if st.button("TÜRKÇE", key="login_lang_tr"):
            st.session_state.language = "tr"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def create_register_form():
    """Create the registration form with validation."""
    # Center content
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Large BAU text with blue background
    st.markdown('<div class="bau-header"><div class="bau-text">BAU</div></div>', unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back", key="back_to_login_screen_register"):
        st.session_state.show_register_form = False
        st.rerun()

    # Get page text based on language
    if st.session_state.language == "tr":
        register_title = "Yeni Hesap Oluştur"
        account_type_label = "Hesap Türü"
        name_label = "Tam İsim"
        email_label = "E-Posta"
        id_label = "Öğrenci/Profesör Kimlik No"
        department_label = "Bölüm"
        password_label = "Şifre"
        confirm_password_label = "Şifreyi Onayla"
        register_button = "KAYIT OL"
        student_text = "Öğrenci"
        professor_text = "Profesör"
        name_placeholder = "Tam adınızı girin"
        email_placeholder = "BAU e-posta adresinizi girin (@bahcesehir.edu.tr)"
        id_placeholder = "Kimlik numaranızı girin"
        department_placeholder = "Bölümünüzü girin"
        password_placeholder = "Bir şifre oluşturun"
        confirm_password_placeholder = "Şifrenizi onaylayın"
        email_error = "Lütfen BAU e-posta adresinizi kullanın (@bahcesehir.edu.tr)"
    else:
        register_title = "Create New Account"
        account_type_label = "Account Type"
        name_label = "Full Name"
        email_label = "Email"
        id_label = "Student/Professor ID"
        department_label = "Department"
        password_label = "Password"
        confirm_password_label = "Confirm Password"
        register_button = "REGISTER"
        student_text = "Student"
        professor_text = "Professor"
        name_placeholder = "Enter your full name"
        email_placeholder = "Enter your BAU email address (@bahcesehir.edu.tr)"
        id_placeholder = "Enter your ID"
        department_placeholder = "Enter your department"
        password_placeholder = "Create a password"
        confirm_password_placeholder = "Confirm your password"
        email_error = "Please use your BAU email address (@bahcesehir.edu.tr)"

    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #003B70; font-size: 2.5rem; font-weight: 800; margin-bottom: 10px;">
                {register_title}
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("register_form"):
        st.markdown("""
        <div style="background-color: white; border-radius: 10px; padding: 25px; 
        box-shadow: 0 4px 15px rgba(0, 59, 112, 0.1); margin-bottom: 20px; border: 1px solid rgba(0, 59, 112, 0.1);">
            <h3 style="color: #003B70; font-weight: 700; margin-bottom: 20px; font-size: 1.5rem;">Account Information</h3>
        """, unsafe_allow_html=True)
        
        # User type selection
        st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
        st.markdown(f'<div style="color: #666; font-size: 14px; margin-bottom: 5px;">{account_type_label}</div>', unsafe_allow_html=True)
        user_type = st.radio("Select account type", [student_text, professor_text], label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Full name field
        st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
        st.markdown(f'<div style="color: #666; font-size: 14px; margin-bottom: 5px;">{name_label}</div>', unsafe_allow_html=True)
        name = st.text_input("Full Name", placeholder=name_placeholder, key="name_input", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Email field
        st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
        st.markdown(f'<div style="color: #666; font-size: 14px; margin-bottom: 5px;">{email_label}</div>', unsafe_allow_html=True)
        email = st.text_input("Email Address", placeholder=email_placeholder, key="reg_email_input", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Student/Professor ID field
        st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
        st.markdown(f'<div style="color: #666; font-size: 14px; margin-bottom: 5px;">{id_label}</div>', unsafe_allow_html=True)
        student_id = st.text_input("Student/Professor ID", placeholder=id_placeholder, key="id_input", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Department field
        st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
        st.markdown(f'<div style="color: #666; font-size: 14px; margin-bottom: 5px;">{department_label}</div>', unsafe_allow_html=True)
        department = st.text_input("Department", placeholder=department_placeholder, key="dept_input", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Password field
        st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
        st.markdown(f'<div style="color: #666; font-size: 14px; margin-bottom: 5px;">{password_label}</div>', unsafe_allow_html=True)
        password = st.text_input("Password", type="password", placeholder=password_placeholder, key="reg_password_input", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Confirm password field
        st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
        st.markdown(f'<div style="color: #666; font-size: 14px; margin-bottom: 5px;">{confirm_password_label}</div>', unsafe_allow_html=True)
        confirm_password = st.text_input("Confirm Password", type="password", placeholder=confirm_password_placeholder, key="confirm_password_input", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        submit = st.form_submit_button(register_button, use_container_width=True)
        
        if submit:
            # Error messages based on language
            if st.session_state.language == "tr":
                error_fill_all = "Lütfen tüm alanları doldurun"
                error_name_format = "İsim sadece harfler ve boşluklar içermelidir"
                error_email_format = "Lütfen geçerli bir e-posta adresi girin"
                error_bau_email = email_error
                error_id_format = "Öğrenci/Profesör Kimlik No sadece rakamlardan oluşmalıdır"
                error_password_match = "Şifreler eşleşmiyor!"
                error_password_length = "Şifre en az 8 karakter uzunluğunda olmalıdır"
                error_password_uppercase = "Şifre en az bir büyük harf içermelidir"
                error_password_lowercase = "Şifre en az bir küçük harf içermelidir"
                error_password_digit = "Şifre en az bir rakam içermelidir"
                success_message = "Kayıt başarılı! Lütfen bilgilerinizle giriş yapın."
                error_saving = "Kullanıcı verisi kaydedilirken hata oluştu:"
            else:
                error_fill_all = "Please fill in all fields"
                error_name_format = "Name should contain only letters and spaces"
                error_email_format = "Please enter a valid email address"
                error_bau_email = email_error
                error_id_format = "Student/Professor ID should contain only numbers"
                error_password_match = "Passwords do not match!"
                error_password_length = "Password must be at least 8 characters long"
                error_password_uppercase = "Password must contain at least one uppercase letter"
                error_password_lowercase = "Password must contain at least one lowercase letter"
                error_password_digit = "Password must contain at least one number"
                success_message = "Registration successful! Please login with your credentials."
                error_saving = "Error saving user data:"
                
            # Validate all fields
            if not all([name, email, student_id, department, password, confirm_password]):
                st.error(error_fill_all)
            elif not name.replace(" ", "").isalpha():
                st.error(error_name_format)
            elif not "@" in email or not "." in email:
                st.error(error_email_format)
            elif not email.endswith("@bahcesehir.edu.tr"):
                st.error(error_bau_email)
            elif not student_id.isdigit():
                st.error(error_id_format)
            elif password != confirm_password:
                st.error(error_password_match)
            elif len(password) < 8:
                st.error(error_password_length)
            elif not any(c.isupper() for c in password):
                st.error(error_password_uppercase)
            elif not any(c.islower() for c in password):
                st.error(error_password_lowercase)
            elif not any(c.isdigit() for c in password):
                st.error(error_password_digit)
            else:
                # Store user data
                user_data = {
                    "name": name,
                    "email": email,
                    "student_id": student_id,
                    "department": department,
                    "user_type": user_type.lower(),
                    "password": password
                }
                
                # Save to database
                try:
                    from services.database import Database
                    db = Database()
                    db.register_user(user_data)
                    
                    st.success(success_message)
                    st.session_state.show_register_form = False
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"{error_saving} {str(e)}")
    
    # Language selector
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("ENGLISH", key="register_lang_en"):
            st.session_state.language = "en"
            st.rerun()
    with col2:
        if st.button("TÜRKÇE", key="register_lang_tr"):
            st.session_state.language = "tr"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def create_sidebar():
    with st.sidebar:
        # st.image("assets/logo.png", width=150)
        st.markdown("---")
        
        if st.session_state.user_type == "student":
            st.markdown("## Student Menu")
            
            if st.button("📋 Dashboard", key="student_dashboard", use_container_width=True):
                st.session_state.page = "student_home"
                st.rerun()
                
            if st.button("📝 Active Quizzes", key="student_quizzes", use_container_width=True):
                st.session_state.page = "student_home"
                st.rerun()
                
            if st.button("📊 Results", key="student_results", use_container_width=True):
                st.session_state.page = "student_results"
                st.rerun()
                
            if st.button("👤 Profile", key="student_profile", use_container_width=True):
                st.session_state.page = "profile"
                st.rerun()
        
        elif st.session_state.user_type == "professor":
            st.markdown("## Professor Menu")
            
            if st.button("📋 Dashboard", key="professor_dashboard", use_container_width=True):
                st.session_state.page = "professor_home"
                st.rerun()
                
            if st.button("📝 Create Quiz", key="professor_create_quiz", use_container_width=True):
                st.session_state.page = "professor_create_quiz"
                st.rerun()
                
            if st.button("📊 Analytics", key="professor_analytics", use_container_width=True):
                st.session_state.page = "professor_analytics"
                st.rerun()
                
            if st.button("👤 Profile", key="professor_profile", use_container_width=True):
                st.session_state.page = "profile"
                st.rerun()
        
        else:  # developer
            st.markdown("## Developer Menu")
            
            if st.button("📋 Dashboard", key="developer_dashboard", use_container_width=True):
                st.session_state.page = "developer_home"
                st.rerun()
                
            if st.button("🔌 API", key="developer_api", use_container_width=True):
                st.session_state.page = "developer_api"
                st.rerun()
                
            if st.button("📊 Logs", key="developer_logs", use_container_width=True):
                st.session_state.page = "developer_logs"
                st.rerun()
                
            if st.button("⚙️ Settings", key="developer_settings", use_container_width=True):
                st.session_state.page = "developer_settings"
                st.rerun()
                
            if st.button("👥 Users", key="developer_users", use_container_width=True):
                st.session_state.page = "developer_users"
                st.rerun()
        
        st.markdown("---")
        
        # Language Selection
        languages = {
            "en": "English",
            "tr": "Turkish"
        }
        
        selected_language = st.selectbox(
            "Language",
            options=list(languages.keys()),
            format_func=lambda x: languages[x],
            index=0 if st.session_state.language == "en" else 1
        )
        
        if selected_language != st.session_state.language:
            st.session_state.language = selected_language
            st.rerun()
        
        # TEMPORARY: Logout Button Hidden (Authentication Disabled)
        # TODO: Re-enable when authentication is restored
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        st.markdown("*Authentication temporarily disabled*", help="Login/logout functionality is currently disabled for easier access")
        
        # Logout functionality commented out for now
        # if st.button("🚪 Logout", use_container_width=True):
        #     # Save session state before logout
        #     try:
        #         from main import save_session_state
        #         save_session_state()
        #     except Exception as e:
        #         print(f"Failed to save session state: {e}")
        #         
        #     # Clear session state and return to login
        #     for key in list(st.session_state.keys()):
        #         if key != "language":  # Keep language preference
        #             del st.session_state[key]
        #     
        #     st.session_state.user_type = None
        #     st.session_state.page = "login"
        #     st.rerun() 