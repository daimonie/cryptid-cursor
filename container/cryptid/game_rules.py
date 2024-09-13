import itertools
import random
from typing import Dict, List

from cryptid.board import  generate_all_structures, get_all_animals
from utils.graph_generate_landscape import get_terrain_types

def generate_all_hints() -> Dict[str, List[str]]:
    """
    Returns a dictionary of game element categories and their corresponding elements.
    
    Returns:
    Dict[str, List[str]]: A dictionary where keys are category descriptions and values are lists of elements.
    """
    structures, colors = generate_all_structures()
    categories = {
        "terrain_type": [
            # Generate unique pairs of terrain types using itertools.combinations
            # This ensures:
            # 1. Each combination is unique
            # 2. Order doesn't matter (e.g., "is_forest_desert" and "is_desert_forest" are the same)
            # 3. A terrain type is not paired with itself
           
            (f"is_{t1}", f"is_{t2}")
            for t1, t2 in itertools.combinations(get_terrain_types(), 2)
        ],
        "within_one": [
            *[(f"is_{terrain}", f"neighbor_is_{terrain}") for terrain in get_terrain_types()],
            *[(f"is_{animal.lower()}", f"neighbor_is_{animal.lower()}") for animal in get_all_animals()]
        ],
        "within_two": [
            *[(f"is_{animal}", f"neighbor_is_{animal}", f"neighbor_neighbor_is_{animal}") for animal in get_all_animals()],
            *[(f"{structure}", f"neighbor_{structure}", f"neighbor_neighbor_{structure}") for structure in structures]
        ],
        "within_three": [
            *[(f"{color}", f"neighbor_{color}", f"neighbor_neighbor_{color}", f"neighbor_neighbor_neighbor_{color}")  for color in colors]
        ]
    } 

    for key in categories:
        categories[key] = [(item,) if isinstance(item, str) else item for item in categories[key]]
    
    return categories 
# write a function to see if a hint applies
# then one that loops through all hints to see how many apply

def verify_map_attributes(G):
    map_attributes = set()
    for node, data in G.nodes(data=True):
        map_attributes.update(data.keys())
    
    hint_attributes = set()
    for category in generate_all_hints().values():
        for hint in category:
            hint_attributes.update(attr for attr in hint if not attr.startswith('neighbor_'))
    
    missing_in_map = hint_attributes - map_attributes
    missing_in_hints = map_attributes - hint_attributes
    
    return list(missing_in_map), list(missing_in_hints)

def generate_hint_combinations(generator):
    all_hints = generate_all_hints()
    hint_combinations = []
    for _ in range(3):
        combination = []
        category = generator.choice(list(all_hints.keys()))
        hint = generator.choice(all_hints[category])
        
        hint_combinations.append(hint)
    
    return hint_combinations

def hint_applies(G, node, hint):
    for attribute in hint:
        if G.nodes[node].get(attribute, False):
            return True
    return False
def count_tiles_fitting_hints(G, hints):
    count = 0
    fitting_nodes = []
    for node in G.nodes():
        if all(hint_applies(G, node, hint) for hint in hints):
            count += 1
            fitting_nodes.append(node)
    return count, fitting_nodes

def initialize_player_pieces(G):
    for node in G.nodes():
        for player in range(1, 4):
            G.nodes[node][f'disc_player{player}'] = False
            G.nodes[node][f'cube_player{player}'] = False
            
def place_player_piece(G, node, player, is_disc):
    piece_type = 'disc' if is_disc else 'cube'
    if player not in ["player1", "player2", "player3"]:
        raise ValueError("player must be 1, 2, or 3")
    
    G.nodes[node][f'{piece_type}_{player}'] = True

def find_available_placements(G, player_hint):
    available_placements = {'cube': [], 'disc': []}
    for node in G.nodes():
        node_fits_hint = hint_applies(G, node, player_hint)
        piece_type = 'disc' if node_fits_hint else 'cube'
        
        # Check if there are no pieces of the current player
        no_own_pieces = not any(G.nodes[node].get(f'{pt}_player{i}', False) 
                                for pt in ['cube', 'disc'] 
                                for i in range(1, 4))
        
        # For cubes, also check if there are no other players' cubes
        no_other_cubes = not any(G.nodes[node].get(f'cube_player{i}', False) 
                                 for i in range(1, 4))
        
        if no_own_pieces and (piece_type == 'disc' or no_other_cubes):
            available_placements[piece_type].append(node)
    
    return available_placements
