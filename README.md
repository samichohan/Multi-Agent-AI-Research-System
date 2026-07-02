# 🧠 Research Intelligence — Multi-Agent AI Research System

An autonomous multi-agent pipeline that researches any topic end-to-end: it **searches** the web, **reads** the most relevant source in depth, **writes** a structured research report, and **critiques** its own work — all orchestrated with LangChain/LangGraph agents and served through a polished Streamlit UI.

---

## ✨ Features

- 🔍 **Search Agent** — queries the web (via Tavily) for recent, reliable sources on the given topic
- 📖 **Reader Agent** — picks the most relevant result and scrapes the page for deeper content
- ✍️ **Writer Chain** — synthesizes the research into a structured, professional report (Introduction, Key Findings, Conclusion, Sources)
- 🧐 **Critic Chain** — independently reviews the generated report and scores it out of 10, with strengths, areas to improve, and a verdict
- 🖥️ **Streamlit UI** — dark, production-styled interface with:
  - Live pipeline status panel (see each agent's progress in real time)
  - Clean report rendering with clickable source links, headings, and bold text
  - A dedicated Critic Report Card (with score) separate from raw pipeline data
  - One-click **.txt** and **.pdf** report export

---

## 🏗️ Architecture

```
                ┌───────────────────┐
   Topic  ───▶  │   Search Agent     │  → finds recent, relevant sources (Tavily)
                └─────────┬─────────┘
                          │
                ┌─────────▼─────────┐
                │   Reader Agent     │  → scrapes the top URL for full content
                └─────────┬─────────┘
                          │
                ┌─────────▼─────────┐
                │   Writer Chain     │  → drafts the structured research report
                └─────────┬─────────┘
                          │
                ┌─────────▼─────────┐
                │   Critic Chain     │  → scores & reviews the report
                └─────────┬─────────┘
                          │
                          ▼
                 Final Report + Feedback
```

Each stage is implemented as a LangChain **agent** (Search, Reader) or **chain** (Writer, Critic), all powered by **Mistral** (`mistral-medium-3-5`) via `langchain_mistralai`.

---

## 📂 Project Structure

```
multi-agent-system/
├── Agents.py          # Agent & chain definitions (search, reader, writer, critic)
├── tools.py           # Tool implementations (web_search via Tavily, scrape_url via BeautifulSoup)
├── pipeline.py         # Orchestrates the 4-step pipeline end-to-end
├── streamlit_app.py    # Streamlit UI (dashboard, live status, report viewer, export)
├── requirements.txt    # Python dependencies
├── .env                # API keys (not committed)
└── README.md
```

---

## ⚙️ Tech Stack

| Layer            | Technology                                  |
|-------------------|----------------------------------------------|
| LLM               | Mistral (`mistral-medium-3-5`) via `langchain_mistralai` |
| Agent Framework   | LangChain (`create_agent`)                    |
| Web Search        | Tavily API                                   |
| Web Scraping      | Requests + BeautifulSoup                     |
| UI                | Streamlit                                    |
| Report Export     | fpdf2 (PDF), native (TXT)                    |
| Markdown Rendering| `markdown` (Python library)                  |

---

## 🚀 Getting Started

### 1. Clone & set up a virtual environment

```bash
git clone <your-repo-url>
cd multi-agent-system
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` should include:

```
streamlit
langchain
langchain-mistralai
langchain-core
beautifulsoup4
requests
tavily-python
python-dotenv
rich
fpdf2
markdown
```

### 3. Add your API keys

Create a `.env` file in the project root:

```
MISTRAL_API_KEY=your_mistral_api_key
TAVILY_API_KEY=your_tavily_api_key
```

### 4. Run the app

**Streamlit UI (recommended):**
```bash
streamlit run streamlit_app.py
```

**Command-line version:**
```bash
python pipeline.py
```

---

## 🖥️ Using the UI

1. Enter a research topic in the input box.
2. Click **🚀 Run Research Pipeline**.
3. Watch the live **Pipeline Status** panel as each agent completes its step.
4. Read the generated **Final Research Report**, with clickable source links.
5. Open the **Critic Report Card** to see the score, strengths, and areas for improvement.
6. Expand **Raw Pipeline Data** to inspect search results, scraped content, or full execution logs.
7. Download the report as **.txt** or **.pdf**.

---

## 🧩 How It Works Internally

- `pipeline.py` → `run_search_agent(topic)` runs all four stages sequentially and returns a `state` dict:
  ```python
  {
      "search_results": "...",
      "scraped_content": "...",
      "report": "...",
      "feedback": "..."
  }
  ```
- `streamlit_app.py` runs this pipeline in a background thread, streams `stdout` into the UI via a queue so the pipeline status panel updates live, then renders the final report using a Markdown-aware formatter (proper headings, bold text, and clickable links exactly as the agents generated them).

---

## 🛣️ Roadmap / Ideas for Extension

- [ ] Multi-source reading (scrape top 3 URLs instead of 1)
- [ ] Persist past research runs (history panel)
- [ ] Swap/compare different LLM providers
- [ ] Add citation-style footnotes in the final report
- [ ] Deploy to Streamlit Community Cloud / Docker

---

## 📄 License

This project is for educational/personal use. Add a license of your choice (MIT recommended) if you plan to open-source it.