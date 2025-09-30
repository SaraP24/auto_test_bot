import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from ai.healing.report_analyzer import analyze_report


st.title("🧠 Self-Healing Dashboard")
suggestions = analyze_report()

if suggestions:
    for title, error, fix in suggestions:
        st.error(f"❌ {title} — {error}")
        st.info(f"💡 Sugerencia: {fix}")
else:
    st.success("✅ No se detectaron errores críticos.")