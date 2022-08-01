from nturl2path import url2pathname
from matplotlib.pyplot import text
from requests import get
from bs4 import BeautifulSoup as soup 
from random import randint
from time import sleep
from pymongo import MongoClient
from pprint import pprint
import os
import sys
import inspect
import time

# Next 4 lines taken from https://stackoverflow.com/questions/714063/importing-modules-from-parent-folder   -user Remi
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
#import KeywordProcessing as kp

start_time = time.time()

# This loop scrapes the first 10 pages of hotels from the below "url"
pages = ["", "oa30-", "oa60-", "oa90-", "oa120-", "oa150-", "oa180-", "oa210-", "oa240-", "oa270-"]

for page in pages:

  headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36 OPR/87.0.4390.45'}
  url = 'https://www.tripadvisor.in/Hotels-g187147{pageKey}Paris_Ile_de_France-Hotels.html'.format(pageKey = page)

  html = get(url, headers=headers, timeout=10, allow_redirects=True)
  bsobj = soup(html.content,'lxml')
  links = []

  # This loop scrapes the first 2 pages of reviews for each hotel
  # Basically reviews from the last month
  pages = ["", "10", "20", "30", "40", "50", "60", "70", "80", "90"]
  for review in bsobj.findAll('a',{'class':'review_count'}):
      for page in pages:
          a = review['href']
          a = 'https://www.tripadvisor.in'+ a
          a = a[:(a.find('Reviews')+7)] + '-or{pageKey1}'.format(pageKey1 = page) + a[(a.find('Reviews')+7):]
          print(a)
          links.append(a)
  reviews = []

  # Connect To Mondo and Write To A Database and Collection
  client = MongoClient()
  db = client.HotelReviews
  collection = db.reviews1

  for link in links:
      d = [5,10,15,20,25]
      headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}
      html2 = get(link.format(i for i in range(5,1000,5)),headers=headers)
      sleep(randint(1,5))
      bsobj2 = soup(html2.content,'lxml')
      hotelName = bsobj2.find(id='HEADING')
      city = bsobj2.find(class_='jcHgx Ci')
      for name, contribution, rating, title, review, trip_type in zip(bsobj2.findAll("a", {"class": "kjIqZ I ui_social_avatar inline"}), bsobj2.findAll(class_="yRNgz"), bsobj2.findAll(class_='ui_bubble_rating'), bsobj2.findAll(class_="KgQgP MC _S b S6 H5 _a"), bsobj2.findAll('q'), bsobj2.findAll(class_="TDKzw _R Me")):
        try:
          reviews.append(review.span.text.strip())

          cleanedReview = " ".join((title.span.text.strip(), review.span.text.strip()))
          result = collection.insert_one(
            {
              'Name' : str(name.attrs['href'])[9:],
              'Contributions' : contribution.text,
              'Rating': rating.attrs['class'][1].replace('bubble_', ''),
              'Review' : cleanedReview,
              'TripType' : trip_type.text,
              ###
              'HotelName' : hotelName.text,
              'City' : city.text
            }
          )
        except:
          result = collection.insert_one(
            {
              'Name' : str(name.attrs['href'])[9:],
              'Contributions' : contribution.text,
              'Rating': rating.attrs['class'][1].replace('bubble_', ''),
              'Review' : "",
              'TripType' : trip_type.text,
              ###
              'HotelName' : hotelName.text,
              'City' : city.text
            }
          )  
        
print("time taken: " + str((time.time() - start_time)))   
### portions of the code were taken from https://www.worthwebscraping.com/scrape-tripadvisor-reviews-using-python/
### Credit worthwebscraping.com

# with open('reviews.csv', 'w', encoding="utf-8") as file:
#   for review in reviews:
#     file.write(review + "\n")


