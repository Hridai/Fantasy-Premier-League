import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.preprocessing import OneHotEncoder, StandardScaler
from abc import ABC, abstractmethod
from ht_analysis.datautils import DataUtils


class ModelUtils(ABC):
    def __init__(self):
        pass
    
    @property
    def dependent_variables(self)->[str]:
        return self._dependent_variables

    @property
    def independent_variables(self)->[str]:
        return self._independent_variables
    
    @property
    def cleaned_df(self)->[pd.DataFrame]:
        '''Close to Raw data - unecessary columns removed, dtypes fixed'''
        return self._cleaned_df
    
    @dependent_variables.setter
    def dependent_variables(self, value)->[str]:
        self._dependent_variables = value
    
    @independent_variables.setter
    def independent_variables(self, value)->[str]:
        self._independent_variables = value
    
    @cleaned_df.setter
    def cleaned_df(self, value)->[pd.DataFrame]:
        self._cleaned_df = value
    
    @abstractmethod    
    def clean_data(self, df)->pd.DataFrame:
        l = self.independent_variables + self.dependent_variables
        return df[l]
    
    def _explore_pairplot(self, df, title):
        plt.figure()
        g = sns.pairplot(df)
        g.fig.suptitle(title, y=1.08, fontsize='xx-large')

    def _explore_corr(self, df, title):
        corr = df.corr()
        plt.figure()
        sns.heatmap(corr, 
            xticklabels=corr.columns.values,
            yticklabels=corr.columns.values).set(title=title)
    
    @abstractmethod    
    def explore_data(self, df, *, title=None):
        self._explore_corr(df, title)
        self._explore_pairplot(df, title)
    
    def _onehotencode_col(self, df_in, field_name):
        ''' Returns df with the field_name removed and appends the one-hot-encoded '''
        encoded_df = df_in[field_name].values
        encoded_df = encoded_df.reshape(1,-1).transpose()
        encoder = OneHotEncoder(handle_unknown='ignore')
        encoder.fit(encoded_df)
        encoder.categories_
        encoded_df = encoder.transform(encoded_df).toarray()
        encoded_df = pd.DataFrame( encoded_df )
        n = df_in[field_name].nunique()
        encoded_df.columns = ['{}_{}'.format(field_name, n) for n in range(1, n + 1)]
        df_in = df_in.drop(field_name,axis=1)
        df_in = pd.concat([df_in,encoded_df],axis=1)
        return df_in.dropna() if df_in.shape[1] > 1 else None
    
    @abstractmethod
    def prep_data(self):
        '''pre-model prep. 1hencode. Split out y from x. Normalize x.'''
        pass
    
    @abstractmethod
    def run(self, *, explore_data=False):
        self.clean_data(self.load_data())
        if explore_data: self.explore_data()
    
class ValueModel(ModelUtils):
    def __init__(self):
        self.independent_variables = ['xG','xA','xP','key_passes',
                                      'xGChain','creativity','influence',
                                      'threat','team','opposition_team',
                                      'position_pl']
        self.dependent_variables = ['total_points']
    
    def load_data(self):
        return DataUtils().get_gameweek_superset()
    
    def clean_data(self, df):
        temp_df = super().clean_data(df)
        self.cleaned_df = temp_df.loc[~temp_df['position_pl'].isin(['GK','DEF'])]
    
    def explore_data(self):
        pos_list = list(sorted(set(self.cleaned_df['position_pl'])))
        for pos in pos_list:
            temp_df = self.cleaned_df.loc[self.cleaned_df['position_pl'] == pos]
            super().explore_data(temp_df, title=pos)
        super().explore_data(self.cleaned_df, title='Overall')
        
    def prep_data(self):
        super().prep_data()
    
    def run(self, *, explore_data=False):
        super().run(explore_data=explore_data)

if __name__ == '__main__':
    bexplore = False
    model = ValueModel().run(explore_data=bexplore)
