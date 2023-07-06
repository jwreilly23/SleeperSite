from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django import forms

# Create your views here.

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

            return render(request, "league_history/history.html", {
                "username": username
            })

        else:

            # If the form is invalid, re-render the page with existing information.
            return render(request, "league_history/index.html", {
                "userForm": UsernameForm()
            })

    return render(request, "league_history/index.html", {
        "userForm": UsernameForm()
    })