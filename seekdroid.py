"""
This source is licensed with Creative Commons Attribution-Share Alike 3.0 Unported
To read the full license: http://creativecommons.org/licenses/by-sa/3.0/
Legal Code: http://creativecommons.org/licenses/by-sa/3.0/legalcode

Authors: 

  Albert Castellana 
  Xavier Ruiz
         
For more information and updates:
  www.onthetopofthewave.com     
    
"""

import re
import cgi
import random
import logging

from waveapi import events
from waveapi import model
from waveapi import robot
from waveapi import document 
from waveapi import ops 

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

__author__ = 'This project is part of a tutorial by http://www.onthetopofthewave.com\n\n It\'s authors are: \n<b>kstellana@gmail.com ( Albert Castellana )<br />enedebe@gmail.com ( Xavier Ruiz )</b>'

__WelcomeMsg__ = "\n\n\nHey there, I\'m Seekdroid,\n   \
I\'ll try to help you find the robot that suits you the most.\n\n\
These are the commands I accept:\n\
\n<b>/list ( number of elements )</b>  - Will list the last robots in our directory.\n\
\n<b>/invite Name</b>  - Will add the specified robot on the conversation.\n\
\n<b>/show Name</b>  - Will show the info related to the robot.\n\
\n<b>/add</b>  - Will add the robot to our database and will \
wait for one of the moderators to accept it\'s adhesion to the list.\n\
\n<b>/leave</b>  - Makes Seekdroid leave the conversation ( Not yet implemented because of the API )\n\
\n<b>/author</b>   - Shows information about the authors of this robot."

__gadget_url__ = 'http://seekdroid.appspot.com/inc/seekdroid_gadget.xml'

#Definim el model de dades
class Robot(db.Model):
  domini = db.StringProperty(multiline=False)
  nom = db.StringProperty(multiline=False)
  autor = db.StringProperty(multiline=False)
  data = db.DateTimeProperty(auto_now_add=True)
  categoria = db.StringProperty(multiline=False)
  valid = db.BooleanProperty()
  descripcio = db.StringProperty(multiline=True)
  num_usuaris = db.IntegerProperty()
  num_vots = db.IntegerProperty()
  link = db.LinkProperty()


class Vot(db.Model):
  domini = db.StringProperty(multiline=False)
  usuari = db.UserProperty()
    
class Autor(db.Model):
  autor = db.StringProperty()
  mail = db.EmailProperty()
  url = db.LinkProperty()
  llista_robots = db.StringListProperty()
  
class Cat(db.Model):
  nom_cat = db.StringProperty()
  num_robots = db.IntegerProperty()

def OnBlipSubmitted(properties, context):
  blip = context.GetBlipById(properties['blipId'])
  contents = blip.GetDocument().GetText()
  
  """SetText() Necesary to avoid repetition of the actions. Everything should be done with SetText but the API fails to put the HTML markup by now""" 
  blip.GetDocument().SetText("")
      
  aux = contents
  while aux.count("/")>0:
    pos = aux.find("/")
    args = aux[pos+1:]
    aux = args
    pos = args.find("/")
    if pos>=0:
       args = args[:pos]
    
    args = args.split()

    if 'author' in args[0]:
      blip.GetDocument().AppendText("\n\n"+__author__+"\n")

    elif 'list' in args[0]:
      
      #number of robots to display
      try:
        n = int(args[1])
      except:
        n = 10
        
      blip.GetDocument().AppendText("\n\n<b>Robot List:</b>\n")

      q = db.GqlQuery("SELECT * FROM Robot WHERE valid = True ORDER BY data DESC")
      robots = q.fetch(n)
      
      for droid in robots:
        blip.GetDocument().AppendText("\n"+droid.nom+" - "+droid.domini+"\n")
      blip.GetDocument().AppendText("\n\n<b>---</b>\n")

    elif 'show' in args[0]:
      robots = Robot.all()
      robots = robots.filter('nom ='," ".join(args[1:]))
      if robots.count() > 0:
        for droid in robots:
          blip.GetDocument().AppendText("\n Show: <b>"+droid.nom+" - </b><i>"+droid.domini+"</i> - \n"+droid.descripcio+"\n")
      else:
        blip.GetDocument().AppendText("\n"+" ".join(args[1:])+" <b> Robot Not found</b> \n")

    elif 'add' in args[0]:
      blip.GetDocument().AppendText("\n\n\n")
      gadget=document.Gadget(__gadget_url__) 
      blip.GetDocument().AppendElement(gadget) 

    elif 'invite' in args[0]:
      robots = Robot.all()
      robots = robots.filter('nom ='," ".join(args[1:]))
      if robots.count() > 0:
        for droid in robots:
          context.GetRootWavelet().AddParticipant(droid.domini)
          blip.GetDocument().AppendText("\n <b>"+droid.nom+"</b>  -  Was added to the conversation.\n")
      else:
        blip.GetDocument().AppendText("\n <b>Robot Not found</b> \n")
        
    elif 'leave' in args[0]:
      try:
        context.GetRootWavelet().RemoveSelf()
      except:
        blip.GetDocument().AppendText("\n<b>Not yet implemented</b>\n")

    elif 'vote' in args[0]:
      robots = Robot.all()
      robots = robots.filter('nom ='," ".join(args[1:]))
      
           
      if robots.count() == 1:
        query = Robot.gql("WHERE domini = :1", robots[0].domini)
        robot = query.get()
        robot.num_vots = robot.num_vots + 1
        robot.put()
        blip.GetDocument().AppendText("\n Vote <b>"+robot.nom+"</b> +1 \n")
      elif robots.count() > 1:
        blip.GetDocument().AppendText("\n <b>Too many coincidences</b> \n")        
      else:
        blip.GetDocument().AppendText("\n <b>Robot Not found</b> \n")
    
"""
    elif 'clean' in args[0]:
      bliplist = context.GetBlips()
      for b in bliplist:
        b.Delete()    
"""

def OnRobotAdded(properties, context):
  """Invoked when the robot has been added."""
  root_wavelet = context.GetRootWavelet()
  root_wavelet.CreateBlip().GetDocument().AppendText(__WelcomeMsg__)

if __name__ == '__main__':
  seekdroid = robot.Robot('SeekDroid', 
      image_url='http://seekdroid.appspot.com/inc/seekdroid.png',
      version='1.20',
      profile_url='http://seekdroid.appspot.com/')
  seekdroid.RegisterHandler(events.BLIP_SUBMITTED, OnBlipSubmitted)
  seekdroid.RegisterHandler(events.WAVELET_SELF_ADDED, OnRobotAdded)
  seekdroid.Run()

"""
Known Bugs:

-Non validated bots can be invited

TIPs

-Stringproperty noseque

"""

