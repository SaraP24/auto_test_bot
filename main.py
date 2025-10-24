import sys
from ai.dashboard.app import st

if __name__ == "__main__":
    try:
        st.run()
    except Exception as e:
        print(f"Error running the application: {e}")
        sys.exit(1)
