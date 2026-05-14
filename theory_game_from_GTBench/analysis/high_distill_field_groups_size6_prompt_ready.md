# Prompt-Ready Size-6 Groups For High Distill

## Purpose

This file rewrites the sampled size-6 field groups into prompt-ready form
for the `high_distill` setting.

Mode interpretation:

- use the same selected 6 fields,
- compute them first,
- then execute a compact decision program derived from those fields,
- keep the final action aligned with the highest-priority applicable rule.

## Tic-Tac-Toe

### Group 1

Use only these computed fields:

- `open_lines_by_player`: lines still completable by each player.
- `immediate_block_actions`: legal moves that stop the opponent's immediate win.
- `center_control_status`: whether center is occupied and by whom.
- `line_completion_distance_by_action`: minimum remaining moves to complete a winning line after each candidate move.
- `draw_preserving_actions`: moves that avoid immediate tactical loss and keep a drawable continuation alive.
- `continuation_pressure_by_action`: coarse class such as `forcing`, `neutral`, `defensive_only`, or `self_exposing`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Tic-Tac-Toe.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- open_lines_by_player: lines still completable by each player.
- immediate_block_actions: legal moves that stop the opponent's immediate win.
- center_control_status: whether center is occupied and by whom.
- line_completion_distance_by_action: minimum remaining moves to complete a winning line after each candidate move.
- draw_preserving_actions: moves that avoid immediate tactical loss and keep a drawable continuation alive.
- continuation_pressure_by_action: coarse class such as `forcing`, `neutral`, `defensive_only`, or `self_exposing`.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [draw_preserving_actions], prioritize actions supported by those fields.
P2. If opponent threat or forced defense is exposed by [immediate_block_actions], keep only legal actions that answer that threat.
P3. Among remaining actions, rank them using the comparative evidence in [line_completion_distance_by_action, continuation_pressure_by_action] and choose the strongest supported action.
P4. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Tic-Tac-Toe

### Group 2

Use only these computed fields:

- `line_status_by_line`: for each winning line, count self marks, opponent marks, and empty cells.
- `immediate_block_actions`: legal moves that stop the opponent's immediate win.
- `dual_threat_count_by_action`: number of future winning threats produced by each legal move.
- `corner_pair_potential_by_action`: whether a move creates or breaks strong corner-based fork structures.
- `line_completion_distance_by_action`: minimum remaining moves to complete a winning line after each candidate move.
- `symmetry_class_by_action`: equivalence classes among legal actions under board symmetry, useful for compression.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Tic-Tac-Toe.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- line_status_by_line: for each winning line, count self marks, opponent marks, and empty cells.
- immediate_block_actions: legal moves that stop the opponent's immediate win.
- dual_threat_count_by_action: number of future winning threats produced by each legal move.
- corner_pair_potential_by_action: whether a move creates or breaks strong corner-based fork structures.
- line_completion_distance_by_action: minimum remaining moves to complete a winning line after each candidate move.
- symmetry_class_by_action: equivalence classes among legal actions under board symmetry, useful for compression.

Decision program:
P0. Choose only from legal actions.
P1. If opponent threat or forced defense is exposed by [immediate_block_actions], keep only legal actions that answer that threat.
P2. Among remaining actions, rank them using the comparative evidence in [dual_threat_count_by_action, line_completion_distance_by_action, symmetry_class_by_action] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Tic-Tac-Toe

### Group 3

Use only these computed fields:

- `open_lines_by_player`: lines still completable by each player.
- `fork_creation_actions`: legal moves creating at least two next-turn winning threats.
- `fork_block_actions`: legal moves that prevent the opponent from creating a fork.
- `center_control_status`: whether center is occupied and by whom.
- `line_completion_distance_by_action`: minimum remaining moves to complete a winning line after each candidate move.
- `draw_preserving_actions`: moves that avoid immediate tactical loss and keep a drawable continuation alive.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Tic-Tac-Toe.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- open_lines_by_player: lines still completable by each player.
- fork_creation_actions: legal moves creating at least two next-turn winning threats.
- fork_block_actions: legal moves that prevent the opponent from creating a fork.
- center_control_status: whether center is occupied and by whom.
- line_completion_distance_by_action: minimum remaining moves to complete a winning line after each candidate move.
- draw_preserving_actions: moves that avoid immediate tactical loss and keep a drawable continuation alive.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [draw_preserving_actions], prioritize actions supported by those fields.
P2. Among remaining actions, rank them using the comparative evidence in [line_completion_distance_by_action] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Tic-Tac-Toe

### Group 4

Use only these computed fields:

- `fork_creation_actions`: legal moves creating at least two next-turn winning threats.
- `fork_block_actions`: legal moves that prevent the opponent from creating a fork.
- `opponent_immediate_reply_threats_by_action`: opponent immediate wins available after each candidate move.
- `forced_reply_count_by_action`: how many opponent replies are forced after each move.
- `corner_pair_potential_by_action`: whether a move creates or breaks strong corner-based fork structures.
- `continuation_pressure_by_action`: coarse class such as `forcing`, `neutral`, `defensive_only`, or `self_exposing`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Tic-Tac-Toe.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- fork_creation_actions: legal moves creating at least two next-turn winning threats.
- fork_block_actions: legal moves that prevent the opponent from creating a fork.
- opponent_immediate_reply_threats_by_action: opponent immediate wins available after each candidate move.
- forced_reply_count_by_action: how many opponent replies are forced after each move.
- corner_pair_potential_by_action: whether a move creates or breaks strong corner-based fork structures.
- continuation_pressure_by_action: coarse class such as `forcing`, `neutral`, `defensive_only`, or `self_exposing`.

Decision program:
P0. Choose only from legal actions.
P1. If opponent threat or forced defense is exposed by [opponent_immediate_reply_threats_by_action], keep only legal actions that answer that threat.
P2. Among remaining actions, rank them using the comparative evidence in [forced_reply_count_by_action, continuation_pressure_by_action] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Tic-Tac-Toe

### Group 5

Use only these computed fields:

- `open_lines_by_player`: lines still completable by each player.
- `dual_threat_count_by_action`: number of future winning threats produced by each legal move.
- `opponent_immediate_reply_threats_by_action`: opponent immediate wins available after each candidate move.
- `center_control_status`: whether center is occupied and by whom.
- `line_completion_distance_by_action`: minimum remaining moves to complete a winning line after each candidate move.
- `draw_preserving_actions`: moves that avoid immediate tactical loss and keep a drawable continuation alive.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Tic-Tac-Toe.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- open_lines_by_player: lines still completable by each player.
- dual_threat_count_by_action: number of future winning threats produced by each legal move.
- opponent_immediate_reply_threats_by_action: opponent immediate wins available after each candidate move.
- center_control_status: whether center is occupied and by whom.
- line_completion_distance_by_action: minimum remaining moves to complete a winning line after each candidate move.
- draw_preserving_actions: moves that avoid immediate tactical loss and keep a drawable continuation alive.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [draw_preserving_actions], prioritize actions supported by those fields.
P2. If opponent threat or forced defense is exposed by [opponent_immediate_reply_threats_by_action], keep only legal actions that answer that threat.
P3. Among remaining actions, rank them using the comparative evidence in [dual_threat_count_by_action, line_completion_distance_by_action] and choose the strongest supported action.
P4. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Tic-Tac-Toe

### Group 6

Use only these computed fields:

- `open_lines_by_player`: lines still completable by each player.
- `immediate_win_actions`: legal moves that complete a line immediately.
- `immediate_block_actions`: legal moves that stop the opponent's immediate win.
- `fork_creation_actions`: legal moves creating at least two next-turn winning threats.
- `center_control_status`: whether center is occupied and by whom.
- `symmetry_class_by_action`: equivalence classes among legal actions under board symmetry, useful for compression.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Tic-Tac-Toe.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- open_lines_by_player: lines still completable by each player.
- immediate_win_actions: legal moves that complete a line immediately.
- immediate_block_actions: legal moves that stop the opponent's immediate win.
- fork_creation_actions: legal moves creating at least two next-turn winning threats.
- center_control_status: whether center is occupied and by whom.
- symmetry_class_by_action: equivalence classes among legal actions under board symmetry, useful for compression.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [immediate_win_actions], prioritize actions supported by those fields.
P2. If opponent threat or forced defense is exposed by [immediate_block_actions], keep only legal actions that answer that threat.
P3. Among remaining actions, rank them using the comparative evidence in [symmetry_class_by_action] and choose the strongest supported action.
P4. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Tic-Tac-Toe

### Group 7

Use only these computed fields:

- `open_lines_by_player`: lines still completable by each player.
- `fork_creation_actions`: legal moves creating at least two next-turn winning threats.
- `fork_block_actions`: legal moves that prevent the opponent from creating a fork.
- `opponent_immediate_reply_threats_by_action`: opponent immediate wins available after each candidate move.
- `center_control_status`: whether center is occupied and by whom.
- `corner_pair_potential_by_action`: whether a move creates or breaks strong corner-based fork structures.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Tic-Tac-Toe.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- open_lines_by_player: lines still completable by each player.
- fork_creation_actions: legal moves creating at least two next-turn winning threats.
- fork_block_actions: legal moves that prevent the opponent from creating a fork.
- opponent_immediate_reply_threats_by_action: opponent immediate wins available after each candidate move.
- center_control_status: whether center is occupied and by whom.
- corner_pair_potential_by_action: whether a move creates or breaks strong corner-based fork structures.

Decision program:
P0. Choose only from legal actions.
P1. If opponent threat or forced defense is exposed by [opponent_immediate_reply_threats_by_action], keep only legal actions that answer that threat.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Tic-Tac-Toe

### Group 8

Use only these computed fields:

- `immediate_win_actions`: legal moves that complete a line immediately.
- `immediate_block_actions`: legal moves that stop the opponent's immediate win.
- `dual_threat_count_by_action`: number of future winning threats produced by each legal move.
- `forced_reply_count_by_action`: how many opponent replies are forced after each move.
- `center_control_status`: whether center is occupied and by whom.
- `symmetry_class_by_action`: equivalence classes among legal actions under board symmetry, useful for compression.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Tic-Tac-Toe.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- immediate_win_actions: legal moves that complete a line immediately.
- immediate_block_actions: legal moves that stop the opponent's immediate win.
- dual_threat_count_by_action: number of future winning threats produced by each legal move.
- forced_reply_count_by_action: how many opponent replies are forced after each move.
- center_control_status: whether center is occupied and by whom.
- symmetry_class_by_action: equivalence classes among legal actions under board symmetry, useful for compression.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [immediate_win_actions], prioritize actions supported by those fields.
P2. If opponent threat or forced defense is exposed by [immediate_block_actions], keep only legal actions that answer that threat.
P3. Among remaining actions, rank them using the comparative evidence in [dual_threat_count_by_action, forced_reply_count_by_action, symmetry_class_by_action] and choose the strongest supported action.
P4. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Tic-Tac-Toe

### Group 9

Use only these computed fields:

- `immediate_win_actions`: legal moves that complete a line immediately.
- `forced_reply_count_by_action`: how many opponent replies are forced after each move.
- `center_control_status`: whether center is occupied and by whom.
- `corner_pair_potential_by_action`: whether a move creates or breaks strong corner-based fork structures.
- `draw_preserving_actions`: moves that avoid immediate tactical loss and keep a drawable continuation alive.
- `symmetry_class_by_action`: equivalence classes among legal actions under board symmetry, useful for compression.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Tic-Tac-Toe.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- immediate_win_actions: legal moves that complete a line immediately.
- forced_reply_count_by_action: how many opponent replies are forced after each move.
- center_control_status: whether center is occupied and by whom.
- corner_pair_potential_by_action: whether a move creates or breaks strong corner-based fork structures.
- draw_preserving_actions: moves that avoid immediate tactical loss and keep a drawable continuation alive.
- symmetry_class_by_action: equivalence classes among legal actions under board symmetry, useful for compression.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [immediate_win_actions, draw_preserving_actions], prioritize actions supported by those fields.
P2. Among remaining actions, rank them using the comparative evidence in [forced_reply_count_by_action, symmetry_class_by_action] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Tic-Tac-Toe

### Group 10

Use only these computed fields:

- `immediate_win_actions`: legal moves that complete a line immediately.
- `fork_creation_actions`: legal moves creating at least two next-turn winning threats.
- `opponent_immediate_reply_threats_by_action`: opponent immediate wins available after each candidate move.
- `draw_preserving_actions`: moves that avoid immediate tactical loss and keep a drawable continuation alive.
- `symmetry_class_by_action`: equivalence classes among legal actions under board symmetry, useful for compression.
- `continuation_pressure_by_action`: coarse class such as `forcing`, `neutral`, `defensive_only`, or `self_exposing`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Tic-Tac-Toe.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- immediate_win_actions: legal moves that complete a line immediately.
- fork_creation_actions: legal moves creating at least two next-turn winning threats.
- opponent_immediate_reply_threats_by_action: opponent immediate wins available after each candidate move.
- draw_preserving_actions: moves that avoid immediate tactical loss and keep a drawable continuation alive.
- symmetry_class_by_action: equivalence classes among legal actions under board symmetry, useful for compression.
- continuation_pressure_by_action: coarse class such as `forcing`, `neutral`, `defensive_only`, or `self_exposing`.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [immediate_win_actions, draw_preserving_actions], prioritize actions supported by those fields.
P2. If opponent threat or forced defense is exposed by [opponent_immediate_reply_threats_by_action], keep only legal actions that answer that threat.
P3. Among remaining actions, rank them using the comparative evidence in [symmetry_class_by_action, continuation_pressure_by_action] and choose the strongest supported action.
P4. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Connect Four

### Group 1

Use only these computed fields:

- `immediate_win_columns`: legal columns that create four in a row now.
- `immediate_block_columns`: legal columns that stop an opponent immediate win.
- `diagonal_completion_windows_by_column`: diagonal threat windows touched by each candidate column.
- `opponent_immediate_reply_wins_by_column`: opponent winning columns after each candidate move.
- `odd_even_threat_parity_by_column`: parity-relevant threat timing by landing row and move order.
- `center_distance_by_column`: distance from the center column, used only after tactical filters.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Connect Four.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- immediate_win_columns: legal columns that create four in a row now.
- immediate_block_columns: legal columns that stop an opponent immediate win.
- diagonal_completion_windows_by_column: diagonal threat windows touched by each candidate column.
- opponent_immediate_reply_wins_by_column: opponent winning columns after each candidate move.
- odd_even_threat_parity_by_column: parity-relevant threat timing by landing row and move order.
- center_distance_by_column: distance from the center column, used only after tactical filters.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [immediate_win_columns], prioritize actions supported by those fields.
P2. If opponent threat or forced defense is exposed by [immediate_block_columns, opponent_immediate_reply_wins_by_column], keep only legal actions that answer that threat.
P3. Among remaining actions, rank them using the comparative evidence in [odd_even_threat_parity_by_column, center_distance_by_column] and choose the strongest supported action.
P4. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Connect Four

### Group 2

Use only these computed fields:

- `threat_cells_by_player`: open cells that would complete a future four if made playable.
- `vertical_completion_windows_by_column`: vertical three-plus-empty patterns enabled by each column.
- `horizontal_completion_windows_by_column`: horizontal threat windows touched by each candidate column.
- `diagonal_completion_windows_by_column`: diagonal threat windows touched by each candidate column.
- `support_dependency_by_column`: whether a future threat depends on filling supporting cells underneath it.
- `odd_even_threat_parity_by_column`: parity-relevant threat timing by landing row and move order.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Connect Four.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- threat_cells_by_player: open cells that would complete a future four if made playable.
- vertical_completion_windows_by_column: vertical three-plus-empty patterns enabled by each column.
- horizontal_completion_windows_by_column: horizontal threat windows touched by each candidate column.
- diagonal_completion_windows_by_column: diagonal threat windows touched by each candidate column.
- support_dependency_by_column: whether a future threat depends on filling supporting cells underneath it.
- odd_even_threat_parity_by_column: parity-relevant threat timing by landing row and move order.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [odd_even_threat_parity_by_column] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Connect Four

