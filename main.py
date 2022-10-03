from time import sleep
from flask import Flask
import json
import wrapper.interractorWrapper as InterractorWrapper

interractor = InterractorWrapper.Interractor('127.0.0.1', '8080')
status = 'normal'

resourceLimiterUrl = ''



app = Flask(__name__)



@app.get('/programming_languages')
def list_programming_languages():
   return {"programming_languages":json('')}


def callResourceLimiter():
    resp = requests.get(self.apiUrl + '/bot/is-under-attack')

def executePipeline():
    callResourceLimiter()



#interractor.ships(33637224)



#interractor.build(33637224,4,1)
#sleep(2)
#interractor.cancelBuild(33637224,4)
#interractor.resources(33637224)


#interractor.resourceBuildings(33637224)