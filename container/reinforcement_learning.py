import numpy as np

import os
import random

from utils.graph_utils import parse_code_to_graph
from cryptid.game_rules import count_tiles_fitting_hints, initialize_player_pieces, find_available_placements, place_player_piece

from cryptid.plotting import plot_hexagonal_grid, plot_hexagonal_test, get_player_colors
if __name__ == "__main__":
  
    generator = np.random.default_rng()


    # Get all JSON files in /opt/container/output except qmatrix.json
    json_files = [f for f in os.listdir('/opt/container/output') if f.endswith('.json') and f != 'qmatrix.json']

    # Randomly select one file
    selected_file = random.choice(json_files) 
    # Unserialize the game board
    game_map, hints_players = parse_code_to_graph(selected_file)
    hints = [_ for _ in hints_players.values()]
    total_count, fitting_nodes = count_tiles_fitting_hints(game_map, hints)
    
    assert total_count == 1, f"Total count is {total_count} for {selected_file}, hints {hints}"

    plot_hexagonal_test(
        game_map, 11, 8, 
        cryptid_markers=fitting_nodes, 
        hints=hints, 
        prefix=f"output/test_reinforcement"
    )
    player_colors = get_player_colors()
    initialize_player_pieces(game_map)

    for i in range(10):
        for player, color in player_colors.items():
            print(f"Round {i}, player {player}, color {color}")
 
            my_moves = find_available_placements(game_map, hints_players[player])
            print(f"Available moves for {player}: Cubes: {len(my_moves['cube'])} options, Discs: {len(my_moves['disc'])} options, Total: {len(my_moves['cube']) + len(my_moves['disc'])} options")
             
            # Pick a random move
            piece_type = random.choice(['cube', 'disc'])
            if my_moves[piece_type]:
                move = random.choice(my_moves[piece_type])
                print(f"Chosen move for {player}: {piece_type} at {move}")
                
                # Place the piece
                place_player_piece(game_map, move, player, piece_type == 'disc')

                # Raise an exception to show the hints of the node at the chosen move
                node_hints = {attr: value for attr, value in game_map.nodes[move].items() if value is True}
                
                            
                plot_hexagonal_grid(
                    game_map, 11, 8, 
                    cryptid_markers=fitting_nodes, 
                    hints=hints, 
                    prefix=f"output/game_move{i}_player_{player}"
                )
            else:
                print(f"No available {piece_type} moves for {player}")