### Group 3

Use only these computed fields:

- `playable_row_by_column`: landing row for a disc in each legal column.
- `immediate_block_columns`: legal columns that stop an opponent immediate win.
- `vertical_completion_windows_by_column`: vertical three-plus-empty patterns enabled by each column.
- `unsafe_columns`: legal columns that hand the opponent an immediate win or decisive forcing threat.
- `center_distance_by_column`: distance from the center column, used only after tactical filters.
- `forcing_status_by_column`: whether the move is `winning_now`, `must_block`, `threatening`, `safe_positional`, or `unsafe`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Connect Four.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- playable_row_by_column: landing row for a disc in each legal column.
- immediate_block_columns: legal columns that stop an opponent immediate win.
- vertical_completion_windows_by_column: vertical three-plus-empty patterns enabled by each column.
- unsafe_columns: legal columns that hand the opponent an immediate win or decisive forcing threat.
- center_distance_by_column: distance from the center column, used only after tactical filters.
- forcing_status_by_column: whether the move is `winning_now`, `must_block`, `threatening`, `safe_positional`, or `unsafe`.

Decision program:
P0. Choose only from legal actions.
P1. If opponent threat or forced defense is exposed by [immediate_block_columns], keep only legal actions that answer that threat.
P2. Exclude actions flagged as unsafe, dominated, overaggressive, or losing by [unsafe_columns].
P3. Among remaining actions, rank them using the comparative evidence in [center_distance_by_column] and choose the strongest supported action.
P4. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Connect Four

### Group 4

Use only these computed fields:

- `vertical_completion_windows_by_column`: vertical three-plus-empty patterns enabled by each column.
- `horizontal_completion_windows_by_column`: horizontal threat windows touched by each candidate column.
- `double_threat_columns`: columns that create two distinct winning threats for the next turn.
- `support_dependency_by_column`: whether a future threat depends on filling supporting cells underneath it.
- `odd_even_threat_parity_by_column`: parity-relevant threat timing by landing row and move order.
- `future_playability_shift_by_column`: which currently unavailable cells become playable after a move.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Connect Four.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- vertical_completion_windows_by_column: vertical three-plus-empty patterns enabled by each column.
- horizontal_completion_windows_by_column: horizontal threat windows touched by each candidate column.
- double_threat_columns: columns that create two distinct winning threats for the next turn.
- support_dependency_by_column: whether a future threat depends on filling supporting cells underneath it.
- odd_even_threat_parity_by_column: parity-relevant threat timing by landing row and move order.
- future_playability_shift_by_column: which currently unavailable cells become playable after a move.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [double_threat_columns], prioritize actions supported by those fields.
P2. Among remaining actions, rank them using the comparative evidence in [odd_even_threat_parity_by_column] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Connect Four

### Group 5

Use only these computed fields:

- `immediate_block_columns`: legal columns that stop an opponent immediate win.
- `threat_cells_by_player`: open cells that would complete a future four if made playable.
- `diagonal_completion_windows_by_column`: diagonal threat windows touched by each candidate column.
- `unsafe_columns`: legal columns that hand the opponent an immediate win or decisive forcing threat.
- `future_playability_shift_by_column`: which currently unavailable cells become playable after a move.
- `forcing_status_by_column`: whether the move is `winning_now`, `must_block`, `threatening`, `safe_positional`, or `unsafe`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Connect Four.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- immediate_block_columns: legal columns that stop an opponent immediate win.
- threat_cells_by_player: open cells that would complete a future four if made playable.
- diagonal_completion_windows_by_column: diagonal threat windows touched by each candidate column.
- unsafe_columns: legal columns that hand the opponent an immediate win or decisive forcing threat.
- future_playability_shift_by_column: which currently unavailable cells become playable after a move.
- forcing_status_by_column: whether the move is `winning_now`, `must_block`, `threatening`, `safe_positional`, or `unsafe`.

Decision program:
P0. Choose only from legal actions.
P1. If opponent threat or forced defense is exposed by [immediate_block_columns], keep only legal actions that answer that threat.
P2. Exclude actions flagged as unsafe, dominated, overaggressive, or losing by [unsafe_columns].
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Connect Four

### Group 6

Use only these computed fields:

- `playable_row_by_column`: landing row for a disc in each legal column.
- `threat_cells_by_player`: open cells that would complete a future four if made playable.
- `vertical_completion_windows_by_column`: vertical three-plus-empty patterns enabled by each column.
- `horizontal_completion_windows_by_column`: horizontal threat windows touched by each candidate column.
- `center_distance_by_column`: distance from the center column, used only after tactical filters.
- `future_playability_shift_by_column`: which currently unavailable cells become playable after a move.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Connect Four.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- playable_row_by_column: landing row for a disc in each legal column.
- threat_cells_by_player: open cells that would complete a future four if made playable.
- vertical_completion_windows_by_column: vertical three-plus-empty patterns enabled by each column.
- horizontal_completion_windows_by_column: horizontal threat windows touched by each candidate column.
- center_distance_by_column: distance from the center column, used only after tactical filters.
- future_playability_shift_by_column: which currently unavailable cells become playable after a move.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [center_distance_by_column] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Connect Four

### Group 7

Use only these computed fields:

- `playable_row_by_column`: landing row for a disc in each legal column.
- `immediate_block_columns`: legal columns that stop an opponent immediate win.
- `double_threat_columns`: columns that create two distinct winning threats for the next turn.
- `support_dependency_by_column`: whether a future threat depends on filling supporting cells underneath it.
- `future_playability_shift_by_column`: which currently unavailable cells become playable after a move.
- `forcing_status_by_column`: whether the move is `winning_now`, `must_block`, `threatening`, `safe_positional`, or `unsafe`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Connect Four.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- playable_row_by_column: landing row for a disc in each legal column.
- immediate_block_columns: legal columns that stop an opponent immediate win.
- double_threat_columns: columns that create two distinct winning threats for the next turn.
- support_dependency_by_column: whether a future threat depends on filling supporting cells underneath it.
- future_playability_shift_by_column: which currently unavailable cells become playable after a move.
- forcing_status_by_column: whether the move is `winning_now`, `must_block`, `threatening`, `safe_positional`, or `unsafe`.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [double_threat_columns], prioritize actions supported by those fields.
P2. If opponent threat or forced defense is exposed by [immediate_block_columns], keep only legal actions that answer that threat.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Connect Four

### Group 8

Use only these computed fields:

- `immediate_win_columns`: legal columns that create four in a row now.
- `vertical_completion_windows_by_column`: vertical three-plus-empty patterns enabled by each column.
- `horizontal_completion_windows_by_column`: horizontal threat windows touched by each candidate column.
- `opponent_immediate_reply_wins_by_column`: opponent winning columns after each candidate move.
- `unsafe_columns`: legal columns that hand the opponent an immediate win or decisive forcing threat.
- `future_playability_shift_by_column`: which currently unavailable cells become playable after a move.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Connect Four.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- immediate_win_columns: legal columns that create four in a row now.
- vertical_completion_windows_by_column: vertical three-plus-empty patterns enabled by each column.
- horizontal_completion_windows_by_column: horizontal threat windows touched by each candidate column.
- opponent_immediate_reply_wins_by_column: opponent winning columns after each candidate move.
- unsafe_columns: legal columns that hand the opponent an immediate win or decisive forcing threat.
- future_playability_shift_by_column: which currently unavailable cells become playable after a move.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [immediate_win_columns], prioritize actions supported by those fields.
P2. If opponent threat or forced defense is exposed by [opponent_immediate_reply_wins_by_column], keep only legal actions that answer that threat.
P3. Exclude actions flagged as unsafe, dominated, overaggressive, or losing by [unsafe_columns].
P4. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Connect Four

### Group 9

Use only these computed fields:

- `playable_row_by_column`: landing row for a disc in each legal column.
- `immediate_block_columns`: legal columns that stop an opponent immediate win.
- `diagonal_completion_windows_by_column`: diagonal threat windows touched by each candidate column.
- `unsafe_columns`: legal columns that hand the opponent an immediate win or decisive forcing threat.
- `support_dependency_by_column`: whether a future threat depends on filling supporting cells underneath it.
- `future_playability_shift_by_column`: which currently unavailable cells become playable after a move.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Connect Four.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- playable_row_by_column: landing row for a disc in each legal column.
- immediate_block_columns: legal columns that stop an opponent immediate win.
- diagonal_completion_windows_by_column: diagonal threat windows touched by each candidate column.
- unsafe_columns: legal columns that hand the opponent an immediate win or decisive forcing threat.
- support_dependency_by_column: whether a future threat depends on filling supporting cells underneath it.
- future_playability_shift_by_column: which currently unavailable cells become playable after a move.

Decision program:
P0. Choose only from legal actions.
P1. If opponent threat or forced defense is exposed by [immediate_block_columns], keep only legal actions that answer that threat.
P2. Exclude actions flagged as unsafe, dominated, overaggressive, or losing by [unsafe_columns].
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Connect Four

### Group 10

Use only these computed fields:

- `playable_row_by_column`: landing row for a disc in each legal column.
- `immediate_win_columns`: legal columns that create four in a row now.
- `immediate_block_columns`: legal columns that stop an opponent immediate win.
- `diagonal_completion_windows_by_column`: diagonal threat windows touched by each candidate column.
- `opponent_immediate_reply_wins_by_column`: opponent winning columns after each candidate move.
- `unsafe_columns`: legal columns that hand the opponent an immediate win or decisive forcing threat.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Connect Four.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- playable_row_by_column: landing row for a disc in each legal column.
- immediate_win_columns: legal columns that create four in a row now.
- immediate_block_columns: legal columns that stop an opponent immediate win.
- diagonal_completion_windows_by_column: diagonal threat windows touched by each candidate column.
- opponent_immediate_reply_wins_by_column: opponent winning columns after each candidate move.
- unsafe_columns: legal columns that hand the opponent an immediate win or decisive forcing threat.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [immediate_win_columns], prioritize actions supported by those fields.
P2. If opponent threat or forced defense is exposed by [immediate_block_columns, opponent_immediate_reply_wins_by_column], keep only legal actions that answer that threat.
P3. Exclude actions flagged as unsafe, dominated, overaggressive, or losing by [unsafe_columns].
P4. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Breakthrough

### Group 1

Use only these computed fields:

- `opponent_immediate_promotion_threats`: opponent actions that promote next turn if not stopped.
- `destination_defense_status_by_action`: whether the landing square is defended by friendly pieces.
- `promotion_distance_by_piece`: remaining forward steps to promote for each relevant piece.
- `fastest_promotion_lane_by_piece`: least-obstructed lane toward promotion for each advanced piece.
- `back_rank_guard_status`: whether the current move weakens the defense against enemy breakthroughs.
- `opponent_counterpromotion_risk_by_action`: whether a candidate move fails to address a stronger opponent race threat.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Breakthrough.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- opponent_immediate_promotion_threats: opponent actions that promote next turn if not stopped.
- destination_defense_status_by_action: whether the landing square is defended by friendly pieces.
- promotion_distance_by_piece: remaining forward steps to promote for each relevant piece.
- fastest_promotion_lane_by_piece: least-obstructed lane toward promotion for each advanced piece.
- back_rank_guard_status: whether the current move weakens the defense against enemy breakthroughs.
- opponent_counterpromotion_risk_by_action: whether a candidate move fails to address a stronger opponent race threat.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [opponent_immediate_promotion_threats], prioritize actions supported by those fields.
P2. If opponent threat or forced defense is exposed by [opponent_immediate_promotion_threats], keep only legal actions that answer that threat.
P3. Among remaining actions, rank them using the comparative evidence in [promotion_distance_by_piece, opponent_counterpromotion_risk_by_action] and choose the strongest supported action.
P4. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Breakthrough

### Group 2

Use only these computed fields:

- `immediate_promotion_actions`: legal actions that reach the goal row now.
- `destination_defense_status_by_action`: whether the landing square is defended by friendly pieces.
- `recapture_risk_by_action`: whether the moved piece can be captured immediately after the move.
- `promotion_distance_by_piece`: remaining forward steps to promote for each relevant piece.
- `fastest_promotion_lane_by_piece`: least-obstructed lane toward promotion for each advanced piece.
- `lane_blocker_count_by_piece`: number of opposing blockers in a piece's most direct race lane.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Breakthrough.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- immediate_promotion_actions: legal actions that reach the goal row now.
- destination_defense_status_by_action: whether the landing square is defended by friendly pieces.
- recapture_risk_by_action: whether the moved piece can be captured immediately after the move.
- promotion_distance_by_piece: remaining forward steps to promote for each relevant piece.
- fastest_promotion_lane_by_piece: least-obstructed lane toward promotion for each advanced piece.
- lane_blocker_count_by_piece: number of opposing blockers in a piece's most direct race lane.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [immediate_promotion_actions], prioritize actions supported by those fields.
P2. Among remaining actions, rank them using the comparative evidence in [recapture_risk_by_action, promotion_distance_by_piece, lane_blocker_count_by_piece] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Breakthrough

### Group 3

Use only these computed fields:

- `opponent_immediate_promotion_threats`: opponent actions that promote next turn if not stopped.
- `capture_actions`: legal diagonal captures and captured target coordinates.
- `promotion_distance_by_piece`: remaining forward steps to promote for each relevant piece.
- `fastest_promotion_lane_by_piece`: least-obstructed lane toward promotion for each advanced piece.
- `material_swing_by_action`: immediate material gain or loss caused by a move.
- `race_leader_after_action`: which side has the fastest promotion route after the move.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Breakthrough.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- opponent_immediate_promotion_threats: opponent actions that promote next turn if not stopped.
- capture_actions: legal diagonal captures and captured target coordinates.
- promotion_distance_by_piece: remaining forward steps to promote for each relevant piece.
- fastest_promotion_lane_by_piece: least-obstructed lane toward promotion for each advanced piece.
- material_swing_by_action: immediate material gain or loss caused by a move.
- race_leader_after_action: which side has the fastest promotion route after the move.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [opponent_immediate_promotion_threats], prioritize actions supported by those fields.
P2. If opponent threat or forced defense is exposed by [opponent_immediate_promotion_threats], keep only legal actions that answer that threat.
P3. Among remaining actions, rank them using the comparative evidence in [promotion_distance_by_piece] and choose the strongest supported action.
P4. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Breakthrough

### Group 4

Use only these computed fields:

- `immediate_promotion_actions`: legal actions that reach the goal row now.
- `recapture_risk_by_action`: whether the moved piece can be captured immediately after the move.
- `material_swing_by_action`: immediate material gain or loss caused by a move.
- `back_rank_guard_status`: whether the current move weakens the defense against enemy breakthroughs.
- `race_leader_after_action`: which side has the fastest promotion route after the move.
- `continuation_race_pressure_by_action`: coarse continuation class such as `force_race`, `stabilize`, `trade_for_time`, or `self_expose`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Breakthrough.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- immediate_promotion_actions: legal actions that reach the goal row now.
- recapture_risk_by_action: whether the moved piece can be captured immediately after the move.
- material_swing_by_action: immediate material gain or loss caused by a move.
- back_rank_guard_status: whether the current move weakens the defense against enemy breakthroughs.
- race_leader_after_action: which side has the fastest promotion route after the move.
- continuation_race_pressure_by_action: coarse continuation class such as `force_race`, `stabilize`, `trade_for_time`, or `self_expose`.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [immediate_promotion_actions], prioritize actions supported by those fields.
P2. Among remaining actions, rank them using the comparative evidence in [recapture_risk_by_action, continuation_race_pressure_by_action] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Breakthrough

