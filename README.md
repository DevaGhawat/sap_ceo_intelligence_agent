# SAP AI CEO Strategic Intelligence Agent

## Project Overview

This project is an NLP and Retrieval-Augmented Generation based Strategic Intelligence Agent for SAP.

The system collects public SAP-related information, stores it in a knowledge repository, retrieves relevant evidence, and generates CEO-level strategic recommendations. The goal is not only to summarize documents, but to transform collected information into useful business insights supported by evidence.

The system is designed to answer questions such as:

* What are the major opportunities for SAP?
* What are the biggest risks?
* What are competitors doing?
* Which technologies or trends should management monitor?
* What strategic action should SAP prioritize next?
* What evidence supports the recommendation?

---

## Selected Company

**Company:** SAP
**Industry:** Enterprise software, cloud ERP, Business AI, analytics, enterprise automation, and digital transformation.

Main focus areas:

* SAP Business AI
* Joule
* SAP BTP
* Cloud ERP
* RISE with SAP
* GROW with SAP
* Autonomous Enterprise
* Enterprise AI risks and opportunities

---

## Current Project Statistics

| Metric                |               Value |
| --------------------- | ------------------: |
| Collected documents   |                 239 |
| Clean documents       |                 239 |
| Data sources          |                   6 |
| Text chunks           |                3398 |
| Average quality score |               90.15 |
| Database              |              SQLite |
| Vector store          |            ChromaDB |
| Embedding model       |    all-MiniLM-L6-v2 |
| Local LLM             | Qwen3:8B via Ollama |

---

## Data Sources

The system collects public information from multiple source types.

| Source Type               | Examples                                                         |
| ------------------------- | ---------------------------------------------------------------- |
| Official SAP sources      | SAP News Center, SAP technical topic feeds                       |
| Financial sources         | Financial news and press release feeds                           |
| External industry sources | TechTarget SearchSAP, TechTarget SearchERP, CIO Dive             |
| Technical sources         | SAP Business AI, cloud ERP, AI, and enterprise software articles |

This satisfies the project requirement of at least **100 collected documents** from at least **3 independent public sources**.

---

## System Architecture Diagram

```mermaid
flowchart TD
    A["Public Sources"] --> B["RSS and Article Extraction"]
    B --> C["SQLite Document Repository"]
    C --> D["Text Cleaning and Deduplication"]
    D --> E["Recursive Character Chunking"]
    E --> F["Embeddings using all-MiniLM-L6-v2"]
    F --> G["ChromaDB Vector Store"]
    G --> H["RAG Evidence Retrieval"]
    H --> I["Qwen3:8B via Ollama"]
    I --> J["CEO-Level Recommendation"]
    J --> K["Streamlit Dashboard"]
```

---

## Data Flow Diagram

```mermaid
flowchart LR
    A["Public Sources"] --> B["Collectors"]
    B --> C["Raw Documents"]
    C --> D["SQLite Database"]
    D --> E["Text Preprocessing"]
    E --> F["Clean Documents"]
    F --> G["Chunking"]
    G --> H["Text Chunks"]
    H --> I["Embedding Model"]
    I --> J["ChromaDB Vector Store"]
    K["CEO Question"] --> L["RAG Retriever"]
    J --> L
    L --> M["Retrieved Evidence"]
    M --> N["Qwen3:8B via Ollama"]
    N --> O["Strategic Recommendation"]
    O --> P["Streamlit Dashboard"]
```

This data flow shows how public information moves through the system. The collected documents are stored in SQLite, cleaned, chunked, embedded, and indexed in ChromaDB. When a CEO-level question is asked, the retriever selects relevant evidence chunks and passes them to the local LLM to generate an evidence-based recommendation.

---

## AI Pipeline

### 1. Data Collection

The system automatically collects SAP-related public documents using RSS feeds and article extraction.

Collector files:

* `official_collector.py`
* `financial_collector.py`
* `technical_collector.py`
* `external_collector.py`

The collectors store the collected content into the SQLite database.

---

### 2. Knowledge Repository

SQLite is used as the main document repository.

Each document stores:

* title
* URL
* source name
* source type
* topic
* raw text
* cleaned text
* word count
* quality score
* published date
* collected timestamp

---

### 3. Preprocessing

The preprocessing step prepares raw web text for NLP processing.

Main cleaning steps:

* HTML tag removal
* web noise removal
* space normalization
* duplicate handling
* cleaned text update in SQLite

Files:

* `preprocess.py` — cleans newly collected documents
* `reclean_all_documents.py` — reapplies cleaning to all documents if the cleaning logic changes

---

### 4. Chunking

Clean documents are split into smaller chunks using recursive character chunking.

