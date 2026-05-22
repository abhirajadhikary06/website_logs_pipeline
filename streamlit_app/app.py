from __future__ import annotations

import json
import sys
from typing import Any
from pathlib import Path

import streamlit as st

from dotenv import load_dotenv
load_dotenv()

if __package__:
    from .duckdb_exact import fetch_exact_row
    from .llm import generate_answer
    from .retriever import retrieve
else:
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from streamlit_app.duckdb_exact import fetch_exact_row
    from streamlit_app.llm import generate_answer
    from streamlit_app.retriever import retrieve


def _format_row(row: dict[str, Any]) -> str:
    return "\n".join(f"- {k}: {v}" for k, v in row.items())


def _format_context_hit(hit: Any) -> str:
    payload = hit.payload
    doc_type = payload.get("doc_type")
    header = (
        f"[score={hit.score:.3f}] {payload.get('source_table')} "
        f"({doc_type})"
    )

    if doc_type == "row":
        exact_row = fetch_exact_row(payload)
        if exact_row:
            return f"{header}\nExact DuckDB values:\n{_format_row(exact_row)}"

        return (
            f"{header}\nExact row lookup returned no record.\nSemantic context:\n{hit.text}"
        )

    return f"{header}\n{hit.text}"


def _context_to_text(contexts: list[dict[str, Any]], max_hits: int = 5) -> str:
    selected = contexts[:max_hits]
    return "\n\n---\n\n".join(_format_context_hit(hit) for hit in selected)


def _build_response(
    question: str,
    history: list[dict[str, str]] | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    try:
        contexts = retrieve(question=question)
    except Exception as exc:
        return f"Retrieval failed: {exc}", []
    if not contexts:
        return "No matching gold knowledge found in Qdrant.", []

    base_answer = _context_to_text(contexts)
    answer = generate_answer(question, base_answer, history=history)

    hit_dump = [
        {
            "score": c.score,
            "doc_type": c.payload.get("doc_type"),
            "source_table": c.payload.get("source_table"),
            "payload": c.payload,
        }
        for c in contexts
    ]
    return answer, hit_dump


def main() -> None:
    st.set_page_config(page_title="Gold RAG Assistant", page_icon=":bar_chart:")
    st.title("Gold Layer Q&A")
    st.caption("Semantic retrieval from Qdrant + exact values from DuckDB")

    if "history" not in st.session_state:
        st.session_state.history = []

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Ask me about the gold models and I’ll pull the relevant Qdrant and DuckDB context.",
            }
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("hits"):
                with st.expander("Retrieved context"):
                    st.code(json.dumps(message["hits"], indent=2, default=str), language="json")

    question = st.chat_input("Ask a question about the gold models")
    if question and question.strip():
        question = question.strip()
        st.session_state.messages.append({"role": "user", "content": question})

        with st.chat_message("assistant"):
            with st.spinner("Searching Qdrant and DuckDB..."):
                history = [
                    {"role": message["role"], "content": message["content"]}
                    for message in st.session_state.messages[:-1]
                    if message["role"] in {"user", "assistant"}
                ]
                answer, hit_dump = _build_response(question, history=history)
            st.markdown(answer)
            if hit_dump:
                with st.expander("Retrieved context"):
                    st.code(json.dumps(hit_dump, indent=2, default=str), language="json")

        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "hits": hit_dump}
        )

        st.session_state.history.append(
            {"question": question, "answer": answer, "hits": hit_dump}
        )


if __name__ == "__main__":
    main()
