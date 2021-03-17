from django.shortcuts import render
from . import util
from django import forms
from encyclopedia.templatetags import markdown_to_html
import random

class NewEntryForm(forms.Form): #form class that inherits built in form lib from Django
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'style': 'width: 800px'}))
    content = forms.CharField(widget=forms.Textarea )

def index(request): # displays list of entry
    request.session["entries"] = util.list_entries()
    return render(request, "encyclopedia/index.html", {
        "entries": request.session["entries"]
    })

def display_html_entry(request, title, entry, editbutton): #displays marked down html version of text
    htmlfile = markdown_to_html.markdowntohtml(util.get_entry(title))
    return render(request, "encyclopedia/entry_template.html", {
        "content": htmlfile,
        "title": entry,
        "editbutton": editbutton
    })

def entry_doesnt_exist(request, title):
    return render(request, "encyclopedia/entry_template.html", {
        "content": f'<h3>ERROR: Page \'{title}\' does not exist </h3>',
        "editbutton": False #editbutton will not show on template page 
    })

def view_entry(request,title): # displays contents of an Entry
    for entry in request.session["entries"]: # entry name exists
        if title.upper() == entry.upper(): # query matches the entire name of an entry in the list
            return display_html_entry(request, title, entry, True) #edit button will show on template page
    return entry_doesnt_exist(request, title)# an entry does not exist
            
def search_entry(request):
    search_title =  request.GET["q"]
    entries = request.session["entries"]
    search_list = [x for x in entries if x.upper().startswith(search_title.upper())] # filter out all the strings that starts with a particular letter

    for entry in entries:
        if search_title.upper() == entry.upper(): # query matches the entire name of an entry in the list
            return display_html_entry(request, search_title, entry, True)
        if (entry.upper().startswith(search_title.upper())):# displays a list of all entries that starts with the given query(letter/s, substring)
            return render(request, "encyclopedia/index.html", {
                "entries": search_list
            })
    return entry_doesnt_exist(request, search_title)

def random_entry(request):
    random_entry = (random.choice(request.session["entries"]))
    return view_entry(request, random_entry)

def new_entry(request):
    if request.method == "POST": 
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]  #form.cleaned data gives access to all data submitted by the user
            content = form.cleaned_data["content"]
            for entry in request.session["entries"]:
                if title.upper() == entry.upper(): # query matches the entire name of an entry in the list
                    if request.POST["edit"]: #for edit entry: If edit button was clicked, page will redirect to the entry's content
                        util.save_entry(title,content) # updates an entry
                        request.session["entries"] += [title]
                        return display_html_entry(request, title, entry, True) #True-> edit button will show on entry_template page
                    
                    return render(request, "encyclopedia/entry_template.html", { # an entry name already exists
                        "content": f'<h3>ERROR: Page \'{title}\' already exists</h3>',
                        "title":title,
                        "editbutton": False # edit button will not be displayed on entry_template page
                    })
            else: # saves a new entry
                util.save_entry(title,content)
                request.session["entries"] += [title]
    return render(request, "encyclopedia/new_entry.html",{
        "form": NewEntryForm(), # creates a blank form
        "page_exists": False # to use create page header in new_entry page
    })

def edit_entry(request, title):
    form = NewEntryForm({
            "content":util.get_entry(title),
            "title": title
    })
    form.fields['title'].widget.attrs['readonly'] = True # title uneditable, only readable
    form.fields['title'].widget.attrs['class'] = 'grayOut' #css for grayout
    return render(request, "encyclopedia/new_entry.html",{ 
        "form": form,
        "page_exists": True # to use edit page header in new_entry page
    })
