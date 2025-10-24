# Auto Test Bot Framework

## Overview
This framework provides tools for DOM analysis and a self-healing dashboard for error reporting.

## Requirements
- Python 3.8+
- pip

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/auto_test_bot.git
   cd auto_test_bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Framework

### On macOS
1. Run the application:
   ```bash
   python3 main.py
   ```
2. Install stramlint app not working
  ```bash
pip3 install streamlit
```

### On Windows
1. Run the application:
   ```cmd
   python main.py
   ```

## Notes
- Ensure all dependencies are installed before running the application.
- Use `python3` instead of `python` if Python 2 is the default on your system.



GENERAR ENV VIRTUAL PARA USAR
- Ejecutá estos comandos uno tras otro desde la raíz del proyecto:

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


Y luego:

python main.py


(Usarás el python del entorno virtual, así evitás conflictos entre versiones o instalaciones globales.)


## How to run auto test bot in CLI

### How to use this tool
1. **Generate Report**: You can run your tests with Playwright and generate a JSON report using `--reporter=json`.
2. **Place Report**: Make sure the report is located at `reports/report.json`.
3. **Run Dashboard**: Run this dashboard with `streamlit run ai/dashboard/app.py`.

#### Powershell
#### Option 1
1) venv\Scripts\activate
2) streamlit run ai/dashboard/app.py 
 
#### Option 2 
1) npm run activate-venv
2) npm run open-dashboard 

### To review the dashboard
`npm run open-dashboard` should be executed in the Streamlit terminal.

How to activate it? 
`npm run activate-venv`  
`streamlit run ai/dashboard/app.py`  
`npm run open-dashboard`  
