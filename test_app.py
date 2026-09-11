import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app import app
import numpy as np

client = TestClient(app)

def test_read_root_or_health():
    """Verify that the API documentation or health check is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200

@patch("app.psycopg2.connect")
@patch("app.embedding_model")
@patch("app.bm25")
@patch("app.reranker")
@patch("app.llm")
def test_query_endpoint_success(mock_llm, mock_reranker, mock_bm25, mock_embedding, mock_pg_connect):
    """Test the /query endpoint by mocking database connections and local ML models."""
    
    # 1. Mock Database Cursor & Results
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        (1, "Sample chunk text regarding testing.", "test_manual.pdf", 5)
    ]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_pg_connect.return_value = mock_conn

    # 2. Mock Embedding Model
    mock_embedding.encode.return_value = MagicMock(tolist=lambda: [0.1] * 384)

    # 3. Mock BM25 Keyword Search (Return a numpy array supporting .argsort())
    mock_bm25.get_scores.return_value = np.array([0.9, 0.5])

    # 4. Mock Cross-Encoder Reranker
    mock_reranker.predict.return_value = [0.95]

    # 5. Mock LangChain LLM Response for both direct callables and .invoke()
    mock_response = MagicMock()
    mock_response.content = "This is a verified test response from the mocked local LLM."
    
    mock_llm.return_value = mock_response
    mock_llm.invoke.return_value = mock_response

    # Act: Send POST request to FastAPI /query endpoint
    # Act: Send POST request to FastAPI /query endpoint
    response = client.post(
        "/query",
        json={"query": "How do I test the pipeline?", "top_k": 3}
    )
    
    # Print detail if it fails
    print("RESPONSE JSON:", response.json())

    # Assert: Verify successful response status and structural schema
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "How do I test the pipeline?"
    assert "mocked local LLM" in data["answer"]
    assert len(data["sources"]) > 0