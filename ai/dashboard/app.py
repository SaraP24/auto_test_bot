import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import plotly.express as px
import json

from ai.healing import report_analyzer as analyzer


st.set_page_config(layout='wide')
st.title("🧯 Self-Healing Test Dashboard 🧯")

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
        st.subheader("❌ Suggestions for Fixing Tests ")
        for item in suggestions:
            # support both legacy (title, error, fix) and new (title, error, fix, details)
            if len(item) == 4:
                title, error, fix, details = item
            else:
                title, error, fix = item
                details = {}

            with st.expander(f"{title} — {error}", expanded=False):
                # Show trace-based suggestion (if analyzer produced one)
                trace_sugg = details.get('trace_suggestion') if isinstance(details, dict) else None
                if trace_sugg:
                    st.markdown('**Suggestion (from trace):**')
                    st.write(trace_sugg)

                # Show only the stack trace per user preference. If none is available,
                # display a short note so the UI doesn't look empty.
                stack = details.get('stack') if isinstance(details, dict) else None
                if stack:
                    st.markdown('**Stack trace:**')
                    st.code(stack, language='')

                    # Show source snippet when available (file + surrounding lines)
                    src = details.get('source_snippet') if isinstance(details, dict) else None
                    if src:
                        # Create a columns layout: file/line info on left, "Open in Editor" button on right
                        col1, col2 = st.columns([0.7, 0.3])
                        with col1:
                            st.markdown(f"**Source:** `{src.get('file')}` (line {src.get('line')})")
                        with col2:
                            # Create VS Code URL: vscode://file/absolute/path:line
                            file_path = src.get('file')
                            if file_path:
                                line = src.get('line', 1)
                                vscode_url = f"vscode://file/{file_path}:{line}"
                                st.link_button("🔍 Abrir en Editor", vscode_url)

                        # pick language from extension for code highlighting
                        ext = os.path.splitext(src.get('file'))[1].lower()
                        lang_map = {'.ts': 'typescript', '.tsx': 'tsx', '.js': 'javascript', '.py': 'python', '.java': 'java'}
                        lang = lang_map.get(ext, '')
                        st.markdown('**Source snippet:**')
                        st.code(src.get('snippet', ''), language=lang)
                else:
                    st.info('No stack trace available for this error.')
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

