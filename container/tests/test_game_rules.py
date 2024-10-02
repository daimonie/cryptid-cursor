import networkx as nx
import numpy as np
import pytest

from cryptid.game_rules import (
    count_possible_hints_for_all_players,
    count_possible_hints_for_player,
    count_tiles_fitting_hints,
    find_available_moves,
    find_available_placements,
    generate_all_hints,
    generate_states,
    hint_applies,
    hint_applies_everywhere,
    initialize_player_pieces,
    place_player_piece,
    process_move_hintcode,
    update_q_matrix,
)
from utils.graph_utils import create_graph


@pytest.fixture
def sample_graph():
    return create_graph()


def test_generate_all_hints():
    hints = generate_all_hints()
    assert isinstance(hints, dict)
    assert all(isinstance(category, list) for category in hints.values())


def test_hint_applies(sample_graph):
    assert hint_applies(sample_graph, "a", ("attr1",))
    assert not hint_applies(sample_graph, "b", ("attr1",))


def test_count_tiles_fitting_hints(sample_graph):
    hints = [("attr1",), ("attr2",)]
    count, fitting_nodes = count_tiles_fitting_hints(sample_graph, hints)
    assert count == 1
    assert fitting_nodes == ["c"]


def test_initialize_player_pieces(sample_graph):
    initialize_player_pieces(sample_graph)
    assert all(
        sample_graph.nodes[node][f"{piece}_player{player}"] == False
        for node in sample_graph.nodes
        for piece in ["disc", "cube"]
        for player in range(1, 4)
    )


def test_place_player_piece(sample_graph):
    initialize_player_pieces(sample_graph)
    place_player_piece(sample_graph, "a", "player1", True)
    assert sample_graph.nodes["a"]["disc_player1"] == True
    assert sample_graph.nodes["a"]["cube_player1"] == False


def test_find_available_placements(sample_graph):
    initialize_player_pieces(sample_graph)
    placements = find_available_placements(sample_graph, ("attr1",))
    assert set(placements["disc"]) == {"a", "c"}
    assert set(placements["cube"]) == {"b"}


def test_find_available_moves(sample_graph):
    initialize_player_pieces(sample_graph)
    hints = {"player1": ("attr1",), "player2": ("attr2",)}
    moves = find_available_moves(sample_graph, "player1", hints)
    assert ("question", "a", "player2") in moves
    assert ("question", "b", "player2") in moves
    assert ("question", "c", "player2") in moves


def test_generate_states():
    move = ("question", "a", "player2")
    player = "player1"
    my_placements = {"cube": ["b", "c"], "disc": []}
    states = generate_states(move, player, my_placements)
    assert len(states) == 3  # 1 disc state + 2 cube states


def test_count_possible_hints_for_player(sample_graph):
    count = count_possible_hints_for_player(sample_graph, "player1")
    assert isinstance(count, int)
    assert count >= 0


def test_count_possible_hints_for_all_players(sample_graph):
    initialize_player_pieces(sample_graph)
    counts = count_possible_hints_for_all_players(sample_graph)
    assert isinstance(counts, tuple)
    assert len(counts) == 3
    assert all(isinstance(count, int) for count in counts)


def test_process_move_hintcode(sample_graph):
    initialize_player_pieces(sample_graph)
    hintcode = process_move_hintcode(sample_graph, "player1")
    assert isinstance(hintcode, str)
    assert hintcode.startswith("player1-")


def test_update_q_matrix():
    q_matrix = {}
    moves = [
        (("cube", "a"), "state1", ("attr1",)),
        (("question", "b", "player2"), "state2", ("attr2",)),
    ]
    final_state = "final_state"
    player_won = True
    updated_q_matrix, reward = update_q_matrix(q_matrix, moves, final_state, player_won)
    assert isinstance(updated_q_matrix, dict)
    assert isinstance(reward, (int, float))
    assert len(updated_q_matrix) > 0
