from unittest.mock import MagicMock, patch
import numpy as np
from fastapi.testclient import TestClient
import pytest

# Import app module directly to manipulate global state
import app
from app import app as fastapi_app

client = TestClient(fastapi_app)


def test_read_root_or_health():
    """Test backend health readiness endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@patch("app.psycopg2.connect")
@patch("app.embedding_model")
@patch("app.bm25")
@patch("app.reranker")
@patch("app.llm")
def test_query_endpoint_success(mock_llm, mock_reranker, mock_bm25, mock_embedding, mock_pg_connect):
    """Test the /query endpoint by mocking database connections, local ML models, and in-memory chunk cache."""

    # 1. Populate global in-memory chunk lookup so guard clause passes
    app.chunk_lookup = {
        1: {
            "chunk_text": "Sample chunk text regarding testing.",
            "source_file": "test_manual.pdf",
            "page_number": 5
        }
    }

    # 2. Mock Database Cursor & Vector Search Results
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        (1, "Sample chunk text regarding testing.", "test_manual.pdf", 5)
    ]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_pg_connect.return_value = mock_conn

    # 3. Mock Embedding Model
    mock_embedding.encode.return_value = MagicMock(tolist=lambda: [0.1] * 384)

    # 4. Mock BM25 Keyword Search
    mock_bm25.get_scores.return_value = np.array([0.9])

    # 5. Mock Cross-Encoder Reranker
    mock_reranker.predict.return_value = [0.95]

    # 6. Mock LangChain LLM Response
    mock_response = MagicMock()
    mock_response.content = "This is a verified test response from the mocked local LLM."
    mock_llm.return_value = mock_response
    mock_llm.invoke.return_value = mock_response

    # Act: Send POST request to FastAPI /query endpoint
    response = client.post(
        "/query",
        json={"query": "How do I test the pipeline?", "top_k": 3}
    )

    # Assert: Verify successful status code and response payload
    assert response.status_code == 200
    json_data = response.json()
    assert "answer" in json_data
    assert "sources" in json_data