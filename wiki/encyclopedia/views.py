from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from . import util
from django.urls import reverse
from django import forms
import random
import markdown2


class NewEntryForm(forms.Form):
    title = forms.CharField(label="Page Title")
    content = forms.CharField(widget=forms.Textarea(attrs={"rows":"5"}))


# Define index route
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
    })


# Define Entry route
def entry(request, title):
    # Check for title in the entries
    entries = (x.upper() for x in util.list_entries())
    if title.upper() not in entries:
        # Return error page if entry does not exist
        return HttpResponse(f"The entry with title {title} was not found")


    # Render entry page if it exist
    return render(request, "encyclopedia/entry.html",{
        "entry": markdown2.markdown(util.get_entry(title)),
        "title": title
    })


# Define Search route
def search(request):
    title = request.POST["q"]
    # Check if query matches in entry
    entries = (x.upper() for x in util.list_entries())
    if title.upper() in entries:
        # Redirect user to the entry page
        return render(request, "encyclopedia/entry.html",{
        "entry": util.get_entry(title),
        "title": title
        })


    else:
        results = []
        for string in util.list_entries():
            if title in string:
                results.append(string)
        return render(request, "encyclopedia/search.html",{
        "results": results
        })

def new(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if title in util.list_entries():
                return HttpResponse("Entry already exist")

            util.save_entry(title, content)
            return render(request, "encyclopedia/entry.html",{
                "entry": util.get_entry(title),
                "title": title
            })
        else:
            return render(request, "encyclopedia/new.html",{
            "form": form
        })


    else:
        return render(request, "encyclopedia/new.html",{
            "form": NewEntryForm()
        })

def edit(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            util.save_entry(title, content)
            return render(request, "encyclopedia/entry.html",{
                "entry": util.get_entry(title),
                "title": title
                })
        else:
            return render(request, "encyclopedia/edit.html",{
            "form": form
            })

    else:
        form = NewEntryForm(request.GET)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            return render(request, "encyclopedia/edit.html",{
                "entry": util.get_entry(title),
                "title": title
                })
        else:
            return render(request, "encyclopedia/edit.html",{
            "form": form
            })


