import itertools
import random
from typing import Dict, List

from cryptid.board import  generate_all_structures, get_all_animals
from utils.graph_generate_landscape import get_terrain_types
from utils.graph_utils import serialize_graph, generate_unique_code


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

def find_available_moves(G, player, hints):
    moves = []
    player_hint = hints[player]
    
    for node in G.nodes():
        # Check if the node has no cube of any player and no disc of the current player
        no_cubes = not any(G.nodes[node].get(f'cube_player{i}', False) for i in range(1, 4))
        no_own_disc = not G.nodes[node].get(f'disc_{player}', False)
        
        if no_cubes and no_own_disc:
            # Add question moves for other players
            for other_player in hints.keys():
                if other_player != player:
                    moves.append(('question', node, other_player))
            
            # Add wild guess move if allowed by the player's hint
            if hint_applies(G, node, player_hint):
                moves.append(('wild_guess', node))
    
    return moves
def generate_states(move, player, my_placements):
    states = []
    if move[0] == 'question':
        node, questioned_player = move[1], move[2]
        for is_disc in [True, False]:
            state = [(questioned_player, node, is_disc)]
            if not is_disc:
                for cube_node in my_placements['cube']:
                    states.append(state + [(player, cube_node, False)])
            else:
                states.append(state)
    else:  # wild_guess
        node = move[1]
        base_state = [(player, node, True)]
        player_order = ['player1', 'player2', 'player3']
        start_index = player_order.index(player)
        for i in range(1, 3):
            next_player = player_order[(start_index + i) % 3]
            for is_disc in [True, False]:
                new_state = base_state + [(next_player, node, is_disc)]
                if not is_disc:
                    for cube_node in my_placements['cube']:
                        states.append(new_state + [(player, cube_node, False)])
                    break
                elif i == 2:
                    states.append(new_state)
    return states
import multiprocessing as mp

def process_move(args):
    game_map, move, player, my_placements = args
    
    possible_states = generate_states(move, player, my_placements)
    final_states = []
    for state in possible_states:
        game_map_copy = game_map.copy()
        for player, node, is_disc in state:
            place_player_piece(game_map_copy, node, player, is_disc)
        serialized = serialize_graph(game_map_copy)
        unique_code = generate_unique_code(serialized)
        final_states.append(unique_code)
        
    return move + (final_states,)

def find_predicted_states(game_map, my_moves, player, my_placements):
    print(f"Starting multiprocessing pool for {len(my_moves)} moves")
    with mp.Pool() as pool:
        args = [(game_map, move, player, my_placements) for move in my_moves]
        moves_with_states = pool.map(process_move, args)
    print("Finished processing all moves")
    return moves_with_states

def save_q_matrix(q_matrix):
    import pickle
    with open('/opt/container/output/qmatrix.pkl', 'wb') as f:
        pickle.dump(q_matrix, f)

def read_qmatrix():
    import pickle
    import os

    qmatrix_path = '/opt/container/output/qmatrix.pkl'
    if os.path.exists(qmatrix_path):
        with open(qmatrix_path, 'rb') as f:
            return pickle.load(f)
    else:
        return {}

def get_q_value(q_matrix, move, state, hint):
    # Return the Q-value for a given state-action pair, defaulting to 1 if unknown
    # Sort the hint list and convert it to a tuple
    sorted_hint = tuple(sorted(hint))
    return q_matrix.get((state, sorted_hint, tuple(move)), 1) 

def select_top_moves(generator, q_matrix, moves_with_states, hint, n=10, learning_rate=0.1):
    if generator.random() < learning_rate:
        return [generator.choice(moves_with_states)]

    scored_moves = []
    for move in moves_with_states:
        states = move[-1]
        # Calculate the average Q-value across all possible resulting states
        # This accounts for the uncertainty in the outcome of each move
        avg_q_value = sum(get_q_value(q_matrix, move[:2], state, hint) for state in states) / len(states)
        scored_moves.append((move, avg_q_value))
    
    # Sort moves by their average Q-value in descending order
    sorted_moves = sorted(scored_moves, key=lambda x: x[1], reverse=True)
    
    # If we have fewer moves than requested, return all of them
    if len(sorted_moves) <= n:
        return [move for move, _ in sorted_moves]
    
    # Find the Q-value of the nth move
    cutoff_score = sorted_moves[n-1][1]
    # Select all moves with Q-value greater than or equal to the cutoff
    top_moves = [move for move, score in sorted_moves if score >= cutoff_score]
    
    # If we have more than n moves due to ties, randomly select n of them
    if len(top_moves) > n:
        indices = generator.choice(range(len(top_moves)), size=n, replace=False)
        return [top_moves[i] for i in indices]
    else:
        return top_moves

