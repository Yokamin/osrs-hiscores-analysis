## OSRS Hiscores Analysis

A Python project for fetching and analyzing Old School RuneScape hiscores data.
Features

- Fetch player data from the OSRS Hiscores API
- Analyze player skills and activities
- Compare players' stats
- ... more to come ...

## Installation

1. Clone the repository:
```
git clone https://github.com/Yokamin/osrs-hiscores-analysis.git
```
2. Navigate to the project directory:
```
cd osrs-hiscores-analysis
```
3. Install the required packages:
```
pip install -r requirements.txt
```

## Usage
To fetch player data:
```python
from src.api.hiscores import HiscoresAPI, GameMode
player_data = HiscoresAPI.get_player_data_from_api("player_name", GameMode.REGULAR)
print(player_data)
```

## Project Structure

* `src/ `: Main source code
    * `api/ `: API interaction modules
    * `models/ `: Data models
    * `utils/ `: Utility functions and helpers
* `scripts/ `: Standalone scripts
* `tests/ `: Unit and integration tests

## Contributing
While this project is primarily for personal use and portfolio demonstration, suggestions and feedback are welcome. Please open an issue to discuss any changes you'd like to see.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

Old School RuneScape and its API are properties of Jagex Ltd.
Thanks to the Python community for providing excellent libraries and tools.
=======
# osrs-hiscores-analysis
A Python project for analyzing Old School RuneScape hiscores data