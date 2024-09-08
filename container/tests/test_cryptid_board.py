import pytest
import networkx as nx
from cryptid.board import (
    generate_game_map,
    add_random_structures,
    enrich_node_attributes,
    generate_structure_color_combinations,
    get_all_animals,
    get_terrain_types
)

def test_generate_game_map():
    rows, cols = 5, 5
    G = generate_game_map(rows, cols)
    
    assert isinstance(G, nx.Graph)
    assert len(G.nodes) == rows * cols
    
    # Check if all nodes have terrain attributes
    terrains = get_terrain_types()
    for node in G.nodes:
        assert any(G.nodes[node].get(f'is_{terrain}', False) for terrain in terrains)

def test_add_random_structures():
    G = nx.grid_2d_graph(5, 5)
    add_random_structures(G, 5, 5)
    
    structures = generate_structure_color_combinations()
    structure_count = sum(1 for node in G.nodes for structure in structures if G.nodes[node].get(structure, False))
    
    assert 4 <= structure_count <= 6  # min_structures=4, max_structures=6

def test_enrich_node_attributes():
    G = nx.Graph()
    G.add_node(1, is_forest=True)
    G.add_node(2, is_forest=False)
    G.add_edge(1, 2)
    
    enriched_G = enrich_node_attributes(G)
    assert enriched_G.nodes[2]['neighbor_is_forest']
    assert enriched_G.nodes[1]['neighbor_is_forest']  # Updated: forest node should have neighbor_is_forest as True
    assert enriched_G.nodes[1]['is_forest']  # Additional check to ensure node 1 is still a forest

def test_generate_structure_color_combinations():
    combinations = generate_structure_color_combinations()
    
    assert 'standing_stone_blue' in combinations
    assert 'abandoned_shack_green' in combinations
    assert len(combinations) == 8  # 2 structures * 4 colors

def test_get_all_animals():
    animals = get_all_animals()
    
    assert 'bear' in animals
    assert 'cougar' in animals
    assert len(animals) == 2

def test_get_terrain_types():
    terrains = get_terrain_types()
    
    assert 'forest' in terrains
    assert 'desert' in terrains
    assert 'water' in terrains
    assert 'mountain' in terrains
    assert 'swamp' in terrains
    assert len(terrains) == 5
