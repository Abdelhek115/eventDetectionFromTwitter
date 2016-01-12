import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

from ...model.Event import Event
from LouvainClusterer.JavaBasedLouvainClusterer import JavaBasedLouvainClusterer as LouvainClusterer
from Utils.Constants import *

class EventDetector :
    #-------------------------------------------------------------------------------------------------------------------------------------
    #   Class constructor
    #-------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self,tweets,similarityMatrixBuilder) :
        self.tweets=np.array(tweets)
        self.similarityMatrixBuilder=similarityMatrixBuilder
        self.events=[]

    #-------------------------------------------------------------------------------------------------------------------------------------
    #   Event detection
    #-------------------------------------------------------------------------------------------------------------------------------------
    def getEvents(self) :
        print "Detecting events ..."
        louvainClusterer=LouvainClusterer(self.tweets,self.similarityMatrixBuilder)
        realClusters=louvainClusterer.getClusters()
        clustersUniqueId=set(realClusters)
        events=[]
        print "\tConstructing events from clusters ..."
        for clusterId in clustersUniqueId :
            tweetsOfClusterId=self.tweets[realClusters==clusterId]
            event=Event(tweetsOfClusterId)
            if (self.isEventImportant(event)) :
                events.append(event)
        self.events=events
        return events

    def isEventImportant(self,event) :
        """
        evaluate if yes or no the event is important
        """
        if (event.userNumber < MIN_USER_NUMBER or len(event.tweets) < MIN_TWEETS_NUMBER) : return False
        tweetPerUserNumber={}
        for tweet in self.tweets :
            try : tweetPerUserNumber[tweet.userId]+=1
            except KeyError : tweetPerUserNumber[tweet.userId]=1
        maximumProportionInThisEvent=float(tweetPerUserNumber[max(list(tweetPerUserNumber), key=lambda userId : tweetPerUserNumber[userId])])/len(self.tweets)
        return (maximumProportionInThisEvent<MAX_TOLERATED_PER_USER)
        
    #-------------------------------------------------------------------------------------------------------------------------------------
    #   Event vizualisation
    #-------------------------------------------------------------------------------------------------------------------------------------
    def getStringOfEvent(self,event) :
        NUM_DIGIT=10**2
        SEPARATOR="\t|"
        PERCENTAGE=0.8
        
        firstIndiceOfInterval,lastIndiceOfInterval=0,int(PERCENTAGE*len(event.tweets))
        estimatedEventDuration=event.tweets[firstIndiceOfInterval].delay(event.tweets[lastIndiceOfInterval])

        while (lastIndiceOfInterval<len(event.tweets)) :
            newEventDuration=event.tweets[firstIndiceOfInterval].delay(event.tweets[lastIndiceOfInterval])
            if (newEventDuration<estimatedEventDuration) : estimatedEventDuration=newEventDuration
            firstIndiceOfInterval+=1
            lastIndiceOfInterval+=1
            
        S="|"+SEPARATOR.join([str(event.eventMedianTime),
                              str(int(estimatedEventDuration)),
                              str(float(int(NUM_DIGIT*event.eventCenter.latitude))/NUM_DIGIT),
                              str(float(int(NUM_DIGIT*event.eventCenter.longitude))/NUM_DIGIT),
                              str(float(int(NUM_DIGIT*event.eventRadius))/NUM_DIGIT),
                              str(event.userNumber),
                              str(len(event.tweets)),
                              ",".join(event.importantHashtags)])+SEPARATOR
        return S
    
    def showTopEvents(self,top=10) :
        if not self.events :
            "No events detected !"
            return
        
        SIZE_OF_LINE=40
        SEPARATOR="\t|"
        HEADER="|"+SEPARATOR.join(["Median time","estimated duration (s)","mean latitude","mean longitude","radius (m)","user number","tweets number","top hashtags"])+SEPARATOR

        TopEvents=sorted(self.events,key=lambda event : len(event.tweets),reverse=True)[0:min(max(1,top),len(self.events))]

        print "-"*SIZE_OF_LINE
        print HEADER
        print "-"*SIZE_OF_LINE 
        for event in TopEvents :
            print self.getStringOfEvent(event)
            print "-"*SIZE_OF_LINE

    def drawEvents(self) :
        events=self.events
        m = Basemap(width=1200000,height=1200000,projection='lcc',resolution='c',lat_0=46,lon_0=3.)
        m.drawcoastlines()
        m.drawmapboundary(fill_color='aqua')
        m.fillcontinents(color='white',lake_color='aqua')
        m.drawcountries()
        for event in events :
            xpt,ypt = m(event.eventCenter.longitude,event.eventCenter.latitude)
            m.plot(xpt,ypt,'bo')
        #m.bluemarble()
        plt.show()
    #----------------------------------------------------------------------------------------------------#
    
    
