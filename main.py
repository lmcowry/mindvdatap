import webapp2, jinja2, os, random
from google.appengine.ext import db
from models import AnswerObj4, GuessObj
import time


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)
listOfGuesses = []



def aColorValidator(guess):
    approvedGuesses = ["b", "r", "g", "c", "m", "y"]

    if guess in approvedGuesses:
        return True
    else:
        return False

def cssColorMaker(aGuess):

    for spotNum in ["spot0", "spot1", "spot2", "spot3"]:
        if getattr(aGuess, spotNum) == "r":
            colorText = "background:red"
        elif getattr(aGuess, spotNum)  == "g":
            colorText = "background:green"
        elif getattr(aGuess, spotNum)  == "b":
            colorText = "background:blue"
        elif getattr(aGuess, spotNum)  == "c":
            colorText = "background:cyan"
        elif getattr(aGuess, spotNum)  == "y":
            colorText = "background:yellow"
        elif getattr(aGuess, spotNum)  == "m":
            colorText = "background:magenta"
        setattr(aGuess, "color{0}".format(spotNum), colorText)

    aGuess.put()


def colorCodeSearcher(color):
    # this will count all total rs in the database, not just each code with a r in the database
    totalCount = 0
    totalCount += AnswerObj4.all().filter("spot0", color).filter("answered", False).count()
    totalCount += AnswerObj4.all().filter("spot1", color).filter("answered", False).count()
    totalCount += AnswerObj4.all().filter("spot2", color).filter("answered", False).count()
    totalCount += AnswerObj4.all().filter("spot3", color).filter("answered", False).count()
    return totalCount


def randomAnswerMaker():
    # this will create one random answer and make sure that it's different from the other answers
    approvedGuesses = ["b", "r", "g", "c", "m", "y"]

    answerAt0 = random.choice(approvedGuesses)
    answerAt1 = random.choice(approvedGuesses)
    answerAt2 = random.choice(approvedGuesses)
    answerAt3 = random.choice(approvedGuesses)
    answerPegList = [answerAt0, answerAt1, answerAt2, answerAt3]

    if AnswerObj4.all().filter("spot0", answerAt0).filter("spot1", answerAt1).filter("spot2", answerAt2).filter("spot3", answerAt3).count() > 0:
        return randomAnswerMaker()
    theAnswer = AnswerObj4(spot0 = answerAt0, spot1 = answerAt1, spot2 = answerAt2, spot3 = answerAt3, answered = False)
    return theAnswer


def lastCorrectAnswer(theGuess):
    # checks if this guess is guessing the last answer
    if correctAnswer(theGuess) and AnswerObj4.all().filter("answered", False).count() == 0:
        return True
    return False


def correctAnswer(theGuess):
    # checks if the guess is a correct answer
    thisMatchesTheGuess = AnswerObj4.all().filter("spot0", theGuess.spot0).filter("spot1", theGuess.spot1).filter("spot2", theGuess.spot2).filter("spot3", theGuess.spot3).filter("answered", False)
    if thisMatchesTheGuess.count() > 0:
        theDbObject = thisMatchesTheGuess.fetch(limit=1)
        # have to do this awkward [0] bullshit because ^ returns a list
        theDbObject[0].answered = True
        theDbObject[0].put()
        return True
    else:
        return False

def firstThreeGiver(first, second, third):
    # gives a clue as to whether the user's first three colors in the guess match any answers
    codesWithFirstThreeLikeThis = AnswerObj4.all().filter("spot0", first).filter("spot1", second).filter("spot2", third).filter("answered", False)
    howMany = codesWithFirstThreeLikeThis.count()
    return str(howMany)

def firstTwoGiver(first, second):
    # gives a clue as to whether the user's first two colors in the guess match any answers
    codesWithFirstTwoLikeThis = AnswerObj4.all().filter("spot0", first).filter("spot1", second).filter("answered", False)
    howMany = codesWithFirstTwoLikeThis.count()
    return str(howMany)

