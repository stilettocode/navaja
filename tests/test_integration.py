from quantum_wiki.cli import build_problem, run_selector


def test_query_retrieval_to_selection_pipeline():
    retrieved, problem = build_problem("Graph shortest paths and breadth-first search", 5, 2)
    result = run_selector("brute-force", problem)
    assert len(retrieved) == 5
    assert len(result.selected_indices) == 2
    assert result.objective == result.objective
