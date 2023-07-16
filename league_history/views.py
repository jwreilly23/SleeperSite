from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django import forms
import requests

# Create your views here.

base_url = "https://api.sleeper.app/v1"
call_count = 0

class UsernameForm(forms.Form):
    userForm = forms.CharField(label="", )

# class LeaguesForm(forms.Form):
#     leaguesForm = forms.CheckboxSelectMultiple(choices=)

def index(request):
    return render(request, "league_history/index.html", {
        "userForm": UsernameForm()
    })

def select_leagues(request):
    if request.method == "POST":
        # Take in the data the user submitted and save it as form
        form = UsernameForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():
            # get form info
            username = form.cleaned_data["userForm"]

            # get user id by username
            user_id = get_user_id(username)

            # reload with banner if username not found
            if not user_id:
                return render(request, "league_history/index.html", {
                "userForm": UsernameForm(),
                "banner": f"Username {username} not found"
            })

            # get user leagues
            user_leagues = get_user_leagues(user_id)

            # render the successful page
            return render(request, "league_history/selectleagues.html", {
                "username": username,
                "leagues": user_leagues,
                "league_count": len(user_leagues),
                "call_count": call_count
            })


def history(request):
    if request.method == "POST":
        # Take in the data the user submitted and save it as form
        form = UsernameForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # get form info
            username = form.cleaned_data["userForm"]

            # get user id by username
            user_id = get_user_id(username)

            # reload with banner if username not found
            if not user_id:
                return render(request, "league_history/index.html", {
                "userForm": UsernameForm(),
                "banner": f"Username {username} not found"
            })


            # get user leagues
            user_leagues = get_user_leagues(user_id)

            # render the successful page
            return render(request, "league_history/history.html", {
                "username": username,
                "leagues": user_leagues,
                "league_count": len(user_leagues),
                "call_count": call_count
            })

        else:

            # If the form is invalid, re-render the page with existing information.
            return render(request, "league_history/index.html", {
                "userForm": UsernameForm()
            })

    return render(request, "league_history/index.html", {
        "userForm": UsernameForm()
    })

def get_user_id(username):
    '''
    Takes a username, returns the user id
    '''
    response = requests.get(base_url+f"/user/{username}").json()
    if response is not None:
        return response["user_id"]
    else:
        return False
    
def get_username(user_id):
    '''
    Takes a username, returns the user id
    '''
    response = requests.get(base_url+f"/user/{user_id}").json()
    global call_count
    call_count += 1

    if response is not None:
        return response["username"]
    else:
        return False

def get_user_leagues(user_id):
    '''
    Takes a user id, returns the list of league names
    '''
    current_year = 2022 # probably update this in the future...
    response = requests.get(base_url+f"/user/{user_id}/leagues/nfl/{current_year}").json()
    global call_count
    call_count += 1

    # loop through and get each league name
    leagues = []
    for league_raw in response:
        # initialize class        
        league = SleeperLeague(league_raw["name"], league_raw["league_id"], league_raw["avatar"], league_raw["total_rosters"])

        # get standings
        # league.set_standings(get_winner_bracket(league.id, league.size))

        leagues.append(league)

    return leagues

def get_winner_bracket(league_id, league_size):
    '''
    Takes a league id, returns a list of [1st, 2nd, 3rd...etc] for top 5 finish
    '''
    # get the playoff brackets
    winners_raw = requests.get(base_url+f"/league/{league_id}/winners_bracket").json()
    global call_count
    call_count += 1
    # losers_raw = requests.get(baseURL+f"/league/{league_id}/losers_bracket").json()

    # get the league rosters, to relate bracket roster id's to usernames
    rosters_dict = {}
    league_rosters_raw = requests.get(base_url+f"/league/{league_id}/rosters").json()
    call_count += 1
    for roster in league_rosters_raw:
        owner_username = get_username(roster["owner_id"])
        rosters_dict[roster["roster_id"]] = owner_username
        # print( str(roster["roster_id"]) + " - " + owner_username)        

    # currently only returning top 6
    final_standings = [None] * league_size

    # fill in standings ... winner (w) == null if the round hasn't finished yet
    for matchup in winners_raw:
        if "p" in matchup:
            # check if no winner...meaning no playoffs (edge case leagues like Megalabowl)
            if matchup["w"] is None:
                return final_standings

            # p is place of winner...meaning if p=1, final_standings[p-1] = winner ... f_s[p] = loser
            final_standings[matchup["p"]-1] = rosters_dict[matchup["w"]]
            final_standings[matchup["p"]] = rosters_dict[matchup["l"]]            

    return final_standings

class SleeperLeague:
    def __init__(self, name, id, avatar, size, standings=None):
        self.name = name
        self.id = id
        self.avatar = avatar
        self.size = size
        self.standings = standings

    def set_standings(self, standings):
        self.standings = standings

