## How to run auto test bot in CLI

### Cómo usar esta herramienta
1. **Generar Reporte**: Corre tus tests con Playwright y genera un reporte JSON usando `--reporter=json`.
2. **Colocar Reporte**: Asegurate de que el reporte esté en `reports/report.json`.
3. **Ejecutar Dashboard**: Corre este dashboard con `streamlit run ai/dashboard/app.py`.

#### Powershell
#### Option 1
1) venv\Scripts\activate
2) streamlit run ai/dashboard/app.py 
 
#### Option 2 
1) npm run activate-venv
2) npm run open-dashboard 


### Para revisar dashboard
npm run open-dashboard debe tirarse en terminal strimlit
como se activa? 
npm run activate-venv
streamlit run ai/dashboard/app.py 
npm run open-dashboard 