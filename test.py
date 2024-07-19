# test.py

from src.api.hiscores import HiscoresAPI, GameMode

def main():
    get_test_data = HiscoresAPI.get_player_data_from_api("killer grr", GameMode.IRONMAN)
    print(get_test_data)

if __name__ == "__main__":
    main()