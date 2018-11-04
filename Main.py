#Usage example:
# python comments.py --videoid='<video_id>'

from YoutubeVideo import YoutubeVideo
from oauth2client.tools import argparser



if __name__ == "__main__":

    # The "videoid" option specifies the YouTube video ID that uniquely
    # identifies the video for which the comment will be inserted.
    argparser.add_argument("--videoid",
                           help="Required; ID for video for which the comment will be inserted.")

    args = argparser.parse_args()

    yvideo1 = YoutubeVideo(args.videoid)


    print("=================== Q1 =====================")
    print("number of comments : {} ".format(yvideo1.comments_count))
    print("============================================")

    print("=================== Q2 =====================")
    top25percent = yvideo1.getTopFirstQuartile()
    for comment in top25percent:
        print('--------------------------------')
        print(comment[0] + " ( "+ str(comment[2]) + " LIKE ) : " + comment[1])
    print("============================================")


    print("=================== Q3 =====================")
    most_common_words =  yvideo1.getFreqDistribution().most_common(10)
    for line in most_common_words:
        print("word {} is repeated {} times.".format(line[0],line[1]))
    print("============================================")


    print("=================== Q4 =====================")
    word_and_freq = yvideo1.getWordFreqAndMean()
    print("word ({}) is repeated {} times, with mean : {:f}".format(word_and_freq[0],word_and_freq[1],word_and_freq[2]))
    print("============================================")


    print("=================== Q5 =====================")
    word12prob = yvideo1.getProbaTwoTerms()
    print("Probability of {} given {} exists is : {:f}".format(word12prob[0],word12prob[1],word12prob[2]))
    print("============================================")


    print("=================== Q6 =====================")

    print("============================================")
    print("Drawing Word Cloud")
    yvideo1.drawWordCloud()

    gender = yvideo1.genderClassify()

    print("Gender Classification result : ")
    print("Male    : {0:.2f} %".format(gender['male']))
    print("Female  : {0:.2f} %".format(gender['female']))
    print("Unknown : {0:.2f} %".format(gender['unknown']))
