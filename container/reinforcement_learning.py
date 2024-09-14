import numpy as np

import os
import random

from utils.graph_utils import parse_code_to_graph
from cryptid.game_rules import (
    count_tiles_fitting_hints,
    initialize_player_pieces,
    find_available_placements,
    place_player_piece,
    find_available_moves,
    hint_applies,
    find_predicted_states
)

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
    # Initial cube placement for each player
    for _ in range(2):
        for player in ['player1', 'player2', 'player3']:
            placements = find_available_placements(game_map, hints_players[player])
            if placements['cube']:
                cube_location = random.choice(placements['cube'])
                place_player_piece(game_map, cube_location, player, False)
                print(f"{player} placed initial cube at {cube_location}")
            else:
                print(f"No available cube placements for {player}")

    for i in range(20):
        for player, color in player_colors.items():
            print(f"Round {i}, player {player}, color {color}")
 
            my_placements = find_available_placements(game_map, hints_players[player])
            print(f"""Available placements for {player}:
    Cubes: {len(my_placements['cube'])} options
    Discs: {len(my_placements['disc'])} options
    Total: {len(my_placements['cube']) + len(my_placements['disc'])} options""")
            
            my_moves = find_available_moves(game_map, player, hints_players)
            my_moves_with_predicted_states = find_predicted_states(game_map, my_moves, player, my_placements)

            selected_move = random.choice(my_moves_with_predicted_states)
            print(f"Selected move: {selected_move[:-1]}")
            print(selected_move[-1])
            other_player_placed_cube = False
            game_won = False
            if selected_move[0] == 'question':
                node = selected_move[1]
                questioned_player = selected_move[2]
                questioned_hint = hints_players[questioned_player]
                answer = hint_applies(game_map, node, questioned_hint)
                print(f"{player} asked {questioned_player} about node {node}. Answer: {answer}")

                piece_type = 'disc' if answer else 'cube'
                place_player_piece(game_map, node, questioned_player, answer)
                print(f"{questioned_player} placed a {piece_type} at node {node}")

                other_player_placed_cube = not answer
            else:
                # Place a disc for the current player at the wild guess location
                node = selected_move[1]
                place_player_piece(game_map, node, player, True)
                print(f"{player} placed a disc at node {node} (wild guess)")

                # Check other players in order
                player_order = ['player1', 'player2', 'player3']
                start_index = player_order.index(player)
                all_discs = True
                for i in range(1, 4):
                    next_player = player_order[(start_index + i) % 3]
                    if hint_applies(game_map, node, hints_players[next_player]):
                        place_player_piece(game_map, node, next_player, True)
                        print(f"{next_player} placed a disc at node {node}")
                    else:
                        place_player_piece(game_map, node, next_player, False)
                        print(f"{next_player} placed a cube at node {node}")
                        all_discs = False
                        other_player_placed_cube = True
                        break  # Stop checking players after a cube is placed
                
                if all_discs:
                    game_won = True
            
            if other_player_placed_cube:
                cube_placements = my_placements['cube']
                if cube_placements:
                    cube_node = random.choice(cube_placements)
                    while cube_node == node:
                        cube_node = random.choice(cube_placements)
                    place_player_piece(game_map, cube_node, player, False)
                    print(f"{player} placed a cube at node {cube_node}")

            plot_hexagonal_grid(
                game_map, 11, 8, 
                cryptid_markers=fitting_nodes, 
                hints=hints, 
                prefix=f"output/game_move{i}_{player}"
            )
            if game_won:
                print(f"{player} won the game!")
                break
            raise Exception("""
            
For next time:
    Write a function that predicts state s'  from (s, a) using the serialize/unique code logic
    Read Q matrix from file or initialize empty one
    Select Move takes a random move from the top 3 options
        we don't know which so first add states s' to the moves, then their Q
        sort the list, make the choice
    Select cube is similar; predict s' for each cube placement option, then choose
        one of the top ones.
    
    After each move, store (s, a, s') in the replay buffer
    update after game ends, use Monte Carlo Q Learning logic from chatgpt
    store the Q matrix in output/qmatrix.json
                            
                            
                            
                            """)