| Setting       | Value |
| ------------- | ----: |
| Chunk size    |   700 |
| Chunk overlap |   120 |

Chunking is used because full articles are too long for direct retrieval and LLM prompting. Smaller chunks help the system retrieve more focused evidence.

---

### 5. Embeddings and Vector Store

Each chunk is converted into a semantic vector using:

```text
all-MiniLM-L6-v2
```

The vectors are stored in ChromaDB. ChromaDB is used for semantic search during RAG retrieval.

---

### 6. RAG Retrieval

When the user asks a CEO-level question, the system retrieves relevant chunks from ChromaDB.

The retrieval logic uses multiple evidence categories:

* main CEO question
* opportunity evidence
* risk evidence
* external market evidence
* customer adoption evidence

This helps the system retrieve a more balanced set of evidence instead of depending on only one query.

---

### 7. CEO Recommendation Generation

The retrieved evidence is passed to a local LLM through Ollama.

Current model:

```text
Qwen3:8B
```

The model is instructed to answer only using retrieved evidence. Each recommendation must include evidence IDs such as `chunk_6385`.

The system does not use OpenAI, Gemini, Claude, or any paid commercial LLM API as the main reasoning engine.

---

## Design Decisions

| Design Decision                                | Reason                                                                                                                            |
| ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| SAP was selected as the company                | SAP has strong public information around Business AI, cloud ERP, Joule, SAP BTP, and enterprise transformation.                   |
| SQLite was used as the document repository     | It is lightweight, local, easy to inspect, and suitable for an academic prototype.                                                |
| ChromaDB was used as the vector store          | It supports persistent local semantic search and works well with sentence embeddings.                                             |
| all-MiniLM-L6-v2 was used for embeddings       | It is lightweight, fast, and suitable for local semantic retrieval.                                                               |
| Recursive character chunking was used          | It keeps chunks manageable while preserving useful context through overlap.                                                       |
| RAG was used instead of only prompting the LLM | RAG grounds the answer in collected evidence and reduces unsupported hallucination.                                               |
| Qwen3:8B through Ollama was used               | It is a freely accessible local LLM and satisfies the requirement of not using paid commercial APIs as the main reasoning engine. |
| Streamlit was used for the dashboard           | It is simple to build, easy to demonstrate, and suitable for an interactive academic prototype.                                   |
| VADER was used for sentiment analysis          | It provides a simple rule-based sentiment baseline for article and content tone.                                                  |
| Evidence IDs were included in the output       | They make the recommendation explainable and allow claims to be traced back to retrieved chunks.                                  |

---

## Dashboard Sections

The Streamlit dashboard contains the required executive intelligence sections.

### 1. Company Overview

Shows:

* company name
* industry
* number of collected documents
* number of data sources
* clean documents
* chunks
* average quality score
* source and topic distribution

### 2. Market Intelligence

Shows:

* recent collected updates
* competitor-related signals
* emerging technologies
* important company announcements

### 3. Opportunity Monitor

Shows:

* opportunity title
* impact level
* evidence
* confidence score

### 4. Risk Monitor

Shows:

* risk title
* risk category
* severity level
* evidence
* confidence score

### 5. Sentiment Analysis

Uses VADER sentiment analysis to estimate the tone of collected articles and public business signals.

Note: This is content-tone sentiment, not direct social media sentiment.

### 6. Strategic Recommendations

Generates CEO-level recommendations with:

* action
* reason
* supporting evidence
* expected impact
* risk
* priority
* confidence

### 7. CEO Briefing

Generates a short executive briefing around three questions:

* What happened?
* Why does it matter?
* What should management do next?

### 8. Project Pipeline

Shows the high-level system flow from data collection to RAG-based CEO recommendations.

---

## Technology Stack

| Component            | Tool / Library               |
| -------------------- | ---------------------------- |
| Programming language | Python                       |
| Dashboard            | Streamlit                    |
| Charts               | Plotly                       |
| Database             | SQLite                       |
| Vector store         | ChromaDB                     |
| Embedding model      | all-MiniLM-L6-v2             |
| LLM                  | Qwen3:8B via Ollama          |
| RAG logic            | LangChain + custom retrieval |
| Sentiment analysis   | VADER                        |
| Text cleaning        | BeautifulSoup, regex         |
| Data handling        | pandas                       |

---

## Project Structure