### Group 5

Use only these computed fields:

- `opponent_immediate_promotion_threats`: opponent actions that promote next turn if not stopped.
- `destination_defense_status_by_action`: whether the landing square is defended by friendly pieces.
- `lane_blocker_count_by_piece`: number of opposing blockers in a piece's most direct race lane.
- `material_swing_by_action`: immediate material gain or loss caused by a move.
- `race_leader_after_action`: which side has the fastest promotion route after the move.
- `continuation_race_pressure_by_action`: coarse continuation class such as `force_race`, `stabilize`, `trade_for_time`, or `self_expose`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Breakthrough.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- opponent_immediate_promotion_threats: opponent actions that promote next turn if not stopped.
- destination_defense_status_by_action: whether the landing square is defended by friendly pieces.
- lane_blocker_count_by_piece: number of opposing blockers in a piece's most direct race lane.
- material_swing_by_action: immediate material gain or loss caused by a move.
- race_leader_after_action: which side has the fastest promotion route after the move.
- continuation_race_pressure_by_action: coarse continuation class such as `force_race`, `stabilize`, `trade_for_time`, or `self_expose`.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [opponent_immediate_promotion_threats], prioritize actions supported by those fields.
P2. If opponent threat or forced defense is exposed by [opponent_immediate_promotion_threats], keep only legal actions that answer that threat.
P3. Among remaining actions, rank them using the comparative evidence in [lane_blocker_count_by_piece, continuation_race_pressure_by_action] and choose the strongest supported action.
P4. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Breakthrough

### Group 6

Use only these computed fields:

- `promotion_distance_by_piece`: remaining forward steps to promote for each relevant piece.
- `fastest_promotion_lane_by_piece`: least-obstructed lane toward promotion for each advanced piece.
- `lane_blocker_count_by_piece`: number of opposing blockers in a piece's most direct race lane.
- `material_swing_by_action`: immediate material gain or loss caused by a move.
- `back_rank_guard_status`: whether the current move weakens the defense against enemy breakthroughs.
- `continuation_race_pressure_by_action`: coarse continuation class such as `force_race`, `stabilize`, `trade_for_time`, or `self_expose`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Breakthrough.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- promotion_distance_by_piece: remaining forward steps to promote for each relevant piece.
- fastest_promotion_lane_by_piece: least-obstructed lane toward promotion for each advanced piece.
- lane_blocker_count_by_piece: number of opposing blockers in a piece's most direct race lane.
- material_swing_by_action: immediate material gain or loss caused by a move.
- back_rank_guard_status: whether the current move weakens the defense against enemy breakthroughs.
- continuation_race_pressure_by_action: coarse continuation class such as `force_race`, `stabilize`, `trade_for_time`, or `self_expose`.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [promotion_distance_by_piece, lane_blocker_count_by_piece, continuation_race_pressure_by_action] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Breakthrough

### Group 7

Use only these computed fields:

- `opponent_immediate_promotion_threats`: opponent actions that promote next turn if not stopped.
- `capture_actions`: legal diagonal captures and captured target coordinates.
- `material_swing_by_action`: immediate material gain or loss caused by a move.
- `back_rank_guard_status`: whether the current move weakens the defense against enemy breakthroughs.
- `opponent_counterpromotion_risk_by_action`: whether a candidate move fails to address a stronger opponent race threat.
- `continuation_race_pressure_by_action`: coarse continuation class such as `force_race`, `stabilize`, `trade_for_time`, or `self_expose`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Breakthrough.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- opponent_immediate_promotion_threats: opponent actions that promote next turn if not stopped.
- capture_actions: legal diagonal captures and captured target coordinates.
- material_swing_by_action: immediate material gain or loss caused by a move.
- back_rank_guard_status: whether the current move weakens the defense against enemy breakthroughs.
- opponent_counterpromotion_risk_by_action: whether a candidate move fails to address a stronger opponent race threat.
- continuation_race_pressure_by_action: coarse continuation class such as `force_race`, `stabilize`, `trade_for_time`, or `self_expose`.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [opponent_immediate_promotion_threats], prioritize actions supported by those fields.
P2. If opponent threat or forced defense is exposed by [opponent_immediate_promotion_threats], keep only legal actions that answer that threat.
P3. Among remaining actions, rank them using the comparative evidence in [opponent_counterpromotion_risk_by_action, continuation_race_pressure_by_action] and choose the strongest supported action.
P4. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Breakthrough

### Group 8

Use only these computed fields:

- `destination_defense_status_by_action`: whether the landing square is defended by friendly pieces.
- `promotion_distance_by_piece`: remaining forward steps to promote for each relevant piece.
- `fastest_promotion_lane_by_piece`: least-obstructed lane toward promotion for each advanced piece.
- `back_rank_guard_status`: whether the current move weakens the defense against enemy breakthroughs.
- `race_leader_after_action`: which side has the fastest promotion route after the move.
- `continuation_race_pressure_by_action`: coarse continuation class such as `force_race`, `stabilize`, `trade_for_time`, or `self_expose`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Breakthrough.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- destination_defense_status_by_action: whether the landing square is defended by friendly pieces.
- promotion_distance_by_piece: remaining forward steps to promote for each relevant piece.
- fastest_promotion_lane_by_piece: least-obstructed lane toward promotion for each advanced piece.
- back_rank_guard_status: whether the current move weakens the defense against enemy breakthroughs.
- race_leader_after_action: which side has the fastest promotion route after the move.
- continuation_race_pressure_by_action: coarse continuation class such as `force_race`, `stabilize`, `trade_for_time`, or `self_expose`.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [promotion_distance_by_piece, continuation_race_pressure_by_action] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Breakthrough

### Group 9

Use only these computed fields:

- `immediate_promotion_actions`: legal actions that reach the goal row now.
- `destination_defense_status_by_action`: whether the landing square is defended by friendly pieces.
- `promotion_distance_by_piece`: remaining forward steps to promote for each relevant piece.
- `race_leader_after_action`: which side has the fastest promotion route after the move.
- `opponent_counterpromotion_risk_by_action`: whether a candidate move fails to address a stronger opponent race threat.
- `continuation_race_pressure_by_action`: coarse continuation class such as `force_race`, `stabilize`, `trade_for_time`, or `self_expose`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Breakthrough.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- immediate_promotion_actions: legal actions that reach the goal row now.
- destination_defense_status_by_action: whether the landing square is defended by friendly pieces.
- promotion_distance_by_piece: remaining forward steps to promote for each relevant piece.
- race_leader_after_action: which side has the fastest promotion route after the move.
- opponent_counterpromotion_risk_by_action: whether a candidate move fails to address a stronger opponent race threat.
- continuation_race_pressure_by_action: coarse continuation class such as `force_race`, `stabilize`, `trade_for_time`, or `self_expose`.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [immediate_promotion_actions], prioritize actions supported by those fields.
P2. Among remaining actions, rank them using the comparative evidence in [promotion_distance_by_piece, opponent_counterpromotion_risk_by_action, continuation_race_pressure_by_action] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Breakthrough

### Group 10

Use only these computed fields:

- `immediate_promotion_actions`: legal actions that reach the goal row now.
- `recapture_risk_by_action`: whether the moved piece can be captured immediately after the move.
- `promotion_distance_by_piece`: remaining forward steps to promote for each relevant piece.
- `material_swing_by_action`: immediate material gain or loss caused by a move.
- `passed_pawn_flag_by_action`: whether the moved piece becomes effectively unblocked on its lane after the action.
- `continuation_race_pressure_by_action`: coarse continuation class such as `force_race`, `stabilize`, `trade_for_time`, or `self_expose`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Breakthrough.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- immediate_promotion_actions: legal actions that reach the goal row now.
- recapture_risk_by_action: whether the moved piece can be captured immediately after the move.
- promotion_distance_by_piece: remaining forward steps to promote for each relevant piece.
- material_swing_by_action: immediate material gain or loss caused by a move.
- passed_pawn_flag_by_action: whether the moved piece becomes effectively unblocked on its lane after the action.
- continuation_race_pressure_by_action: coarse continuation class such as `force_race`, `stabilize`, `trade_for_time`, or `self_expose`.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [immediate_promotion_actions], prioritize actions supported by those fields.
P2. Among remaining actions, rank them using the comparative evidence in [recapture_risk_by_action, promotion_distance_by_piece, continuation_race_pressure_by_action] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Nim

### Group 1

Use only these computed fields:

- `large_pile_count_by_action`: number of piles with size greater than one in each successor.
- `phase_classification_by_action`: `normal_phase` versus `misere_endgame` after each action.
- `zero_nim_sum_flag_by_action`: whether the successor nim-sum is zero.
- `all_singletons_flag_by_action`: whether the successor state contains only singleton piles.
- `terminal_take_last_flag_by_action`: whether the move removes the final remaining match.
- `opponent_position_value_by_action`: whether the opponent receives a winning, losing, or unclear continuation state.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Nim.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- large_pile_count_by_action: number of piles with size greater than one in each successor.
- phase_classification_by_action: `normal_phase` versus `misere_endgame` after each action.
- zero_nim_sum_flag_by_action: whether the successor nim-sum is zero.
- all_singletons_flag_by_action: whether the successor state contains only singleton piles.
- terminal_take_last_flag_by_action: whether the move removes the final remaining match.
- opponent_position_value_by_action: whether the opponent receives a winning, losing, or unclear continuation state.

Decision program:
P0. Choose only from legal actions.
P1. Exclude actions flagged as unsafe, dominated, overaggressive, or losing by [terminal_take_last_flag_by_action].
P2. Among remaining actions, rank them using the comparative evidence in [large_pile_count_by_action, phase_classification_by_action, zero_nim_sum_flag_by_action, opponent_position_value_by_action] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Nim

### Group 2

Use only these computed fields:

- `total_matches_after_action`: total remaining matches after each move.
- `large_pile_count_by_action`: number of piles with size greater than one in each successor.
- `all_singletons_flag_by_action`: whether the successor state contains only singleton piles.
- `terminal_take_last_flag_by_action`: whether the move removes the final remaining match.
- `endgame_parity_target_by_action`: whether the successor singleton parity is favorable under misere endgame logic.
- `opponent_position_value_by_action`: whether the opponent receives a winning, losing, or unclear continuation state.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Nim.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- total_matches_after_action: total remaining matches after each move.
- large_pile_count_by_action: number of piles with size greater than one in each successor.
- all_singletons_flag_by_action: whether the successor state contains only singleton piles.
- terminal_take_last_flag_by_action: whether the move removes the final remaining match.
- endgame_parity_target_by_action: whether the successor singleton parity is favorable under misere endgame logic.
- opponent_position_value_by_action: whether the opponent receives a winning, losing, or unclear continuation state.

Decision program:
P0. Choose only from legal actions.
P1. Exclude actions flagged as unsafe, dominated, overaggressive, or losing by [terminal_take_last_flag_by_action].
P2. Among remaining actions, rank them using the comparative evidence in [large_pile_count_by_action, endgame_parity_target_by_action, opponent_position_value_by_action] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Nim

### Group 3

Use only these computed fields:

- `large_pile_count_by_action`: number of piles with size greater than one in each successor.
- `nim_sum_by_action`: xor value of the successor state when normal-phase logic is relevant.
- `all_singletons_flag_by_action`: whether the successor state contains only singleton piles.
- `terminal_take_last_flag_by_action`: whether the move removes the final remaining match.
- `forced_loss_indicator`: whether every legal move passes a winning state to the opponent.
- `action_equivalence_classes_by_successor_state`: actions that differ syntactically but induce the same successor state class.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Nim.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- large_pile_count_by_action: number of piles with size greater than one in each successor.
- nim_sum_by_action: xor value of the successor state when normal-phase logic is relevant.
- all_singletons_flag_by_action: whether the successor state contains only singleton piles.
- terminal_take_last_flag_by_action: whether the move removes the final remaining match.
- forced_loss_indicator: whether every legal move passes a winning state to the opponent.
- action_equivalence_classes_by_successor_state: actions that differ syntactically but induce the same successor state class.

Decision program:
P0. Choose only from legal actions.
P1. Exclude actions flagged as unsafe, dominated, overaggressive, or losing by [terminal_take_last_flag_by_action, forced_loss_indicator].
P2. Among remaining actions, rank them using the comparative evidence in [large_pile_count_by_action, nim_sum_by_action, action_equivalence_classes_by_successor_state] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Nim

### Group 4

Use only these computed fields:

- `nonzero_pile_count_by_action`: number of nonempty piles in each successor.
- `large_pile_count_by_action`: number of piles with size greater than one in each successor.
- `phase_classification_by_action`: `normal_phase` versus `misere_endgame` after each action.
- `nim_sum_by_action`: xor value of the successor state when normal-phase logic is relevant.
- `zero_nim_sum_flag_by_action`: whether the successor nim-sum is zero.
- `opponent_position_value_by_action`: whether the opponent receives a winning, losing, or unclear continuation state.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Nim.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- nonzero_pile_count_by_action: number of nonempty piles in each successor.
- large_pile_count_by_action: number of piles with size greater than one in each successor.
- phase_classification_by_action: `normal_phase` versus `misere_endgame` after each action.
- nim_sum_by_action: xor value of the successor state when normal-phase logic is relevant.
- zero_nim_sum_flag_by_action: whether the successor nim-sum is zero.
- opponent_position_value_by_action: whether the opponent receives a winning, losing, or unclear continuation state.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [nonzero_pile_count_by_action, large_pile_count_by_action, phase_classification_by_action, nim_sum_by_action, zero_nim_sum_flag_by_action, opponent_position_value_by_action] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Nim

### Group 5

Use only these computed fields:

- `total_matches_after_action`: total remaining matches after each move.
- `phase_classification_by_action`: `normal_phase` versus `misere_endgame` after each action.
- `nim_sum_by_action`: xor value of the successor state when normal-phase logic is relevant.
- `zero_nim_sum_flag_by_action`: whether the successor nim-sum is zero.
- `all_singletons_flag_by_action`: whether the successor state contains only singleton piles.
- `action_equivalence_classes_by_successor_state`: actions that differ syntactically but induce the same successor state class.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Nim.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- total_matches_after_action: total remaining matches after each move.
- phase_classification_by_action: `normal_phase` versus `misere_endgame` after each action.
- nim_sum_by_action: xor value of the successor state when normal-phase logic is relevant.
- zero_nim_sum_flag_by_action: whether the successor nim-sum is zero.
- all_singletons_flag_by_action: whether the successor state contains only singleton piles.
- action_equivalence_classes_by_successor_state: actions that differ syntactically but induce the same successor state class.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [phase_classification_by_action, nim_sum_by_action, zero_nim_sum_flag_by_action, action_equivalence_classes_by_successor_state] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Nim

### Group 6

Use only these computed fields:

- `legal_move_effects`: successor pile state for every legal move.
- `singleton_count_by_action`: number of size-one piles in each successor.
- `phase_classification_by_action`: `normal_phase` versus `misere_endgame` after each action.
- `endgame_parity_target_by_action`: whether the successor singleton parity is favorable under misere endgame logic.
- `forced_loss_indicator`: whether every legal move passes a winning state to the opponent.
- `action_equivalence_classes_by_successor_state`: actions that differ syntactically but induce the same successor state class.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Nim.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- legal_move_effects: successor pile state for every legal move.
- singleton_count_by_action: number of size-one piles in each successor.
- phase_classification_by_action: `normal_phase` versus `misere_endgame` after each action.
- endgame_parity_target_by_action: whether the successor singleton parity is favorable under misere endgame logic.
- forced_loss_indicator: whether every legal move passes a winning state to the opponent.
- action_equivalence_classes_by_successor_state: actions that differ syntactically but induce the same successor state class.

