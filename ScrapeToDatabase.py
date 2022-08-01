from nturl2path import url2pathname
from matplotlib.pyplot import text
import requests
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
import KeywordProcessing as kp

start_time = time.time()

pages = ["", "oa30-", "oa60-", "oa90-", "oa120-", "oa150-", "oa180-", "oa210-", "oa240-", "oa270-"]
reviewPages = ["", "10", "20", "30"]

for page in pages:

  headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36 OPR/87.0.4390.45'}
  url = 'https://www.tripadvisor.in/Hotels-g187147-{pageKey}Paris_Ile_de_France-Hotels.html'.format(pageKey = page)

  html = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
  bsobj = soup(html.content,'lxml')
  links = []


  ### TODO this script only grabs the first pages of review for each hotel. 
  for review in bsobj.findAll('a',{'class':'review_count'}):
    for reviewPage in reviewPages:
      a = review['href']
      a = 'https://www.tripadvisor.in'+ a
      a = a[:(a.find('Reviews')+7)] + '-or{reviewPageKey}'.format(reviewPageKey = reviewPage) + a[(a.find('Reviews')+7):]
      print(a)
      links.append(a)

  reviews = []
  # connect to mondo database and write values
  client = MongoClient()
  db = client.HotelReviews
  collection = db.reviews

  for link in links:
      d = [5,10,15,20,25]
      headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}
      html2 = requests.get(link.format(i for i in range(5,1000,5)),headers=headers)
      sleep(randint(1,5))
      bsobj2 = soup(html2.content,'lxml')
      hotelName = bsobj2.find(id='HEADING')
      for review, rating, reviewer, dateOfStay in zip(bsobj2.findAll('q'), bsobj2.findAll(class_='ui_bubble_rating'), bsobj2.findAll("a", {"class": "kjIqZ I ui_social_avatar inline"}), bsobj2.findAll("span",{"class": "teHYY _R Me S4 H3"})):
          reviews.append(review.span.text.strip())
          #### TODO the ratings are off. Not sure why, but I believe it is because there must be a ui_bubble_rating higher up in the doc that is getting pulled
          cleanedReview = review.span.text.strip()
          sentiment = kp.sentiment_analysis(cleanedReview)
          result = collection.insert_one(
            {
              'Review':cleanedReview,
              #'Keywords':kp.extract_keyword(cleanedReview),
              #'Rating':rating.attrs['class'][1].replace('bubble_', ''),
              'HotelName': hotelName.text,
              #'positive': sentiment['pos'],
              #'negative': sentiment['neg'],
              #'neutral': sentiment['neu'],
              'featureRatings': kp.keyword_analysis(cleanedReview),
              'Reviewer': str(reviewer.attrs['href'])[9:],
              'dateOfStay': dateOfStay.text[14:]
            }
          )

        
        
print("time taken: " + str((time.time() - start_time)))   
### portions of the code were taken from https://www.worthwebscraping.com/scrape-tripadvisor-reviews-using-python/
### Credit worthwebscraping.com


        
# with open('reviews.csv', 'w', encoding="utf-8") as file:
#   for review in reviews:
#     file.write(review + "\n")

