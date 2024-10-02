import pytest
import networkx as nx
import numpy as np
from cryptid.board import (
    generate_structure_color_combinations,
    select_random_structures,
    try_location,
    find_empty_location,
    add_structure_to_graph,
    add_random_structures,
    generate_all_structures,
    get_all_animals,
    get_terrain_types,
    generate_game_map
)
from utils.graph_utils import create_graph

def test_generate_structure_color_combinations():
    combinations = generate_structure_color_combinations()
    assert len(combinations) == 8  # 2 structures * 4 colors
    assert "standing_stone_blue" in combinations
    assert "abandoned_shack_green" in combinations

def test_select_random_structures():
    generator = np.random.default_rng(seed=42)
    all_structures = generate_structure_color_combinations()
    
    selected = select_random_structures(generator, all_structures, 2, 4)
    assert 2 <= len(selected) <= 4
    assert all(s in all_structures for s in selected)
  
def test_add_structure_to_graph():
    G = nx.Graph()
    G.add_node(('a', 'b'))
    add_structure_to_graph(G, "standing_stone_blue", ('a', 'b'))
    
    assert G.nodes[('a', 'b')]["standing_stone_blue"] == True
    assert G.nodes[('a', 'b')]["standing_stone"] == True
    assert G.nodes[('a', 'b')]["blue"] == True

def test_add_random_structures():
    generator = np.random.default_rng(seed=42)
    G = nx.grid_2d_graph(3, 3)
    rows, cols = 3, 3
    
    add_random_structures(generator, G, rows, cols, min_structures=2, max_structures=4)
    
    structure_count = sum(1 for node in G.nodes for attr, value in G.nodes[node].items() if value and '_' in attr)
    assert 2 <= structure_count <= 4

def test_generate_all_structures():
    structures, colors = generate_all_structures()
    assert structures == ['standing_stone', 'abandoned_shack']
    assert colors == ['blue', 'green', 'white', 'black']

def test_get_all_animals():
    animals = get_all_animals()
    assert animals == ['bear', 'cougar']

def test_get_terrain_types():
    terrains = get_terrain_types()
    assert terrains == ['forest', 'desert', 'water', 'mountain', 'swamp']

def test_generate_game_map():
    generator = np.random.default_rng(seed=42)
    rows, cols = 5, 5
    G = generate_game_map(generator, rows, cols)
    
    assert isinstance(G, nx.Graph)
    assert len(G.nodes) == rows * cols
    
    # Check for animal areas
    assert any(G.nodes[node].get('is_bear', False) for node in G.nodes)
    assert any(G.nodes[node].get('is_cougar', False) for node in G.nodes)
     

# Run the tests
if __name__ == "__main__":
    pytest.main([__file__])
