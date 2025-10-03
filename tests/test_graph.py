from lorestitch.graph.metrics import out_degree, in_degree
def test_degrees():
    g = {"a": ["b","c"], "b": [], "c": ["a"]}
    assert out_degree(g)["a"] == 2
    indeg = in_degree(g)
    assert indeg["a"] == 1 and indeg["b"] == 1 and indeg["c"] == 1
