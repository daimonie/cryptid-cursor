# Cryptid Cursor

Testing Cursor AI by building a cryptid reinforcement learning model

## Generate game maps
Go to `make dev` and elevate to root. Run main.py several times to generate a number
of game maps and store their data.

## Generate AI playthrough
Same as game maps, but run reinforcement_learning.py to have three AIs play through a random game. This should fill output/Q_matrix

The plan uses episodic Q-learning to train the AI to play the game. The actual rewards are:
- -1 point for each move made
- -10 points for an incorrect guess
- 100 points for winning the game
- 0 points for losing the game

These rewards encourage the AI to win quickly while avoiding incorrect guesses.

## Episodic Q-Learning

Episodic Q-learning is a reinforcement learning technique used to train agents in environments with discrete episodes. In our Cryptid AI:

1. Episodes: Each game is an episode.
2. States: Board configurations and player knowledge.
3. Actions: Placing pieces, asking questions, or guessing.
4. Q-values: Estimated future rewards for state-action pairs.

Parameters:
- Learning rate (α): 0.1
- Discount factor (γ): 0.9
- Exploration rate (ε): 0.1

Our implementation uses a modified reward update function that considers both immediate penalties and the final outcome. The Q-value update formula is:

Q(s,a) ← Q(s,a) + α[R(t) + γ * max(Q(s',a')) - Q(s,a)]

Where:
- s, a: Current state-action pair
- s', a': Next state and possible actions
- R(t): Reward at time step t, calculated as:
  R(t) = move_penalty * (1 - γ^(T-t)) / (1-γ) + (γ^(T-t)) * R

  T: Total number of steps in the episode
  t: Current step
  R: Final reward (win_reward or lose_penalty)

This approach balances immediate move penalties with the discounted final reward, allowing the AI to learn strategies that consider both short-term costs and long-term outcomes.


