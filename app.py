import streamlit as st
import json
import time
from groq import Groq

client = Groq(api_key="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")

if 'total_requests' not in st.session_state:
    st.session_state.total_requests = 0
if 'total_latency' not in st.session_state:
    st.session_state.total_latency = 0
if 'success_count' not in st.session_state:
    st.session_state.success_count = 0
if 'last_json' not in st.session_state:
    st.session_state.last_json = None

def process_pipeline(user_prompt):
    start_time = time.time()
    
    s1 = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": "Extract features as JSON. Structure it logically."},
                  {"role": "user", "content": user_prompt}],
        response_format={"type": "json_object"}
    )
    
    s2 = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": "Generate detailed DB and API schema JSON. Ensure all relationships and data types (integer, varchar, boolean, etc.) are explicitly defined."},
                  {"role": "user", "content": s1.choices[0].message.content}],
        response_format={"type": "json_object"}
    )
    
    end_time = time.time()
    latency = round(end_time - start_time, 2)
    
    return json.loads(s2.choices[0].message.content), latency

st.set_page_config(page_title="AI Platform Compiler", layout="wide")
st.title("Founding Intern Task: AI Platform Compiler 🚀")

st.subheader("System Performance Dashboard")
col1, col2, col3, col4 = st.columns(4)

avg_latency = round(st.session_state.total_latency / st.session_state.total_requests, 2) if st.session_state.total_requests > 0 else 0
success_rate = round((st.session_state.success_count / st.session_state.total_requests) * 100, 2) if st.session_state.total_requests > 0 else 0

col1.metric("Total Requests", st.session_state.total_requests)
col2.metric("Success Rate", f"{success_rate}%")
col3.metric("Avg Latency", f"{avg_latency}s")
col4.metric("Pipeline Stages", "3 Stages")

st.divider()

user_input = st.text_area("Enter App Requirements:", "Enter the Prompt")

if st.button("Execute Pipeline"):
    try:
        with st.spinner("Processing through 3-Stage Pipeline..."):
            final_config, latency = process_pipeline(user_input)
            
            st.session_state.total_requests += 1
            st.session_state.success_count += 1
            st.session_state.total_latency += latency
            st.session_state.last_json = final_config # Saving result
            
            st.success(f"Validated JSON Generated in {latency}s!")
            st.rerun()

    except Exception as e:
        st.session_state.total_requests += 1
        st.error(f"System Error: {e}")

if st.session_state.last_json:
    st.subheader("Final System Configuration (Database & API Schema)")
    st.json(st.session_state.last_json)