Decision program:
P0. Choose only from legal actions.
P1. Exclude actions flagged as unsafe, dominated, overaggressive, or losing by [forced_loss_indicator].
P2. Among remaining actions, rank them using the comparative evidence in [singleton_count_by_action, phase_classification_by_action, endgame_parity_target_by_action, action_equivalence_classes_by_successor_state] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Nim

### Group 7

Use only these computed fields:

- `legal_move_effects`: successor pile state for every legal move.
- `nonzero_pile_count_by_action`: number of nonempty piles in each successor.
- `zero_nim_sum_flag_by_action`: whether the successor nim-sum is zero.
- `all_singletons_flag_by_action`: whether the successor state contains only singleton piles.
- `endgame_parity_target_by_action`: whether the successor singleton parity is favorable under misere endgame logic.
- `action_equivalence_classes_by_successor_state`: actions that differ syntactically but induce the same successor state class.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Nim.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- legal_move_effects: successor pile state for every legal move.
- nonzero_pile_count_by_action: number of nonempty piles in each successor.
- zero_nim_sum_flag_by_action: whether the successor nim-sum is zero.
- all_singletons_flag_by_action: whether the successor state contains only singleton piles.
- endgame_parity_target_by_action: whether the successor singleton parity is favorable under misere endgame logic.
- action_equivalence_classes_by_successor_state: actions that differ syntactically but induce the same successor state class.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [nonzero_pile_count_by_action, zero_nim_sum_flag_by_action, endgame_parity_target_by_action, action_equivalence_classes_by_successor_state] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Nim

### Group 8

Use only these computed fields:

- `legal_move_effects`: successor pile state for every legal move.
- `nonzero_pile_count_by_action`: number of nonempty piles in each successor.
- `large_pile_count_by_action`: number of piles with size greater than one in each successor.
- `singleton_count_by_action`: number of size-one piles in each successor.
- `phase_classification_by_action`: `normal_phase` versus `misere_endgame` after each action.
- `endgame_parity_target_by_action`: whether the successor singleton parity is favorable under misere endgame logic.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Nim.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- legal_move_effects: successor pile state for every legal move.
- nonzero_pile_count_by_action: number of nonempty piles in each successor.
- large_pile_count_by_action: number of piles with size greater than one in each successor.
- singleton_count_by_action: number of size-one piles in each successor.
- phase_classification_by_action: `normal_phase` versus `misere_endgame` after each action.
- endgame_parity_target_by_action: whether the successor singleton parity is favorable under misere endgame logic.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [nonzero_pile_count_by_action, large_pile_count_by_action, singleton_count_by_action, phase_classification_by_action, endgame_parity_target_by_action] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Nim

### Group 9

Use only these computed fields:

- `total_matches_after_action`: total remaining matches after each move.
- `large_pile_count_by_action`: number of piles with size greater than one in each successor.
- `endgame_parity_target_by_action`: whether the successor singleton parity is favorable under misere endgame logic.
- `opponent_position_value_by_action`: whether the opponent receives a winning, losing, or unclear continuation state.
- `forced_loss_indicator`: whether every legal move passes a winning state to the opponent.
- `action_equivalence_classes_by_successor_state`: actions that differ syntactically but induce the same successor state class.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Nim.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- total_matches_after_action: total remaining matches after each move.
- large_pile_count_by_action: number of piles with size greater than one in each successor.
- endgame_parity_target_by_action: whether the successor singleton parity is favorable under misere endgame logic.
- opponent_position_value_by_action: whether the opponent receives a winning, losing, or unclear continuation state.
- forced_loss_indicator: whether every legal move passes a winning state to the opponent.
- action_equivalence_classes_by_successor_state: actions that differ syntactically but induce the same successor state class.

Decision program:
P0. Choose only from legal actions.
P1. Exclude actions flagged as unsafe, dominated, overaggressive, or losing by [forced_loss_indicator].
P2. Among remaining actions, rank them using the comparative evidence in [large_pile_count_by_action, endgame_parity_target_by_action, opponent_position_value_by_action, action_equivalence_classes_by_successor_state] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Nim

### Group 10

Use only these computed fields:

- `total_matches_after_action`: total remaining matches after each move.
- `large_pile_count_by_action`: number of piles with size greater than one in each successor.
- `singleton_count_by_action`: number of size-one piles in each successor.
- `zero_nim_sum_flag_by_action`: whether the successor nim-sum is zero.
- `endgame_parity_target_by_action`: whether the successor singleton parity is favorable under misere endgame logic.
- `opponent_position_value_by_action`: whether the opponent receives a winning, losing, or unclear continuation state.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Nim.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- total_matches_after_action: total remaining matches after each move.
- large_pile_count_by_action: number of piles with size greater than one in each successor.
- singleton_count_by_action: number of size-one piles in each successor.
- zero_nim_sum_flag_by_action: whether the successor nim-sum is zero.
- endgame_parity_target_by_action: whether the successor singleton parity is favorable under misere endgame logic.
- opponent_position_value_by_action: whether the opponent receives a winning, losing, or unclear continuation state.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [large_pile_count_by_action, singleton_count_by_action, zero_nim_sum_flag_by_action, endgame_parity_target_by_action, opponent_position_value_by_action] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Pig

### Group 1

Use only these computed fields:

- `score_after_stop`: score obtained by banking the current turn total.
- `bust_probability`: probability of losing the current turn total on the next roll.
- `expected_safe_gain`: expected point gain conditional on not busting.
- `one_roll_expected_value`: one-step expected value proxy for choosing `roll`.
- `score_gap`: `self_score - opponent_score`.
- `roll_vs_stop_margin`: compact comparison between certain stop value and risk-adjusted roll value.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Pig.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- score_after_stop: score obtained by banking the current turn total.
- bust_probability: probability of losing the current turn total on the next roll.
- expected_safe_gain: expected point gain conditional on not busting.
- one_roll_expected_value: one-step expected value proxy for choosing `roll`.
- score_gap: `self_score - opponent_score`.
- roll_vs_stop_margin: compact comparison between certain stop value and risk-adjusted roll value.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [bust_probability, expected_safe_gain, one_roll_expected_value, roll_vs_stop_margin] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Pig

### Group 2

Use only these computed fields:

- `bust_probability`: probability of losing the current turn total on the next roll.
- `expected_safe_gain`: expected point gain conditional on not busting.
- `one_roll_expected_value`: one-step expected value proxy for choosing `roll`.
- `bank_value_ratio`: current bankable value relative to the remaining distance to target.
- `desperation_level`: how much extra variance is justified by the score race.
- `roll_vs_stop_margin`: compact comparison between certain stop value and risk-adjusted roll value.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Pig.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- bust_probability: probability of losing the current turn total on the next roll.
- expected_safe_gain: expected point gain conditional on not busting.
- one_roll_expected_value: one-step expected value proxy for choosing `roll`.
- bank_value_ratio: current bankable value relative to the remaining distance to target.
- desperation_level: how much extra variance is justified by the score race.
- roll_vs_stop_margin: compact comparison between certain stop value and risk-adjusted roll value.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [bust_probability, expected_safe_gain, one_roll_expected_value, bank_value_ratio, roll_vs_stop_margin] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Pig

### Group 3

Use only these computed fields:

- `stop_leaves_opponent_near_finish`: whether stopping hands the turn to an opponent who is already close to winning.
- `bust_probability`: probability of losing the current turn total on the next roll.
- `safe_roll_outcome_distribution`: non-bust roll outcomes and resulting new turn totals.
- `self_distance_to_target`: points needed for self to finish.
- `desperation_level`: how much extra variance is justified by the score race.
- `roll_vs_stop_margin`: compact comparison between certain stop value and risk-adjusted roll value.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Pig.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- stop_leaves_opponent_near_finish: whether stopping hands the turn to an opponent who is already close to winning.
- bust_probability: probability of losing the current turn total on the next roll.
- safe_roll_outcome_distribution: non-bust roll outcomes and resulting new turn totals.
- self_distance_to_target: points needed for self to finish.
- desperation_level: how much extra variance is justified by the score race.
- roll_vs_stop_margin: compact comparison between certain stop value and risk-adjusted roll value.

Decision program:
P0. Choose only from legal actions.
P1. If opponent threat or forced defense is exposed by [stop_leaves_opponent_near_finish], keep only legal actions that answer that threat.
P2. Among remaining actions, rank them using the comparative evidence in [bust_probability, self_distance_to_target, roll_vs_stop_margin] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Pig

### Group 4

Use only these computed fields:

- `bust_probability`: probability of losing the current turn total on the next roll.
- `bust_loss`: number of temporary points lost if a bust occurs now.
- `score_gap`: `self_score - opponent_score`.
- `opponent_distance_to_target`: points needed for opponent to finish.
- `desperation_level`: how much extra variance is justified by the score race.
- `roll_vs_stop_margin`: compact comparison between certain stop value and risk-adjusted roll value.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Pig.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- bust_probability: probability of losing the current turn total on the next roll.
- bust_loss: number of temporary points lost if a bust occurs now.
- score_gap: `self_score - opponent_score`.
- opponent_distance_to_target: points needed for opponent to finish.
- desperation_level: how much extra variance is justified by the score race.
- roll_vs_stop_margin: compact comparison between certain stop value and risk-adjusted roll value.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [bust_probability, opponent_distance_to_target, roll_vs_stop_margin] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Pig

### Group 5

Use only these computed fields:

- `stop_leaves_opponent_near_finish`: whether stopping hands the turn to an opponent who is already close to winning.
- `bust_probability`: probability of losing the current turn total on the next roll.
- `expected_safe_gain`: expected point gain conditional on not busting.
- `self_distance_to_target`: points needed for self to finish.
- `race_pressure_class`: coarse state such as `ahead_safe`, `behind_chasing`, `must_finish_soon`, or `opponent_threatening`.
- `desperation_level`: how much extra variance is justified by the score race.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Pig.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- stop_leaves_opponent_near_finish: whether stopping hands the turn to an opponent who is already close to winning.
- bust_probability: probability of losing the current turn total on the next roll.
- expected_safe_gain: expected point gain conditional on not busting.
- self_distance_to_target: points needed for self to finish.
- race_pressure_class: coarse state such as `ahead_safe`, `behind_chasing`, `must_finish_soon`, or `opponent_threatening`.
- desperation_level: how much extra variance is justified by the score race.

Decision program:
P0. Choose only from legal actions.
P1. If opponent threat or forced defense is exposed by [stop_leaves_opponent_near_finish], keep only legal actions that answer that threat.
P2. Among remaining actions, rank them using the comparative evidence in [bust_probability, expected_safe_gain, self_distance_to_target, race_pressure_class] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Pig

### Group 6

Use only these computed fields:

- `one_roll_expected_value`: one-step expected value proxy for choosing `roll`.
- `score_gap`: `self_score - opponent_score`.
- `opponent_distance_to_target`: points needed for opponent to finish.
- `race_pressure_class`: coarse state such as `ahead_safe`, `behind_chasing`, `must_finish_soon`, or `opponent_threatening`.
- `desperation_level`: how much extra variance is justified by the score race.
- `roll_vs_stop_margin`: compact comparison between certain stop value and risk-adjusted roll value.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Pig.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- one_roll_expected_value: one-step expected value proxy for choosing `roll`.
- score_gap: `self_score - opponent_score`.
- opponent_distance_to_target: points needed for opponent to finish.
- race_pressure_class: coarse state such as `ahead_safe`, `behind_chasing`, `must_finish_soon`, or `opponent_threatening`.
- desperation_level: how much extra variance is justified by the score race.
- roll_vs_stop_margin: compact comparison between certain stop value and risk-adjusted roll value.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [one_roll_expected_value, opponent_distance_to_target, race_pressure_class, roll_vs_stop_margin] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Pig

### Group 7

Use only these computed fields:

- `score_after_stop`: score obtained by banking the current turn total.
- `bust_probability`: probability of losing the current turn total on the next roll.
- `safe_roll_outcome_distribution`: non-bust roll outcomes and resulting new turn totals.
- `one_roll_expected_value`: one-step expected value proxy for choosing `roll`.
- `score_gap`: `self_score - opponent_score`.
- `opponent_distance_to_target`: points needed for opponent to finish.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Pig.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- score_after_stop: score obtained by banking the current turn total.
- bust_probability: probability of losing the current turn total on the next roll.
- safe_roll_outcome_distribution: non-bust roll outcomes and resulting new turn totals.
- one_roll_expected_value: one-step expected value proxy for choosing `roll`.
- score_gap: `self_score - opponent_score`.
- opponent_distance_to_target: points needed for opponent to finish.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [bust_probability, one_roll_expected_value, opponent_distance_to_target] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Pig

### Group 8

Use only these computed fields:

- `score_after_stop`: score obtained by banking the current turn total.
- `stop_leaves_opponent_near_finish`: whether stopping hands the turn to an opponent who is already close to winning.
- `bust_loss`: number of temporary points lost if a bust occurs now.
- `opponent_distance_to_target`: points needed for opponent to finish.
- `bank_value_ratio`: current bankable value relative to the remaining distance to target.
- `roll_vs_stop_margin`: compact comparison between certain stop value and risk-adjusted roll value.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Pig.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- score_after_stop: score obtained by banking the current turn total.
- stop_leaves_opponent_near_finish: whether stopping hands the turn to an opponent who is already close to winning.
- bust_loss: number of temporary points lost if a bust occurs now.
- opponent_distance_to_target: points needed for opponent to finish.
- bank_value_ratio: current bankable value relative to the remaining distance to target.
- roll_vs_stop_margin: compact comparison between certain stop value and risk-adjusted roll value.

Decision program:
P0. Choose only from legal actions.
P1. If opponent threat or forced defense is exposed by [stop_leaves_opponent_near_finish], keep only legal actions that answer that threat.
P2. Among remaining actions, rank them using the comparative evidence in [opponent_distance_to_target, bank_value_ratio, roll_vs_stop_margin] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Pig

### Group 9

Use only these computed fields:

- `expected_safe_gain`: expected point gain conditional on not busting.
- `score_gap`: `self_score - opponent_score`.
- `opponent_distance_to_target`: points needed for opponent to finish.
- `race_pressure_class`: coarse state such as `ahead_safe`, `behind_chasing`, `must_finish_soon`, or `opponent_threatening`.
- `bank_value_ratio`: current bankable value relative to the remaining distance to target.
- `desperation_level`: how much extra variance is justified by the score race.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Pig.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- expected_safe_gain: expected point gain conditional on not busting.
- score_gap: `self_score - opponent_score`.
- opponent_distance_to_target: points needed for opponent to finish.
- race_pressure_class: coarse state such as `ahead_safe`, `behind_chasing`, `must_finish_soon`, or `opponent_threatening`.
- bank_value_ratio: current bankable value relative to the remaining distance to target.
- desperation_level: how much extra variance is justified by the score race.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [expected_safe_gain, opponent_distance_to_target, race_pressure_class, bank_value_ratio] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Pig

### Group 10

Use only these computed fields:

- `stop_wins_now`: whether stopping reaches or exceeds target immediately.
- `stop_leaves_opponent_near_finish`: whether stopping hands the turn to an opponent who is already close to winning.
- `bust_probability`: probability of losing the current turn total on the next roll.
- `safe_roll_outcome_distribution`: non-bust roll outcomes and resulting new turn totals.
- `self_distance_to_target`: points needed for self to finish.
- `bank_value_ratio`: current bankable value relative to the remaining distance to target.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Pig.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- stop_wins_now: whether stopping reaches or exceeds target immediately.
- stop_leaves_opponent_near_finish: whether stopping hands the turn to an opponent who is already close to winning.
- bust_probability: probability of losing the current turn total on the next roll.
- safe_roll_outcome_distribution: non-bust roll outcomes and resulting new turn totals.
- self_distance_to_target: points needed for self to finish.
- bank_value_ratio: current bankable value relative to the remaining distance to target.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [stop_wins_now], prioritize actions supported by those fields.
P2. If opponent threat or forced defense is exposed by [stop_leaves_opponent_near_finish], keep only legal actions that answer that threat.
P3. Among remaining actions, rank them using the comparative evidence in [bust_probability, self_distance_to_target, bank_value_ratio] and choose the strongest supported action.
P4. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## First-Sealed Auction