def find_available_cube_moves(game_map, player, hints):
    placements = find_available_placements(game_map, hints[player])
    return [('cube', node) for node in placements['cube']]

def select_top_cube_moves(generator, q_matrix, cube_moves, hint, n=10, learning_rate=0.1):
    if generator.random() < learning_rate:
        return [generator.choice(cube_moves)]

    scored_moves = []
    for move in cube_moves:
        q_value = get_q_value(q_matrix, move, None, hint)  # No state for cube moves
        scored_moves.append((move, q_value))
    
    sorted_moves = sorted(scored_moves, key=lambda x: x[1], reverse=True)
    
    if len(sorted_moves) <= n:
        return [move for move, _ in sorted_moves]
    
    cutoff_score = sorted_moves[n-1][1]
    top_moves = [move for move, score in sorted_moves if score >= cutoff_score]
    
    if len(top_moves) > n:
        indices = generator.choice(range(len(top_moves)), size=n, replace=False)
        return [top_moves[i] for i in indices]
    else:
        return top_moves

def policy_cube(generator, top_cube_moves):
    index = generator.choice(range(len(top_cube_moves)))
    return top_cube_moves[index]

def update_q_matrix(q_matrix, moves, final_state, hints, **kwargs):
    learning_rate = kwargs.get('learning_rate', 0.1)
    discount_factor = kwargs.get('discount_factor', 0.9)
    move_penalty = kwargs.get('move_penalty', -1)
    lose_penalty = kwargs.get('lose_penalty', -10)
    win_reward = kwargs.get('win_reward', 100)
    cube_penalty = kwargs.get('cube_penalty', -2)  # Additional penalty for placing a cube
    
    last_move = moves[-1]
    last_move_type = last_move[0]
    final_reward = win_reward if last_move_type == 'wild_guess' else lose_penalty

    for i in range(len(moves) - 1, -1, -1):
        move, state, hint = moves[i]
        next_state = moves[i+1][1] if i < len(moves) - 1 else final_state

        current_q = q_matrix.get((state, hint, tuple(move[:2])), 0)

        if move[0] == 'cube':
            reward = cube_penalty
        elif i == len(moves) - 1:
            reward = final_reward
        else:
            reward = move_penalty

        if i < len(moves) - 1:
            next_move = moves[i+1]
            next_q = q_matrix.get((next_state, hint, tuple(next_move[:2])), 0)
        else:
            next_q = 0  # Final state has no next move

        new_q = current_q + learning_rate * (reward + discount_factor * next_q_max - current_q)

        q_matrix[(state, hint, tuple(move[:2]))] = new_q

    return q_matrix
def policy(generator, top_moves):
    indices = generator.choice(range(len(top_moves)), size=1)[0]
    return top_moves[indices]

def update_q_matrix(q_matrix, moves, final_state, hints, **kwargs):
    learning_rate = kwargs.get('learning_rate', 0.1)
    discount_factor = kwargs.get('discount_factor', 0.9)
    move_penalty = kwargs.get('move_penalty', -1)
    lose_penalty = kwargs.get('lose_penalty', -10)
    win_reward = kwargs.get('win_reward', 100)
    
    # Determine the final reward based on the game outcome
import itertools
import random
from typing import Dict, List

from cryptid.board import  generate_all_structures, get_all_animals
from utils.graph_generate_landscape import get_terrain_types
from utils.graph_utils import serialize_graph, generate_unique_code


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

