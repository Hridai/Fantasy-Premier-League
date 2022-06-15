import os

import pandas as pd


class DataUtils():
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
        '''Source is FPL data, weekly gameweek player data'''
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

    def get_understat_pl_link(self):
        fpath = os.path.join(self.season_path, '', 'id_dict.csv')
        df = pd.read_csv(fpath)
        df.index = df['Understat_ID']
        df = df.drop(['Understat_ID', 
                     ' Understat_Name', 
                     ' FPL_Name'], 
                    axis=1)
        return df.to_dict('dict')[' FPL_ID']

    def get_player_id_list(self):
        '''Player name : FPL ID'''
        fpath = os.path.join(self.season_path, '', 'player_idlist.csv')
        df = pd.read_csv(fpath)
        df['player_name'] = df['first_name'] + ' ' + df['second_name']
        df.index = df['player_name']
        df = df.drop(['first_name', 
                     'second_name',
                     'player_name'], 
                    axis=1)
        return df.to_dict('dict')['id']

    def get_gameweek_superset(self):
        ''' Link understats to FPL gameweek player level data'''
        d_id_link = self.get_understat_pl_link()
        # df_pl = self.get_player_agg_data()
        df_gw = self.get_gw_data()
        df_us = self.get_player_understat_data() # To be joined...
        # Process fields
        df_us = df_us.replace({'player_id': d_id_link})
        df_gw['kickoff_date'] = pd.to_datetime(df_gw['kickoff_time'])
        df_us['date'] = pd.to_datetime(df_us['date'])
        df_gw['kickoff_date'] = df_gw['kickoff_date'].dt.date
        df_us['date'] = df_us['date'].dt.date
        id_dict = self.get_player_id_list()
        df_gw['player_id'] = df_gw['name']
        df_gw = df_gw.replace({'player_id': id_dict})
        # Join tables
        temp_df = pd.merge(df_us, 
                             df_gw, 
                             how='inner', 
                             left_on = ['player_id','date'], 
                             right_on = ['player_id','kickoff_date'],
                             suffixes = ("_us","_pl"))
        # joined_df = pd.merge(temp_df, 
        #                      df_gw, 
        #                      how='inner', 
        #                      left_on = ['player_name_pl','round'], 
        #                      right_on = ['name', 'round'],
        #                      suffixes = ("","_gw"))
        temp_df['team'] = temp_df.apply(
            lambda x: x['h_team'] if x['was_home'] else x['a_team'],
            axis=1)
        temp_df['opposition_team'] = temp_df.apply(
            lambda x: x['a_team'] if x['was_home'] else x['h_team'],
            axis=1)
        temp_df['value'] = temp_df['value'] / 10
        temp_df['kickoff_time'] = temp_df.apply(
            lambda x: pd.to_datetime(x['kickoff_time']).time(),
            axis=1)
        return temp_df.dropna().reset_index(drop=True)

if __name__ == '__main__':
    dh = DataUtils()
    # res2 = dh.get_player_id_list()
    # res3 = dh.get_understat_pl_link()
    res = dh.get_gameweek_superset()
    
    
