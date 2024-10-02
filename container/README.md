# Cryptid Cursor

Testing Cursor AI by building a cryptid reinforcement learning model

## Generate game maps
Run `main.py` to:
- Generate a valid Cryptid game board
- Create hint combinations
- Verify that exactly one tile fits all hints
- Plot the game board
- Save the serialized game state

## Train AI through gameplay
Run `reinforcement_learning.py` to:
- Load a randomly selected game state
- Simulate a 3-player game using Q-learning
- Update the Q-matrix based on game outcomes
- Save the updated Q-matrix for future use

Both scripts use the `/opt/container/output` directory for storing and retrieving data.