def clueGiver(theGuess):
    # creates a clue for each guess
    # checks for colors exactly in those spots for the ! clue
    # checks for colors not in those spots for the ? clue

    theseMatchSpot0 = AnswerObj4.all().filter("spot0", theGuess.spot0).filter("answered", False).count()
    theseMatchSpot1 = AnswerObj4.all().filter("spot1", theGuess.spot1).filter("answered", False).count()
    theseMatchSpot2 = AnswerObj4.all().filter("spot2", theGuess.spot2).filter("answered", False).count()
    theseMatchSpot3 = AnswerObj4.all().filter("spot3", theGuess.spot3).filter("answered", False).count()

    if theseMatchSpot0 > 0:
        sendThisString = "{0}!".format(theseMatchSpot0)
        theGuess.clue0 = sendThisString
    else:
        howMany = colorCodeSearcher("c")
        sendThisString = "{0}?".format(colorCodeSearcher(theGuess.spot0))
        theGuess.clue0 = sendThisString

    if theseMatchSpot1 > 0:
        sendThisString = "{0}!".format(theseMatchSpot1)
        theGuess.clue1 = sendThisString
    else:
        sendThisString = "{0}?".format(colorCodeSearcher(theGuess.spot1))
        theGuess.clue1 = sendThisString

    if theseMatchSpot2 > 0:
        sendThisString = "{0}!".format(theseMatchSpot2)
        theGuess.clue2 = sendThisString
    else:
        sendThisString = "{0}?".format(colorCodeSearcher(theGuess.spot2))
        theGuess.clue2 = sendThisString

    if theseMatchSpot3 > 0:
        sendThisString = "{0}!".format(theseMatchSpot3)
        theGuess.clue3 = sendThisString
    else:
        sendThisString = "{0}?".format(colorCodeSearcher(theGuess.spot3))
        theGuess.clue3 = sendThisString

class SuperHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class DeletePageHandler(SuperHandler):
    def render_front(self):
        self.render("deletePage.html")

    def get(self):
        self.render_front()

    def post(self):
        # although this works, it wouldn't work with more than 20 answers.  refactor
        theAnswerObj4List = AnswerObj4.all().fetch(limit=20)
        for anAnswer in theAnswerObj4List:
            anAnswer.delete()
        #same here
        theGuessObjList = GuessObj.all().fetch(limit=100)
        for aGuess in theGuessObjList:
            aGuess.delete()

        # gets rid of all the past guesses
        howMany = len(listOfGuesses)
        for x in range(howMany):
            listOfGuesses.pop()

        self.redirect("/")


class AddPageHandler(SuperHandler):
    def render_front(self):
        self.render("addPage.html")

    def get(self):
        self.render_front()

    def post(self):
        random1 = randomAnswerMaker()
        random1.put()
        random2 = randomAnswerMaker()
        random2.put()
        random3 = randomAnswerMaker()
        random3.put()
        random4 = randomAnswerMaker()
        random4.put()
        random5 = randomAnswerMaker()
        random5.put()




        self.redirect("/")

class MainPageHandler(SuperHandler):

    def render_front(self, guessAt0="", guessAt1="", guessAt2="", guessAt3="", error="", firstThree="", firstTwo=""):

        self.render("theModel.html", guessAt0=guessAt0, guessAt1=guessAt1, guessAt2=guessAt2, guessAt3=guessAt3, error=error, firstThree="", firstTwo="", listOfGuesses=listOfGuesses)

    def get(self):
        self.render_front()

    def post(self):
        guessAt0 = self.request.get("guessAt0")
        guessAt1 = self.request.get("guessAt1")
        guessAt2 = self.request.get("guessAt2")
        guessAt3 = self.request.get("guessAt3")


        if aColorValidator(guessAt0) and aColorValidator(guessAt1) and aColorValidator(guessAt2) and aColorValidator(guessAt3):

            firstThree = firstThreeGiver(guessAt0, guessAt1, guessAt2)
            firstTwo = firstTwoGiver(guessAt0, guessAt1)

            if len(listOfGuesses) == 0:
                thisGuess = GuessObj(spot0=guessAt0, spot1=guessAt1, spot2=guessAt2, spot3=guessAt3, firstThree=firstThree, firstTwo=firstTwo, timeStarted=time.time())
            else:
                thisGuess = GuessObj(spot0=guessAt0, spot1=guessAt1, spot2=guessAt2, spot3=guessAt3, firstThree=firstThree, firstTwo=firstTwo)
            listOfGuesses.append(thisGuess)

            if correctAnswer(thisGuess):
                if lastCorrectAnswer(thisGuess):
                    theTimeNow = time.time()
                    duration = theTimeNow - listOfGuesses[0].timeStarted
                    self.response.out.write("You've won it all.  It took {0} guesses and {1} seconds".format(len(listOfGuesses), duration))
                cssColorMaker(thisGuess)

                thisGuess.clue0 = "Win"
                thisGuess.clue1 = ""
                thisGuess.clue2 = ""
                thisGuess.clue3 = ""
                self.render_front()

            else:
                clueGiver(thisGuess)
                cssColorMaker(thisGuess)

                self.render_front()

        else:
            error = "Possible answers are r, g, b, c, m, y.  Please try again"
            self.render_front(guessAt0, guessAt1, guessAt2, guessAt3, error)


app = webapp2.WSGIApplication([
    ('/', MainPageHandler),
    ('/add', AddPageHandler),
    ('/delete', DeletePageHandler)

], debug=True)
