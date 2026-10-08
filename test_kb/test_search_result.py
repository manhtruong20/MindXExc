from kb.document import Document
from kb.search_result import SearchResult


def test_search_result_wraps_document_and_match_type():
    doc = Document("doc-1", "Welcome email", "Hello", "/templates/email")

    result = SearchResult(document=doc, match_type="semantic")

    assert result.document is doc
    assert result.match_type == "semantic"