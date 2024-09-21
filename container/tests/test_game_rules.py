


import pytest
import networkx as nx
from cryptid.game_rules import (
    find_available_placements,
    generate_moves,
    generate_states,
    process_move,
    find_predicted_states,
    get_q_value,
    select_top_moves,
    find_available_cube_moves,
    select_top_cube_moves
)

def test_find_available_placements():
    G = nx.Graph()
    G.add_node('A1', is_forest=True, is_water=False)
    G.add_node('A2', is_forest=False, is_water=True)
    hint = ['forest']
    
    placements = find_available_placements(G, hint)
    assert 'A1' in placements['disc']
    assert 'A2' not in placements['disc']

def test_generate_moves():
    G = nx.Graph()
    G.add_node('A1', is_forest=True, cube_player1=False, disc_player1=False)
    G.add_node('A2', is_forest=False, cube_player1=False, disc_player1=False)
    hints = {'player1': ['forest'], 'player2': ['water']}
    
    moves = generate_moves(G, 'player1', hints)
    assert ('question', 'A1', 'player2') in moves
    assert ('wild_guess', 'A1') in moves

def test_generate_states():
    move = ('question', 'A1', 'player2')
    player = 'player1'
    my_placements = {'cube': ['B1', 'B2']}
    
    states = generate_states(move, player, my_placements)
    assert len(states) == 3  # 1 disc state + 2 cube states

def test_process_move():
    G = nx.Graph()
    G.add_node('A1', is_forest=True)
    move = ('question', 'A1', 'player2')
    player = 'player1'
    my_placements = {'cube': ['B1']}
    
    result = process_move((G, move, player, my_placements))
    assert len(result) == 4  # move + final_states

def test_get_q_value():
    q_matrix = {(('A1', True), ('forest',), ('question', 'A1', 'player2')): 0.5}
    move = ('question', 'A1', 'player2')
    state = ('A1', True)
    hint = ['forest']
    
    value = get_q_value(q_matrix, move, state, hint)
    assert value == 0.5

def test_select_top_moves():
    generator = pytest.importorskip("numpy.random").default_rng()
    q_matrix = {
        (('A1', True), ('forest',), ('question', 'A1', 'player2')): 0.8,
        (('A2', False), ('forest',), ('wild_guess', 'A2')): 0.6
    }
    moves_with_states = [
        (('question', 'A1', 'player2'), [('A1', True)]),
        (('wild_guess', 'A2'), [('A2', False)])
    ]
    hint = ['forest']
    
    top_moves = select_top_moves(generator, q_matrix, moves_with_states, hint, n=1)
    assert len(top_moves) == 1
    assert top_moves[0][0] == ('question', 'A1', 'player2')

def test_find_available_cube_moves():
    G = nx.Graph()
    G.add_node('A1', is_forest=True, cube_player1=False)
    G.add_node('A2', is_forest=False, cube_player1=False)
    hints = {'player1': ['forest']}
    
    cube_moves = find_available_cube_moves(G, 'player1', hints)
    assert ('cube', 'A1') in cube_moves
    assert ('cube', 'A2') not in cube_moves

def test_select_top_cube_moves():
    generator = pytest.importorskip("numpy.random").default_rng()
    q_matrix = {
        (('A1', True), ('forest',), ('cube', 'A1')): 0.8,
        (('A2', False), ('forest',), ('cube', 'A2')): 0.6
    }
    cube_moves = [('cube', 'A1'), ('cube', 'A2')]
    hint = ['forest']
    
    top_moves = select_top_cube_moves(generator, q_matrix, cube_moves, hint, n=1)
    assert len(top_moves) == 1
    assert top_moves[0] == ('cube', 'A1')
