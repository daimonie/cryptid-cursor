import networkx as nx
import pytest

from utils.graph_generate_landscape import (
    assign_random_attribute,
    generate_hexagonal_grid_graph,
    get_hexagonal_neighbors,
    get_terrain_types,
    node_id_to_row_col,
    row_col_to_node_id,
)


def test_assign_random_attribute():
    attributes = ["is_forest", "is_water", "is_mountain"]
    result = assign_random_attribute(attributes)
    assert sum(result.values()) == 1
    assert all(isinstance(value, bool) for value in result.values())


@pytest.mark.parametrize(
    "node_id, expected",
    [
        ((0, 0), (0, 0)),
        (("A", "A"), (0, 0)),
        ("AA", (0, 0)),
        ((2, 3), (2, 3)),
        (("C", "D"), (2, 3)),
        ("CD", (2, 3)),
    ],
)
def test_node_id_to_row_col(node_id, expected):
    assert node_id_to_row_col(node_id) == expected


@pytest.mark.parametrize(
    "row, col, node_format, expected",
    [
        (0, 0, (0, 0), (0, 0)),
        (0, 0, ("A", "A"), ("A", "A")),
        (0, 0, "AA", "AA"),
        (2, 3, (0, 0), (2, 3)),
        (2, 3, ("A", "A"), ("C", "D")),
        (2, 3, "AA", "CD"),
    ],
)
def test_row_col_to_node_id(row, col, node_format, expected):
    assert row_col_to_node_id(row, col, node_format) == expected


def test_get_hexagonal_neighbors():
    rows, cols = 5, 5
    # Test for even row
    neighbors = get_hexagonal_neighbors(2, 2, rows, cols)
    assert (1, 1) in neighbors
    assert (1, 2) in neighbors
    assert (1, 3) in neighbors
    assert (2, 1) in neighbors
    assert (2, 3) in neighbors
    assert (3, 2) in neighbors
    assert len(neighbors) == 6

    # Test for odd row
    neighbors = get_hexagonal_neighbors(1, 2, rows, cols)
    assert (0, 1) in neighbors
    assert (0, 2) in neighbors
    assert (0, 3) in neighbors
    assert (1, 1) in neighbors
    assert (1, 3) in neighbors
    assert (2, 2) in neighbors
    assert len(neighbors) == 6


def test_generate_hexagonal_grid_graph():
    rows, cols = 4, 4
    G = generate_hexagonal_grid_graph(rows, cols)
    assert isinstance(G, nx.Graph)
    assert len(G.nodes) == rows * cols

    terrain_types = get_terrain_types()
    for node, data in G.nodes(data=True):
        assert sum(data[f"is_{terrain}"] for terrain in terrain_types) == 1

    # Check hexagonal connectivity
    for row in range(rows):
        for col in range(cols):
            neighbors = get_hexagonal_neighbors(row, col, rows, cols)
            node = (row, col)
            assert all((r, c) in G.neighbors(node) for r, c in neighbors)


def test_get_terrain_types():
    terrains = get_terrain_types()
    assert set(terrains) == {"swamp", "forest", "water", "mountain", "desert"}
