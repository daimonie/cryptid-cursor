import numpy as np
import os
import random
from cryptid.game_rules import (
    count_tiles_fitting_hints,
    initialize_player_pieces,
    find_available_placements,
    place_player_piece,
    find_available_moves,
    hint_applies,
    find_predicted_states,
    read_qmatrix,
    find_available_cube_moves,
    select_top_moves,
    policy,
    select_top_cube_moves,
    policy_cube,
    update_q_matrix,
    save_q_matrix
)
from utils.graph_utils import parse_code_to_graph, serialize_graph
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
    q_matrix = read_qmatrix()
    replay_buffer = []
    # Initial cube placement for each player
    for _ in range(2):
        for player in ['player1', 'player2', 'player3']:
            print(f"Finding available placements for {player}...")
            placements = find_available_placements(game_map, hints_players[player])
            if placements['cube']:
                print(f"Finding available cube moves for {player}...")
                cube_moves = find_available_cube_moves(game_map, player, hints_players)
                print(f"Selecting top cube moves for {player}...")
                top_cube_moves = select_top_cube_moves(generator, q_matrix, cube_moves, hints_players[player])
                print(f"Choosing cube location for {player}...")
                cube_location = policy_cube(generator, top_cube_moves)[1]
                print(f"Placing cube for {player}...")
                place_player_piece(game_map, cube_location, player, False)
                print(f"{player} placed initial cube at {cube_location}")
            else:
                print(f"No available cube placements for {player}")

    game_won = False
    for i in range(20):
        for player, color in player_colors.items():
            print(f"Round {i}, player {player}, color {color}")
 
            my_placements = find_available_placements(game_map, hints_players[player])
            if not my_placements['disc'] and not my_placements['cube']:
                print(f"{player} has no available moves. Game ends.")
                game_won = False
                break

            print(f"""Available placements for {player}:
    Cubes: {len(my_placements['cube'])} options
    Discs: {len(my_placements['disc'])} options
    Total: {len(my_placements['cube']) + len(my_placements['disc'])} options""")
            print(f"Finding available moves for {player}...")
            my_moves = find_available_moves(game_map, player, hints_players)
            print(f"Predicting states for {len(my_moves)} possible moves...")
            my_moves_with_predicted_states = find_predicted_states(game_map, my_moves, player, my_placements)

            print(f"Selecting top moves based on Q-values...")
            top_moves = select_top_moves(generator, q_matrix, my_moves_with_predicted_states, hints_players[player])
            print(f"Choosing move from top {len(top_moves)} moves...")
            selected_move = policy(generator, top_moves)
            
            print(f"Selected move: {selected_move[:-1]}")
            print(f"Possible resulting states: {selected_move[-1]}")
            
            print("Storing current state, action, and player's hint in replay buffer...")
            current_state = serialize_graph(game_map)
            replay_buffer.append((current_state, selected_move[:2], hints_players[player]))
            
            other_player_placed_cube = False
            if selected_move[0] == 'question':
                node = selected_move[1]
                questioned_player = selected_move[2]
                questioned_hint = hints_players[questioned_player]
                answer = hint_applies(game_map, node, questioned_hint)
                print(f"Round {i}: {player} asked {questioned_player} about node {node}. Answer: {answer}")

                piece_type = 'disc' if answer else 'cube'
                place_player_piece(game_map, node, questioned_player, answer)
                print(f"{questioned_player} placed a {piece_type} at node {node}")

                other_player_placed_cube = not answer
            else:
                print(f"Round {i}: {player} is making a wild guess...")
                node = selected_move[1]
                place_player_piece(game_map, node, player, True)
                print(f"{player} placed a disc at node {node} (wild guess)")

                print("Checking other players' responses...")
                player_order = ['player1', 'player2', 'player3']
                start_index = player_order.index(player)
                all_discs = True
                for j in range(1, 4):
                    next_player = player_order[(start_index + j) % 3]
                    if hint_applies(game_map, node, hints_players[next_player]):
                        place_player_piece(game_map, node, next_player, True)
                        print(f"{next_player} placed a disc at node {node}")
                    else:
                        place_player_piece(game_map, node, next_player, False)
                        print(f"{next_player} placed a cube at node {node}")
                        all_discs = False
                        other_player_placed_cube = True
                        print("A cube was placed, stopping the wild guess process")
                        break  # Stop checking players after a cube is placed
                if all_discs:
                    game_won = True
                    break
            
            if other_player_placed_cube:
                cube_moves = find_available_cube_moves(game_map, player, hints_players)
                if not cube_moves:
                    print(f"{player} has no available cube moves. Game ends.")
                    game_won = False
                    break
                cube_move = policy_cube(generator, top_cube_moves)
                cube_node = cube_move[1]
                place_player_piece(game_map, cube_node, player, False)
                print(f"{player} placed a cube at node {cube_node}")

        if game_won:
            print(f"Game won by {player}!")
            break

    if not game_won:
        print("Game ended without a winner.")

    # Update Q-matrix after the game ends
    final_state = serialize_graph(game_map)
    for player in player_colors.keys():
        player_moves = [move for move in replay_buffer if move[2] == hints_players[player]]
        piece_counts = {
            p: {'disc': sum(1 for node in game_map.nodes() if game_map.nodes[node].get(f'disc_{p}', False)),
                'cube': sum(1 for node in game_map.nodes() if game_map.nodes[node].get(f'cube_{p}', False))}
            for p in player_colors.keys() if p != player
        }
        player_won = game_won and player == last_player
        q_matrix, final_reward = update_q_matrix(
            q_matrix,
            player_moves,
            final_state,
            hints_players,
            piece_counts,
            player_won
        )
        print(f"Final reward for {player}: {final_reward}")

    # Save updated Q-matrix 
    save_q_matrix(q_matrix)
