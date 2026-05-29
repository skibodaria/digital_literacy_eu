# ==================================
# GENERATE MAPPING COLUMNS FILE
# ==================================

import pandas as pd
import re
import os

def read_eurobarometer(file_path:str, header=8):
    """This functions reads an Excel file to get each tab from it and save it a dictionary of pandas dataframes.
    Takes two arguments:
    - a path to the file (string)
    - amount of rows before the header (by default 8 as in most of the Eurobarometer files) (integer)
    The function drops first two tabs (normally Content and Countries).
    Returns a dictionary of dataframes.
    """
    # read all the sheets as dictionary of dataframes:
    try: 
        dict_of_dfs = pd.read_excel(file_path, sheet_name=None, header=8)

        # get rid of the front page and country list:
        front_page = next(iter(dict_of_dfs))
        del dict_of_dfs[front_page]
        country_page = next(iter(dict_of_dfs))
        del dict_of_dfs[country_page]

        return dict_of_dfs
    
    except Exception as e:
        print(f"Something went wrong with file reading: {e}.")


def generate_mapping_candidates(dict_dfs, map_path, threshold=63):
    """
    Scans all sheets, runs basic cleaning, finds columns exceeding threshold,
    and writes them to the mapping CSV as candidates needing a short name.
    Only adds rows that aren't already in the mapping file.
    """
    existing = pd.read_csv(map_path) if os.path.exists(map_path) else pd.DataFrame(columns=['raw_phrase', 'clean_phrase'])
    already_mapped = set(existing['raw_phrase'].str.lower().str.strip())

    candidates = []
    for sheet, df in dict_dfs.items():
        for col in df.columns:
            if col == 'Unnamed: 1':
                continue
            col_str = normalise_col(col)
            if len(col_str) > threshold and col_str not in already_mapped:
                candidates.append({'raw_phrase': col_str, 'clean_phrase': ''})

    new_rows = pd.DataFrame(candidates).drop_duplicates(subset='raw_phrase') if candidates else pd.DataFrame(columns=['raw_phrase', 'clean_phrase'])
    updated = pd.concat([existing, new_rows], ignore_index=True)
    
    # always write the file
    updated.to_csv(map_path, index=False)
    print(f"Wrote {len(updated)} rows to {map_path}.")
    print(f"  - {len(new_rows)} new candidates added.")
    
    unfilled = updated[updated['clean_phrase'].str.strip() == '']
    if not unfilled.empty:
        print(f"  - {len(unfilled)} rows still need a clean_phrase filled in.")
        return False
    
    print("All mappings complete — ready to run pipeline.")
    return True

def normalise_col(col_str: str) -> str:
    col_str = str(col_str).lower().strip()
    col_str = re.sub(r"['\",]", '', col_str)
    col_str = re.sub(r'[\s/:]+', '_', col_str)
    col_str = re.sub(r'[^\w]', '_', col_str)
    col_str = re.sub(r'_+', '_', col_str)
    col_str = col_str.strip('_')
    return col_str


if __name__ == '__main__':
    dict_of_dfs = read_eurobarometer('./eurobarometer_data/eb_105.xlsx')
    if dict_of_dfs is None:
        print("read_eurobarometer returned None — check the path and file.")
    else:
        print(f"Loaded {len(dict_of_dfs)} sheets: {list(dict_of_dfs.keys())}")
        generate_mapping_candidates(dict_of_dfs, 'map_test.csv', 10)