def find_available_moves(G, player, hints):
    moves = []
    player_hint = hints[player]
    
    for node in G.nodes():
        # Check if the node has no cube of any player and no disc of the current player
        no_cubes = not any(G.nodes[node].get(f'cube_player{i}', False) for i in range(1, 4))
        no_own_disc = not G.nodes[node].get(f'disc_{player}', False)
        
        if no_cubes and no_own_disc:
            # Add question moves for other players
            for other_player in hints.keys():
                if other_player != player:
                    moves.append(('question', node, other_player))
            
            # Add wild guess move if allowed by the player's hint
            if hint_applies(G, node, player_hint):
                moves.append(('wild_guess', node))
    
    return moves
def generate_states(move, player, my_placements):
    states = []
    if move[0] == 'question':
        node, questioned_player = move[1], move[2]
        for is_disc in [True, False]:
            state = [(questioned_player, node, is_disc)]
            if not is_disc:
                for cube_node in my_placements['cube']:
                    states.append(state + [(player, cube_node, False)])
            else:
                states.append(state)
    else:  # wild_guess
        node = move[1]
        base_state = [(player, node, True)]
        player_order = ['player1', 'player2', 'player3']
        start_index = player_order.index(player)
        for i in range(1, 3):
            next_player = player_order[(start_index + i) % 3]
            for is_disc in [True, False]:
                new_state = base_state + [(next_player, node, is_disc)]
                if not is_disc:
                    for cube_node in my_placements['cube']:
                        states.append(new_state + [(player, cube_node, False)])
                    break
                elif i == 2:
                    states.append(new_state)
    return states
import multiprocessing as mp

def process_move_mapcode(G, current_player):

    serialized = serialize_graph(G)
    unique_code = generate_unique_code(serialized)

    return unique_code

def process_move(args):
    game_map, move, player, my_placements = args
    
    possible_states = generate_states(move, player, my_placements)
    final_states = []
    for state in possible_states:
        game_map_copy = game_map.copy()
        for player, node, is_disc in state:
            place_player_piece(game_map_copy, node, player, is_disc)
        # too much lock in with this logic. We need to play vs the others
        # state_code = process_move_mapcode(game_map_copy, player)
        state_code = process_move_hintcode(game_map_copy, player)
        final_states.append(state_code)
        
    return move + (final_states,)

def hint_applies_everywhere(game_map, player, hint):
    for node in game_map.nodes():
        if hint_applies(game_map, node, hint):
            if game_map.nodes[node].get(f'cube_{player}', False):
                return False
    return True

def count_possible_hints(game_map, player):
    all_hints = generate_all_hints()
    possible_hints_count = 0
    for hint in all_hints:
        if hint_applies_everywhere(game_map, player, hint):
            possible_hints_count += 1
    return possible_hints_count

def count_possible_hints_for_all_players(game_map, current_player):
    player_order = ['player1', 'player2', 'player3']
    hint_counts = []
    
    for player in player_order:
        possible_hints = count_possible_hints(game_map, player)
        if player == current_player:
            possible_hints = 1
        hint_counts.append(possible_hints)
    
    return tuple(hint_counts)

def process_move_hintcode(G, player):
    hints_counts = count_possible_hints_for_all_players(G, player)
    return "-".join([f"{hint}" for hint in hints_counts])


def find_predicted_states(game_map, my_moves, player, my_placements):
    print(f"Starting multiprocessing pool for {len(my_moves)} moves")
    with mp.Pool() as pool:
        args = [(game_map, move, player, my_placements) for move in my_moves]
        moves_with_states = pool.map(process_move, args)
    print("Finished processing all moves")
    return moves_with_states
 
def get_q_value(q_matrix, move, state, hint):
    # Return the Q-value for a given state-action pair, defaulting to 1 if unknown
    # Sort the hint list and convert it to a tuple
    sorted_hint = tuple(sorted(hint))
    return q_matrix.get((state, sorted_hint, tuple(move)), 1) 

