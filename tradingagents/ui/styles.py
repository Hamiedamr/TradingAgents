
import streamlit as st

def apply_styles():
    """Apply custom CSS for a premium, ChatGPT-like feel."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

        /* Global Font */
        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #1e1e1e; /* Darker sidebar */
            border-right: 1px solid #333;
        }

        /* Chat Message Styling */
        .stChatMessage {
            background-color: #2b2b2b;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
            border: 1px solid #3e3e3e;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow-wrap: anywhere; /* Force break long words/URLs */
            word-break: break-word;   /* detailed wrapping */
        }
        
        /* User Message Specifics */
        .stChatMessage[data-testid="stChatMessage"][aria-label="user"] {
            background-color: #3b3b3b;
        }

        /* Assistant/AI Message Specifics */
        .stChatMessage[data-testid="stChatMessage"][aria-label="assistant"] {
            background-color: transparent;
            border: none;
            box-shadow: none;
            /* Ensure content inside assistant messages also wraps */
            overflow-wrap: anywhere;
            word-break: break-word;
        }

        /* Input Button Styling */
        .stButton button {
            background-color: #10a37f; /* OpenAI Green-ish */
            color: white;
            border-radius: 6px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.2s ease;
            width: 100%;
        }
        .stButton button:hover {
            background-color: #0d8a6a;
            border-color: #0d8a6a;
            box-shadow: 0 2px 8px rgba(16, 163, 127, 0.4);
        }

        /* Headers */
        h1, h2, h3 {
            color: #ececf1;
            font-weight: 600;
        }
        
        /* Markdown Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1em 0;
            border-radius: 8px;
            overflow: hidden;
        }
        th {
            background-color: #343541;
            color: #ececf1;
            padding: 12px;
            text-align: left;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #4d4d4f;
            color: #d1d5db;
        }
        
        /* Spinner */
        .stSpinner > div {
            border-top-color: #10a37f !important;
        }
        </style>
    """, unsafe_allow_html=True)
