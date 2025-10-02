# auto_test_bot
# Framework de Testing Inteligente y Autocurativo

## 🎯 Objetivo
Diseñar un framework de automatización de pruebas end-to-end con Playwright + TypeScript, que integre capacidades de self-healing, machine learning para detección de patrones de fallos, y generación de reportes inteligentes. El bot usará Python para el backend de IA.

## 🧱 Módulos del Proyecto

### 1. Playwright + TypeScript Core
- Modulariza el framework con Page Object Model + Fixtures.
- Implementa pruebas para una web page.
- Añade lógica de retry inteligente y logging personalizado.

### 2. Self-Healing Engine (Python + ML)
- Usa Python para analizar logs de fallos y detectar patrones (por ejemplo, cambios en selectores).
- Entrena un modelo simple (Random Forest o SVM) para predecir si un test fallará por selector roto, timeout, o error de red.
- Implementa un sistema de sugerencias: si el test falla por selector, propone alternativas usando BeautifulSoup + heurísticas.

### 3. Auto-Resumen de PRs y Fallos (Generative AI)
- Usa una API de LLM (puede ser OpenAI o HuggingFace) para:
  - Resumir pull requests.
  - Generar explicaciones de fallos en lenguaje humano.
  - Proponer fixes con tono sarcástico si el error es obvio.

### 4. Dashboard de Resultados
- Usa Python + Flask o FastAPI para mostrar:
  - Resultados de tests.
  - Fallos autocurados.
  - Sugerencias del bot.
  - Gráficos de predicción de fallos.

## 🛠️ Tech Stack

| Componente | Herramienta |
|------------|-------------|
| Testing | Playwright + TypeScript |
| ML & Self-Healing | Python (scikit-learn, pandas, BeautifulSoup) |
| Generative AI | OpenAI API / HuggingFace Transformer |
| Backend opcional - Results Dashboard | FastAPI / Flask / Streamlit |
| CI/CD | GitHub Actions / Playwright Test Reporter |

## 📂 Estructura del Proyecto

```
AutoTestBot/
├── tests/                  # Casos de prueba E2E
├── pages/                  # Page Objects
├── utils/                  # Logger, manejo de errores, helpers
├── fixtures/               # Fixtures para setup/teardown
├── interfaces/             # Interfaces TypeScript
├── config/                 # Configuración Playwright
├── reports/                # Evidencias y trazas
├── ai/                     # Módulos Python para ML y generación
│   ├── healing/           # Self-healing engine
│   ├── modules/           # Clasificador, clustering, predictor
│   └── dashboard/         # Dashboard de resultados
└── README.md              # Documentación técnica
```

## 🚀 Cómo Usar

### Ejecutar Tests
```bash
npx playwright test
```

### Dashboard de Resultados

#### Requisitos previos
1. **Generar Reporte**: Corre tus tests con Playwright y genera un reporte JSON usando `--reporter=json`.
2. **Colocar Reporte**: Asegurate de que el reporte esté en `reports/report.json`.

#### Opción 1: PowerShell
```powershell
# Activar entorno virtual
venv\Scripts\activate

# Ejecutar dashboard
streamlit run ai/dashboard/app.py
```

#### Opción 2: NPM Scripts
```bash
# Activar entorno virtual
npm run activate-venv

# Abrir dashboard
npm run open-dashboard
```

#### Comandos disponibles
```bash
npm run activate-venv        # Activa el entorno virtual Python
npm run open-dashboard       # Ejecuta el dashboard con Streamlit
```

## 🧠 Etapas de Desarrollo

### Etapa 1: Fundamentos del Framework (Playwright + TypeScript)
**Objetivos:**
- Implementar una arquitectura modular basada en Page Object Model.
- Incorporar utilitarios reutilizables para logging, manejo de errores y configuración.
- Establecer una base sólida para escalar hacia inteligencia artificial y bots.

**Buenas prácticas:**
- Tipado estricto con TypeScript.
- Uso de fixtures para setup/teardown.
- Logging estructurado con niveles (info, warning, error).
- Configuración de retries, screenshots y trace viewer.

### Etapa 2: Módulo de Self-Healing (Python)
**Objetivos:**
- Detectar fallos por cambios en el DOM (selectores rotos).
- Sugerir alternativas de localización mediante heurísticas y scraping.

**Implementación:**
- Captura de errores `locator not found`.
- Análisis del HTML con BeautifulSoup.
- Generación de sugerencias en formato JSON para revisión manual o aplicación automática.

```json
{
  "LoginPage.usernameInput": {
    "original": "#user",
    "suggested": "input[name='username']"
  }
}
```

### Etapa 3: Generación de Explicaciones y Documentación (IA Generativa)
**Objetivos:**
- Interpretar logs de errores y generar explicaciones técnicas.
- Automatizar resúmenes de pull requests y documentación de pruebas.

**Implementación:**
- Integración con OpenAI API o HuggingFace.
- Prompts estructurados para generar contenido técnico y contextual.
- Posibilidad de exportar reportes en Markdown o HTML.

### Etapa 4: Predicción de Fallos (Machine Learning)
**Objetivos:**
- Anticipar fallos antes de ejecutar pruebas.
- Identificar patrones de inestabilidad en el sistema bajo prueba.

**Implementación:**
- Dataset: logs históricos de ejecución.
- Features: duración, tipo de test, cambios recientes, frecuencia de fallos.
- Modelo: Random Forest o XGBoost.
- Output: probabilidad de fallo + recomendación preventiva.

### Etapa 5: Integración con Bots y CI/CD
**Objetivos:**
- Notificar resultados y sugerencias vía Discord o Slack.
- Ejecutar pruebas desde comandos del bot.
- Integración con GitHub Actions para ejecución continua.

## 💡 Bonus Ideas
- Entrena el bot para reconocer patrones de errores comunes en tu equipo.
- Haz que el bot aprenda de los fixes que tú aplicás manualmente.

## 📋 TODO

### Pipeline de Datos y ML
```
[Scraping] → [JSON5] → [Pandas] → [ML con scikit-learn] → [Visualización con Plotly] → [Resumen con OpenAI]
```

### Próximos Pasos
- [ ] Completar módulo de self-healing
- [ ] Integrar clasificador de errores
- [ ] Implementar predictor de fallos
- [ ] Mejorar dashboard con más visualizaciones
- [ ] Añadir integración con bots de comunicación
- [ ] Automatizar generación de documentación con IA
