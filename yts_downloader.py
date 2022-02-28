import re
import argparse
import requests
from bs4 import BeautifulSoup
from sys import argv

TORRENT_FILE = "torrents"
NAME_FILE = "movies.txt"

TORRENTS = []

def get_torrents(url, t):
	try:
		r = requests.get(url, timeout=7)
	except requests.Timeout:
		print('Request timeout')
		return None
	else:
		torrents = {}
		torrents.update({'title':t})
		torrents.update({'year': url[-4:]})
		soup = BeautifulSoup(r.text, 'html.parser')
		links = soup.find_all('a');
		for link in links:
			title = link.get('title')
			if title:
				if t in title and 'Torrent' in title and not 'BluRay' in title: 
					tor = link.get('href')[link.get('href').rfind("/")+1:]
					res = re.search(r"(\d+)p", title)
					if res:
						res = res.group(1)
						torrents.update({res:{}})
						torrents[res].update({'link': tor})
						torrents[res].update({'url': link.get('href')})
		return torrents

def addTorrent(torrent):
	keys = list(torrent.keys())

	if '1080' in keys:
		return torrent['1080']['link']
	elif '720' in keys:	
		return torrent['720']['link']
	else:
		return ""

def addNames(names):
	films = open(NAME_FILE, "r").read().splitlines()
	for name in names:
		if not name in films:
			films.append(name)
			print("{} added to films".format(name))
		else:
			print("{} already in films".format(name))

	open(NAME_FILE, "w").write('\n'.join(films)+'\n')

def addTorrents(torrents):
	films = open(TORRENT_FILE, "r").read().splitlines()
	for name in torrents:
		if not name in films:
			print("added torrent: ", name)
			films.append(name)

	open(TORRENT_FILE, "w").write('\n'.join(films)+'\n')

def doSomething(torrents):
	for i,movie in enumerate(torrents):
		print("{0} : {1} - {2}".format(len(torrents)-i, movie['title'], movie['year']))
	
	if len(torrents) == 1:
		choices = [0]
	else:
		choices = [len(torrents)-int(s) for s in input("please select films to add (numbers separated by a space ex: 1 2 4) : ").split(" ")]
	names_to_add = []
	torrents_to_add = []
	for i in choices:
		print("added {}".format(torrents[i]['title']))
		names_to_add.append(torrents[i]['title'])
		torrents_to_add.append(addTorrent(torrents[i]))
	#addNames(names_to_add)
	#addTorrents(torrents_to_add)
	for t in torrents_to_add: TORRENTS.append(t)

	print("\n")

def main(movie):
	films = open(NAME_FILE, "r").read().splitlines()
	if movie in films:
		print(movie, " already added")
		return 0
	movie_name = movie.replace(' ', '%20')
	URL = 'https://yts.mx/browse-movies/{}/all/all/0/latest/0/all'.format(movie_name)
	try:
		r = requests.get(URL, timeout=7, params={'limit':50,'movie_count':50})
	except requests.Timeout:
		print('Request timeout')
	else:
		torrents = []
		soup = BeautifulSoup(r.text, 'html.parser')

		h2 = soup.find_all('h2')
		number_search = re.search(r"(<b>)(.*)(</b>)", str(h2))
		if number_search:
			number_of_films = int(number_search.group(2).replace(",", ""))
			print("Found {} films matching {}".format(number_of_films, movie))
			if number_of_films == 0:
				return 0
		else:
			print("can't find number of films")
			print(h2)
			return 0
		
		page = 1
		limit=20

		while  page < number_of_films / limit + 1:
			titles = soup.find_all(class_="browse-movie-title")
			if titles:
				for t in titles:
					href_search = re.search(r"href=\"(.*)\"", str(t))
					if href_search: url = href_search.group(1)
					torrents.append(get_torrents(url, t.text))

			page += 1
			payload = {
				'limit': limit,
				'page': page
			}
			r = requests.get('https://yts.mx/browse-movies/{}/all/all/0/latest/0/all'.format(movie_name), timeout=7, params=payload)
			soup = BeautifulSoup(r.text, 'html.parser')

		doSomething(torrents)
	return 0

def files(movies):
	films = open(movies, "r").read().splitlines() 
	for f in films:
		if f != "":
			if f[0] != '"':
				main(f)

# Uncomment this for testing
if __name__ == "__main__":
	if len(argv) > 1:
		for i in range(1, len(argv), 2):
			if argv[i] == '-s':
				main(argv[i+1])
			if argv[i] == '-f':
				files(argv[i+1])


	else:
		while True:
			i = input("Film: ")
			if i == "exit" or i == "quit" or i == "q":
 				break	
			main(i)

	for t in TORRENTS:
		print(t)

# vim:tabstop=4:shiftwidth=4:noexpandtab
