from unittest.mock import MagicMock, patch
import numpy as np

from fastapi.testclient import TestClient
import pytest

import app
from app import app as fastapi_app

client = TestClient(fastapi_app)


def test_read_root_or_health():
    """Verify backend health readiness endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in ["ready", "ok"]


@patch("app.psycopg2.connect")
@patch("app.embedding_model")
@patch("app.bm25")
@patch("app.reranker")
@patch("app.llm")
def test_query_endpoint_success(mock_llm, mock_reranker, mock_bm25, mock_embedding, mock_pg_connect):
    """Test the /query endpoint by mocking database connections, ML models, and in-memory document state."""

    # 1. Populate required in-memory global state
    doc_id = 1
    sample_chunk = {
        "text": "Sample chunk text regarding testing.",
        "source": "test_manual.pdf",
        "page": 5
    }

    app.doc_ids = [doc_id]
    app.chunk_lookup = {doc_id: sample_chunk}
    app.bm25 = mock_bm25
    app.embedding_model = mock_embedding
    app.reranker = mock_reranker
    app.llm = mock_llm

    # 2. Mock Database Cursor & Vector Search Return Values
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        (doc_id, "Sample chunk text regarding testing.", "test_manual.pdf", 5, 0.95)
    ]

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_pg_connect.return_value = mock_conn

    # 3. Mock Embedding Model (.encode().tolist())
    mock_vector = MagicMock()
    mock_vector.tolist.return_value = [0.1] * 384
    mock_embedding.encode.return_value = mock_vector

    # 4. Mock BM25 Keyword Search
    mock_bm25.get_scores.return_value = np.array([0.9])

    # 5. Mock Cross-Encoder Reranker
    mock_reranker.predict.return_value = np.array([0.98])

    # 6. Mock LangChain LLM Output Chain
    mock_llm_response = MagicMock()
    mock_llm_response.content = "This is a verified test response from the mocked local LLM."

    mock_llm.invoke.return_value = mock_llm_response
    mock_llm.return_value = mock_llm_response

    # Act: Send POST request to FastAPI /query endpoint
    response = client.post(
        "/query",
        json={"query": "How do I test the pipeline?", "top_k": 3}
    )

    if response.status_code != 200:
        print("\n================ ERROR DETAIL ================")
        print(response.json())
        print("==============================================\n")

    # Assert: Verify 200 OK and response schema
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "How do I test the pipeline?"
    assert "mocked local LLM" in data["answer"]
    assert len(data["sources"]) > 0