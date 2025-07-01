import streamlit as st
import requests
import fitz  # PyMuPDF
from datetime import datetime
from markdown2 import markdown

# Set OpenRouter API key
openai_api_key = st.secrets["openai_api_key"]

st.set_page_config(page_title="Health Checkup Analyzer", layout="wide")

st.title("🏥 Health Checkup Analyzer")
st.write("Upload a PDF health report and get analysis powered by AI.")

uploaded_file = st.file_uploader("📄 Upload your health report (PDF)", type="pdf")
language = st.selectbox("Select Language", ["English", "Hindi"])
patient_name = st.text_input("Patient Name (Optional)", value="Patient")

if uploaded_file:
    st.success("✅ PDF Uploaded Successfully")
    with st.spinner("📤 Extracting text from PDF..."):
        try:
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            extracted_text = ""
            for page in doc:
                extracted_text += page.get_text()
            st.success(f"✅ Extracted {len(extracted_text)} characters from PDF")
        except Exception as e:
            st.error(f"❌ Error extracting text: {e}")
            st.stop()

    # Generate analysis using OpenRouter (GPT)
    st.subheader("🧠 AI Analysis Result")
    with st.spinner("🔍 Analyzing report using AI..."):
        try:
            system_prompt = "You are a helpful medical assistant that explains health checkup reports to patients in easy language. Include medical explanation, possible health issues, dietary tips, and recommendations."
            if language == "Hindi":
                system_prompt = "आप एक सहायक मेडिकल असिस्टेंट हैं जो हेल्थ रिपोर्ट को आसान हिंदी में समझाते हैं। कृपया मरीज की रिपोर्ट पढ़कर उसका सारांश, संभावित समस्याएं, डाइट टिप्स और सलाह दें।"

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openchat/openchat-3.5-1210",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": extracted_text}
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.7
                }
            )
            result = response.json()
            final_answer = result["choices"][0]["message"]["content"]
            clean_html = markdown(final_answer)
            st.markdown(clean_html, unsafe_allow_html=True)

            # Offer download
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"health_analysis_{patient_name.replace(' ', '_').lower()}_{now}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(clean_html)
            with open(filename, "rb") as f:
                st.download_button("📥 Download Full Report", f, file_name=filename)
        except Exception as e:
            st.error(f"Error analyzing health report: {e}")