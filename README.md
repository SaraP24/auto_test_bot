# auto_test_bot
# Framework de Testing Inteligente y Autocurativo

## 🎯 Objetivo
Diseñar un framework de automatización de pruebas end-to-end con Playwright + TypeScript, que integre capacidades de self-healing, machine learning para detección de patrones de fallos, y generación de reportes inteligentes. El bot usa Python para el backend de IA y para el dashboard.

## Contenido de este README
- Descripción general del proyecto
- Módulos principales y arquitectura
- Requisitos e instalación (incluye instrucciones para Windows/PowerShell)
- Cómo ejecutar tests y el dashboard
- Notas sobre el módulo de IA y self-healing

## 🧱 Módulos del Proyecto

1) Playwright + TypeScript Core
  - Page Object Model + fixtures y utilidades.
  - Pruebas E2E y manejo de retries inteligentes.

2) Self-Healing Engine (Python + ML)
  - Analiza fallos y detecta patrones (selectores rotos, timeouts, errores de red).
  - Entrenamiento de modelos simples (scikit-learn) para clasificación de fallos.
  - Sugerencias automáticas de selectores usando BeautifulSoup y heurísticas.

3) Generative AI (resúmenes y explicaciones)
  - Integración opcional con OpenAI/HuggingFace para generar explicaciones y resúmenes.

4) Dashboard de Resultados (Streamlit / FastAPI / Flask)
  - Visualiza resultados de tests, fallos autocurados, y sugerencias del bot.

## 🛠️ Tech Stack

| Componente                           | Herramienta                                  |
|--------------------------------------|----------------------------------------------|
| Testing                              | Playwright + TypeScript                      |
| ML & Self-Healing                    | Python (scikit-learn, pandas, BeautifulSoup) |
| Generative AI                        | OpenAI API / HuggingFace Transformer         |
| Backend / Dashboard                  | Streamlit / FastAPI / Flask                  |
| CI/CD                                | GitHub Actions / Playwright Test Reporter    |

## 📂 Estructura del Proyecto (resumen)

```
auto_test_bot/
├── ai/                     # Módulos Python (healing, dashboard, análisis)
├── tests/                  # Casos de prueba E2E (Playwright)
├── pages/                  # Page Objects (TypeScript)
├── fixtures/               # Fixtures para Playwright
├── utils/                  # Helpers, Logger, Timeouts
├── reports/                # Reportes y trazas
└── README.md               # Este archivo (combinado)
```

## 🚀 Requisitos e Instalación (Python parte AI/Dashboard)

Requisitos mínimos:
- Python 3.8+
- pip

Archivo de dependencias: `requirements.txt` (en la raíz).

Instalación (recomendado: virtualenv):

PowerShell (Windows) — pasos rápidos:

```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\Activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar dashboard (Streamlit)
streamlit run ai/dashboard/app.py
```

Si `python -m venv venv` falla en Windows (mensaje como "no se encontró Python"), asegúrate de que Python esté instalado y accesible en PATH. Alternativas:
- Instalar Python desde https://www.python.org/downloads/ y marcar "Add Python to PATH" durante la instalación.
- Usar el alias correcto (`python3`) si aplica.

Notas: En algunas instalaciones de Windows, el mensaje sugiere instalar desde Microsoft Store; es preferible instalar la distribución oficial de python.org o usar una distribución gestionada (Anaconda / Miniconda) si lo prefieres.

## 🚀 Cómo Usar (Playwright + Dashboard)

Ejecutar tests (desde la raíz del proyecto):

```bash
npx playwright test
```

Genera reporte JSON para el dashboard en reports/report.json:

Ejecutar el dashboard (Streamlit):

PowerShell:
```powershell
venv\Scripts\Activate
streamlit run ai/dashboard/app.py
```

También hay scripts npm que pueden ayudar (ver `package.json`):
- `npm run create:venv` (si está definido)
- `npm run activate-venv` (activa el venv, si está definido)
- `npm run open-dashboard` (lanza la URL del dashboard)

## 🧠 Detalles del Módulo de Self-Healing

Flujo básico:
- Capturar errores tipo `locator not found` desde Playwright.
- Analizar el HTML actual con BeautifulSoup.
- Generar sugerencias de selectores en JSON para revisión o aplicación automática.

Ejemplo de sugerencia (JSON):

```json
{
  "LoginPage.usernameInput": {
    "original": "#user",
    "suggested": "input[name='username']"
  }
}
```

## 🧠 Etapas de Desarrollo del Proyecto

- Etapa 1: Arquitectura Playwright + POM + fixtures
- Etapa 2: Self-healing engine en Python
- Etapa 3: Generación de explicaciones con LLMs
- Etapa 4: Predictor de fallos con ML
- Etapa 5: Integración con CI/CD y notificaciones

## 📋 TODO

- [ ] Completar módulo de self-healing
- [ ] Integrar clasificador de errores
- [ ] Implementar predictor de fallos
- [ ] Mejorar dashboard con visualizaciones