### Group 1

Use only these computed fields:

- `bid_shading_amount`: `valuation - bid` for each legal bid.
- `overbid_actions`: legal bids above private value.
- `zero_surplus_actions`: bids equal to private value.
- `tie_case_if_bid_equals_opponent`: tie-handling assumption if the rules or implementation specify one.
- `robust_bid_interval_under_belief_range`: bids that remain reasonable across a range of opponent bid beliefs.
- `aggressiveness_class_by_bid`: coarse label such as `too_passive`, `moderate_shade`, `near_value`, or `overbid`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for First-Sealed Auction.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- bid_shading_amount: `valuation - bid` for each legal bid.
- overbid_actions: legal bids above private value.
- zero_surplus_actions: bids equal to private value.
- tie_case_if_bid_equals_opponent: tie-handling assumption if the rules or implementation specify one.
- robust_bid_interval_under_belief_range: bids that remain reasonable across a range of opponent bid beliefs.
- aggressiveness_class_by_bid: coarse label such as `too_passive`, `moderate_shade`, `near_value`, or `overbid`.

Decision program:
P0. Choose only from legal actions.
P1. Exclude actions flagged as unsafe, dominated, overaggressive, or losing by [overbid_actions].
P2. Among remaining actions, rank them using the comparative evidence in [zero_surplus_actions, aggressiveness_class_by_bid] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## First-Sealed Auction

### Group 2

Use only these computed fields:

- `bid_rank_order`: legal bids sorted from least to most aggressive.
- `win_probability_assumption_by_bid`: explicit assumed winning chance for each candidate bid under the current belief model.
- `tie_case_if_bid_equals_opponent`: tie-handling assumption if the rules or implementation specify one.
- `profit_floor_by_bid`: worst-case profit implication if the bid wins.
- `regret_if_lose_with_low_bid`: missed-value pressure from shading too much.
- `regret_if_win_with_high_bid`: profit erosion from shading too little.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for First-Sealed Auction.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- bid_rank_order: legal bids sorted from least to most aggressive.
- win_probability_assumption_by_bid: explicit assumed winning chance for each candidate bid under the current belief model.
- tie_case_if_bid_equals_opponent: tie-handling assumption if the rules or implementation specify one.
- profit_floor_by_bid: worst-case profit implication if the bid wins.
- regret_if_lose_with_low_bid: missed-value pressure from shading too much.
- regret_if_win_with_high_bid: profit erosion from shading too little.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [win_probability_assumption_by_bid] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## First-Sealed Auction

### Group 3

Use only these computed fields:

- `bid_rank_order`: legal bids sorted from least to most aggressive.
- `overbid_actions`: legal bids above private value.
- `zero_surplus_actions`: bids equal to private value.
- `surplus_if_win_by_bid`: payoff if each bid wins.
- `win_probability_assumption_by_bid`: explicit assumed winning chance for each candidate bid under the current belief model.
- `regret_if_win_with_high_bid`: profit erosion from shading too little.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for First-Sealed Auction.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- bid_rank_order: legal bids sorted from least to most aggressive.
- overbid_actions: legal bids above private value.
- zero_surplus_actions: bids equal to private value.
- surplus_if_win_by_bid: payoff if each bid wins.
- win_probability_assumption_by_bid: explicit assumed winning chance for each candidate bid under the current belief model.
- regret_if_win_with_high_bid: profit erosion from shading too little.

Decision program:
P0. Choose only from legal actions.
P1. Exclude actions flagged as unsafe, dominated, overaggressive, or losing by [overbid_actions].
P2. Among remaining actions, rank them using the comparative evidence in [zero_surplus_actions, surplus_if_win_by_bid, win_probability_assumption_by_bid] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## First-Sealed Auction

### Group 4

Use only these computed fields:

- `bid_shading_ratio`: `(valuation - bid) / valuation` where defined.
- `zero_surplus_actions`: bids equal to private value.
- `win_probability_assumption_by_bid`: explicit assumed winning chance for each candidate bid under the current belief model.
- `expected_surplus_by_bid`: win-probability-weighted surplus for each bid.
- `tie_case_if_bid_equals_opponent`: tie-handling assumption if the rules or implementation specify one.
- `regret_if_lose_with_low_bid`: missed-value pressure from shading too much.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for First-Sealed Auction.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- bid_shading_ratio: `(valuation - bid) / valuation` where defined.
- zero_surplus_actions: bids equal to private value.
- win_probability_assumption_by_bid: explicit assumed winning chance for each candidate bid under the current belief model.
- expected_surplus_by_bid: win-probability-weighted surplus for each bid.
- tie_case_if_bid_equals_opponent: tie-handling assumption if the rules or implementation specify one.
- regret_if_lose_with_low_bid: missed-value pressure from shading too much.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [expected_surplus_by_bid], prioritize actions supported by those fields.
P2. Among remaining actions, rank them using the comparative evidence in [zero_surplus_actions, win_probability_assumption_by_bid, expected_surplus_by_bid] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## First-Sealed Auction

### Group 5

Use only these computed fields:

- `overbid_actions`: legal bids above private value.
- `surplus_if_win_by_bid`: payoff if each bid wins.
- `profit_floor_by_bid`: worst-case profit implication if the bid wins.
- `regret_if_lose_with_low_bid`: missed-value pressure from shading too much.
- `regret_if_win_with_high_bid`: profit erosion from shading too little.
- `aggressiveness_class_by_bid`: coarse label such as `too_passive`, `moderate_shade`, `near_value`, or `overbid`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for First-Sealed Auction.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- overbid_actions: legal bids above private value.
- surplus_if_win_by_bid: payoff if each bid wins.
- profit_floor_by_bid: worst-case profit implication if the bid wins.
- regret_if_lose_with_low_bid: missed-value pressure from shading too much.
- regret_if_win_with_high_bid: profit erosion from shading too little.
- aggressiveness_class_by_bid: coarse label such as `too_passive`, `moderate_shade`, `near_value`, or `overbid`.

Decision program:
P0. Choose only from legal actions.
P1. Exclude actions flagged as unsafe, dominated, overaggressive, or losing by [overbid_actions].
P2. Among remaining actions, rank them using the comparative evidence in [surplus_if_win_by_bid, aggressiveness_class_by_bid] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## First-Sealed Auction

### Group 6

Use only these computed fields:

- `bid_rank_order`: legal bids sorted from least to most aggressive.
- `bid_shading_amount`: `valuation - bid` for each legal bid.
- `overbid_actions`: legal bids above private value.
- `win_probability_assumption_by_bid`: explicit assumed winning chance for each candidate bid under the current belief model.
- `tie_case_if_bid_equals_opponent`: tie-handling assumption if the rules or implementation specify one.
- `profit_floor_by_bid`: worst-case profit implication if the bid wins.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for First-Sealed Auction.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- bid_rank_order: legal bids sorted from least to most aggressive.
- bid_shading_amount: `valuation - bid` for each legal bid.
- overbid_actions: legal bids above private value.
- win_probability_assumption_by_bid: explicit assumed winning chance for each candidate bid under the current belief model.
- tie_case_if_bid_equals_opponent: tie-handling assumption if the rules or implementation specify one.
- profit_floor_by_bid: worst-case profit implication if the bid wins.

Decision program:
P0. Choose only from legal actions.
P1. Exclude actions flagged as unsafe, dominated, overaggressive, or losing by [overbid_actions].
P2. Among remaining actions, rank them using the comparative evidence in [win_probability_assumption_by_bid] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## First-Sealed Auction

### Group 7

Use only these computed fields:

- `bid_shading_amount`: `valuation - bid` for each legal bid.
- `overbid_actions`: legal bids above private value.
- `positive_surplus_actions`: bids below private value.
- `surplus_if_win_by_bid`: payoff if each bid wins.
- `expected_surplus_by_bid`: win-probability-weighted surplus for each bid.
- `aggressiveness_class_by_bid`: coarse label such as `too_passive`, `moderate_shade`, `near_value`, or `overbid`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for First-Sealed Auction.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- bid_shading_amount: `valuation - bid` for each legal bid.
- overbid_actions: legal bids above private value.
- positive_surplus_actions: bids below private value.
- surplus_if_win_by_bid: payoff if each bid wins.
- expected_surplus_by_bid: win-probability-weighted surplus for each bid.
- aggressiveness_class_by_bid: coarse label such as `too_passive`, `moderate_shade`, `near_value`, or `overbid`.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [positive_surplus_actions, expected_surplus_by_bid], prioritize actions supported by those fields.
P2. Exclude actions flagged as unsafe, dominated, overaggressive, or losing by [overbid_actions].
P3. Among remaining actions, rank them using the comparative evidence in [positive_surplus_actions, surplus_if_win_by_bid, expected_surplus_by_bid, aggressiveness_class_by_bid] and choose the strongest supported action.
P4. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## First-Sealed Auction

### Group 8

Use only these computed fields:

- `bid_rank_order`: legal bids sorted from least to most aggressive.
- `overbid_actions`: legal bids above private value.
- `win_probability_assumption_by_bid`: explicit assumed winning chance for each candidate bid under the current belief model.
- `regret_if_lose_with_low_bid`: missed-value pressure from shading too much.
- `regret_if_win_with_high_bid`: profit erosion from shading too little.
- `robust_bid_interval_under_belief_range`: bids that remain reasonable across a range of opponent bid beliefs.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for First-Sealed Auction.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- bid_rank_order: legal bids sorted from least to most aggressive.
- overbid_actions: legal bids above private value.
- win_probability_assumption_by_bid: explicit assumed winning chance for each candidate bid under the current belief model.
- regret_if_lose_with_low_bid: missed-value pressure from shading too much.
- regret_if_win_with_high_bid: profit erosion from shading too little.
- robust_bid_interval_under_belief_range: bids that remain reasonable across a range of opponent bid beliefs.

Decision program:
P0. Choose only from legal actions.
P1. Exclude actions flagged as unsafe, dominated, overaggressive, or losing by [overbid_actions].
P2. Among remaining actions, rank them using the comparative evidence in [win_probability_assumption_by_bid] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## First-Sealed Auction

### Group 9

Use only these computed fields:

- `zero_surplus_actions`: bids equal to private value.
- `surplus_if_win_by_bid`: payoff if each bid wins.
- `win_probability_assumption_by_bid`: explicit assumed winning chance for each candidate bid under the current belief model.
- `regret_if_win_with_high_bid`: profit erosion from shading too little.
- `robust_bid_interval_under_belief_range`: bids that remain reasonable across a range of opponent bid beliefs.
- `aggressiveness_class_by_bid`: coarse label such as `too_passive`, `moderate_shade`, `near_value`, or `overbid`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for First-Sealed Auction.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- zero_surplus_actions: bids equal to private value.
- surplus_if_win_by_bid: payoff if each bid wins.
- win_probability_assumption_by_bid: explicit assumed winning chance for each candidate bid under the current belief model.
- regret_if_win_with_high_bid: profit erosion from shading too little.
- robust_bid_interval_under_belief_range: bids that remain reasonable across a range of opponent bid beliefs.
- aggressiveness_class_by_bid: coarse label such as `too_passive`, `moderate_shade`, `near_value`, or `overbid`.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [zero_surplus_actions, surplus_if_win_by_bid, win_probability_assumption_by_bid, aggressiveness_class_by_bid] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## First-Sealed Auction

### Group 10

Use only these computed fields:

- `bid_rank_order`: legal bids sorted from least to most aggressive.
- `zero_surplus_actions`: bids equal to private value.
- `positive_surplus_actions`: bids below private value.
- `profit_floor_by_bid`: worst-case profit implication if the bid wins.
- `regret_if_lose_with_low_bid`: missed-value pressure from shading too much.
- `regret_if_win_with_high_bid`: profit erosion from shading too little.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for First-Sealed Auction.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- bid_rank_order: legal bids sorted from least to most aggressive.
- zero_surplus_actions: bids equal to private value.
- positive_surplus_actions: bids below private value.
- profit_floor_by_bid: worst-case profit implication if the bid wins.
- regret_if_lose_with_low_bid: missed-value pressure from shading too much.
- regret_if_win_with_high_bid: profit erosion from shading too little.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [positive_surplus_actions], prioritize actions supported by those fields.
P2. Among remaining actions, rank them using the comparative evidence in [zero_surplus_actions, positive_surplus_actions] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Kuhn Poker

### Group 1

Use only these computed fields:

- `hand_strength_class`: weak, medium, or strong relative to the deck.
- `legal_action_context`: semantic mapping of available actions in this node.
- `possible_opponent_cards`: opponent cards consistent with my private card.
- `call_value_by_opponent_card`: card-conditioned payoff if I call.
- `expected_value_by_action`: belief-weighted expected value for each legal action.
- `action_risk_profile`: coarse class such as `thin_value`, `clear_bluff`, `safe_check`, `defensive_fold`, or `high_variance_call`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Kuhn Poker.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- hand_strength_class: weak, medium, or strong relative to the deck.
- legal_action_context: semantic mapping of available actions in this node.
- possible_opponent_cards: opponent cards consistent with my private card.
- call_value_by_opponent_card: card-conditioned payoff if I call.
- expected_value_by_action: belief-weighted expected value for each legal action.
- action_risk_profile: coarse class such as `thin_value`, `clear_bluff`, `safe_check`, `defensive_fold`, or `high_variance_call`.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [hand_strength_class, call_value_by_opponent_card, expected_value_by_action, action_risk_profile] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Kuhn Poker

### Group 2

Use only these computed fields:

- `information_set_class`: coarse label for the current node such as `opening_action`, `facing_bet`, or `post-check response`.
- `hand_strength_class`: weak, medium, or strong relative to the deck.
- `fold_value`: guaranteed value of folding when that action is legal.
- `bet_fold_equity`: value gained when a bet induces folds.
- `expected_value_by_action`: belief-weighted expected value for each legal action.
- `opponent_response_if_i_bet`: likely reply classes after each betting action.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Kuhn Poker.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- information_set_class: coarse label for the current node such as `opening_action`, `facing_bet`, or `post-check response`.
- hand_strength_class: weak, medium, or strong relative to the deck.
- fold_value: guaranteed value of folding when that action is legal.
- bet_fold_equity: value gained when a bet induces folds.
- expected_value_by_action: belief-weighted expected value for each legal action.
- opponent_response_if_i_bet: likely reply classes after each betting action.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [information_set_class, hand_strength_class, fold_value, expected_value_by_action] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Kuhn Poker

### Group 3

Use only these computed fields:

- `information_set_class`: coarse label for the current node such as `opening_action`, `facing_bet`, or `post-check response`.
- `possible_opponent_cards`: opponent cards consistent with my private card.
- `posterior_over_opponent_cards`: belief over those cards from public history.
- `showdown_result_by_opponent_card`: win/loss outcome if the hand reaches showdown against each possible opponent card.
- `call_value_by_opponent_card`: card-conditioned payoff if I call.
- `bluff_incentive`: whether weak-card betting can profit from fold equity.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Kuhn Poker.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- information_set_class: coarse label for the current node such as `opening_action`, `facing_bet`, or `post-check response`.
- possible_opponent_cards: opponent cards consistent with my private card.
- posterior_over_opponent_cards: belief over those cards from public history.
- showdown_result_by_opponent_card: win/loss outcome if the hand reaches showdown against each possible opponent card.
- call_value_by_opponent_card: card-conditioned payoff if I call.
- bluff_incentive: whether weak-card betting can profit from fold equity.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [information_set_class, call_value_by_opponent_card] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Kuhn Poker

