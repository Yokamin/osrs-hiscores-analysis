# TODO

## Current Sprint
- [ ] Create data_processor.py to process data returned from API using templates from category_loader.py
- [ ] Implement player comparison feature
    This would allow the actual comparison between two or more players.
    - Compare with individual Game Mode ranks per player
    - Compare with specific Game Mode ranks for all players
        - Specified Game Mode or determined by list of players
            - Needs Game Mode determination logic
- [ ] Implement validation for multiple players
    Currently, validate_username() only validates one player at a time.
    - Add logic to input list of players and output valid + invalid
        - Further logic to process this
- [ ] Implement processing of determined Game Modes
    Currently determine_game_mode() determines Game Mode one player at a time.
    - Implement logic to process list of usernames
    - Process returned data to determine common Game Mode or argument to keep on an individual level
- [ ] Add unit tests for core functions

## Future Improvements
- [ ] Create html output for results

## Documentation
- [ ] Update installation documentation
- [ ] Update usage documentation

## Long-term Goals
- [ ] Integrate with AI to display a more dynamic breakdown on a per-comparison level