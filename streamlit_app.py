import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

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
    if not openai_api_key:
        st.error("OpenAI API Key is missing. Please ensure OPENAI_API_KEY is configured in Streamlit Secrets.")
    elif not user_query or not source_url:
        st.error("Please fill in your required needs.")
    else:
        with st.spinner("Scraping documentation & aligning package..."):
            scraped_text, error = scrape_webpage(source_url)
            
            if error:
                st.error(f"Error scraping docs: {error}")
            else:
                client = OpenAI(api_key=openai_api_key)
                
                # UPDATED PROMPT: Explicitly matches against the "Packages" section on the website
                package_prompt = f"""
                You are a Solution Architect for The Weather Company.
                
                SCRAPED DOCS CONTENT FROM WEBSITE:
                {scraped_text[:12000]}
                
                CLIENT NEED (QUERY):
                "{user_query}"
                
                INSTRUCTIONS:
                1. Look through the scraped text specifically for the section/header labeled "Packages" (or official package offerings listed on the website).
                2. Identify the EXACT official Package name(s) listed under that Packages section that contain the endpoints/data needed for the client's request.
                3. Structure the output into 4 clear sections using Markdown:

                   - 📦 **Official Website Package Match** (State the EXACT package name(s) as listed under the 'Packages' header on the website).
                   - 🏷️ **Endpoints Residing in this Package** (List the specific API endpoints/data fields from the page that belong to this package).
                   - 🛠️ **Included Capabilities (Layman's Terms)** (Explain what the endpoints inside this package actually do in simple plain English).
                   - 🎯 **Business Alignment** (Explain why subscribing to this specific package fulfills the client's requirements).
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