def select_top_moves(generator, q_matrix, moves_with_states, hint, n=10):
    scored_moves = []
    for move in moves_with_states:
        states = move[-1]
        # Calculate the average Q-value across all possible resulting states
        # This accounts for the uncertainty in the outcome of each move
        avg_q_value = sum(get_q_value(q_matrix, move[:2], state, hint) for state in states) / len(states)
        scored_moves.append((move, avg_q_value))
    
    # Sort moves by their average Q-value in descending order
    sorted_moves = sorted(scored_moves, key=lambda x: x[1], reverse=True)
    
    # If we have fewer moves than requested, return all of them
    if len(sorted_moves) <= n:
        return [move for move, _ in sorted_moves]
    
    # Find the Q-value of the nth move
    cutoff_score = sorted_moves[n-1][1]
    # Select all moves with Q-value greater than or equal to the cutoff
    top_moves = [move for move, score in sorted_moves if score >= cutoff_score]
    
    # If we have more than n moves due to ties, randomly select n of them
    if len(top_moves) > n:
        indices = generator.choice(range(len(top_moves)), size=n, replace=False)
        return [top_moves[i] for i in indices]
    else:
        return top_moves

def find_available_cube_moves(game_map, player, hints):
    placements = find_available_placements(game_map, hints[player])
    return [('cube', node) for node in placements['cube']]

def select_top_cube_moves(generator, q_matrix, cube_moves, hint, n=10):
    scored_moves = []
    for move in cube_moves:
        q_value = get_q_value(q_matrix, move, None, hint)  # No state for cube moves
        scored_moves.append((move, q_value))
    
    sorted_moves = sorted(scored_moves, key=lambda x: x[1], reverse=True)
    
    if len(sorted_moves) <= n:
        return [move for move, _ in sorted_moves]
    
    cutoff_score = sorted_moves[n-1][1]
    top_moves = [move for move, score in sorted_moves if score >= cutoff_score]
    
    if len(top_moves) > n:
        indices = generator.choice(range(len(top_moves)), size=n, replace=False)
        return [top_moves[i] for i in indices]
    else:
        return top_moves

def policy_cube(generator, top_cube_moves):
    index = generator.choice(range(len(top_cube_moves)))
    return top_cube_moves[index]

def policy(generator, top_moves):
    indices = generator.choice(range(len(top_moves)), size=1)[0]
    return top_moves[indices]

def update_q_matrix(q_matrix, moves, final_state, player_won, **kwargs):
    learning_rate = kwargs.get('learning_rate', 0.1)
    discount_factor = kwargs.get('discount_factor', 0.9)
    move_penalty = kwargs.get('move_penalty', -1)
    lose_penalty = kwargs.get('lose_penalty', -10)
    win_reward = kwargs.get('win_reward', 100)

    # Determine the final reward based on the game outcome
    last_move = moves[-1]
    last_move_type = last_move[0]
    final_reward = lose_penalty
    if player_won:
        final_reward = win_reward
        print(f"This player won and gets {final_reward} extra win reward points!")
    else:
        print(f"This player lost and gets {final_reward} as a penalty.")
 

    # Iterate through moves in reverse order
    for i in range(len(moves) - 1, -1, -1):
        move, state, hint = moves[i]
        # Generate a sorted tuple from the hint
        hint_tuple = tuple(sorted(hint))
        
        next_state = moves[i+1][1] if i < len(moves) - 1 else final_state

        # Calculate the current Q-value using the hint tuple
        current_q = q_matrix.get((state, hint_tuple, tuple(move[:2])), 0)

        # Calculate the reward for this move 
        T = len(moves)
        t = T - i - 1  # Current step (reversed)
        R = final_reward
        gamma = discount_factor
        
        if i == len(moves) - 1:
            reward = R
        else:
            # This formula calculates the discounted future reward.
            # - (1 - gamma**(T-t)) / (1-gamma) is the sum of discounted penalties for each step
            # (gamma**(T-t)) * R is the discounted final reward
            # Together, they provide a balanced reward that considers both immediate penalties and the final outcome
            reward = move_penalty* (1 - gamma**(T-t)) / (1-gamma) + (gamma**(T-t)) * R
        # Get the maximum Q-value for the next state
        next_q_max = q_matrix.get((next_state, hint_tuple, tuple(move[:2])), 0)

        # Update the Q-value
        new_q = current_q + learning_rate * (reward + discount_factor * next_q_max - current_q)

        # Store the updated Q-value
        q_matrix[(state, hint_tuple, tuple(move[:2]))] = new_q

    return q_matrix, final_reward + move_penalty * len(moves)
