import numpy as np

from cryptid.board import generate_game_map, plot_hexagonal_grid
from cryptid.game_rules import verify_map_attributes, generate_hint_combinations, count_tiles_fitting_hints

if __name__ == "__main__":
  
    generator = np.random.default_rng()
    if False:
        seed = 42  # You can change this to any integer value
        generator = np.random.default_rng(seed)
    # Generate game map
    game_map = generate_game_map(generator, 11, 8)

    # Verify hints
    missing_in_map, missing_in_hints = verify_map_attributes(game_map)

    print("Verification results:")
    print("Missing in map:", missing_in_map)
    print("Missing in hints:", missing_in_hints)


    # Generate hint combinations
    hint_combinations = generate_hint_combinations(generator)

    print("\nGenerated hint combinations:")
    for i, combination in enumerate(hint_combinations, 1):
        print(f"Combination {i}:")
        for hint in combination:
            print(f"  {hint}") 


    # Count tiles fitting hint combinations

    print("\nNumber of tiles fitting each hint combination:")
    for i, combination in enumerate(hint_combinations, 1):
        count = count_tiles_fitting_hints(game_map, [combination])
        print(f"Combination {i}: {count} tile(s)")

    # Count tiles fitting all hint combinations together
    total_count = count_tiles_fitting_hints(game_map, hint_combinations)
    print(f"\nNumber of tiles fitting all hint combinations: {total_count}")



    print("\nGenerating 10 game boards and reporting counts:")
    for iteration in range(1, 11):
        print(f"\nIteration {iteration}:")
        
        # Generate new game map
        game_map = generate_game_map(generator, 11, 8)
        
        # Generate new hint combinations
        hint_combinations = generate_hint_combinations(generator)
        
        # Count tiles fitting all hint combinations together
        total_count, fitting_nodes = count_tiles_fitting_hints(game_map, hint_combinations)
        print(f"Tiles fitting all hint combinations: {total_count}")
        print(f"Nodes fitting all hint combinations: {fitting_nodes}")
        
        if total_count >= 1:
            plot_hexagonal_grid(
                game_map, 11, 8, 
                cryptid_markers=fitting_nodes, 
                hints=hint_combinations, 
                prefix=f"iteration_{iteration}"
            )
            
            print(f"Hexagonal grid map plotted for iteration {iteration}")
            import time
            time.sleep(3)