import os
import pandas as pd

DATA_DIR = r"6af458274c1e8_data_pack\Data Pack"

def inspect_pe_duplicates():
    pe_df = pd.read_csv(os.path.join(DATA_DIR, "playing_eleven.csv"))
    dups = pe_df[pe_df.duplicated(subset=['match_id', 'player_id'], keep=False)].sort_values(by=['match_id', 'player_id'])
    print(f"Total duplicate rows in playing_eleven: {len(dups)}")
    print(dups.head(20).to_string())

if __name__ == '__main__':
    inspect_pe_duplicates()
