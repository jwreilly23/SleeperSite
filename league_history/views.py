from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django import forms
import requests

# Create your views here.

baseURL = "https://api.sleeper.app/v1"

class UsernameForm(forms.Form):
    userForm = forms.CharField(label="", )

def index(request):
    return render(request, "league_history/index.html", {
        "userForm": UsernameForm()
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


            # get the 1st, 2nd, 3rd place finish



            # render the successful page
            return render(request, "league_history/history.html", {
                "username": username,
                "leagues": user_leagues,
                "league_count": len(user_leagues)
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
    response = requests.get(baseURL+f"/user/{username}").json()
    if response is not None:
        return response["user_id"]
    else:
        return False

def get_user_leagues(user_id):
    '''
    Takes a user id, returns the list of league names
    '''
    current_year = 2022 # probably update this in the future...
    response = requests.get(baseURL+f"/user/{user_id}/leagues/nfl/{current_year}").json()

    # loop through and get each league name
    leagues = []
    for league in response:
        # maybe make this a class? league.Name, league.Id, etc.
        leagues.append(SleeperLeague(league["name"], league["league_id"], league["avatar"]))

    return leagues

def get_winner_bracket(league_id):
    '''
    Takes a league id, returns a list of [1st, 2nd, 3rd...etc] for top 5 finish
    '''
    response = requests.get(baseURL+f"/league/{league_id}/winners_bracket").json()

    # currently only returning top 6
    final_standings = [None] * 3

    # loop through twice to find the highest round number...accounts for playoffs with any number of rounds
    final_round = 1
    for matchup in response:
        if matchup["r"] > final_round:
            final_round = matchup["r"]

    for matchup in response:
        # check if final round
        if matchup["r"] == final_round:
            # 1st and 2nd
            if matchup["p"] == 1:




class SleeperLeague:
    def __init__(self, name, id, avatar):
        self.name = name
        self.id = id
        self.avatar = avatar

