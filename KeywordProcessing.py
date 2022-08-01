import spacy
from rake_nltk import Rake
import yake
import pandas as pd
import nltk
import csv
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from pymongo import MongoClient
from nltk.corpus import wordnet
import numpy as np 

### These three sections of code represent nlp applied to keyword extraction
#https://towardsdatascience.com/keyword-extraction-process-in-python-with-natural-language-processing-nlp-d769a9069d5c

# nlp = spacy.load("en_core_web_sm")
# with open('reviews.txt', 'r', encoding="utf-8") as file:
#     keywords = nlp(file.read())
#     strKeywords = []
#     for keyword in keywords:
#         strKeywords.append(str(keyword))
#     print(set(strKeywords))


# rake_nltk_var = Rake()

# with open('reviews.txt', 'r', encoding="utf-8") as file:
#     rake_nltk_var.extract_keywords_from_text(file.read())
#     keyword_raked = rake_nltk_var.get_ranked_phrases()
#     print(keyword_raked)

def extract_keyword(content): #must be a string
    kw_extractor = yake.KeywordExtractor()
    language = "en"
    max_ngram_size = 20
    duplication_threshold = 0.9
    numOfKeywords = 20
    custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=duplication_threshold, top=numOfKeywords, features=None)
    keywords = custom_kw_extractor.extract_keywords(content)
    return keywords

### these next lines of code will be for nlp applied to sentiment analysis
# https://towardsdatascience.com/7-nlp-techniques-you-can-easily-implement-with-python-dc0ade1a53c2

def sentiment_analysis(content): #must be a dictionary
    sid = SentimentIntensityAnalyzer()
    sentiment = sid.polarity_scores(content)
    return sentiment

def keyword_analysis(review): # Requires a String. The single review will be passed into this function and each keyword will be scored and returned
        # Break paragraph into sentences
        sentanceList = nltk.tokenize.sent_tokenize(review)

        cleanCount = 0
        staffCount = 0
        noiseCount = 0
        lightingCount = 0
        safetyCount = 0
        comfortCount = 0
        smellCount = 0
        
        cleanWordList = synonyms_and_antonyms("clean") 
        staffWordList = synonyms_and_antonyms("staff") 
        noiseWordList = synonyms_and_antonyms("noise") 
        lightingWordList = synonyms_and_antonyms("lighting") 
        safetyWordList = synonyms_and_antonyms("safety") 
        comfortWordList = synonyms_and_antonyms("comfort") 
        smellWordList = synonyms_and_antonyms("smell") 

        for sentance in sentanceList:
            # Rate the keyword Clean
            cleanCount = cleanCount + rate_word(sentance, cleanWordList)

            # Rate the keyword staff
            staffCount = staffCount + rate_word(sentance, staffWordList)

            # Rate the keyword noise
            noiseCount = noiseCount + rate_word(sentance, noiseWordList)
            
            # Rate the keyword lighting
            lightingCount = lightingCount + rate_word(sentance, lightingWordList)

            # Rate the keyword safety
            safetyCount = safetyCount + rate_word(sentance, safetyWordList)

            # Rate the keyword comfort
            comfortCount = comfortCount + rate_word(sentance, comfortWordList)

            # Rate the keyword smell
            smellCount = smellCount + rate_word(sentance, smellWordList)

        featureRating = {
            'clean': cleanCount,
            'staff': staffCount,
            'noise': noiseCount,
            'lighting': lightingCount,
            'safety': safetyCount,
            'comfort': comfortCount,
            'smell': smellCount
        }

        return featureRating
            
def rate_word(sentance, wordList):
    returnInt = 0
    if any(word in sentance for word in wordList):
        sentiment = sentiment_analysis(sentance)
        if sentiment['pos'] > sentiment['neg']:
            returnInt = 1
        elif sentiment['neg'] > sentiment['pos']:
            returnInt = -1
    
    with open("sentances.csv", mode='a', encoding = "utf-8", newline = '') as csv_file:
        sentance_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        wordSet = set(wordList)
        for word in wordSet:
            if word in sentance:
                sentance_writer.writerow([word, sentance])
                break


    return returnInt
            

def synonyms_and_antonyms(word): 
    # next 7 lines taken from https://www.guru99.com/wordnet-nltk.html
    synonyms = []
    antonyms = []
    synonyms.append(word)
    # TODO APPEND THE ACTUAL WORD TO THE ARRAY
    for syn in wordnet.synsets(word):
        for l in syn.lemmas():
            synonyms.append(l.name())
            if l.antonyms():
                antonyms.append(l.antonyms()[0].name())
    
    return np.concatenate((synonyms, antonyms))