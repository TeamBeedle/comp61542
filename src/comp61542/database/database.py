from comp61542.statistics import average
import itertools
import numpy as np
import difflib
from xml.sax import handler, make_parser, SAXException
import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
from priodict import priorityDictionary


PublicationType = [
    "Conference Paper", "Journal", "Book", "Book Chapter"]

class Publication:
    CONFERENCE_PAPER = 0
    JOURNAL = 1
    BOOK = 2
    BOOK_CHAPTER = 3

    def __init__(self, pub_type, title, year, authors):
        self.pub_type = pub_type
        self.title = title
        if year:
            self.year = int(year)
        else:
            self.year = -1
        self.authors = authors

    def get_first_author_id(self):
        if self.authors:
            return self.authors[0]

    def get_last_author_id(self):
        if self.authors:
            return self.authors[len(self.authors) - 1]

    def is_sole(self, author):
        if self.is_first(author) and len(self.authors) == 1:
            return True
        else:
            return False

    def is_first(self, author):
        if self.authors[0] == author:
           return True
        else:
            return False

    def is_last(self, author):
        i = len(self.authors)
        if self.authors[i-1] == author:
            return True
        else:
            return False


class Author:
    def __init__(self, name):
        self.name = name

class Stat:
    STR = ["Mean", "Median", "Mode"]
    FUNC = [average.mean, average.median, average.mode]
    MEAN = 0
    MEDIAN = 1
    MODE = 2

