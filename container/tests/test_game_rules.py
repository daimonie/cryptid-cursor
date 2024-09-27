import pytest
import networkx as nx
import numpy as np
import os
import pickle
from unittest.mock import patch, MagicMock

from cryptid.game_rules import (
    process_move,
    find_predicted_states,
    save_q_matrix,
    read_qmatrix,
    get_q_value,
    select_top_moves,
    find_available_cube_moves,
    select_top_cube_moves,
    policy_cube,
    update_q_matrix,
    policy,
    generate_all_hints,
    verify_map_attributes,
    generate_hint_combinations,
    hint_applies,
    count_tiles_fitting_hints,
    initialize_player_pieces,
    place_player_piece,
    find_available_placements,
    find_available_moves,
    generate_states,
    process_move_mapcode,
    hint_applies_everywhere,
    count_possible_hints_for_player,
    count_possible_hints_for_all_players,
    process_move_hintcode
)

@pytest.fixture
def sample_graph():
    G = nx.Graph()
    G.add_node(1, is_forest=True, is_mountain=False, is_bear=True)
    G.add_node(2, is_desert=True, is_water=False, is_cougar=True)
    G.add_node(3, is_mountain=True, is_forest=False, is_bear=False)
    return G

@pytest.fixture
def sample_q_matrix():
    return {
        ('state1', ('hint1',), ('move1',)): 0.5,
        ('state2', ('hint2',), ('move2',)): 0.7
    }

def test_process_move():
    game_map = nx.Graph()
    game_map.add_node(1, is_forest=True)
    game_map.add_node(2, is_desert=True)
    move = ('question', 1, 'player2')
    player = 'player1'
    my_placements = {'cube': [2], 'disc': [1]}
    result = process_move((game_map, move, player, my_placements))
    assert isinstance(result, tuple)
    assert len(result) == 4  # move + final_states

def test_find_predicted_states():
    game_map = nx.Graph()
    game_map.add_node(1, is_forest=True)
    game_map.add_node(2, is_desert=True)
    my_moves = [('question', 1, 'player2'), ('wild_guess', 2)]
    player = 'player1'
    my_placements = {'cube': [2], 'disc': [1]}
    result = find_predicted_states(game_map, my_moves, player, my_placements)
    assert isinstance(result, list)
    assert len(result) == 2

def test_save_q_matrix(tmp_path):
    q_matrix = {'test': 'data'}
    with patch('cryptid.game_rules.open') as mock_open:
        save_q_matrix(q_matrix)
        mock_open.assert_called_once_with('/opt/container/output/qmatrix.pkl', 'wb')

def test_read_qmatrix():
    with patch('os.path.exists', return_value=True), \
         patch('cryptid.game_rules.open', create=True) as mock_open, \
         patch('pickle.load', return_value={'test': 'data'}):
        result = read_qmatrix()
        assert result == {'test': 'data'}
        mock_open.assert_called_once_with('/opt/container/output/qmatrix.pkl', 'rb')

def test_get_q_value(sample_q_matrix):
    assert get_q_value(sample_q_matrix, ('move1',), 'state1', ('hint1',)) == 0.5
    assert get_q_value(sample_q_matrix, ('move3',), 'state3', ('hint3',)) == 1  # Default value

def test_select_top_moves():
    generator = np.random.default_rng(42)
    q_matrix = {('state1', ('hint1',), ('move1',)): 0.5, ('state1', ('hint1',), ('move2',)): 0.7}
    moves_with_states = [('move1', 1, ['state1']), ('move2', 2, ['state1'])]
    hint = ('hint1',)
    result = select_top_moves(generator, q_matrix, moves_with_states, hint, n=1)
    assert len(result) == 1
    assert 'move2' in [_[0] for _ in moves_with_states]

def test_find_available_cube_moves(sample_graph):
    hints = {'player1': ('is_forest',)}
    result = find_available_cube_moves(sample_graph, 'player1', hints)
    assert set(result) == {('cube', 2), ('cube', 3)}

