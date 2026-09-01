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

# --- THE WEATHER COMPANY CUSTOM STYLING (CSS) ---
# --- THE WEATHER COMPANY CUSTOM STYLING (CSS) ---
WEATHER_THEME_CSS = """
<style>
    /* Global Styles */
    .stApp {
        background-color: #f4f7f9;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Top Header Banner with Logo */
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
    .weather-header img {
        height: 65px;
        background-color: #ffffff;
        padding: 6px;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
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
    .stTextInput label {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        color: #003366 !important;
        margin-bottom: 8px !important;
    }
    
    div[data-baseweb="input"] {
        border: 2.5px solid #00509e !important;
        border-radius: 10px !important;
        background-color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(0, 80, 158, 0.12) !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-baseweb="input"]:hover {
        border-color: #002244 !important;
        box-shadow: 0 6px 18px rgba(0, 80, 158, 0.22) !important;
    }

    div[data-baseweb="input"] input {
        font-size: 1.1rem !important;
        padding: 12px 14px !important;
        color: #1a1a1a !important;
    }
    
    /* Card Container */
    .weather-card {
        background-color: #ffffff;
        border: 1px solid #e1e8ed;
        border-radius: 10px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #00509e !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 12px 28px !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #003366 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    /* Links */
    a.weather-link-btn {
        display: inline-block;
        background-color: #28a745;
        color: white !important;
        padding: 12px 20px;
        text-decoration: none;
        border-radius: 6px;
        font-weight: bold;
        margin-top: 15px;
    }
    a.weather-link-btn:hover {
        background-color: #218838;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #002244;
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
</style>
"""

st.markdown(WEATHER_THEME_CSS, unsafe_allow_html=True)

# --- BRANDED HEADER WITH LOGO ---
st.markdown("""
<div class="weather-header">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/The_Weather_Channel_logo.svg/320px-The_Weather_Channel_logo.svg.png" alt="TWC Logo">
    <div>
        <h1>The Weather Company — Data Package Configurator</h1>
        <p>Layman Requirements Scraper & API Package Alignment Engine</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR: API SETUP ---
# --- SIDEBAR: API SETUP ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/1/15/The_Weather_Channel_logo.svg", width=120)
    st.header("Admin Controls")
    
    # Automatically check Streamlit Secrets first; fallback to text box if missing
    if "OPENAI_API_KEY" in st.secrets:
        openai_api_key = st.secrets["OPENAI_API_KEY"]
        st.success("✅ OpenAI API Key loaded automatically!")
    else:
        openai_api_key = st.text_input("OpenAI API Key", type="password")
        st.caption("Configured for automated crawling of Weather.com developer docs.")

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

# --- INPUT SECTION ---
col1, col2 = st.columns([2, 1])

with col1:
    user_query = st.text_input(
        "Describe your client's data requirement (in plain layman terms):",
        placeholder="e.g., I need historical wind speeds and gust alerts in Poland for insurance claims."
    )

with col2:
    source_url = st.text_input(
        "Weather Documentation URL:",
        value="https://developer.weather.com/docs/home"
    )

generate_btn = st.button("Generate Tailored Solution Package")

# --- EXECUTION PIPELINE ---
if generate_btn:
    if not openai_api_key:
        st.error("Please provide an OpenAI API Key in the sidebar.")
    elif not user_query or not source_url:
        st.error("Please fill in all fields.")
    else:
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
                
                Build a crisp, modern package summary for the client.
                Format using clean HTML/Markdown with headers and bullet points:
                1. Package Title & Summary (Layman summary)
                2. Included Data Features (Translate technical terms to simple plain-English capabilities)
                3. Business Value & Alignment (Why this fits their exact query)
                """

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": package_prompt}]
                )
                
                result_text = response.choices[0].message.content

                # --- RESULT DISPLAY CARD ---
                st.markdown(f"""
                <div class="weather-card">
                    {result_text}
                    <hr style="border:0; border-top:1px solid #e1e8ed; margin: 20px 0;">
                    <a href="{source_url}" target="_blank" class="weather-link-btn">
                        🔗 Open Scraped Source Documentation ({source_url})
                    </a>
                </div>
                """, unsafe_allow_html=True)
