# Master's thesis Sebastian Cornelius Bergh

Title: Personalised Recommendations of Upcoming Sport Events

Supervisors: Assoc. Prof. Dr. Mehdi Elahi

Co-supervisors: Dr. Lars Skjærven, and Astrid Tessem

Scientific environment: This study takes place within the Department of Information Science and Media Studies at the University of Bergen. It is a part of Work Package 2 of the MediaFutures center, which concentrates on user modeling, personalization, and engagement. The research is conducted in collaboration with the media platform TV 2.

### ALS_model
Contains code for the creation of the ALS model with some TV2 related components missing. Requires modifications to run without these. The ALS model itself is also not included due to privacy reasons.

### Online_experiment 2
Demonstrates an example of how upcoming events are scored and recommended for one user in online experiment 2. This is a simplified version of the code used in production and is written in Python instead of Go. In this example, the ALS model is not used to score items; instead, pre-set scores are used.

### Preprossesing_and_usage
Contains some more preprocessing and usage of the models. The "preprocessing_for_models.py" file contains preprocessing steps the for raw datasets received from TV 2, resulting in final datasets that can be fed into the models. The "tournament_recommendationss_and_user_history.py" file shows how the scaled datasets can be used to train an ALS (not the altered one used in production) model. It also shows an example of how the model can be used to recommend tournaments, comparing the results to the users' watch history.

### Visualization
Contains visualization used to create some of the figures in the thesis.   