import json


''' 
This is an example of the functionality of online experiment 2. It shows how upcoming events are scored for one user.
'''

# Load upcoming sports events
def load_relevant_sport_events(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

# Load the predefined cf scores
def load_cf_scores(file_path):
    with open(file_path, "r") as file:
        cf_scores = json.load(file)
    return cf_scores

# Checks is the team is explicit favorites
def is_favorite_team(participants, team_favorites):
    for participant in participants:
        if participant in team_favorites:
            return True
    return False

# Calculate the scores and finds the drop off for each sport type, tournament and team
def calculate_cf_scores(cf_scores, relevant_sport_events):
    sport_scores = cf_scores['sportCfScores']
    tournament_scores = cf_scores['tournamentCfScores']
    participant_scores = cf_scores['participantScores']

    sport_type_scores = [sport_scores.get(event["AssetMetadata"]["VimondCategorySportType"].lower(), 0) if event["AssetMetadata"]["VimondCategorySportType"] else 0 for event in relevant_sport_events]
    tournament_id_scores = [tournament_scores.get(event["SportMetadata"]["TournamentTemplateId"].lower(), 0) for event in relevant_sport_events]
    participant_id_scores = [participant_scores.get(str(participant_id), 0) for event in relevant_sport_events for participant_id in event["SportMetadata"]["Participants"] if str(participant_id) in participant_scores]


    _,cf_scores['minSportTypeScore'] = find_top_and_knekk(sport_type_scores)
    _,cf_scores['minTournAndTeamScore'] = find_top_and_knekk(participant_id_scores)

    return cf_scores

# Calculated the drop off
def find_top_and_knekk(scores):
    copy_scores = scores.copy()
    copy_scores.sort(reverse=True)
    prev_score = copy_scores[0]
    if len(copy_scores) == 1:
        return prev_score, prev_score
    for score in copy_scores[1:]:
        if score > prev_score * 0.1:
            prev_score = score
        else:
            break
    if prev_score < 0.5:
        return copy_scores[0], 0.5
    return copy_scores[0], prev_score

# Creates the recommended list
def recommend_sport_event(team_favorites, cf_scores, relevant_sport_events):
    returned_sport_events = []

    for event in relevant_sport_events:
        score = 0.0

        if event["SportMetadata"] is not None and event["SportMetadata"]["Participants"] is not None:
            if is_favorite_team(event["SportMetadata"]["Participants"], team_favorites):
                returned_sport_events.append(event)
                continue
        
        if event["SportMetadata"] is None:
            if event["AssetMetadata"]["VimondCategorySportType"] is not None:
                sport_type = event["AssetMetadata"]["VimondCategorySportType"].lower()
                if sport_type in cf_scores['sportCfScores']:
                    score += cf_scores['sportCfScores'][sport_type]
            
            if score >= cf_scores['minSportTypeScore']:
                returned_sport_events.append(event)
        else:
            if event["SportMetadata"]["TournamentTemplateId"] is not None:
                tournament_id = event["SportMetadata"]["TournamentTemplateId"]
                if tournament_id in cf_scores['tournamentCfScores']:
                    score += cf_scores['tournamentCfScores'][tournament_id] * 0.2

            if event["SportMetadata"]["ParticipantIds"] is not None:
                for participant_id in event["SportMetadata"]["Participants"]:
                    if participant_id in cf_scores['participantScores']:
                        score += cf_scores['participantScores'][participant_id]

            if score >= cf_scores['minTournAndTeamScore']:
                returned_sport_events.append(event)

    return returned_sport_events

def main():
    # Simulate upcoming sport events
    relevant_sport_events = load_relevant_sport_events("Online_experient_2/relevant_sport_events.json")

    # Simulate the ALS score of different sports, tournaments and participants for the user. Normally these scores
    # are calculated from the ALS model by getting the recommended items and corresponting scores
    cf_scores = load_cf_scores("Online_experient_2/cf_scores.json")

    # Simulate favorites for the user    
    team_favorites = ["Team A", "Team B"]

    # The name of all available events
    print("All upcoming sports events:")
    for event in relevant_sport_events:
        print(event["Name"]["EventName"])

    # Identify the users score for sports, tournaments, and participants and get the min scores (threshold)
    cf_scores = calculate_cf_scores(cf_scores, relevant_sport_events)

    # Get the items to be recommended
    returned_sport_events = recommend_sport_event(team_favorites, cf_scores, relevant_sport_events)

    # Print the recommended sport events
    print("Recommended sports events:")
    for event in returned_sport_events:
        print(event["Name"]["EventName"])

# Execute the main method
if __name__ == "__main__":
    main()
