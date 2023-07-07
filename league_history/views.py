from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django import forms
import requests

# Create your views here.

baseURL = "https://api.sleeper.app/v1"

class UsernameForm(forms.Form):
    userForm = forms.CharField(label="", initial="Username", )

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

            return render(request, "league_history/history.html", {
                "username": username,
                "leagues": user_leagues
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
    current_year = 2023 # probably update this in the future...
    response = requests.get(baseURL+f"/user/{user_id}/leagues/nfl/{current_year}").json()

    # loop through and get each league name
    league_names = []
    for league in response:
        # maybe make this a class? league.Name, league.Id, etc.
        league_names.append(league["name"])

    return league_names