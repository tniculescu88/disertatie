# disertatie
existing file:
(user-location.csv)

1)dbscan.py - runs the dbscan, and creates the transition lists and matrix, and plots the graphs
 (transition_mat.json, transition_list.json, sp_trans_list.json, user-location-clustered.csv)
2)processing.py - write in the csv the interest points snap points and streets (user_location_partially_written.csv)
3)google_requsts_urls.py - formats the google requests (google_requests.json)
4)call_google_api.py - calls the google requests (google_answers.json)
5)updating_user_location_with_google_answers.py - adds google answers to the csv (user_location_with_snap_points.csv)
6)here_requests.py - formats and calls the here requests (here_answers.json)
7)updating_user_location_with_here_answers.py - adds here answers to the csv (user_location_with_snap_points_and_streets.csv)
8)adding_streets_to_matrix.py - adds the streets names to the matrix (transition_mat_with_streets.json)
interest_point_schedule.py - compute 24 x 7 x 10 matrix schedule (schedule.json)
routes_max_times.py - compute the routes max times (routes_max_times.json)
interest_points_max_times.py - compute the max times of staying in each interest point (max_times.json)
show_graph.py - plots the collected points and the interest points
main.py - tests if the user has got lost or confused and sends an alert