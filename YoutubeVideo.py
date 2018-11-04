import os
import json
import math

import io
import matplotlib.pyplot as plt
import numpy as np

from urllib.request import urlopen
from collections import Counter
from PIL import Image
from os import path
from wordcloud import WordCloud, STOPWORDS
from sklearn.feature_extraction.text import CountVectorizer

from apiclient.discovery import build_from_document,build
from apiclient.errors import HttpError


class YoutubeVideo:
    """
    YoutubeVideo class contains different attributes and methods
    for doing some statistics on youtube comment
    """

    def __init__(self, video_id):
        """
        get comments from youtube and save them
        comments are stored in a json file
        """
        self.video_id = video_id

        # some Youtube API INFO
        YOUTUBE_API_SERVICE_NAME = "your_api_here"
        YOUTUBE_API_VERSION = "v3"
        DEVELOPER_KEY = "developer_key_here"

        try:
            # if json file of the main video exists no need to dump the comments again
            if not os.path.exists(video_id + '.json'):
                youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
                self.video_comment_threads = self.get_comment_threads(youtube, self.video_id)
        except HttpError as e:
            print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
        else:
            print("listed !")

        # save comments in a txt file analyzing
        self.saveCommentsToFile()

        # number of comments of a youtube video
        self.comments_count = self.getCommentsCount()



    # Call the API's commentThreads.list method to list the existing comment threads.
    def get_comment_threads(self,youtube, video_id):

        results = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            textFormat="plainText",
            maxResults=100
        ).execute()

        # get replies of the comment
        for item in results["items"]:
            if item['snippet']['totalReplyCount'] > 0:
                parent_id = item['id']
                self.get_comments(youtube, parent_id,video_id)
            # save comments in json file
            with open( video_id + '.json', 'a') as fp:
                json.dump(item, fp)
                fp.write('\n')
            print(item)

        # go to next page and get the other comments
        while ("nextPageToken" in results):
            results = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                pageToken=results["nextPageToken"],
                textFormat="plainText",
            ).execute()

            # get replies of the comment
            for item in results["items"]:
                if item['snippet']['totalReplyCount'] > 0:
                    parent_id = item['id']
                    self.get_comments(youtube, parent_id, video_id)

                comment = item["snippet"]["topLevelComment"]
                with open( video_id + '.json', 'a') as fp:
                    json.dump(item, fp)
                    fp.write('\n')
                print(item)

        return results["items"]

    # Call the API's comments.list method to list the existing comment replies.
    def get_comments(self,youtube, parent_id,video_id):
        results = youtube.comments().list(
            part="snippet",
            parentId=parent_id,
            textFormat="plainText",
            maxResults=100
        ).execute()
        # save replies in json file
        for item in results["items"]:
            with open( video_id + '.json', 'a') as fp:
                json.dump(item, fp)
                fp.write('\n')
            print(item)

        return results["items"]


    def getCommentsCount(self):
        # get number of comments of a file

        count = 0
        with open(self.video_id+ ".json", 'r') as fp:
            for line in fp:
                count += 1

        return count

    def getTopFirstQuartile(self):

        comment_tuple = list()

        with open(self.video_id + ".json", 'r') as fp:

            # make list of tuples : name,comment,likecount and plublication date
            for line in fp:
                comment = json.loads(line)
                if comment['kind'] == 'youtube#commentThread':
                    snippet = comment['snippet']['topLevelComment']['snippet']
                    comment_tuple.append((snippet['authorDisplayName'],
                                          snippet['textOriginal'],
                                          snippet['likeCount'],
                                          snippet['publishedAt']))

        # sort the list by likeCount
        comment_tuple = sorted(comment_tuple, key=lambda tup: tup[2], reverse=True)

        # limit for 25%
        stop = int(math.floor(self.comments_count / 4))

        comment_tuple2 = list()

        for line in comment_tuple[0:stop]:
            if line[2] != 0 and line[2] != None:
                comment_tuple2.append(line)
        return comment_tuple2

    def saveCommentsToFile(self):
        """ save comments in a text file """

        with open(self.video_id + '_words.txt', "w") as lf:
            with open(self.video_id + '.json', "r") as sf:
                for line in sf:

                    comment_thread = json.loads(line)
                    if comment_thread['kind'] == 'youtube#commentThread':
                        comment_text = comment_thread['snippet']['topLevelComment']['snippet']['textOriginal']
                        lf.write("%s\n" % comment_text.encode('UTF-8'))


    def getFreqDistribution(self):
        """ get frequency distribution of comments """


        # define stopwords to delete from the frequency distribution list
        stopwords = set(map(str.lower, STOPWORDS))

        ngram_vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 1), min_df=1)

        with io.open(self.video_id + '_words.txt', 'r', encoding='utf8') as fin:

            X = ngram_vectorizer.fit_transform(fin)
            vocab = ngram_vectorizer.get_feature_names()
            counts = X.sum(axis=0).A1
            freq_distribution_list = zip(vocab, counts)
            freq_distribution = list()

            for element in freq_distribution_list:
                if element[0].lower() not in stopwords:
                    # add to list
                    freq_distribution.append(element)

            freq_distribution = Counter(dict(freq_distribution))

        return freq_distribution

    def getWordFreqAndMean(self):
        """ get word frequency and mean """
        #word to lookup for
        word = input("give a word : ")

        # frequency distrubition counter
        freq_count = 0

        with open(self.video_id + '_words.txt', "r") as fp:
            for line in fp:
                if word.lower() in line:
                    freq_count += 1

        if freq_count == 0:

            return word, freq_count, float(0)
        else:
            return word, freq_count, float(freq_count)/float(self.comments_count)


    def getProbaTwoTerms(self):
        """ this method calculates the probability of word 1 given that word2 exists"""
        word1 = input("give first word : ")
        word2 = input("give second word : ")

        word1And2Count = 0
        word2Count = 0

        with open(self.video_id + '_words.txt', "r") as fp:
            for line in fp:
                if word1 in line and word2 in line:
                    word1And2Count += 1
                if word2 in line:
                    word2Count += 1

            if word2Count == 0:
                return (word1, word2, float(0))
            else:
                return (word1,word2,float(word1And2Count) / float(word2Count))

    def genderClassify(self):
        """ classify gender by name"""

        # API key for gender classifier gender-api.com
        myKey = "FnganytQWZZavexctb"

        male_count = 0
        female_count = 0
        other_count = 0

        with open(self.video_id + '.json', "r") as fp:
            for line in fp:
                comment = json.loads(line)
                if comment['kind'] == 'youtube#commentThread':
                    name = comment['snippet']['topLevelComment']['snippet']['authorDisplayName']

                    firstname = name.split(" ")[0]

                    url = "https://gender-api.com/get?key=" + str(myKey)+ "&name=" +str(firstname.encode('utf-8'))

                    response = urlopen(url)

                    decoded = response.read().decode('utf-8')

                    data = json.loads(decoded)

                    if data["gender"] == 'male':
                        male_count += 1
                    elif data["gender"] == 'female':
                        female_count += 1
                    else:
                        other_count += 1

                    print("Gender: " + data["gender"])  # Gender: male
                total =  male_count + female_count + other_count
                if total >= 30:
                    break


        return {'male':float(male_count)*100/float(total),
                'female':float(female_count)*100/float(total),
                'unknown':float(other_count)*100/float(total)}


    def drawWordCloud(self):

        """ draw wordcloud """
        # get frequency distribution
        freq_distribution = self.getFreqDistribution()

        d = path.dirname(__file__)

        mask = np.array(Image.open(path.join(d, "oyiqfxojyqrnsi1pcj24.png")))

        wc = WordCloud(max_words=1000,
                       mask=mask,
                       margin=10,
                       random_state=1).generate_from_frequencies(freq_distribution)

        # store default colored image
        default_colors = wc.to_array()

        wc.to_file(self.video_id + ".png")

        plt.title("Words Frequency")
        plt.imshow(default_colors, interpolation="bilinear")
        plt.axis("off")
        plt.show()








