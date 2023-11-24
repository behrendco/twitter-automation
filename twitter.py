import tweepy
import time
import random
import requests
import json
import progressbar
from PIL import Image, ImageDraw, ImageFont

# Account info/API credentials
ACCOUNT_HANDLE = ""
API_KEY = ""
API_SECRET = ""
ACCESS_KEY = ""
ACCESS_SECRET = ""

# Get random motivational quote and author from Zenquotes
def getQuote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    return json_data[0]["q"].strip(), json_data[0]["a"].strip()

# Create image of quote text using the quote and author
def createImage(quote, author):
    x1, y1 = 612, 612
    fnt = ImageFont.truetype("Cinzel-Regular.ttf", 30)
    img = Image.new("RGB", (x1, y1), color = (0, 0, 0))
    d = ImageDraw.Draw(img)

    sum = 0
    for letter in quote:
        sum += d.textsize(letter, font=fnt)[0]

    avg_letter_len = sum / len(quote)
    letters_per_line = (x1 / 1.618) / avg_letter_len
    
    sentence = '"'
    i = 0
    for letter in quote:
        if i < letters_per_line or letter != " ":
            sentence += letter
        else:
            sentence += "\n"
            i = 0
        i += 1
        
    sentence += '"\n\n{0} '.format(u'\u2014')
    i = 0
    for letter in author:
        if i < letters_per_line or letter != " ":
            sentence += letter
        else:
            sentence += "\n"
            i = 0
        i += 1
    
    dim = d.textsize(sentence, font = fnt)
    x2 = dim[0]
    y2 = dim[1]
    qx = (x1/2 - x2/2)
    qy = (y1/2 - y2/2)
    d.text((qx, qy), sentence, align = "center", font = fnt, fill = (255, 255, 255))
    img.save("quote.png")

# Send a photo Tweet using the generated quote text image
def tweetPhoto(api):
    try:
        quote, author = getQuote()
        createImage(quote, author)
        api.update_status_with_media(status = "", filename = "quote.png")
        print("Tweeted Photo")
    except:
        print("Error Tweeting Photo")

# Send a text Tweet using the retrieved quote and author
def tweetQuote(api):
    try:
        quote, author = getQuote()
        author = "@elonmusk" if author == "Elon Musk" else author
        author = "@naval" if author == "Naval Ravikant" else author
        api.update_status('"' + quote + '"\n\n{0} '.format(u'\u2014') + author)
        print("Tweeted Quote")
    except:
        print("Error Tweeting Quote")

# Automate engagement with users who follow accounts that we also follow
def likeTweets(api):  
    count = 0
    attempts = 0
    consec_fails = 0

    friends = []
    for page in tweepy.Cursor(api.get_friends, screen_name = ACCOUNT_HANDLE, count = 100).pages():
        friends.extend(page)
    target_user = random.choice(friends).screen_name
        
    followers = tweepy.Cursor(api.get_followers, screen_name = target_user).items(250)
    run = True
    success = False
    print("Liking Tweets by users following @" + target_user + "...")
    with progressbar.ProgressBar(max_value = 250) as bar:
        while run:
            try:
                user = next(followers)
            except StopIteration:
                success = True
                break
            except:
                break
            
            try:
                tweet = api.user_timeline(user_id = user.id)[0]
                api.create_favorite(tweet.id)
                count += 1
                consec_fails = 0
            except:
                consec_fails += 1
                if consec_fails >= 10:
                    run = False

            time.sleep(5)
            attempts += 1
            bar.update(attempts)

    if success:
        print("Liked " + str(count) + " / " + str(attempts) + " Tweets")
    else:
        print("Error: Liked " + str(count) + " / " + str(attempts) + " Tweets")

# Twitter authentication
def twitterAPI():
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    print("Logged into Twitter as @" + ACCOUNT_HANDLE)
    return tweepy.API(auth)

# Growth tasks automation
def automateEngagement():
    api = twitterAPI()
    rand = random.randrange(6)
    if rand == 0:
        tweetPhoto(api)
    else:
        tweetQuote(api)
    likeTweets(api)

if __name__ == "__main__":
    automateEngagement()