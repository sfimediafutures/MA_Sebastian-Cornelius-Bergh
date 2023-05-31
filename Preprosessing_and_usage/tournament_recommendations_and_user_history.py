from implicit.als import AlternatingLeastSquares
import pandas as pd
from scipy.sparse import coo_matrix
import numpy as np

'''
This file shows how the scaled dataset can be used to train an ALS model. This example just
shows the ALS imported directly from implicit.als, and not the altered version used in production.
The file also shows an example of how the model can be used to recommend tournaments, comparing the 
results to the users watch history.

The file mostly consists of methods for collecting additional information about the recommended tournaments,
as well as information about the users watch history.
'''

# Import the 'scaled_df_tournament.csv' file created in the preprosessing_for_models.py file 
df_tournament = pd.read_csv('viewing.csv')

# Import the sport_events CSV file to get more information about some tournaments
sport_events = pd.read_csv ('sport_events.csv')


# Change 'profileId' and 'tournamentTemplateId' to category type
df_tournament['profileId'] = df_tournament['profileId'].astype('category')
df_tournament['tournamentTemplateId'] = df_tournament['tournamentTemplateId'].astype('category')

uim = coo_matrix(
     (df_tournament['normDuration'].astype(np.float32),
     (df_tournament['profileId'].cat.codes,
      df_tournament['tournamentTemplateId'].cat.codes))
)
uim = uim.tocsr()

items = dict(enumerate(df_tournament['tournamentTemplateId'].cat.categories))
users = dict(enumerate(df_tournament['profileId'].cat.categories))

factors = 8
iterations = 50
regularization = 0.1

als = AlternatingLeastSquares(factors=factors,iterations=iterations, regularization=regularization) 
als.fit(uim)

# Find the users who have watched more than 5 different tournaments
def find_active_users():
    activeUsers = []
    for user in users:
        if uim[user].getnnz() > 5:
            activeUsers.append(user)  
    
    return activeUsers

# Returns the tournaments the user has watched 
def watchedByUser(ids):
    user = userId(ids)
    watched_tourn = df_tournament.loc[df_tournament["profileId"] == user]
    return np.array(watched_tourn["tournamentTemplateId"])

# Returns the id of the recommended tournament
def recommendedId(sportsList):
    sports=[]
    for el in sportsList:
        sport = items[el]
        sports.append(sport)
    return sports

# Returns the user id 
def userId(ids):
    userId = users[ids]
    return userId

# Returns the name of the tournament from the id
def tournamentName(id):
    tournaments = []
    for tourns in id:
        tournaments.append(itemName(tourns))
    return tournaments    

# Returns the name of the sport from the tournament id
def sportName(id):
    sports = []
    for sport in id:
        t = sport_events.loc[sport_events["tournamentTemplateId"] == sport]
        sports.append(t["sportTypeName"].values[0])
    return sports
    
# Returns the name of the sport from a single tournament id
def singleSportName(id):
    i = itemId(id)
    s = sport_events.loc[sport_events["tournamentTemplateId"] == i]
    return(s["sportTypeName"].values[0])

# Returns single id of an item
def itemId(ids):
    item = items[ids]
    return item
    
# Returns single name of item
def itemName(id):
    name = sport_events.loc[sport_events["tournamentTemplateId"] == id]
    return name["tournamentTemplateName"].values[0]

# Returns list of tournaments
def fromIdstoName(ids):
    tournamentNames = []
    for i in ids:
        tId = itemId(i)
        name = itemName(tId)
        tournamentNames.append(name)
    return tournamentNames

# Checks how many of the predicted that the user have watched 
def precission(pred=[], watched=[], N=int):
    c = sum(el in watched for el in pred)
    return c/N

# Takes a spesific user and how many items to recommend
def spesificUser(id, N=int):
    ids, score = als.recommend(userid=id,user_items=uim[id],N=N, filter_already_liked_items=False)
    watchedTourns = tournamentName(watchedByUser(id))
    recommendedTrouns = tournamentName(recommendedId(ids))
    return watchedTourns, recommendedTrouns

# Recommendations for the most active users. Also calculating precision and displaying the users previous watch history
def main():
    total_pres = 0
    count = 0
    # activeUsers = find_active_users()

    for i in users:
        ids,score = als.recommend(userid=i,user_items=uim[i],N=3, filter_already_liked_items=False)
        score
        print(score)
        print("User:",userId(i))
        print("Tournaments recommended:", tournamentName(recommendedId(ids)))
        print("Score:", score)
        print("Tournaments watched:",tournamentName(watchedByUser(i)))
        print("Different sports watched:",list(set(sportName(watchedByUser(i)))))
        print("Different sports recommended:",list(set(sportName(recommendedId(ids)))))
        pres = precission(recommendedId(ids), watchedByUser(i), 6)
        print(pres)
        print("----------------------------------------------------------------")
        total_pres+=pres
        count+=1

    print("total pres =", total_pres/count)

if __name__ == "__main__":
    main()