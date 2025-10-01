import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import plotly.express as px
from ai.healing.report_analyzer import analyze_report
from ai.healing.report_analyzer import get_error_stats


st.title("🧠 Self-Healing Dashboard")
suggestions = analyze_report()

if suggestions:
    for title, error, fix in suggestions:
        st.error(f"❌ {title} — {error}")
        st.info(f"💡 Sugerencia: {fix}")
else:
    st.success("✅ Critical errors not found!")

    st.subheader("📊 Errors distribution")

stats = get_error_stats()
fig = px.pie(
    names=list(stats.keys()),
    values=list(stats.values()),
    title="Error Types Distribution",
    color_discrete_sequence=px.colors.qualitative.Set3
)
st.plotly_chart(fig, use_container_width=True)

