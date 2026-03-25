# RAG Incident Response Assistant (part of teaching practice)

Built as part of the YouTube series "Production AI Engineering from Scratch".
Every line of code in this repo is explained in detail in the video.
No hand-waving. No magic. Just code and the reasoning behind it.


## What Is This?

This is a RAG (Retrieval Augmented Generation) system that reads internal runbooks
and answers incident questions using only what is written in those runbooks.


### The Problem It Solves

When an alert fires at 2am, your on-call engineer opens a 40-page runbook,
searches for the right section under pressure, and hopes it is not outdated.
That process used to take my team 45 minutes from alert to first remediation action.

This system cuts that to under 3 minutes.
The engineer types the error they are seeing.
The system returns the exact runbook steps for that specific error.
No searching. No guessing. No hallucination.


### How It Works

There are three steps happening inside this system.

Step 1 — EMBED

All runbook documents are split into small chunks and converted into vectors.
A vector is a list of numbers that represents the meaning of a piece of text.
Two chunks that describe the same concept will have similar vectors
even if they use completely different words.

Step 2 — RETRIEVE

When a question comes in, it is also converted into a vector.
The system finds the stored chunks whose vectors are closest to the question vector.
These are the most semantically relevant pieces of the runbook.

Step 3 — GENERATE

The retrieved chunks are handed to the LLM alongside the question.
The LLM reads the chunks and generates an answer grounded in that specific content.
It is not guessing from training data. It is reading your runbooks.

Think of it as the difference between a closed-book exam and an open-book exam.
RAG gives the LLM the book.

---

## Project Structure

```
rag-incident-assistant/
    rag_teaching.py              complete annotated source code
    runbooks/
        service_x_runbook.txt   API gateway incidents
        database_runbook.txt    PostgreSQL incidents
        redis_runbook.txt       Redis incidents
    requirements.txt            all dependencies
    README.md                   this file
```

---

## Runbook Dataset

Three realistic incident runbooks are included as sample data.

service_x_runbook.txt
    Covers connection refused errors, high latency, auth token failures,
    and an escalation matrix. Service X is a fictional API gateway that depends
    on Redis for caching and PostgreSQL for auth tokens.

database_runbook.txt
    Covers connection limit exceeded, replication lag, disk space critical,
    and slow queries. Includes real PostgreSQL commands and diagnostic queries.

redis_runbook.txt
    Covers Redis down or not responding, high memory usage, cache stampede,
    and stale distributed locks. Includes redis-cli commands and fix procedures.

These files are intentionally realistic. Every symptom, command, and fix
was written to reflect actual on-call scenarios. Use them as-is or
replace them with your own internal runbooks.

---

## Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/rag-incident-assistant.git
cd rag-incident-assistant
```

### 2. Install dependencies

```bash
pip install langchain langchain-community langchain-openai langchain-text-splitters chromadb tiktoken openai
```

### 3. Set your OpenAI API key

Open rag_teaching.py and replace line 57:

```python
os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"
```

### 4. Set your runbook paths

If you are running in Google Colab with Google Drive mounted, update lines 66-70:

```python
RUNBOOK_PATHS = [
    "/content/drive/MyDrive/service_x_runbook.txt",
    "/content/drive/MyDrive/database_runbook.txt",
    "/content/drive/MyDrive/redis_runbook.txt",
]
```

If you are running locally, use relative paths:

```python
RUNBOOK_PATHS = [
    "runbooks/service_x_runbook.txt",
    "runbooks/database_runbook.txt",
    "runbooks/redis_runbook.txt",
]
```

### 5. Run the script

```bash
python rag_teaching.py
```

The script prints a confirmation at every step so you know exactly where it is.
It finishes by running six test questions automatically.
Three that should answer correctly. Three that should refuse.

---

## Expected Output

When working correctly, the six test questions produce this behavior:

```
QUESTION: Redis is not responding and the process seems crashed
Retrieved 4 chunks — all from redis_runbook.txt
Answer: Check the Redis process with systemctl status redis.
        If not running, check journalctl -u redis -n 200 to see why it stopped...

QUESTION: What is RAG and how does it work?
Retrieved 4 chunks — unrelated runbook content
Answer: I don't have enough runbook context for this — escalate to Tier 2.
```

The refusal on the last three tests is correct behavior, not a bug.
The hallucination guard is working exactly as designed.

---

## Key Design Decisions

chunk_size=500, chunk_overlap=50

Each chunk is at most 500 characters. The last 50 characters of each chunk
overlap with the start of the next chunk. This prevents important information
from being lost at chunk boundaries. If a key sentence spans two chunks,
both chunks carry part of it and either can be retrieved if relevant.

k=4 retrieved chunks

The top 4 most relevant chunks are passed to the LLM per question.
More chunks means more context but also higher token cost and slower response.
4 is the sweet spot for these runbooks — enough context, minimal noise.

temperature=0

The LLM produces fully deterministic output. The same question always gives
the same answer. For incident response you never want randomness.

The hallucination guard

The prompt explicitly tells the LLM to say "escalate to Tier 2" if the
retrieved context does not contain enough information to answer.
Without this instruction the LLM will confidently invent an answer.
This single line is what makes the system trustworthy in production.

---

## Running in Google Colab

This repo was built and tested in Google Colab. A few things to know.

The vector database is saved to /tmp/chroma_db by default.
This folder is wiped when your Colab session fully resets.
To persist the database across sessions, change CHROMA_PATH to a Google Drive path:

```python
CHROMA_PATH = "/content/drive/MyDrive/chroma_db"
```

If you see an "attempt to write a readonly database" error from Chroma,
it means the chroma_db folder has a permissions issue.
The fix is to change CHROMA_PATH to /tmp/chroma_db which is always writable in Colab.

---

## What Comes Next

This is Video 1 of the series.

Video 2 — Multi-Agent Orchestration with LangGraph

What happens when a single RAG chain is not enough.
How to build agents that can reason, plan, and use tools.
The failure modes nobody talks about in papers.

Video 3 — Evaluation Framework for RAG

How do you know if your RAG system is actually working?
Building automated evals so you catch retrieval failures before your users do.

Subscribe to follow the series: https://youtube.com/@yourchannel

---

## Dependencies

```
langchain                core framework for chaining LLM components
langchain-community      document loaders and Chroma vector store integration
langchain-openai         OpenAI embeddings and chat model wrappers
langchain-text-splitters RecursiveCharacterTextSplitter
chromadb                 local vector database
tiktoken                 token counting for OpenAI models
openai                   underlying OpenAI API client
```

---

## License

MIT License. Use this freely, build on it, share it.
If this helped you, the best thing you can do is share the video with another engineer.

---