```text
sap_ceo_intelligence_agent/
├── data/
├── database/
│   └── intelligence.db
├── src/
│   ├── collectors/
│   │   ├── base_collector.py
│   │   ├── official_collector.py
│   │   ├── financial_collector.py
│   │   ├── technical_collector.py
│   │   └── external_collector.py
│   ├── dashboard/
│   │   ├── dashboard_utils.py
│   │   ├── company_overview_tab.py
│   │   ├── market_intelligence_tab.py
│   │   ├── opportunity_monitor_tab.py
│   │   ├── risk_monitor_tab.py
│   │   ├── sentiment_analysis_tab.py
│   │   ├── strategic_recommendations_tab.py
│   │   ├── ceo_briefing_tab.py
│   │   └── project_pipeline_tab.py
│   ├── pipeline/
│   │   ├── preprocess.py
│   │   ├── reclean_all_documents.py
│   │   ├── chunking.py
│   │   └── build_vector_store.py
│   ├── rag/
│   │   ├── prompts.py
│   │   ├── retrieval.py
│   │   └── rag_chain.py
│   ├── config.py
│   ├── database.py
│   └── quality_checks.py
├── vector_store/
├── app.py
├── README.md
├── requirements.txt
└── .gitignore
```

---

## How to Run

### 1. Create virtual environment

```powershell
python -m venv .venv
```

### 2. Activate virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install requirements

```powershell
python -m pip install -r requirements.txt
```

### 4. Pull the Ollama model

```powershell
ollama pull qwen3:8b
```

### 5. Initialize database

```powershell
python -m src.database
```

### 6. Collect documents

```powershell
python -m src.collectors.official_collector
python -m src.collectors.financial_collector
python -m src.collectors.technical_collector
python -m src.collectors.external_collector
```

### 7. Preprocess documents

```powershell
python -m src.pipeline.preprocess
```

If preprocessing logic is updated and all documents need to be cleaned again:

```powershell
python -m src.pipeline.reclean_all_documents
```

### 8. Create chunks

```powershell
python -m src.pipeline.chunking
```

### 9. Build vector store

```powershell
python -m src.pipeline.build_vector_store
```

### 10. Test RAG chain

```powershell
python -m src.rag.rag_chain
```

### 11. Run dashboard

```powershell
python -m streamlit run app.py --server.fileWatcherType none
```

---

## Example CEO Question

```text
If you were SAP's CEO today, what strategic action should be prioritized in Business AI and cloud ERP, and why?
```

The system retrieves evidence chunks and generates a CEO-level recommendation with supporting evidence IDs.

---

## Evidence Control

The system includes prompt-level controls to reduce hallucination:

* the LLM must use only retrieved evidence
* valid evidence IDs are passed into the prompt
* fake evidence IDs are not allowed
* every recommendation must cite evidence
* unsupported risks are restricted
* financial claims are blocked unless present in evidence
* the output includes evidence limitations

---

## Requirement Mapping

| Requirement                      | Project Implementation                               | Status    |
| -------------------------------- | ---------------------------------------------------- | --------- |
| 100+ documents                   | 239 documents collected                              | Satisfied |
| 3+ public sources                | 6 sources used                                       | Satisfied |
| Automatic data collection        | RSS and article extraction collectors                | Satisfied |
| Knowledge repository             | SQLite and ChromaDB                                  | Satisfied |
| Clean, deduplicate, embed, index | Preprocessing, chunking, embeddings, vector indexing | Satisfied |
| Opportunities, risks, trends     | Dashboard intelligence sections                      | Satisfied |
| CEO recommendations              | RAG + Qwen3:8B recommendation generation             | Satisfied |
| Evidence-based output            | Evidence IDs, evidence tables, evidence preview      | Satisfied |
| Executive dashboard              | Streamlit dashboard with required sections           | Satisfied |
| Free/open-source LLM             | Qwen3:8B through Ollama                              | Satisfied |

---

## Limitations

This is an academic prototype, so it has some limitations:

* Public web sources may change over time.
* SAP official sources may naturally present SAP positively.
* Sentiment analysis shows article tone, not direct customer opinion.
* Risk and opportunity labels are based on heuristic logic.
* Local LLM generation is slower than paid cloud APIs.
* The system supports strategic analysis, but it is not a financial forecasting model.

---

## Future Improvements

Possible improvements:

* add more external competitor sources
* add hybrid retrieval using BM25 and embeddings
* improve risk classification using a trained model
* add source freshness weighting
* add PDF export for CEO briefings
* evaluate recommendations against human-labelled strategic relevance

---

## Final Summary

This project demonstrates a complete NLP and RAG-based Strategic Intelligence Agent for SAP. It collects public information, stores it in a structured repository, processes and embeds the text, retrieves relevant evidence, and generates CEO-level strategic recommendations using a local open-source LLM.

The final system is evidence-based, explainable, and aligned with the goal of transforming information into strategic decisions.
