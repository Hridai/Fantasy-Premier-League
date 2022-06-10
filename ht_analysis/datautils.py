import os

import pandas as pd


class DataHelper():
    def __init__(self, season_year='2021-22'):
        self.root_path = os.path.join(os.getcwd(),'data')
        self.season_year = season_year
        self.season_path = os.path.join(self.root_path, self.season_year)

    def get_gw_data(self):
        subfolder = 'gws'
        sub_path = os.path.join(self.season_path, subfolder)
        fpath = os.path.join(sub_path, 'merged_gw.csv')
        return pd.read_csv(fpath)

    def get_player_agg_data(self):
        subfolder = 'players'
        filename = 'gw.csv'
        fpath = os.path.join(self.season_path, subfolder)
        df_res = pd.DataFrame()
        for dirpath, dirnames, filenames in os.walk(fpath):
            if filename in filenames:
                df = pd.read_csv(os.path.join(dirpath, filename))
                filename_split = dirpath.split('\\')[-1].split('_')
                pname = ' '.join(filename_split[0:-1])
                p_id = int(filename_split[-1])
                df.insert(0, 'player_name', pname)
                df.insert(0, 'player_id', p_id)
                df_res = pd.concat([df_res, df])
        return df_res
    
    def get_player_understat_data(self):
        subfolder = 'understat'
        filename = 'gw.csv'
        fpath = os.path.join(self.season_path, subfolder)
        df_res = pd.DataFrame()
        for dirpath, dirnames, filenames in os.walk(fpath):
            for filename in filenames:
                if 'understat_' in filename:
                    continue
                temp_path = os.path.join(dirpath, filename)
                df = pd.read_csv(temp_path)
                filename_split = temp_path.split('\\')[-1].split('_')
                pname = ' '.join(filename_split[0:-1])
                p_id = int(filename_split[-1][:-4]) # Strip out .csv at the end
                df.insert(0, 'player_name', pname)
                df.insert(0, 'player_id', p_id)
                df_res = pd.concat([df_res, df])
        return df_res
    
    def get_understat_summary_data(self):
        fpath = os.path.join(self.season_path, 'understat', 'understat_player.csv')
        return pd.read_csv(fpath)

    def get_gw_pl_superset(self):
        df_pl = self.get_player_agg_data()
        df_gw = self.get_gw_data()
        # df_us = self.get_player_understat_data() # To be joined...
        joined_df = pd.merge(df_pl, 
                             df_gw, 
                             how='left', 
                             left_on = ['player_name','round'], 
                             right_on = ['name', 'round'],
                             suffixes = ("_pl","_gw"))
        return joined_df.dropna().reset_index(drop=True)

if __name__ == '__main__':
    dh = DataHelper()
    # res = dh.get_gw_pl_superset()
    # res2 = dh.get_understat_summary_data()
    # res3 = dh.get_player_understat_data()