### Group 4

Use only these computed fields:

- `information_set_class`: coarse label for the current node such as `opening_action`, `facing_bet`, or `post-check response`.
- `pot_size`: current pot before acting.
- `facing_bet`: whether my current choice responds to an opponent bet.
- `call_value_by_opponent_card`: card-conditioned payoff if I call.
- `bluff_incentive`: whether weak-card betting can profit from fold equity.
- `value_bet_incentive`: whether strong-card betting extracts value from worse hands or calls.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Kuhn Poker.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- information_set_class: coarse label for the current node such as `opening_action`, `facing_bet`, or `post-check response`.
- pot_size: current pot before acting.
- facing_bet: whether my current choice responds to an opponent bet.
- call_value_by_opponent_card: card-conditioned payoff if I call.
- bluff_incentive: whether weak-card betting can profit from fold equity.
- value_bet_incentive: whether strong-card betting extracts value from worse hands or calls.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [information_set_class, call_value_by_opponent_card, value_bet_incentive] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Kuhn Poker

### Group 5

Use only these computed fields:

- `legal_action_context`: semantic mapping of available actions in this node.
- `showdown_result_by_opponent_card`: win/loss outcome if the hand reaches showdown against each possible opponent card.
- `call_value_by_opponent_card`: card-conditioned payoff if I call.
- `bluff_incentive`: whether weak-card betting can profit from fold equity.
- `expected_value_by_action`: belief-weighted expected value for each legal action.
- `opponent_response_if_i_bet`: likely reply classes after each betting action.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Kuhn Poker.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- legal_action_context: semantic mapping of available actions in this node.
- showdown_result_by_opponent_card: win/loss outcome if the hand reaches showdown against each possible opponent card.
- call_value_by_opponent_card: card-conditioned payoff if I call.
- bluff_incentive: whether weak-card betting can profit from fold equity.
- expected_value_by_action: belief-weighted expected value for each legal action.
- opponent_response_if_i_bet: likely reply classes after each betting action.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [call_value_by_opponent_card, expected_value_by_action] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Kuhn Poker

### Group 6

Use only these computed fields:

- `information_set_class`: coarse label for the current node such as `opening_action`, `facing_bet`, or `post-check response`.
- `pot_size`: current pot before acting.
- `facing_bet`: whether my current choice responds to an opponent bet.
- `possible_opponent_cards`: opponent cards consistent with my private card.
- `bet_fold_equity`: value gained when a bet induces folds.
- `action_risk_profile`: coarse class such as `thin_value`, `clear_bluff`, `safe_check`, `defensive_fold`, or `high_variance_call`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Kuhn Poker.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- information_set_class: coarse label for the current node such as `opening_action`, `facing_bet`, or `post-check response`.
- pot_size: current pot before acting.
- facing_bet: whether my current choice responds to an opponent bet.
- possible_opponent_cards: opponent cards consistent with my private card.
- bet_fold_equity: value gained when a bet induces folds.
- action_risk_profile: coarse class such as `thin_value`, `clear_bluff`, `safe_check`, `defensive_fold`, or `high_variance_call`.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [information_set_class, action_risk_profile] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Kuhn Poker

### Group 7

Use only these computed fields:

- `pot_size`: current pot before acting.
- `possible_opponent_cards`: opponent cards consistent with my private card.
- `call_value_by_opponent_card`: card-conditioned payoff if I call.
- `bluff_incentive`: whether weak-card betting can profit from fold equity.
- `value_bet_incentive`: whether strong-card betting extracts value from worse hands or calls.
- `action_risk_profile`: coarse class such as `thin_value`, `clear_bluff`, `safe_check`, `defensive_fold`, or `high_variance_call`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Kuhn Poker.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- pot_size: current pot before acting.
- possible_opponent_cards: opponent cards consistent with my private card.
- call_value_by_opponent_card: card-conditioned payoff if I call.
- bluff_incentive: whether weak-card betting can profit from fold equity.
- value_bet_incentive: whether strong-card betting extracts value from worse hands or calls.
- action_risk_profile: coarse class such as `thin_value`, `clear_bluff`, `safe_check`, `defensive_fold`, or `high_variance_call`.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [call_value_by_opponent_card, value_bet_incentive, action_risk_profile] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Kuhn Poker

### Group 8

Use only these computed fields:

- `legal_action_context`: semantic mapping of available actions in this node.
- `bluff_incentive`: whether weak-card betting can profit from fold equity.
- `value_bet_incentive`: whether strong-card betting extracts value from worse hands or calls.
- `expected_value_by_action`: belief-weighted expected value for each legal action.
- `opponent_response_if_i_bet`: likely reply classes after each betting action.
- `action_risk_profile`: coarse class such as `thin_value`, `clear_bluff`, `safe_check`, `defensive_fold`, or `high_variance_call`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Kuhn Poker.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- legal_action_context: semantic mapping of available actions in this node.
- bluff_incentive: whether weak-card betting can profit from fold equity.
- value_bet_incentive: whether strong-card betting extracts value from worse hands or calls.
- expected_value_by_action: belief-weighted expected value for each legal action.
- opponent_response_if_i_bet: likely reply classes after each betting action.
- action_risk_profile: coarse class such as `thin_value`, `clear_bluff`, `safe_check`, `defensive_fold`, or `high_variance_call`.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [value_bet_incentive, expected_value_by_action, action_risk_profile] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Kuhn Poker

### Group 9

Use only these computed fields:

- `legal_action_context`: semantic mapping of available actions in this node.
- `possible_opponent_cards`: opponent cards consistent with my private card.
- `posterior_over_opponent_cards`: belief over those cards from public history.
- `showdown_result_by_opponent_card`: win/loss outcome if the hand reaches showdown against each possible opponent card.
- `bluff_incentive`: whether weak-card betting can profit from fold equity.
- `value_bet_incentive`: whether strong-card betting extracts value from worse hands or calls.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Kuhn Poker.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- legal_action_context: semantic mapping of available actions in this node.
- possible_opponent_cards: opponent cards consistent with my private card.
- posterior_over_opponent_cards: belief over those cards from public history.
- showdown_result_by_opponent_card: win/loss outcome if the hand reaches showdown against each possible opponent card.
- bluff_incentive: whether weak-card betting can profit from fold equity.
- value_bet_incentive: whether strong-card betting extracts value from worse hands or calls.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [value_bet_incentive] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Kuhn Poker

### Group 10

Use only these computed fields:

- `hand_strength_class`: weak, medium, or strong relative to the deck.
- `facing_bet`: whether my current choice responds to an opponent bet.
- `posterior_over_opponent_cards`: belief over those cards from public history.
- `showdown_result_by_opponent_card`: win/loss outcome if the hand reaches showdown against each possible opponent card.
- `fold_value`: guaranteed value of folding when that action is legal.
- `action_risk_profile`: coarse class such as `thin_value`, `clear_bluff`, `safe_check`, `defensive_fold`, or `high_variance_call`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Kuhn Poker.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- hand_strength_class: weak, medium, or strong relative to the deck.
- facing_bet: whether my current choice responds to an opponent bet.
- posterior_over_opponent_cards: belief over those cards from public history.
- showdown_result_by_opponent_card: win/loss outcome if the hand reaches showdown against each possible opponent card.
- fold_value: guaranteed value of folding when that action is legal.
- action_risk_profile: coarse class such as `thin_value`, `clear_bluff`, `safe_check`, `defensive_fold`, or `high_variance_call`.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [hand_strength_class, fold_value, action_risk_profile] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Liar's Dice

### Group 1

Use only these computed fields:

- `my_face_count`: how many of the bid face I personally hold.
- `probability_each_raise_true`: truth probability estimate for each legal raise.
- `challenge_threshold_gap`: amount by which the current bid exceeds a chosen plausibility threshold.
- `aggressive_raise_candidates`: legally available raises that rely on stronger bluff assumptions.
- `opponent_bluff_likelihood_from_history`: history-based belief about whether the opponent tends to overstate bids.
- `consistency_with_private_evidence`: whether a candidate action is aligned with, stretches, or contradicts my own dice evidence.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Liar's Dice.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- my_face_count: how many of the bid face I personally hold.
- probability_each_raise_true: truth probability estimate for each legal raise.
- challenge_threshold_gap: amount by which the current bid exceeds a chosen plausibility threshold.
- aggressive_raise_candidates: legally available raises that rely on stronger bluff assumptions.
- opponent_bluff_likelihood_from_history: history-based belief about whether the opponent tends to overstate bids.
- consistency_with_private_evidence: whether a candidate action is aligned with, stretches, or contradicts my own dice evidence.

Decision program:
P0. Choose only from legal actions.
P1. If opponent threat or forced defense is exposed by [challenge_threshold_gap], keep only legal actions that answer that threat.
P2. Exclude actions flagged as unsafe, dominated, overaggressive, or losing by [aggressive_raise_candidates].
P3. Among remaining actions, rank them using the comparative evidence in [my_face_count, probability_each_raise_true] and choose the strongest supported action.
P4. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Liar's Dice

### Group 2

Use only these computed fields:

- `my_bid_support_count`: how many of the current bid are directly supported by my private dice.
- `slack_above_current_bid`: how far the current bid is above my private evidence before relying on unknown dice.
- `bluff_pressure_index`: how strongly the current state pressures someone to bluff rather than continue honestly.
- `aggressive_raise_candidates`: legally available raises that rely on stronger bluff assumptions.
- `opponent_bluff_likelihood_from_history`: history-based belief about whether the opponent tends to overstate bids.
- `consistency_with_private_evidence`: whether a candidate action is aligned with, stretches, or contradicts my own dice evidence.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Liar's Dice.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- my_bid_support_count: how many of the current bid are directly supported by my private dice.
- slack_above_current_bid: how far the current bid is above my private evidence before relying on unknown dice.
- bluff_pressure_index: how strongly the current state pressures someone to bluff rather than continue honestly.
- aggressive_raise_candidates: legally available raises that rely on stronger bluff assumptions.
- opponent_bluff_likelihood_from_history: history-based belief about whether the opponent tends to overstate bids.
- consistency_with_private_evidence: whether a candidate action is aligned with, stretches, or contradicts my own dice evidence.

Decision program:
P0. Choose only from legal actions.
P1. Exclude actions flagged as unsafe, dominated, overaggressive, or losing by [aggressive_raise_candidates].
P2. Among remaining actions, rank them using the comparative evidence in [my_bid_support_count, bluff_pressure_index] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Liar's Dice

### Group 3

Use only these computed fields:

- `legal_raise_space`: all legal raises from the current state.
- `my_face_count`: how many of the bid face I personally hold.
- `probability_each_raise_true`: truth probability estimate for each legal raise.
- `bluff_pressure_index`: how strongly the current state pressures someone to bluff rather than continue honestly.
- `conservative_raise_candidates`: raises with relatively high truth support.
- `liar_vs_raise_ev_proxy`: compact comparison between challenging now and continuing the bidding sequence.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Liar's Dice.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- legal_raise_space: all legal raises from the current state.
- my_face_count: how many of the bid face I personally hold.
- probability_each_raise_true: truth probability estimate for each legal raise.
- bluff_pressure_index: how strongly the current state pressures someone to bluff rather than continue honestly.
- conservative_raise_candidates: raises with relatively high truth support.
- liar_vs_raise_ev_proxy: compact comparison between challenging now and continuing the bidding sequence.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [conservative_raise_candidates], prioritize actions supported by those fields.
P2. Among remaining actions, rank them using the comparative evidence in [my_face_count, probability_each_raise_true, bluff_pressure_index] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Liar's Dice

### Group 4

Use only these computed fields:

- `minimum_next_bid_rule`: exact legality rule for the next non-challenge raise.
- `legal_raise_space`: all legal raises from the current state.
- `my_face_count`: how many of the bid face I personally hold.
- `my_bid_support_count`: how many of the current bid are directly supported by my private dice.
- `challenge_threshold_gap`: amount by which the current bid exceeds a chosen plausibility threshold.
- `conservative_raise_candidates`: raises with relatively high truth support.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Liar's Dice.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- minimum_next_bid_rule: exact legality rule for the next non-challenge raise.
- legal_raise_space: all legal raises from the current state.
- my_face_count: how many of the bid face I personally hold.
- my_bid_support_count: how many of the current bid are directly supported by my private dice.
- challenge_threshold_gap: amount by which the current bid exceeds a chosen plausibility threshold.
- conservative_raise_candidates: raises with relatively high truth support.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [conservative_raise_candidates], prioritize actions supported by those fields.
P2. If opponent threat or forced defense is exposed by [challenge_threshold_gap], keep only legal actions that answer that threat.
P3. Among remaining actions, rank them using the comparative evidence in [my_face_count, my_bid_support_count] and choose the strongest supported action.
P4. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Liar's Dice

### Group 5

Use only these computed fields:

- `minimum_next_bid_rule`: exact legality rule for the next non-challenge raise.
- `my_bid_support_count`: how many of the current bid are directly supported by my private dice.
- `probability_current_bid_true`: belief that the current bid is true given my dice and public history.
- `probability_each_raise_true`: truth probability estimate for each legal raise.
- `challenge_threshold_gap`: amount by which the current bid exceeds a chosen plausibility threshold.
- `liar_vs_raise_ev_proxy`: compact comparison between challenging now and continuing the bidding sequence.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Liar's Dice.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- minimum_next_bid_rule: exact legality rule for the next non-challenge raise.
- my_bid_support_count: how many of the current bid are directly supported by my private dice.
- probability_current_bid_true: belief that the current bid is true given my dice and public history.
- probability_each_raise_true: truth probability estimate for each legal raise.
- challenge_threshold_gap: amount by which the current bid exceeds a chosen plausibility threshold.
- liar_vs_raise_ev_proxy: compact comparison between challenging now and continuing the bidding sequence.

Decision program:
P0. Choose only from legal actions.
P1. If opponent threat or forced defense is exposed by [challenge_threshold_gap], keep only legal actions that answer that threat.
P2. Among remaining actions, rank them using the comparative evidence in [my_bid_support_count, probability_current_bid_true, probability_each_raise_true] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Liar's Dice

### Group 6

Use only these computed fields:

- `minimum_next_bid_rule`: exact legality rule for the next non-challenge raise.
- `my_bid_support_count`: how many of the current bid are directly supported by my private dice.
- `probability_current_bid_true`: belief that the current bid is true given my dice and public history.
- `bluff_pressure_index`: how strongly the current state pressures someone to bluff rather than continue honestly.
- `conservative_raise_candidates`: raises with relatively high truth support.
- `consistency_with_private_evidence`: whether a candidate action is aligned with, stretches, or contradicts my own dice evidence.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Liar's Dice.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- minimum_next_bid_rule: exact legality rule for the next non-challenge raise.
- my_bid_support_count: how many of the current bid are directly supported by my private dice.
- probability_current_bid_true: belief that the current bid is true given my dice and public history.
- bluff_pressure_index: how strongly the current state pressures someone to bluff rather than continue honestly.
- conservative_raise_candidates: raises with relatively high truth support.
- consistency_with_private_evidence: whether a candidate action is aligned with, stretches, or contradicts my own dice evidence.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [conservative_raise_candidates], prioritize actions supported by those fields.
P2. Among remaining actions, rank them using the comparative evidence in [my_bid_support_count, probability_current_bid_true, bluff_pressure_index] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Liar's Dice

### Group 7

Use only these computed fields:

- `minimum_next_bid_rule`: exact legality rule for the next non-challenge raise.
- `legal_raise_space`: all legal raises from the current state.
- `unknown_dice_count`: number of dice whose faces I do not observe.
- `bluff_pressure_index`: how strongly the current state pressures someone to bluff rather than continue honestly.
- `conservative_raise_candidates`: raises with relatively high truth support.
- `liar_vs_raise_ev_proxy`: compact comparison between challenging now and continuing the bidding sequence.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Liar's Dice.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- minimum_next_bid_rule: exact legality rule for the next non-challenge raise.
- legal_raise_space: all legal raises from the current state.
- unknown_dice_count: number of dice whose faces I do not observe.
- bluff_pressure_index: how strongly the current state pressures someone to bluff rather than continue honestly.
- conservative_raise_candidates: raises with relatively high truth support.
- liar_vs_raise_ev_proxy: compact comparison between challenging now and continuing the bidding sequence.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [conservative_raise_candidates], prioritize actions supported by those fields.
P2. Among remaining actions, rank them using the comparative evidence in [unknown_dice_count, bluff_pressure_index] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Liar's Dice

### Group 8

Use only these computed fields:

- `minimum_next_bid_rule`: exact legality rule for the next non-challenge raise.
- `my_face_count`: how many of the bid face I personally hold.
- `my_bid_support_count`: how many of the current bid are directly supported by my private dice.
- `probability_each_raise_true`: truth probability estimate for each legal raise.
- `bluff_pressure_index`: how strongly the current state pressures someone to bluff rather than continue honestly.
- `consistency_with_private_evidence`: whether a candidate action is aligned with, stretches, or contradicts my own dice evidence.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Liar's Dice.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- minimum_next_bid_rule: exact legality rule for the next non-challenge raise.
- my_face_count: how many of the bid face I personally hold.
- my_bid_support_count: how many of the current bid are directly supported by my private dice.
- probability_each_raise_true: truth probability estimate for each legal raise.
- bluff_pressure_index: how strongly the current state pressures someone to bluff rather than continue honestly.
- consistency_with_private_evidence: whether a candidate action is aligned with, stretches, or contradicts my own dice evidence.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [my_face_count, my_bid_support_count, probability_each_raise_true, bluff_pressure_index] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Liar's Dice

### Group 9

Use only these computed fields:

- `legal_raise_space`: all legal raises from the current state.
- `slack_above_current_bid`: how far the current bid is above my private evidence before relying on unknown dice.
- `challenge_threshold_gap`: amount by which the current bid exceeds a chosen plausibility threshold.
- `conservative_raise_candidates`: raises with relatively high truth support.
- `liar_vs_raise_ev_proxy`: compact comparison between challenging now and continuing the bidding sequence.
- `consistency_with_private_evidence`: whether a candidate action is aligned with, stretches, or contradicts my own dice evidence.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Liar's Dice.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- legal_raise_space: all legal raises from the current state.
- slack_above_current_bid: how far the current bid is above my private evidence before relying on unknown dice.
- challenge_threshold_gap: amount by which the current bid exceeds a chosen plausibility threshold.
- conservative_raise_candidates: raises with relatively high truth support.
- liar_vs_raise_ev_proxy: compact comparison between challenging now and continuing the bidding sequence.
- consistency_with_private_evidence: whether a candidate action is aligned with, stretches, or contradicts my own dice evidence.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [conservative_raise_candidates], prioritize actions supported by those fields.
P2. If opponent threat or forced defense is exposed by [challenge_threshold_gap], keep only legal actions that answer that threat.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Liar's Dice

### Group 10

Use only these computed fields:

- `minimum_next_bid_rule`: exact legality rule for the next non-challenge raise.
- `my_face_count`: how many of the bid face I personally hold.
- `probability_current_bid_true`: belief that the current bid is true given my dice and public history.
- `probability_each_raise_true`: truth probability estimate for each legal raise.
- `bluff_pressure_index`: how strongly the current state pressures someone to bluff rather than continue honestly.
- `conservative_raise_candidates`: raises with relatively high truth support.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Liar's Dice.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- minimum_next_bid_rule: exact legality rule for the next non-challenge raise.
- my_face_count: how many of the bid face I personally hold.
- probability_current_bid_true: belief that the current bid is true given my dice and public history.
- probability_each_raise_true: truth probability estimate for each legal raise.
- bluff_pressure_index: how strongly the current state pressures someone to bluff rather than continue honestly.
- conservative_raise_candidates: raises with relatively high truth support.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [conservative_raise_candidates], prioritize actions supported by those fields.
P2. Among remaining actions, rank them using the comparative evidence in [my_face_count, probability_current_bid_true, probability_each_raise_true, bluff_pressure_index] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Negotiation

### Group 1

Use only these computed fields:

- `self_payoff_of_latest_offer`: my utility if I accept the current offer.
- `bundle_substitutability_from_self_view`: which items are near-substitutes or complements from my utility perspective.
- `opponent_demand_pattern_from_history`: revealed preference clues from past offers and utterances.
- `utterance_offer_consistency`: whether a message and a concrete proposal tell the same strategic story.
- `pareto_candidate_status_from_self_side`: whether a proposal looks efficient from my utility side without assuming exact opponent values.
- `agree_vs_counteroffer_margin`: compact comparison between accepting now and holding out for a better but less certain outcome.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Negotiation.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- self_payoff_of_latest_offer: my utility if I accept the current offer.
- bundle_substitutability_from_self_view: which items are near-substitutes or complements from my utility perspective.
- opponent_demand_pattern_from_history: revealed preference clues from past offers and utterances.
- utterance_offer_consistency: whether a message and a concrete proposal tell the same strategic story.
- pareto_candidate_status_from_self_side: whether a proposal looks efficient from my utility side without assuming exact opponent values.
- agree_vs_counteroffer_margin: compact comparison between accepting now and holding out for a better but less certain outcome.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [self_payoff_of_latest_offer, agree_vs_counteroffer_margin] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Negotiation

### Group 2

Use only these computed fields:

- `disagreement_payoff`: utility of ending without agreement if that is defined, otherwise the default zero-like baseline.
- `minimum_acceptable_payoff`: threshold below which agreement is not worth taking given current information.
- `max_self_payoff_feasible_offer`: best self-side feasible offer in the legal proposal space.
- `offer_feasibility_check`: whether a candidate allocation respects item-pool constraints.
- `acceptance_probability_proxy_by_offer`: belief-based estimate that the opponent may accept a candidate offer.
- `strategic_stage_goal`: coarse goal such as `close_now`, `probe_preferences`, `signal toughness`, or `trade for agreement`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Negotiation.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- disagreement_payoff: utility of ending without agreement if that is defined, otherwise the default zero-like baseline.
- minimum_acceptable_payoff: threshold below which agreement is not worth taking given current information.
- max_self_payoff_feasible_offer: best self-side feasible offer in the legal proposal space.
- offer_feasibility_check: whether a candidate allocation respects item-pool constraints.
- acceptance_probability_proxy_by_offer: belief-based estimate that the opponent may accept a candidate offer.
- strategic_stage_goal: coarse goal such as `close_now`, `probe_preferences`, `signal toughness`, or `trade for agreement`.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [disagreement_payoff, minimum_acceptable_payoff, max_self_payoff_feasible_offer, acceptance_probability_proxy_by_offer] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Negotiation

### Group 3

Use only these computed fields:

- `disagreement_payoff`: utility of ending without agreement if that is defined, otherwise the default zero-like baseline.
- `max_self_payoff_feasible_offer`: best self-side feasible offer in the legal proposal space.
- `concession_cost_by_candidate_offer`: how much self utility each candidate concession gives up.
- `bundle_substitutability_from_self_view`: which items are near-substitutes or complements from my utility perspective.
- `acceptance_probability_proxy_by_offer`: belief-based estimate that the opponent may accept a candidate offer.
- `opponent_demand_pattern_from_history`: revealed preference clues from past offers and utterances.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Negotiation.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- disagreement_payoff: utility of ending without agreement if that is defined, otherwise the default zero-like baseline.
- max_self_payoff_feasible_offer: best self-side feasible offer in the legal proposal space.
- concession_cost_by_candidate_offer: how much self utility each candidate concession gives up.
- bundle_substitutability_from_self_view: which items are near-substitutes or complements from my utility perspective.
- acceptance_probability_proxy_by_offer: belief-based estimate that the opponent may accept a candidate offer.
- opponent_demand_pattern_from_history: revealed preference clues from past offers and utterances.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [disagreement_payoff, max_self_payoff_feasible_offer, acceptance_probability_proxy_by_offer] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Negotiation

### Group 4

Use only these computed fields:

- `self_payoff_of_latest_offer`: my utility if I accept the current offer.
- `minimum_acceptable_payoff`: threshold below which agreement is not worth taking given current information.
- `offer_feasibility_check`: whether a candidate allocation respects item-pool constraints.
- `opponent_demand_pattern_from_history`: revealed preference clues from past offers and utterances.
- `pareto_candidate_status_from_self_side`: whether a proposal looks efficient from my utility side without assuming exact opponent values.
- `agree_vs_counteroffer_margin`: compact comparison between accepting now and holding out for a better but less certain outcome.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Negotiation.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- self_payoff_of_latest_offer: my utility if I accept the current offer.
- minimum_acceptable_payoff: threshold below which agreement is not worth taking given current information.
- offer_feasibility_check: whether a candidate allocation respects item-pool constraints.
- opponent_demand_pattern_from_history: revealed preference clues from past offers and utterances.
- pareto_candidate_status_from_self_side: whether a proposal looks efficient from my utility side without assuming exact opponent values.
- agree_vs_counteroffer_margin: compact comparison between accepting now and holding out for a better but less certain outcome.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [self_payoff_of_latest_offer, minimum_acceptable_payoff, agree_vs_counteroffer_margin] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Negotiation

### Group 5

Use only these computed fields:

- `self_payoff_of_latest_offer`: my utility if I accept the current offer.
- `disagreement_payoff`: utility of ending without agreement if that is defined, otherwise the default zero-like baseline.
- `max_self_payoff_feasible_offer`: best self-side feasible offer in the legal proposal space.
- `high_value_item_priority`: ranking of items by my private value density.
- `opponent_demand_pattern_from_history`: revealed preference clues from past offers and utterances.
- `utterance_offer_consistency`: whether a message and a concrete proposal tell the same strategic story.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Negotiation.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- self_payoff_of_latest_offer: my utility if I accept the current offer.
- disagreement_payoff: utility of ending without agreement if that is defined, otherwise the default zero-like baseline.
- max_self_payoff_feasible_offer: best self-side feasible offer in the legal proposal space.
- high_value_item_priority: ranking of items by my private value density.
- opponent_demand_pattern_from_history: revealed preference clues from past offers and utterances.
- utterance_offer_consistency: whether a message and a concrete proposal tell the same strategic story.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [self_payoff_of_latest_offer, disagreement_payoff, max_self_payoff_feasible_offer, high_value_item_priority] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Negotiation

### Group 6

Use only these computed fields:

- `self_payoff_of_latest_offer`: my utility if I accept the current offer.
- `max_self_payoff_feasible_offer`: best self-side feasible offer in the legal proposal space.
- `concession_cost_by_candidate_offer`: how much self utility each candidate concession gives up.
- `acceptance_probability_proxy_by_offer`: belief-based estimate that the opponent may accept a candidate offer.
- `pareto_candidate_status_from_self_side`: whether a proposal looks efficient from my utility side without assuming exact opponent values.
- `agree_vs_counteroffer_margin`: compact comparison between accepting now and holding out for a better but less certain outcome.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Negotiation.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- self_payoff_of_latest_offer: my utility if I accept the current offer.
- max_self_payoff_feasible_offer: best self-side feasible offer in the legal proposal space.
- concession_cost_by_candidate_offer: how much self utility each candidate concession gives up.
- acceptance_probability_proxy_by_offer: belief-based estimate that the opponent may accept a candidate offer.
- pareto_candidate_status_from_self_side: whether a proposal looks efficient from my utility side without assuming exact opponent values.
- agree_vs_counteroffer_margin: compact comparison between accepting now and holding out for a better but less certain outcome.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [self_payoff_of_latest_offer, max_self_payoff_feasible_offer, acceptance_probability_proxy_by_offer, agree_vs_counteroffer_margin] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Negotiation

### Group 7

Use only these computed fields:

- `self_payoff_of_latest_offer`: my utility if I accept the current offer.
- `disagreement_payoff`: utility of ending without agreement if that is defined, otherwise the default zero-like baseline.
- `max_self_payoff_feasible_offer`: best self-side feasible offer in the legal proposal space.
- `high_value_item_priority`: ranking of items by my private value density.
- `offer_feasibility_check`: whether a candidate allocation respects item-pool constraints.
- `agree_vs_counteroffer_margin`: compact comparison between accepting now and holding out for a better but less certain outcome.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Negotiation.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- self_payoff_of_latest_offer: my utility if I accept the current offer.
- disagreement_payoff: utility of ending without agreement if that is defined, otherwise the default zero-like baseline.
- max_self_payoff_feasible_offer: best self-side feasible offer in the legal proposal space.
- high_value_item_priority: ranking of items by my private value density.
- offer_feasibility_check: whether a candidate allocation respects item-pool constraints.
- agree_vs_counteroffer_margin: compact comparison between accepting now and holding out for a better but less certain outcome.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [self_payoff_of_latest_offer, disagreement_payoff, max_self_payoff_feasible_offer, high_value_item_priority, agree_vs_counteroffer_margin] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Negotiation

### Group 8

Use only these computed fields:

- `max_self_payoff_feasible_offer`: best self-side feasible offer in the legal proposal space.
- `high_value_item_priority`: ranking of items by my private value density.
- `bundle_substitutability_from_self_view`: which items are near-substitutes or complements from my utility perspective.
- `offer_feasibility_check`: whether a candidate allocation respects item-pool constraints.
- `acceptance_probability_proxy_by_offer`: belief-based estimate that the opponent may accept a candidate offer.
- `strategic_stage_goal`: coarse goal such as `close_now`, `probe_preferences`, `signal toughness`, or `trade for agreement`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Negotiation.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- max_self_payoff_feasible_offer: best self-side feasible offer in the legal proposal space.
- high_value_item_priority: ranking of items by my private value density.
- bundle_substitutability_from_self_view: which items are near-substitutes or complements from my utility perspective.
- offer_feasibility_check: whether a candidate allocation respects item-pool constraints.
- acceptance_probability_proxy_by_offer: belief-based estimate that the opponent may accept a candidate offer.
- strategic_stage_goal: coarse goal such as `close_now`, `probe_preferences`, `signal toughness`, or `trade for agreement`.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [max_self_payoff_feasible_offer, high_value_item_priority, acceptance_probability_proxy_by_offer] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Negotiation

### Group 9

Use only these computed fields:

- `self_payoff_of_latest_offer`: my utility if I accept the current offer.
- `disagreement_payoff`: utility of ending without agreement if that is defined, otherwise the default zero-like baseline.
- `max_self_payoff_feasible_offer`: best self-side feasible offer in the legal proposal space.
- `high_value_item_priority`: ranking of items by my private value density.
- `acceptance_probability_proxy_by_offer`: belief-based estimate that the opponent may accept a candidate offer.
- `strategic_stage_goal`: coarse goal such as `close_now`, `probe_preferences`, `signal toughness`, or `trade for agreement`.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Negotiation.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- self_payoff_of_latest_offer: my utility if I accept the current offer.
- disagreement_payoff: utility of ending without agreement if that is defined, otherwise the default zero-like baseline.
- max_self_payoff_feasible_offer: best self-side feasible offer in the legal proposal space.
- high_value_item_priority: ranking of items by my private value density.
- acceptance_probability_proxy_by_offer: belief-based estimate that the opponent may accept a candidate offer.
- strategic_stage_goal: coarse goal such as `close_now`, `probe_preferences`, `signal toughness`, or `trade for agreement`.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [self_payoff_of_latest_offer, disagreement_payoff, max_self_payoff_feasible_offer, high_value_item_priority, acceptance_probability_proxy_by_offer] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Negotiation

