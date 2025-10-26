import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import plotly.express as px
import json

from ai.healing import report_analyzer as analyzer


st.set_page_config(layout='wide')
st.title("🧠 Self-Healing Dashboard")

# Sidebar: controls
st.sidebar.header("Report settings")
report_path = st.sidebar.text_input('Report path', value='reports/report.json')
uploaded = st.sidebar.file_uploader('Or upload report (JSON)', type=['json'])
dedupe = st.sidebar.checkbox('Deduplicate results', value=True, help='Group suggestions by (test,title, error type)')


@st.cache_data
def cached_load(path: str):
    return analyzer.load_report(path=path)


def load_parsed_report():
    if uploaded is not None:
        try:
            content = uploaded.read()
            parsed = json.loads(content.decode('utf-8'))
            return parsed
        except Exception as e:
            st.sidebar.error(f"Error parsing uploaded file: {e}")
            return None
    # else try cached load from disk
    try:
        return cached_load(report_path)
    except Exception as e:
        st.sidebar.error(f"Error loading report from path: {e}")
        return None


parsed = load_parsed_report()

if parsed is None:
    st.warning("No report loaded yet. Please provide a valid JSON report or path.")
else:
    # Ask analyzer for detailed suggestions (including raw message and parsed location)
    suggestions = analyzer.analyze_report(report=parsed, dedupe=dedupe, return_details=True)
    if suggestions:
        st.subheader("❌ Suggestions")
        for item in suggestions:
            # support both legacy (title, error, fix) and new (title, error, fix, details)
            if len(item) == 4:
                title, error, fix, details = item
            else:
                title, error, fix = item
                details = {}

            with st.expander(f"{title} — {error}"):
                st.write(f"Sugerencia: {fix}")
                # show raw message if available
                if details.get('message'):
                    st.markdown(f"**Mensaje:** `{details.get('message')}`")
                # show parsed location if available
                if details.get('parsed_location'):
                    pl = details.get('parsed_location')
                    loc_parts = []
                    if pl.get('file'):
                        loc_parts.append(f"file: {pl.get('file')}")
                    if pl.get('line'):
                        loc_parts.append(f"line: {pl.get('line')}")
                    if pl.get('col'):
                        loc_parts.append(f"col: {pl.get('col')}")
                    st.write('Parsed location: ' + ', '.join(loc_parts))
                # show stack if present
                if details.get('stack'):
                    st.code(details.get('stack'))
    else:
        st.success("✅ Critical errors not found!")

    st.subheader("📊 Errors distribution")
    stats = analyzer.get_error_stats(report=parsed, dedupe=dedupe)
    fig = px.pie(
        names=list(stats.keys()),
        values=list(stats.values()),
        title="Error Types Distribution",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig, use_container_width=True)

