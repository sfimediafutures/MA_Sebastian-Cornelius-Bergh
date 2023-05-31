import numpy as np
import pandas as pd
from sklearn import preprocessing



'''
This file handles general preprosessing of the files to prepare datasets 
to feed the recommendation models
'''

def importing_and_combining_files():
    sport_events = pd.read_csv ('')
    metadata = pd.read_csv('')
    participants = pd.read_csv('')
    df4 = pd.read_parquet('')
    df5 = pd.read_parquet('')
    df6 = pd.read_parquet('')
    df7 = pd.read_parquet('')
    df8 = pd.read_parquet('')
    df9 = pd.read_parquet('')
    df10 = pd.read_parquet('')

    viweing_sessions = pd.concat([df4, df5, df6, df7, df8, df9, df10])

    sport_events['itemId'] = sport_events['itemId'].str.replace('a-', '')
    metadata['itemId'] = metadata['itemId'].str.replace('a-', '')

    return(sport_events, metadata, participants, viweing_sessions)


def preprosess_sport(sport_events, metadata, viewing_sessions):
    df_slice = metadata.copy()
    df_slice["categoryTitlePath"] = df_slice["categoryTitlePath"].str.slice(1, -1)
    split = df_slice["categoryTitlePath"].str.split(',',expand=True)[1].str.replace("'", "")
    df_slice["sport"] = split
    df_slice["sport"] = df_slice["sport"].str.slice(1,)

    df2_sport = df_slice[["itemId","sport"]]
    df_sport = sport_events[["itemId", "sportTypeName"]]

    df_combined = pd.merge(df_sport, df2_sport, on='itemId', how='outer')
    df_combined["sportTypeName"] = df_combined["sportTypeName"].fillna(df_combined["sport"])
    df_combined["sport"] = df_combined["sport"].fillna(df_combined["sportTypeName"])
    df_combined.drop(["sportTypeName"], axis=1, inplace=True)

    df_viewing = viewing_sessions[["profileId","assetId", "durationSec"]]

    df_profile_watched = pd.merge(df_viewing, df_combined.rename(columns={'itemId':'assetId'}), on='assetId', how='inner')

    df_sport = df_profile_watched[["durationSec"]].groupby([df_profile_watched.profileId,df_profile_watched.sport]).apply(sum).reset_index()

    scaled_df_sport = scale_df(df_sport)
    scaled_df_sport.to_csv("scaled_df_sport.csv")

    return df_sport


def preprosess_tournament(sport_events, viewing_sessions):
    tournements = sport_events[["itemId", "tournamentTemplateId"]]
    df_viewing = viewing_sessions[["profileId","assetId", "durationSec"]]

    df_asset = pd.merge(df_viewing, tournements.rename(columns={'itemId':'assetId'}), on='assetId', how='inner')
    df_asset.drop(["assetId"], axis=1, inplace=True)

    df_tournament = df_asset[["durationSec"]].groupby([df_asset.profileId,df_asset.tournamentTemplateId]).apply(sum).reset_index()

    scaled_df_tournament = scale_df(df_tournament)
    scaled_df_tournament.to_csv("scaled_df_tournament.csv")

    return scaled_df_tournament


def scale_df(df):
    scaled=df.copy()
    min_max_scaler = preprocessing.MinMaxScaler()
    x = np.array(scaled["durationSec"]).reshape(-1,1)
    x_scaled = min_max_scaler.fit_transform(x)
    scaled["normDuration"] = x_scaled
    scaled.drop(["durationSec"], axis=1,inplace=True)
    
    return scaled

def main():
    sport_events, metadata, participants, viweing_sessions = importing_and_combining_files()

    df_sport = preprosess_sport(sport_events, metadata, viweing_sessions)
    df_tournaments = preprosess_tournament(sport_events,viweing_sessions)

if __name__ == "__main__":
    main()