def test_select_top_cube_moves():
    generator = np.random.default_rng(42)
    q_matrix = {(None, ('hint1',), ('cube', 1)): 0.5, (None, ('hint1',), ('cube', 2)): 0.7}
    cube_moves = [('cube', 1), ('cube', 2)]
    hint = ('hint1',)
    result = select_top_cube_moves(generator, q_matrix, cube_moves, hint, n=1)
    assert len(result) == 1
    assert result[0] == ('cube', 2)

def test_policy_cube():
    generator = np.random.default_rng(42)
    top_cube_moves = [('cube', 1), ('cube', 2), ('cube', 3)]
    result = policy_cube(generator, top_cube_moves)
    assert result in top_cube_moves

def test_update_q_matrix():
    q_matrix = {}
    moves = [
        (('move1',), 'state1', ('hint1',)),
        (('move2',), 'state2', ('hint1',))
    ]
    final_state = 'state3'
    player_won = True
    result, reward = update_q_matrix(q_matrix, moves, final_state, player_won)
    assert isinstance(result, dict)
    assert isinstance(reward, (int, float))

def test_policy():
    generator = np.random.default_rng(42)
    top_moves = [('move1', 1), ('move2', 2), ('move3', 3)]
    result = policy(generator, top_moves)
    assert result in top_moves

def test_generate_all_hints():
    result = generate_all_hints()
    assert isinstance(result, dict)
    assert 'terrain_type' in result
    assert 'within_one' in result
    assert 'within_two' in result
    assert 'within_three' in result

def test_verify_map_attributes(sample_graph):
    missing_in_map, missing_in_hints = verify_map_attributes(sample_graph)
    assert isinstance(missing_in_map, list)
    assert isinstance(missing_in_hints, list)

def test_generate_hint_combinations():
    generator = np.random.default_rng(42)
    result = generate_hint_combinations(generator)
    assert isinstance(result, list)
    assert len(result) == 3

def test_hint_applies(sample_graph):
    assert hint_applies(sample_graph, 1, ('is_forest',))
    assert not hint_applies(sample_graph, 1, ('is_desert',))

def test_count_tiles_fitting_hints(sample_graph):
    hints = [('is_forest',), ('is_mountain',)]
    count, fitting_nodes = count_tiles_fitting_hints(sample_graph, hints)
    assert count == 0 

def test_initialize_player_pieces(sample_graph):
    initialize_player_pieces(sample_graph)
    for node in sample_graph.nodes():
        for player in range(1, 4):
            assert sample_graph.nodes[node][f'disc_player{player}'] == False
            assert sample_graph.nodes[node][f'cube_player{player}'] == False

def test_place_player_piece(sample_graph):
    place_player_piece(sample_graph, 1, 'player1', True)
    assert sample_graph.nodes[1]['disc_player1'] == True
    
    with pytest.raises(ValueError):
        place_player_piece(sample_graph, 1, 'player4', True)

def test_find_available_placements(sample_graph):
    initialize_player_pieces(sample_graph)
    placements = find_available_placements(sample_graph, ('is_forest',))
    assert placements['disc'] == [1]
    assert set(placements['cube']) == {2, 3}

def test_find_available_moves(sample_graph):
    initialize_player_pieces(sample_graph)
    hints = {'player1': ('is_forest',), 'player2': ('is_desert',), 'player3': ('is_mountain',)}
    moves = find_available_moves(sample_graph, 'player1', hints)
    assert ('question', 2, 'player2') in moves
    assert ('question', 3, 'player3') in moves
    assert ('wild_guess', 1) in moves

def test_generate_states():
    move = ('question', 1, 'player2')
    player = 'player1'
    my_placements = {'cube': [2, 3]}
    states = generate_states(move, player, my_placements)
    assert len(states) == 3  # Two possible states for cube placement, one for disc

def test_process_move_mapcode(sample_graph):
    result = process_move_mapcode(sample_graph, 'player1')
    assert isinstance(result, str)

def test_hint_applies_everywhere(sample_graph):
    assert hint_applies_everywhere(sample_graph, 'player1', ('is_forest',))
