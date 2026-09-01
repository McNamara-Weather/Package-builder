import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import re  # Used for Regular Expression PII & Company Name Detection

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Weather Data Package Builder | Powered by The Weather Company Docs", 
    page_icon="🌤️", 
    layout="wide"
)

# --- AUTOMATIC API KEY FETCH FROM SECRETS ---
if "OPENAI_API_KEY" in st.secrets:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
else:
    openai_api_key = ""

# --- SECURITY GUARDRAIL FUNCTION (PII & COMPANY NAME SCANNER) ---
def check_for_restricted_data(text):
    """
    Scans input text for sensitive PII and Company/Organization Name patterns.
    Returns (True, "Type") if detected, otherwise (False, None).
    """
    patterns = {
        "Social Security Number (SSN)": r'\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b',
        "Credit/Debit Card Number": r'\b(?:\d[ -]*?){13,16}\b',
        "Email Address": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        "Phone Number": r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        # Detects corporate identifiers (Inc, LLC, Corp, Ltd, Company, Group, GmbH, Holdings, etc.)
        "Company / Organization Name": r'\b[A-Za-z0-9&.\'-]+\s+(?:Inc|Inc\.|LLC|Corp|Corp\.|Corporation|Ltd|Ltd\.|Limited|Co|Company|Group|Holdings|GmbH|PLC)\b'
    }
    
    for data_type, pattern in patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            return True, data_type
            
    return False, None

# --- THE WEATHER COMPANY CUSTOM STYLING (CSS) ---
WEATHER_THEME_CSS = """
<style>
    /* Global Styles */
    .stApp {
        background-color: #f4f7f9;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Top Header Banner */
    .weather-header {
        background: linear-gradient(135deg, #003366 0%, #00509e 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .weather-header h1 {
        color: #ffffff !important;
        font-weight: 700;
        margin: 0;
        font-size: 2.2rem;
    }
    .weather-header p {
        color: #b0c4de !important;
        margin-top: 5px;
        font-size: 1.05rem;
        margin-bottom: 0;
    }

    /* --- PROMINENT SEARCH INPUT FIELD STYLING --- */
    div[data-testid="stTextInput"] label {
        font-size: 1.35rem !important;
        font-weight: 800 !important;
        color: #002244 !important;
        margin-bottom: 12px !important;
    }
    
    div[data-testid="stTextInput"] > div,
    div[data-testid="stTextInput"] div[data-baseweb="input"] {
        border: 3px solid #003366 !important;
        border-radius: 12px !important;
        background-color: #ffffff !important;
        box-shadow: 0 6px 18px rgba(0, 51, 102, 0.18) !important;
        padding: 2px !important;
    }
    
    div[data-testid="stTextInput"] > div:hover,
    div[data-testid="stTextInput"] > div:focus-within {
        border-color: #00509e !important;
        box-shadow: 0 8px 22px rgba(0, 80, 158, 0.3) !important;
    }

    div[data-testid="stTextInput"] input {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        padding: 12px 16px !important;
        color: #000000 !important;
    }
    
    /* Buttons */
    .stButton>button, div[data-testid="stFormSubmitButton"]>button {
        background-color: #00509e !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 12px 28px !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover, div[data-testid="stFormSubmitButton"]>button:hover {
        background-color: #003366 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
</style>
"""

st.markdown(WEATHER_THEME_CSS, unsafe_allow_html=True)

# --- BRANDED HEADER WITH EMBEDDED LOGO ---
st.markdown("""
<div class="weather-header">
    <svg width="65" height="65" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0;">
        <rect width="120" height="120" rx="20" fill="#00509e"/>
        <path d="M 30,65 A 20,20 0 0,1 65,50 A 25,25 0 0,1 100,65 A 15,15 0 0,1 95,90 L 30,90 A 15,15 0 0,1 30,65 Z" fill="#ffffff"/>
        <circle cx="45" cy="42" r="14" fill="#ffcc00"/>
    </svg>
    <div>
        <h1>The Weather Company — Data Package Configurator</h1>
        <p>Layman Requirements Scraper & API Package Alignment Engine</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SCRAPER FUNCTION ---
def scrape_webpage(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            tag.decompose()
            
        content_tags = soup.find_all(['h1', 'h2', 'h3', 'p', 'li', 'td', 'th'])
        clean_lines = [tag.get_text(strip=True) for tag in content_tags if len(tag.get_text(strip=True)) > 5]
        return "\n".join(clean_lines), None
    except Exception as e:
        return None, str(e)

# --- INPUT FORM (ENABLES ENTER KEY TO EXECUTE SEARCH) ---
with st.form(key="search_form", border=False):
    col1, col2 = st.columns([2, 1])

    with col1:
        user_query = st.text_input(
            "Type off of your required needs",
            placeholder="e.g., I need historical wind speeds and gust alerts in Poland for insurance claims."
        )

    with col2:
        source_url = st.text_input(
            "Weather Documentation URL:",
            value="https://developer.weather.com/docs/home"
        )

    generate_btn = st.form_submit_button("Generate Tailored Solution Package")

# Refresh button placed cleanly outside form
if st.button("🔄 Refresh Page"):
    st.rerun()

# --- EXECUTION PIPELINE ---
if generate_btn:
    # 🛑 SECURITY CHECK: Scan for PII and Company Names
    has_restricted_data, data_type = check_for_restricted_data(user_query)
    
    if has_restricted_data:
        st.error(
            f"⚠️ **Security Alert: Restricted Information Detected ({data_type}).**\n\n"
            f"For privacy and compliance reasons, queries containing personal data (SSNs, credit cards, emails, phone numbers) "
            f"or specific company/organization names cannot be processed. Please remove this information and try again."
        )
    elif not openai_api_key:
        st.error("OpenAI API Key is missing. Please ensure OPENAI_API_KEY is configured in Streamlit Secrets.")
    elif not user_query or not source_url:
        st.error("Please fill in your required needs.")
    else:
        # Proceed with scraping & generating response
        with st.spinner("Scraping documentation & aligning package..."):
            scraped_text, error = scrape_webpage(source_url)
            
            if error:
                st.error(f"Error scraping docs: {error}")
            else:
                client = OpenAI(api_key=openai_api_key)
                
                package_prompt = f"""
                You are a Solution Architect for The Weather Company.
                SCRAPED DOCS CONTENT: {scraped_text[:10000]}
                CLIENT NEED: "{user_query}"
                
                Build a crisp, executive solution package for the client.
                Format using clean Markdown with headers and bullet points:

                1. 📦 **Recommended Package Name & Executive Summary** (Layman summary of the total solution).
                2. 🏷️ **Required API Packages & Endpoints** (Specify EXACTLY which Weather Company package tier or API product—e.g., Core Weather Data, Historical On-Demand Package, Severe Weather Package, Location Services—each suggested endpoint resides in).
                3. 🛠️ **Included Capabilities** (Translate technical parameters into simple plain-English features/benefits).
                4. 🎯 **Business Value & Alignment** (Explain why this specific package combination fits their exact query).
                """

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": package_prompt}]
                )
                
                result_text = response.choices[0].message.content

                # --- RESULT DISPLAY CARD ---
                st.markdown("---")
                st.markdown(result_text)
                st.divider()
                st.link_button(f"🔗 Open Scraped Source Documentation ({source_url})", source_url)