### Group 10

Use only these computed fields:

- `disagreement_payoff`: utility of ending without agreement if that is defined, otherwise the default zero-like baseline.
- `concession_cost_by_candidate_offer`: how much self utility each candidate concession gives up.
- `opponent_demand_pattern_from_history`: revealed preference clues from past offers and utterances.
- `utterance_offer_consistency`: whether a message and a concrete proposal tell the same strategic story.
- `strategic_stage_goal`: coarse goal such as `close_now`, `probe_preferences`, `signal toughness`, or `trade for agreement`.
- `agree_vs_counteroffer_margin`: compact comparison between accepting now and holding out for a better but less certain outcome.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Negotiation.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- disagreement_payoff: utility of ending without agreement if that is defined, otherwise the default zero-like baseline.
- concession_cost_by_candidate_offer: how much self utility each candidate concession gives up.
- opponent_demand_pattern_from_history: revealed preference clues from past offers and utterances.
- utterance_offer_consistency: whether a message and a concrete proposal tell the same strategic story.
- strategic_stage_goal: coarse goal such as `close_now`, `probe_preferences`, `signal toughness`, or `trade for agreement`.
- agree_vs_counteroffer_margin: compact comparison between accepting now and holding out for a better but less certain outcome.

Decision program:
P0. Choose only from legal actions.
P1. Among remaining actions, rank them using the comparative evidence in [disagreement_payoff, agree_vs_counteroffer_margin] and choose the strongest supported action.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Iterated Prisoner's Dilemma

### Group 1

Use only these computed fields:

- `opponent_recent_actions`: short recent suffix of opponent behavior.
- `opponent_defection_rate`: fraction of opponent defection moves.
- `reciprocity_pattern_flag`: whether the opponent appears to mirror my last action or respond conditionally.
- `trigger_strategy_state`: coarse repeated-game state such as `cooperate`, `punish`, `test_repair`, or `exploit-resistant`.
- `stage_game_payoff_table`: the one-shot payoff ordering relevant this round.
- `punishment_credibility`: whether current history makes retaliation threats believable.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Iterated Prisoner's Dilemma.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- opponent_recent_actions: short recent suffix of opponent behavior.
- opponent_defection_rate: fraction of opponent defection moves.
- reciprocity_pattern_flag: whether the opponent appears to mirror my last action or respond conditionally.
- trigger_strategy_state: coarse repeated-game state such as `cooperate`, `punish`, `test_repair`, or `exploit-resistant`.
- stage_game_payoff_table: the one-shot payoff ordering relevant this round.
- punishment_credibility: whether current history makes retaliation threats believable.

Decision program:
P0. Choose only from legal actions.
P1. If opponent threat or forced defense is exposed by [punishment_credibility], keep only legal actions that answer that threat.
P2. Among remaining actions, rank them using the comparative evidence in [stage_game_payoff_table] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Iterated Prisoner's Dilemma

### Group 2

Use only these computed fields:

- `opponent_defection_rate`: fraction of opponent defection moves.
- `opponent_streak_type`: current streak such as repeated cooperation or repeated defection.
- `reciprocity_pattern_flag`: whether the opponent appears to mirror my last action or respond conditionally.
- `trigger_strategy_state`: coarse repeated-game state such as `cooperate`, `punish`, `test_repair`, or `exploit-resistant`.
- `one_step_best_response`: immediate one-round best response to the opponent's likely current action.
- `repair_opportunity_flag`: whether one side defected recently but the history still supports restoring cooperation.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Iterated Prisoner's Dilemma.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- opponent_defection_rate: fraction of opponent defection moves.
- opponent_streak_type: current streak such as repeated cooperation or repeated defection.
- reciprocity_pattern_flag: whether the opponent appears to mirror my last action or respond conditionally.
- trigger_strategy_state: coarse repeated-game state such as `cooperate`, `punish`, `test_repair`, or `exploit-resistant`.
- one_step_best_response: immediate one-round best response to the opponent's likely current action.
- repair_opportunity_flag: whether one side defected recently but the history still supports restoring cooperation.

Decision program:
P0. Choose only from legal actions.
P1. If opponent threat or forced defense is exposed by [repair_opportunity_flag], keep only legal actions that answer that threat.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Iterated Prisoner's Dilemma

### Group 3

Use only these computed fields:

- `trigger_strategy_state`: coarse repeated-game state such as `cooperate`, `punish`, `test_repair`, or `exploit-resistant`.
- `last_round_outcome`: previous round action profile and payoff implication.
- `punishment_credibility`: whether current history makes retaliation threats believable.
- `exploitation_risk_if_silent`: risk of being repeatedly exploited by cooperating now.
- `repair_opportunity_flag`: whether one side defected recently but the history still supports restoring cooperation.
- `current_action_long_run_tradeoff`: compact summary of short-run gain versus long-run relationship value.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Iterated Prisoner's Dilemma.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- trigger_strategy_state: coarse repeated-game state such as `cooperate`, `punish`, `test_repair`, or `exploit-resistant`.
- last_round_outcome: previous round action profile and payoff implication.
- punishment_credibility: whether current history makes retaliation threats believable.
- exploitation_risk_if_silent: risk of being repeatedly exploited by cooperating now.
- repair_opportunity_flag: whether one side defected recently but the history still supports restoring cooperation.
- current_action_long_run_tradeoff: compact summary of short-run gain versus long-run relationship value.

Decision program:
P0. Choose only from legal actions.
P1. If opponent threat or forced defense is exposed by [punishment_credibility, repair_opportunity_flag], keep only legal actions that answer that threat.
P2. Exclude actions flagged as unsafe, dominated, overaggressive, or losing by [exploitation_risk_if_silent].
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Iterated Prisoner's Dilemma

### Group 4

Use only these computed fields:

- `opponent_recent_actions`: short recent suffix of opponent behavior.
- `reciprocity_pattern_flag`: whether the opponent appears to mirror my last action or respond conditionally.
- `forgiveness_pattern_flag`: whether the opponent returns to cooperation after punishment phases.
- `trigger_strategy_state`: coarse repeated-game state such as `cooperate`, `punish`, `test_repair`, or `exploit-resistant`.
- `last_round_outcome`: previous round action profile and payoff implication.
- `punishment_credibility`: whether current history makes retaliation threats believable.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Iterated Prisoner's Dilemma.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- opponent_recent_actions: short recent suffix of opponent behavior.
- reciprocity_pattern_flag: whether the opponent appears to mirror my last action or respond conditionally.
- forgiveness_pattern_flag: whether the opponent returns to cooperation after punishment phases.
- trigger_strategy_state: coarse repeated-game state such as `cooperate`, `punish`, `test_repair`, or `exploit-resistant`.
- last_round_outcome: previous round action profile and payoff implication.
- punishment_credibility: whether current history makes retaliation threats believable.

Decision program:
P0. Choose only from legal actions.
P1. If opponent threat or forced defense is exposed by [punishment_credibility], keep only legal actions that answer that threat.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Iterated Prisoner's Dilemma

### Group 5

Use only these computed fields:

- `opponent_streak_type`: current streak such as repeated cooperation or repeated defection.
- `reciprocity_pattern_flag`: whether the opponent appears to mirror my last action or respond conditionally.
- `forgiveness_pattern_flag`: whether the opponent returns to cooperation after punishment phases.
- `one_step_best_response`: immediate one-round best response to the opponent's likely current action.
- `punishment_credibility`: whether current history makes retaliation threats believable.
- `current_action_long_run_tradeoff`: compact summary of short-run gain versus long-run relationship value.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Iterated Prisoner's Dilemma.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- opponent_streak_type: current streak such as repeated cooperation or repeated defection.
- reciprocity_pattern_flag: whether the opponent appears to mirror my last action or respond conditionally.
- forgiveness_pattern_flag: whether the opponent returns to cooperation after punishment phases.
- one_step_best_response: immediate one-round best response to the opponent's likely current action.
- punishment_credibility: whether current history makes retaliation threats believable.
- current_action_long_run_tradeoff: compact summary of short-run gain versus long-run relationship value.

Decision program:
P0. Choose only from legal actions.
P1. If opponent threat or forced defense is exposed by [punishment_credibility], keep only legal actions that answer that threat.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Iterated Prisoner's Dilemma

### Group 6

Use only these computed fields:

- `opponent_recent_actions`: short recent suffix of opponent behavior.
- `opponent_streak_type`: current streak such as repeated cooperation or repeated defection.
- `reciprocity_pattern_flag`: whether the opponent appears to mirror my last action or respond conditionally.
- `forgiveness_pattern_flag`: whether the opponent returns to cooperation after punishment phases.
- `stage_game_payoff_table`: the one-shot payoff ordering relevant this round.
- `future_cooperation_value_proxy`: rough long-run value of keeping mutual cooperation alive.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Iterated Prisoner's Dilemma.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- opponent_recent_actions: short recent suffix of opponent behavior.
- opponent_streak_type: current streak such as repeated cooperation or repeated defection.
- reciprocity_pattern_flag: whether the opponent appears to mirror my last action or respond conditionally.
- forgiveness_pattern_flag: whether the opponent returns to cooperation after punishment phases.
- stage_game_payoff_table: the one-shot payoff ordering relevant this round.
- future_cooperation_value_proxy: rough long-run value of keeping mutual cooperation alive.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [future_cooperation_value_proxy], prioritize actions supported by those fields.
P2. Among remaining actions, rank them using the comparative evidence in [stage_game_payoff_table, future_cooperation_value_proxy] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Iterated Prisoner's Dilemma

### Group 7

Use only these computed fields:

- `last_round_outcome`: previous round action profile and payoff implication.
- `stage_game_payoff_table`: the one-shot payoff ordering relevant this round.
- `one_step_best_response`: immediate one-round best response to the opponent's likely current action.
- `punishment_credibility`: whether current history makes retaliation threats believable.
- `exploitation_risk_if_silent`: risk of being repeatedly exploited by cooperating now.
- `repair_opportunity_flag`: whether one side defected recently but the history still supports restoring cooperation.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Iterated Prisoner's Dilemma.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- last_round_outcome: previous round action profile and payoff implication.
- stage_game_payoff_table: the one-shot payoff ordering relevant this round.
- one_step_best_response: immediate one-round best response to the opponent's likely current action.
- punishment_credibility: whether current history makes retaliation threats believable.
- exploitation_risk_if_silent: risk of being repeatedly exploited by cooperating now.
- repair_opportunity_flag: whether one side defected recently but the history still supports restoring cooperation.

Decision program:
P0. Choose only from legal actions.
P1. If opponent threat or forced defense is exposed by [punishment_credibility, repair_opportunity_flag], keep only legal actions that answer that threat.
P2. Exclude actions flagged as unsafe, dominated, overaggressive, or losing by [exploitation_risk_if_silent].
P3. Among remaining actions, rank them using the comparative evidence in [stage_game_payoff_table] and choose the strongest supported action.
P4. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Iterated Prisoner's Dilemma

### Group 8

Use only these computed fields:

- `forgiveness_pattern_flag`: whether the opponent returns to cooperation after punishment phases.
- `trigger_strategy_state`: coarse repeated-game state such as `cooperate`, `punish`, `test_repair`, or `exploit-resistant`.
- `last_round_outcome`: previous round action profile and payoff implication.
- `stage_game_payoff_table`: the one-shot payoff ordering relevant this round.
- `future_cooperation_value_proxy`: rough long-run value of keeping mutual cooperation alive.
- `current_action_long_run_tradeoff`: compact summary of short-run gain versus long-run relationship value.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Iterated Prisoner's Dilemma.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- forgiveness_pattern_flag: whether the opponent returns to cooperation after punishment phases.
- trigger_strategy_state: coarse repeated-game state such as `cooperate`, `punish`, `test_repair`, or `exploit-resistant`.
- last_round_outcome: previous round action profile and payoff implication.
- stage_game_payoff_table: the one-shot payoff ordering relevant this round.
- future_cooperation_value_proxy: rough long-run value of keeping mutual cooperation alive.
- current_action_long_run_tradeoff: compact summary of short-run gain versus long-run relationship value.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [future_cooperation_value_proxy], prioritize actions supported by those fields.
P2. Among remaining actions, rank them using the comparative evidence in [stage_game_payoff_table, future_cooperation_value_proxy] and choose the strongest supported action.
P3. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Iterated Prisoner's Dilemma

### Group 9

Use only these computed fields:

- `opponent_recent_actions`: short recent suffix of opponent behavior.
- `opponent_streak_type`: current streak such as repeated cooperation or repeated defection.
- `trigger_strategy_state`: coarse repeated-game state such as `cooperate`, `punish`, `test_repair`, or `exploit-resistant`.
- `future_cooperation_value_proxy`: rough long-run value of keeping mutual cooperation alive.
- `repair_opportunity_flag`: whether one side defected recently but the history still supports restoring cooperation.
- `current_action_long_run_tradeoff`: compact summary of short-run gain versus long-run relationship value.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Iterated Prisoner's Dilemma.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- opponent_recent_actions: short recent suffix of opponent behavior.
- opponent_streak_type: current streak such as repeated cooperation or repeated defection.
- trigger_strategy_state: coarse repeated-game state such as `cooperate`, `punish`, `test_repair`, or `exploit-resistant`.
- future_cooperation_value_proxy: rough long-run value of keeping mutual cooperation alive.
- repair_opportunity_flag: whether one side defected recently but the history still supports restoring cooperation.
- current_action_long_run_tradeoff: compact summary of short-run gain versus long-run relationship value.

Decision program:
P0. Choose only from legal actions.
P1. If any forcing or immediately favorable candidate set is exposed by [future_cooperation_value_proxy], prioritize actions supported by those fields.
P2. If opponent threat or forced defense is exposed by [repair_opportunity_flag], keep only legal actions that answer that threat.
P3. Among remaining actions, rank them using the comparative evidence in [future_cooperation_value_proxy] and choose the strongest supported action.
P4. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```

## Iterated Prisoner's Dilemma

### Group 10

Use only these computed fields:

- `opponent_recent_actions`: short recent suffix of opponent behavior.
- `opponent_defection_rate`: fraction of opponent defection moves.
- `opponent_streak_type`: current streak such as repeated cooperation or repeated defection.
- `one_step_best_response`: immediate one-round best response to the opponent's likely current action.
- `punishment_credibility`: whether current history makes retaliation threats believable.
- `repair_opportunity_flag`: whether one side defected recently but the history still supports restoring cooperation.

Suggested `high_distill` prompt block:

```text
You are executing a high_distill field program for Iterated Prisoner's Dilemma.

Current state and legal actions are already given.
Do not invent extra fields outside this group.

Compute exactly these 6 derived fields:
- opponent_recent_actions: short recent suffix of opponent behavior.
- opponent_defection_rate: fraction of opponent defection moves.
- opponent_streak_type: current streak such as repeated cooperation or repeated defection.
- one_step_best_response: immediate one-round best response to the opponent's likely current action.
- punishment_credibility: whether current history makes retaliation threats believable.
- repair_opportunity_flag: whether one side defected recently but the history still supports restoring cooperation.

Decision program:
P0. Choose only from legal actions.
P1. If opponent threat or forced defense is exposed by [punishment_credibility, repair_opportunity_flag], keep only legal actions that answer that threat.
P2. If multiple actions remain tied, use the full 6-field bundle as tie-break evidence and then choose one legal fallback.

After executing the decision program:
1. keep the final decision consistent with the highest-priority applicable rule,
2. cite only fields from this group as evidence,
3. choose one legal action,
4. return only the final action in the required output format.
```
