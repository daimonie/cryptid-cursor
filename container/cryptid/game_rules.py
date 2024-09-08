import itertools
from typing import Dict, List

from cryptid.board import generate_structure_combinations, get_all_animals
from utils.graph_generate_landscape import get_terrain_types

def get_game_element_categories() -> Dict[str, List[str]]:
    """
    Returns a dictionary of game element categories and their corresponding elements.
    
    Returns:
    Dict[str, List[str]]: A dictionary where keys are category descriptions and values are lists of elements.
    """
    return {
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
            *[f"is_{terrain}" for terrain in get_terrain_types()],
            *[f"is_{animal.lower()}" for animal in get_all_animals()]
        ],
        "within_two": [
            *[f"is_{animal}" for animal in get_all_animals()],
            *[structure for structure, _ in generate_structure_combinations()]
        ],
        "within_three": [
            *[color for _, color in generate_structure_combinations()]
        ]
    }
# write a function to see if a hint applies
# then one that loops through all hints to see how many apply

