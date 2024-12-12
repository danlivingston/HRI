# modules/compare_move.py

from typing import Dict, List, Tuple, Optional


def compare_cube_positions_new_and_missing(
        cubes_old: Dict[str, str],
        cubes_new: Dict[str, str]
) -> List[Tuple[Optional[str], Optional[str]]]:
    """
    Compare two sets of cube positions and determine movements, captures, and new/removals.

    Args:
        cubes_old (dict): The old positions of cubes.
        cubes_new (dict): The new positions of cubes.

    Returns:
        list: A list of movement tuples in the format (from_position, to_position).
    """
    movements = []
    old_positions = set(cubes_old.keys())
    new_positions = set(cubes_new.keys())

    # Initialize lists for removals and additions
    removed_cubes = []
    added_cubes = []

    # Handle color changes: treat as removal and addition
    common_positions = old_positions & new_positions
    for pos in common_positions:
        old_color = cubes_old[pos]
        new_color = cubes_new[pos]
        if old_color != new_color:
            removed_cubes.append((pos, old_color))
            added_cubes.append((pos, new_color))

    # Identify removed and added positions excluding color changes
    removed_positions = old_positions - new_positions
    added_positions = new_positions - old_positions

    # Add to removals
    for pos in removed_positions:
        removed_cubes.append((pos, cubes_old[pos]))

    # Add to additions
    for pos in added_positions:
        added_cubes.append((pos, cubes_new[pos]))

    # Match removed cubes to added cubes based on color to detect movements
    matched_removed = set()
    matched_added = set()
    movement_targets = set()

    for i, (removed_pos, removed_color) in enumerate(removed_cubes):
        for j, (added_pos, added_color) in enumerate(added_cubes):
            if removed_color == added_color and j not in matched_added:
                movements.append((removed_pos, added_pos))
                matched_removed.add(i)
                matched_added.add(j)
                movement_targets.add(added_pos)  # Record movement target
                break  # Move to next removed cube after a match

    # Handle remaining removals and additions
    for i, (removed_pos, _) in enumerate(removed_cubes):
        if i not in matched_removed and removed_pos not in movement_targets:
            movements.append((removed_pos, None))  # Removal or capture

    for j, (added_pos, _) in enumerate(added_cubes):
        if j not in matched_added:
            movements.append((None, added_pos))  # New cube

    return movements
