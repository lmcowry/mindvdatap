from google.appengine.ext import db

class AnswerObj4(db.Model):


    spot0 = db.StringProperty(required = True)
    spot1 = db.StringProperty(required = True)
    spot2 = db.StringProperty(required = True)
    spot3 = db.StringProperty(required = True)
    answered = db.BooleanProperty(required = True)








class GuessObj(db.Model):
    # will just be the guess.  will also have clues added later
    spot0 = db.StringProperty(required = True)
    spot1 = db.StringProperty(required = True)
    spot2 = db.StringProperty(required = True)
    spot3 = db.StringProperty(required = True)

    timeStarted = db.FloatProperty()

    clue0 = db.StringProperty()
    clue1 = db.StringProperty()
    clue2 = db.StringProperty()
    clue3 = db.StringProperty()

    colorspot0 = db.StringProperty()
    colorspot1 = db.StringProperty()
    colorspot2 = db.StringProperty()
    colorspot3 = db.StringProperty()

    firstThree = db.StringProperty()
    firstTwo = db.StringProperty()
