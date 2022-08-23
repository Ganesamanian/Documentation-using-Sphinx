#!/usr/bin/env python -tt
# coding: utf-8


# Importing the Libraries
import sqlite3
from myapp.models import *
from neomodel import db
import re

# Function to webscrappe the EuroNcap webpage
def web_scrapping():

    conn = sqlite3.connect('index_EN.sqlite')
    cur = conn.cursor()

    cur.execute('''DROP TABLE IF EXISTS Car ''')
    cur.execute('''DROP TABLE IF EXISTS Brand ''')
    cur.execute('''DROP TABLE IF EXISTS Year ''')
    cur.execute('''DROP TABLE IF EXISTS Star ''')

    cur.execute('''DROP TABLE IF EXISTS ResultAll ''')
    cur.execute('''DROP TABLE IF EXISTS Pedestrian ''')
    cur.execute('''DROP TABLE IF EXISTS SafetyAssist ''')

    cur.execute('''CREATE TABLE IF NOT EXISTS Car
        (id INTEGER PRIMARY KEY, model TEXT UNIQUE, year_id INTEGER, 
        brand_id INTEGER, star_id INTEGER, url TEXT UNIQUE)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS Brand
        (id INTEGER PRIMARY KEY, name TEXT UNIQUE)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS Year
        (id INTEGER PRIMARY KEY, year TEXT UNIQUE)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS Star
        (id INTEGER PRIMARY KEY, Star TEXT UNIQUE)''')


    conn_1 = sqlite3.connect('file:spiderEN.sqlite?mode=ro', uri=True)
    cur_1 = conn_1.cursor()

    allsenders = list()
    cur_1.execute('''SELECT url,html FROM Pages''')
    
    return cur_1


# Function to remove the unwanted url
def link_screening(link_end, links, prefix):

    """
        Function to clean the urls from the list

        Inputs:
            link_end: gives the end of the main link
                      to match the start of the next
                      link
            links   : list of urls
            prefix  : main url with http

        Return:
            Collection: List of cleaned links


    """

    collection = []

    for link in links:

        # Example "en/about euroncap/"
        look_for_end = str(link).find("/"+link_end, 0, 3)
        look_for_https =  str(link).find("https", 0, 5)
        
        if look_for_end==0:
            # Example "http://www.euroncap.com/en/about euroncap/"
            collection.append(prefix[0:-4]+link)
        
        if look_for_https==0:
            collection.append(link)

    # Set is used to remove duplicates
    return set(collection)


# Function to establish connection between pages
# in Neo4j as nodes
def graph(data):

    """
        This function used to create knowledge graph
        as same as the EuroNcap webpages

        Input:
            Data: Webpage url along with the data
                  of the page in html format

        Return: 
            Nothing creates the graph in Neo4j
            database


    """

    # Variable Declaration
    URLS = []
    HTMLS = []    
    created_URLS = []

    # Main loop
    for URL,HTML in data:

        # Add "/" at the end of the url
        # as the url in html ends with "/"
	    URLS.append(URL+"/")
	    HTMLS.append(HTML)
    
    # Created range for debugging    
    urls = URLS[0:400]
    htmls = HTMLS[0:400]	 

    # Loop for debugging
    for url, html in zip(urls,htmls):
        
        # Query the databse to find if the node already exists
        query = db.cypher_query("MATCH (a:Page) WHERE a.page_url = \""+ str(url)+"\" RETURN True") 

        # Node doesn't exists already
        if url not in created_URLS and query[0] == []:
            
            created_URLS.append(url)
            end_url = url.split("/")[-2 if url.split("/")[-1]== '' else -1 ]
            current_page = Page(page_name= end_url, page_url=url).save()

            # Get all the nodes in database at present
            all_nodes = Page.nodes.all()

            # Get the previous page from current page
            url_split = url.split("/")
            url_split.remove('')
            url_split[0] = url_split[0]+"/"
            prev_url = '/'.join([str(elem) for elem in url_split[0:-2]])

            # query if the previous url is valid and exists
            query = db.cypher_query("MATCH (a:Page) WHERE a.page_url = \""+ str(prev_url)+"/\" RETURN True")
            
            # If the previous page exists connect to the current page
            if query[0] !=[]:

                previous_page = Page.nodes.get(page_url=prev_url+"/")
                current_page.relation.connect(previous_page)             


            # Extract links/url from the html of the current page
            raw_links = re.findall(r'href=[\'"]?([^#\'" >]+)', str(html))
            cleaned_links = link_screening(end_url, raw_links, url)
            

            # Connect the extracted links to current page
            for link in cleaned_links:            
                if link in URLS and link.find(url)==0 and len(link.split("/"))==len(url.split("/"))+1 and link not in created_URLS:

                    created_URLS.append(link)
                    next_page = Page(page_name=link.split("/")[-2 if link.split("/")[-1]== '' else -1 ], page_url=link).save()
                    next_page.relation.connect(current_page)
                    
            

        # Node exists already        
        else:  
            
            # Query and get the node/page
            node = (db.cypher_query("MATCH (a:Page) WHERE a.page_url = \""+ str(url)+"\" RETURN a.page_name, a.page_url"))[0][0]
            all_nodes = Page.nodes.all()
            existing_page = Page.nodes.get(page_name=node[0])
            
            raw_links = re.findall(r'href=[\'"]?([^#\'" >]+)', str(html))
            cleaned_links = link_screening(end_url, raw_links, url)
            

            for link in cleaned_links:            
                if link in URLS and link.find(url)==0 and len(link.split("/"))==len(url.split("/"))+1 and link not in created_URLS:

                    created_URLS.append(link)
                    next_page = Page(page_name=link.split("/")[-2 if link.split("/")[-1]== '' else -1 ], page_url=link).save()
                    next_page.relation.connect(existing_page)
                    
    return 	 
		


if __name__ == '__main__':

    # Webscrape the EuroNcap webpage
    data = web_scrapping()

    # Establish the connection with Neo4j
    db.set_connection('bolt://neo4j:Minion1$@localhost:7687')
    
    # Delete all the existing nodes
    db.cypher_query("MATCH (n) DETACH DELETE n")
    
    # Main Function to connect the nodes
    graph(data)

    

    

  



