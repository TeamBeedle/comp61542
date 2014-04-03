from comp61542 import app
from database import database
from flask import (render_template, request)

def format_data(data):
    fmt = "%.2f"
    result = []
    for item in data:
        if type(item) is list:
            result.append(", ".join([ (fmt % i).rstrip('0').rstrip('.') for i in item ]))
        else:
            result.append((fmt % item).rstrip('0').rstrip('.'))
    return result

@app.route("/averages")
def showAverages():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"averages"}
    args['title'] = "Averaged Data"
    args['description'] = "Average statistics for publications, authors and years!"
    tables = []
    headers = ["Average", "Conference Paper", "Journal", "Book", "Book Chapter", "All Publications"]
    averages = [ database.Stat.MEAN, database.Stat.MEDIAN, database.Stat.MODE ]
    tables.append({
        "id":1,
        "title":"Average Authors per Publication",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_authors_per_publication(i)[1])
                for i in averages ] })
    tables.append({
        "id":2,
        "title":"Average Publications per Author",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_publications_per_author(i)[1])
                for i in averages ] })
    tables.append({
        "id":3,
        "title":"Average Publications in a Year",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_publications_in_a_year(i)[1])
                for i in averages ] })
    tables.append({
        "id":4,
        "title":"Average Authors in a Year",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_authors_in_a_year(i)[1])
                for i in averages ] })

    args['tables'] = tables
    return render_template("averages.html", args=args)

@app.route("/coauthors")
def showCoAuthors():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    PUB_TYPES = ["Conference Papers", "Journals", "Books", "Book Chapters", "All Publications"]
    args = {"dataset":dataset, "id":"coauthors"}
    args["title"] = "Co-Authors"
    args['description'] = "List all co-authors of an author, between a given time in a given publication type!"


    start_year = db.min_year
    if "start_year" in request.args:
        start_year = int(request.args.get("start_year"))

    end_year = db.max_year
    if "end_year" in request.args:
        end_year = int(request.args.get("end_year"))

    pub_type = 4
    if "pub_type" in request.args:
        pub_type = int(request.args.get("pub_type"))

    args["data"] = db.get_coauthor_data(start_year, end_year, pub_type)
    args["start_year"] = start_year
    args["end_year"] = end_year
    args["pub_type"] = pub_type
    args["min_year"] = db.min_year
    args["max_year"] = db.max_year
    args["start_year"] = start_year
    args["end_year"] = end_year
    args["pub_str"] = PUB_TYPES[pub_type]
    return render_template("coauthors.html", args=args)

@app.route("/")
def showStatisticsMenu():
    dataset = app.config['DATASET']
    args = {"dataset":dataset}
    return render_template('statistics.html', args=args)

@app.route("/statisticsdetails/<status>")
def showPublicationSummary(status):
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":status}

    if (status == "publication_summary"):
        args["title"] = "Publication Summary"
        args["data"] = db.get_publication_summary()

    if (status == "publication_author"):
        args["title"] = "Author Publication"
        args["data"] = db.get_publications_by_author()

    if (status == "publication_year"):
        args["title"] = "Publication by Year"
        args["data"] = db.get_publications_by_year()

    if (status == "author_year"):
        args["title"] = "Author by Year"
        args["data"] = db.get_author_totals_by_year()

    if (status == "appearance_author"):
        args["title"] = "Appearance"
        args["data"] = db.get_number_of_appearance_by_author()

    return render_template('statistics_details.html', args=args)

@app.route("/searchauthors")
def showSearchAuthor():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"searchauthor"}
    args['title'] = "Search Author"
    args['description'] = "Input the author's name you want to search!"
    tables = []
    headers = ["Author Name"]
    #, "Conference Paper", "Journal", "Book", "Book Chapter", "Number of times first Author", "Number of times last Author", "All Publications", "Number of CoAuthors"]

    author_name = ""

    if "author_name" in request.args:
        author_name = request.args.get("author_name")

    header, data = db.search_authors(author_name.strip())
    #dataWithDistance = []
    if data == None:
        lastname = author_name.rsplit(None,1)[0]
        firstname = author_name.rsplit(None,1)[::-1][0]
        header, data = db.search_authors(firstname + " " + lastname)
        if data == None:
            data = ()
            headers = ["No author found"]

    if len(data) == 1:
        return showAuthorStats(data[0][0])

    """for i in range(len(data)):
        dataWithDistance.append([data[i], distanceFirstname[i], distanceLastname[i]])"""
    # dataWithDistance = [data, distanceFirstname, distanceLastname]
    tables.append({
        "id":1,
        "title":"Author Statistics Details",
        "header":headers,
        "rows": data})

    args['tables'] = tables

    return render_template('searchauthors.html', args=args)

@app.route("/authorStats/<author_name>")
def showAuthorStats(author_name):
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"searchauthor"}
    args['title'] = "Search Author"
    args['description'] = "Results:"
    tables = []

    tables.append({
        "id":1,
        "title":"Author general statistics",
        "header":["Author Name", "Number of conference papers", "Number of journals", "Number of books", "Number of book chapters", "Total", "Number of Coauthors"],
        "rows": db.get_all_author_stats(author_name)})
    tables.append({
        "id":2,
        "title":"Author first appearances",
        "header":["Author Name", "Appear first in Conference Paper", "Appear first in Journal", "Appear first in Book", "Appear first in Book Chapter", "Total"],
        "rows": db.get_first_author_stats(author_name)})
    tables.append({
        "id":3,
        "title":"Author last appearances",
        "header":["Author Name", "Appear last in Conference Paper", "Appear last in Journal", "Appear last in Book", "Appear last in Book Chapter", "Total"],
        "rows": db.get_last_author_stats(author_name)})
    tables.append({
        "id":4,
        "title":"Sole author statistics",
        "header":["Author Name", "Sole author in Conference Paper", "Sole author in Journal", "Sole author in Book", "Sole author in Book Chapter", "Total"],
        "rows": db.get_sole_author_stats(author_name)})

    args['tables'] = tables

    return render_template('authorStats.html', args=args)

@app.route("/distance")
def showDistance():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"distances"}
    args['title'] = "Distances"
    args['description'] = "Enter two author names to find their degree of separation.<br />X = No connection or author not found"

    if "author_name1" in request.args and "author_name2" in request.args:
        author_name1 = request.args.get("author_name1")
        author_name2 = request.args.get("author_name2")
        args['a1'] = author_name1
        args['a2'] = author_name2
        args['result'] = db.get_distance_between_authors(author_name1, author_name2)

    return render_template('distance.html', args=args)

#to test dijkstras, not a feature yet (or ever)
@app.route("/test")
def dijkstra():
    db = app.config['DATABASE']
    print db.get_distance_between_authors("Ceri Stefano", "Fraternali Piero")
    # return render_template(statist)