from typing import Dict, List, Tuple

def out_degree(g: Dict[str, List[str]]) -> Dict[str, int]:
    return {k: len(v) for k, v in g.items()}

def in_degree(g: Dict[str, List[str]]) -> Dict[str, int]:
    inc = {k: 0 for k in g}
    for _, neigh in g.items():
        for t in neigh:
            if t in inc: inc[t] += 1
    return inc

def top_nodes_by_degree(g: Dict[str, List[str]], n: int = 5) -> List[Tuple[str, int]]:
    deg = {k: len(v) for k, v in g.items()}
    return sorted(deg.items(), key=lambda x: -x[1])[:n]
