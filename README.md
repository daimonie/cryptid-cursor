# Cryptid Cursor

Testing Cursor AI by building a cryptid reinforcement learning model

## Generate game maps
Go to `make dev` and elevate to root. Run main.py several times to generate a number
of game maps and store their data.

## Generate AI playthrough
Same as game maps, but run reinforcement_learning.py to have three AIs play through a random game. This should fill output/Q_matrix

The plan is to use episodic Q-learning to train the AI to play the game. I think the scoring will be:
- -1 point per 3 cubes placed
- -1 point per 3 rounds
- 100 points for a win