class Database:
    def read(self, filename):
        self.publications = []
        self.authors = []
        self.coauthors = {}
        self.distances = {}
        self.author_idx = {}
        self.min_year = None
        self.max_year = None

        handler = DocumentHandler(self)
        parser = make_parser()
        parser.setContentHandler(handler)
        infile = open(filename, "r")
        valid = True
        try:
            parser.parse(infile)
        except SAXException as e:
            valid = False
            print "Error reading file (" + e.getMessage() + ")"
        infile.close()

        for p in self.publications:
            if self.min_year == None or p.year < self.min_year:
                self.min_year = p.year
            if self.max_year == None or p.year > self.max_year:
                self.max_year = p.year

        self.distances = [[999 for x in range(len(self.authors))] for x in range(len(self.authors))]

        return valid

    def get_all_authors(self):
        return self.author_idx.keys()

    def get_coauthor_data(self, start_year, end_year, pub_type):
        coauthors = self.coauthors
        for p in self.publications:
            if ((start_year == None or p.year >= start_year) and
                (end_year == None or p.year <= end_year) and
                (pub_type == 4 or pub_type == p.pub_type)):
                for a in p.authors:
                    for a2 in p.authors:
                        if a != a2:
                            try:
                                coauthors[a].add(a2)
                            except KeyError:
                                coauthors[a] = set([a2])
        def display(db, coauthors, author_id):
            return "%s (%d)" % (db.authors[author_id].name, len(coauthors[author_id]))

        header = ("Author", "Co-Authors")
        data = []
        for a in coauthors:
            data.append([ display(self, coauthors, a),
                ", ".join([
                    display(self, coauthors, ca) for ca in coauthors[a] ]) ])

        return (header, data)

    def get_average_authors_per_publication(self, av):
        header = ("Conference Paper", "Journal", "Book", "Book Chapter", "All Publications")

        auth_per_pub = [[], [], [], []]

        for p in self.publications:
            auth_per_pub[p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [ func(auth_per_pub[i]) for i in np.arange(4) ] + [ func(list(itertools.chain(*auth_per_pub))) ]
        return (header, data)

    def get_average_publications_per_author(self, av):
        header = ("Conference Paper", "Journal", "Book", "Book Chapter", "All Publications")

        pub_per_auth = np.zeros((len(self.authors), 4))

        for p in self.publications:
            for a in p.authors:
                pub_per_auth[a, p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [ func(pub_per_auth[:, i]) for i in np.arange(4) ] + [ func(pub_per_auth.sum(axis=1)) ]
        return (header, data)

    def get_average_publications_in_a_year(self, av):
        header = ("Conference Paper",
            "Journal", "Book", "Book Chapter", "All Publications")

        ystats = np.zeros((int(self.max_year) - int(self.min_year) + 1, 4))

        for p in self.publications:
            ystats[p.year - self.min_year][p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [ func(ystats[:, i]) for i in np.arange(4) ] + [ func(ystats.sum(axis=1)) ]
        return (header, data)

    def get_average_authors_in_a_year(self, av):
        header = ("Conference Paper",
            "Journal", "Book", "Book Chapter", "All Publications")

        yauth = [ [set(), set(), set(), set(), set()] for _ in range(int(self.min_year), int(self.max_year) + 1) ]

        for p in self.publications:
            for a in p.authors:
                yauth[p.year - self.min_year][p.pub_type].add(a)
                yauth[p.year - self.min_year][4].add(a)

        ystats = np.array([ [ len(S) for S in y ] for y in yauth ])

        func = Stat.FUNC[av]

        data = [ func(ystats[:, i]) for i in np.arange(5) ]
        return (header, data)

    def get_publication_summary_average(self, av):
        header = ("Details", "Conference Paper",
            "Journal", "Book", "Book Chapter", "All Publications")

        pub_per_auth = np.zeros((len(self.authors), 4))
        auth_per_pub = [[], [], [], []]

        for p in self.publications:
            auth_per_pub[p.pub_type].append(len(p.authors))
            for a in p.authors:
                pub_per_auth[a, p.pub_type] += 1

        name = Stat.STR[av]
        func = Stat.FUNC[av]

        data = [
            [name + " authors per publication"]
                + [ func(auth_per_pub[i]) for i in np.arange(4) ]
                + [ func(list(itertools.chain(*auth_per_pub))) ],
            [name + " publications per author"]
                + [ func(pub_per_auth[:, i]) for i in np.arange(4) ]
                + [ func(pub_per_auth.sum(axis=1)) ] ]
        return (header, data)

    def get_publication_summary(self):
        header = ("Details", "Conference Paper",
            "Journal", "Book", "Book Chapter", "Total")

        plist = [0, 0, 0, 0]
        alist = [set(), set(), set(), set()]

        for p in self.publications:
            plist[p.pub_type] += 1
            for a in p.authors:
                alist[p.pub_type].add(a)
        # create union of all authors
        ua = alist[0] | alist[1] | alist[2] | alist[3]

        data = [
            ["Number of publications"] + plist + [sum(plist)],
            ["Number of authors"] + [ len(a) for a in alist ] + [len(ua)] ]

        return (header, data)

    def get_average_authors_per_publication_by_author(self, av):
        header = ("Author", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapers", "All publications")

        astats = [ [[], [], [], []] for _ in range(len(self.authors)) ]
        for p in self.publications:
            for a in p.authors:
                astats[a][p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [ [self.authors[i].name]
            + [ func(L) for L in astats[i] ]
            + [ func(list(itertools.chain(*astats[i]))) ]
            for i in range(len(astats)) ]
        return (header, data)

    # def get_numberoftime_author_appear(self, author):
    #     numOfTimeAppearFirst = 0
    #     numOfTimeAppearLast = 0
    #
    #     for p in self.publications:
    #         if author == p.get_last_author_id():
    #             numOfTimeAppearLast += 1
    #         if author == p.get_first_author_id():
    #             numOfTimeAppearFirst += 1
    #
    #
    #     return (numOfTimeAppearFirst, numOfTimeAppearLast)


    # def get_publications_by_author(self):
    #     header = ("Author", "Number of conference papers",
    #         "Number of journals", "Number of books",
    #         "Number of book chapters", "Total")
    #
    #     astats = [ [0, 0, 0, 0] for _ in range(len(self.authors)) ]
    #     for p in self.publications:
    #         for a in p.authors:
    #             astats[a][p.pub_type] += 1
    #
    #
    #     data = [ [self.authors[i].name] + astats[i] + [sum(astats[i])]
    #         for i in range(len(astats)) ]
    #
    #     return (header, data)


    def get_publications_by_author(self):
        header = ("Author", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapters", "Number of Times First Author",
            "Number of Times Last Author", "Number of Times Sole Author", "Total")

        astats = [ [0, 0, 0, 0] for _ in range(len(self.authors)) ]
        fstats = [ [0, 0, 0] for _ in range(len(self.authors)) ]
        for p in self.publications:
            for a in p.authors:
                astats[a][p.pub_type] += 1
                if p.is_sole(a):
                    fstats[a][2] += 1
                elif p.is_last(a):
                    fstats[a][1] += 1
                elif p.is_first(a):
                    fstats[a][0] += 1

        data = [ [self.authors[i].name] + astats[i] + fstats[i] + [sum(astats[i])]
            for i in range(len(astats)) ]
        return (header, data)

    def get_number_of_appearance_by_author(self):
        header = ("Author", "Appear first in Conference Paper",
                            "Appear first in Journal",
                            "Appear first in Book",
                            "Appear first in Book Chapter",
                            "Appear last in Conference Paper",
                            "Appear last in Journal",
                            "Appear last in Book",
                            "Appear last in Book Chapter",
                            "Appear sole in Conference Paper",
                            "Appear sole in Journal",
                            "Appear sole in Book",
                            "Appear sole in Book Chapter",)

        fstats = [ [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]] for _ in range(len(self.authors)) ]
        for p in self.publications:
            for a in p.authors:
                if p.is_sole(a):
                    fstats[a][2][p.pub_type] += 1
                elif p.is_last(a):
                    fstats[a][1][p.pub_type] += 1
                elif p.is_first(a):
                    fstats[a][0][p.pub_type] += 1

        data = [ [self.authors[i].name]  + fstats[i][0] + fstats[i][1] + fstats[i][2]
            for i in range(len(fstats)) ]
        return (header, data)

    def get_average_authors_per_publication_by_year(self, av):
        header = ("Year", "Conference papers",
            "Journals", "Books",
            "Book chapers", "All publications")

        ystats = {}
        for p in self.publications:
            try:
                ystats[p.year][p.pub_type].append(len(p.authors))
            except KeyError:
                ystats[p.year] = [[], [], [], []]
                ystats[p.year][p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [ [y]
            + [ func(L) for L in ystats[y] ]
            + [ func(list(itertools.chain(*ystats[y]))) ]
            for y in ystats ]
        return (header, data)

    def get_publications_by_year(self):
        header = ("Year", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapers", "Total")

        ystats = {}
        for p in self.publications:
            try:
                ystats[p.year][p.pub_type] += 1
            except KeyError:
                ystats[p.year] = [0, 0, 0, 0]
                ystats[p.year][p.pub_type] += 1

        data = [ [y] + ystats[y] + [sum(ystats[y])] for y in ystats ]

        """dates = []
        data2 = []
        for i in range(len(list)):
            dates.append(list[i][0])
            data2.append(list[i][1])"""
        return (header, data)

    def draw_coauthors(self, author_name):
        author_id = self.author_idx[author_name]
        data = self._get_collaborations(author_id, False)
        nodes = [author_name]
        for key in data:
            nodes.append(self.authors[key].name)
        G=nx.Graph()
        G.add_star(nodes)
        pos=nx.spring_layout(G)
        colors=range(1)
        nx.draw(G)
        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized()
        plt.show()

    def get_average_publications_per_author_by_year(self, av):
        header = ("Year", "Conference papers",
            "Journals", "Books",
            "Book chapers", "All publications")

        ystats = {}
        for p in self.publications:
            try:
                s = ystats[p.year]
            except KeyError:
                s = np.zeros((len(self.authors), 4))
                ystats[p.year] = s
            for a in p.authors:
                s[a][p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [ [y]
            + [ func(ystats[y][:, i]) for i in np.arange(4) ]
            + [ func(ystats[y].sum(axis=1)) ]
            for y in ystats ]
        return (header, data)

    def get_author_totals_by_year(self):
        header = ("Year", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapers", "Total")

        ystats = {}
        for p in self.publications:
            try:
                s = ystats[p.year][p.pub_type]
            except KeyError:
                ystats[p.year] = [set(), set(), set(), set()]
                s = ystats[p.year][p.pub_type]
            for a in p.authors:
                s.add(a)
        data = [ [y] + [len(s) for s in ystats[y]] + [len(ystats[y][0] | ystats[y][1] | ystats[y][2] | ystats[y][3])]
            for y in ystats ]
        return (header, data)

    def add_publication(self, pub_type, title, year, authors):
        if year == None or len(authors) == 0:
            print "Warning: excluding publication due to missing information"
            print "    Publication type:", PublicationType[pub_type]
            print "    Title:", title
            print "    Year:", year
            print "    Authors:", ",".join(authors)
            return
        if title == None:
            print "Warning: adding publication with missing title [ %s %s (%s) ]" % (PublicationType[pub_type], year, ",".join(authors))
        idlist = []
        for a in authors:
            try:
                idlist.append(self.author_idx[a])
            except KeyError:
                a_id = len(self.authors)
                self.author_idx[a] = a_id
                idlist.append(a_id)
                self.authors.append(Author(a))
        self.publications.append(
            Publication(pub_type, title, year, idlist))
        if (len(self.publications) % 100000) == 0:
            print "Adding publication number %d (number of authors is %d)" % (len(self.publications), len(self.authors))

        if self.min_year == None or year < self.min_year:
            self.min_year = year
        if self.max_year == None or year > self.max_year:
            self.max_year = year

    def _get_collaborations(self, author_id, include_self):
        data = {}
        for p in self.publications:
            if author_id in p.authors:
                for a in p.authors:
                    try:
                        data[a] += 1
                    except KeyError:
                        data[a] = 1
        if not include_self:
            del data[author_id]
        return data

    def get_coauthor_details(self, name):
        author_id = self.author_idx[name]
        data = self._get_collaborations(author_id, True)
        return [ (self.authors[key].name, data[key])
            for key in data ]

    def get_coauthor_ids(self, name):
        author_id = self.author_idx[name]
        data = self._get_collaborations(author_id, True)
        return [ (self.authors[key], data[key])
            for key in data ]

    def get_network_data(self):
        na = len(self.authors)

        nodes = [ [self.authors[i].name, -1] for i in range(na) ]
        links = set()
        for a in range(na):
            collab = self._get_collaborations(a, False)
            nodes[a][1] = len(collab)
            for a2 in collab:
                if a < a2:
                    links.add((a, a2))
        return (nodes, links)

    def get_distance_between_authors(self, author1, author2):
        distance = 'X'
        if self.author_idx.get(author1) == None :
            return 'X1'
        if self.author_idx.get(author2) == None:
            return 'X2'
        author1_id = self.author_idx[author1]
        author2_id = self.author_idx[author2]

        node_path = self.bfs(author1_id,author2_id)
        """
        visited_authors = []
        distance = 0
        coauthors = self._get_collaborations(author1_id, False)
        if coauthors.has_key(author2_id):
            return distance
        visited_authors.append(author1_id)

        while coauthors:
            queue = coauthors
            distance += 1
            for coauthor in queue:
                if coauthor not in visited_authors:
                    coauthors_list = self._get_collaborations(coauthor, False)
                    visited_authors.append(coauthor)
                    if author2_id in coauthors_list:
                        return distance
        """
        if len(node_path) == 0:
            distance = 'X'
        else:
            distance = len(node_path) - 2

        return distance

    def bfs(self, start, end):

        if start == end:
            return []

        # maintain a queue of paths
        queue = []
        visited_nodes = []
        path_list = []

        # push the first path into the queue
        queue.append(start)
        path_list.append([start])
        while queue:
            # get the first path from the queue
            node = queue.pop(0)
            current_path = list(path_list.pop(0))
            visited_nodes.append(node)

            coauthors = self._get_collaborations(node, False)
            if end in coauthors:
                current_path.append(end)
                return current_path

            diff_nodes = [item for item in set(coauthors) if item not in list(itertools.chain(visited_nodes,queue))]
            if diff_nodes:
                for item in diff_nodes:
                    queue.append(item)
                    new_path = list(current_path)
                    new_path.append(item)
                    path_list.append(new_path)

            """
            # get the last node from the path
            #node = path[-1]
            # path found
            if node == end:
                return path
            # enumerate all adjacent nodes, construct a new path and push it into the queue
            #for adjacent in graph.get(node, []):
            #    new_path = list(path)
            #    new_path.append(adjacent)
            #    queue.append(new_path)
            """
        return []

    def search_author(self, author_name):
        header, data = self.get_publications_by_author()
        if self.author_idx.get(author_name) == None:
            return None, None
        author_id = self.author_idx[author_name]
        coauthorData = self._get_collaborations(author_id, False)
        newHeader = list(header)
        newHeader.append("Number of Coauthor")
        data[author_id].append(len(coauthorData))
        return (newHeader[0], data[author_id][0])

    def search_authors(self, author_name):
        authors = []
        nameStartsWithWord = []
        surnameStartsWithWord = []
        wordBetween = []
        for key in self.author_idx.keys():
            if author_name.lower() in key.lower():
                lastname = key.rsplit(None,1)[0]
                firstname = key.rsplit(None,1)[::-1][0]
                distanceLastname = int(round(difflib.SequenceMatcher(None, author_name.lower(), lastname.lower()).ratio() * 100))
                distanceFirstname = int(round(difflib.SequenceMatcher(None, author_name.lower(), firstname.lower()).ratio() * 100))
                author_details = [key, distanceLastname, distanceFirstname]
                if lastname.lower().startswith(author_name.lower()):
                    surnameStartsWithWord.append(author_details)
                elif firstname.lower().startswith(author_name.lower()):
                    nameStartsWithWord.append(author_details)
                else:
                    wordBetween.append(author_details)
                #authors.append(author_details)
        newHeader = ["Author name"]
        surnameStartsWithWord.sort(key=lambda x: (-x[1], x[0]), reverse=False)
        nameStartsWithWord.sort(key=lambda x: (-x[2], x[0]), reverse=False)
        wordBetween.sort(key=lambda x: (-x[1], x[0]), reverse=False)
        authors = surnameStartsWithWord + nameStartsWithWord + wordBetween
        for item in authors:
            del item[2]
            del item[1]
        if len(authors) == 0:
            return None, None
        return (newHeader, authors)

    def get_all_author_stats(self, author_name):
        header, data = self.get_publications_by_author()
        if self.author_idx.get(author_name) == None:
            return None, None
        author_id = self.author_idx[author_name]
        coauthorData = self._get_collaborations(author_id, False)
        newHeader = list(header)
        newHeader.append("Number of Coauthor")
        data = data[author_id]
        newData = data[:5]
        newData.append(data[8])
        newData.append(len(coauthorData))
        return newData

    def get_first_author_stats(self, author_name):

        header, data = self.get_number_of_appearance_by_author()
        if self.author_idx.get(author_name) == None:
            return None, None
        author_id = self.author_idx[author_name]
        data = data[author_id]
        newData = data[:5]
        newData.append(sum(newData[1:5]))
        return newData

    def get_last_author_stats(self, author_name):

        header, data = self.get_number_of_appearance_by_author()
        if self.author_idx.get(author_name) == None:
            return None, None
        author_id = self.author_idx[author_name]
        data = data[author_id]
        newData = []
        newData.append(data[0])
        newData += data[5:9]
        newData.append(sum(data[5:9]))
        return newData

    def get_sole_author_stats(self, author_name):

        header, data = self.get_number_of_appearance_by_author()
        if self.author_idx.get(author_name) == None:
            return None, None
        author_id = self.author_idx[author_name]
        data = data[author_id]
        newData = []
        newData.append(data[0])
        newData += data[9:]
        newData.append(sum(data[9:]))
        return newData

    # #gets distance from this author to all the other authors
    # def get_author_distances(self, author_name):
    #     # author_id = self.author_idx[author_name]
    #     author_id = 0
    #     self.distances[author_id] = self.Dijkstra(author_id)
    #     #self.distances[author] = self.Dijkstra(self, author)
    #
    #     return self.distances[author_id]
    #
    #
    # def Dijkstra(self,start,end=None):
    #
    #     #G = self.distances
    #     D = [999 for _ in range(len(self.authors))]
    #     P = self._get_collaborations(start, False).keys()
    #     Q = priorityDictionary()
    #     Q[start] = 0
    #
    #     for v in Q:
    #         D[v] = Q[v]
    #         if v == end: break
    #
    #         for w in self.distances[v]:
    #             vwLength = D[v] + self.distances[v][w]
    #             if w in D:
    #                 if vwLength < D[w]:
    #                     raise ValueError, "Dijkstra Error: Found better in already final Vertex! "
    #             elif w not in Q or vwLength < Q[w]:
    #                 Q[w] = vwLength
    #                 P[w] = v
    #     return D

    def get_plot_data_for_statistic_details(self, data):
        plotted_label = [0 for _ in range(len(data))]
        plotted_data = [[0 for __ in range(len(data))] for _ in range(len(data[0]) - 1)]
        for i in range(len(data)):
            plotted_label[i] = data[i][0]
            for j in range(len(data[0]) - 1):
                plotted_data[j][i] = data[i][j + 1]
        return plotted_label, plotted_data


class DocumentHandler(handler.ContentHandler):
    TITLE_TAGS = [ "sub", "sup", "i", "tt", "ref" ]
    PUB_TYPE = {
        "inproceedings":Publication.CONFERENCE_PAPER,
        "article":Publication.JOURNAL,
        "book":Publication.BOOK,
        "incollection":Publication.BOOK_CHAPTER }

    def __init__(self, db):
        self.tag = None
        self.chrs = ""
        self.clearData()
        self.db = db

    def clearData(self):
        self.pub_type = None
        self.authors = []
        self.year = None
        self.title = None

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startElement(self, name, attrs):
        if name in self.TITLE_TAGS:
            return
        if name in DocumentHandler.PUB_TYPE.keys():
            self.pub_type = DocumentHandler.PUB_TYPE[name]
        self.tag = name
        self.chrs = ""

    def endElement(self, name):
        if self.pub_type == None:
            return
        if name in self.TITLE_TAGS:
            return
        d = self.chrs.strip()
        if self.tag == "author":
            self.authors.append(" ".join(d.rsplit(None,1)[::-1]))
        elif self.tag == "title":
            self.title = d
        elif self.tag == "year":
            self.year = int(d)
        elif name in DocumentHandler.PUB_TYPE.keys():
            self.db.add_publication(
                self.pub_type,
                self.title,
                self.year,
                self.authors)
            self.clearData()
        self.tag = None
        self.chrs = ""

    def characters(self, chrs):
        if self.pub_type != None:
            self.chrs += chrs
