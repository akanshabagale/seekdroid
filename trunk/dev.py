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

import cgi
import os
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import users

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

class MainPage(webapp.RequestHandler):
  def get(self):
    q = db.GqlQuery("SELECT * FROM Robot WHERE valid = True ORDER BY data DESC")
    robots = q.fetch(10)
    template_values = {
      'robots': robots 
      }
    
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

class addRobot(webapp.RequestHandler):
  def post(self):
    robot = Robot()
  
    robot.domini = self.request.get('domini')
    robot.nom = self.request.get('nom')
    robot.autor = self.request.get('autor')
    robot.categoria = self.request.get('categoria')
    robot.descripcio = self.request.get('descripcio')
#    robot.link = self.request.get('link')
    robot.num_usuaris = 0
    robot.num_vots = 0
    robot.valid = False
    robot.put()
    self.redirect('/addRobot_Done')


class addRobot_Done(webapp.RequestHandler):
  def get(self):
    self.response.out.write("The Robot was Added Successfully!")

class voteRobot(webapp.RequestHandler):
  def post(self):
    user = users.get_current_user()
    if user:
      q2 = Vot.gql("WHERE domini = :1 AND usuari= :2", self.request.get('domini'), user)
      t1 = q2.count()
#      self.response.out.write(q2.domini)
      if t1 == 0:
        vot = Vot(domini = self.request.get('domini'), usuari = user)
        vot.put()
        query = Robot.gql("WHERE domini = :1", self.request.get('domini'))
        robot = query.get()
        robot.num_vots = robot.num_vots + 1
        robot.put()
        self.redirect('/')
      else:
      	self.redirect('/')
    else: 
      self.redirect(users.create_login_url('/'))
      
class admin(webapp.RequestHandler):
  
  def get(self):
    if users.is_current_user_admin():
      robots = db.GqlQuery("SELECT * FROM Robot WHERE valid = False ORDER BY data ASC")
      template_values = {
        'robots': robots 
        }

      path = os.path.join(os.path.dirname(__file__), 'admin.html')
      self.response.out.write(template.render(path, template_values))
    else:
      self.redirect(users.create_login_url('/admin'))
  
  def post(self):
    
    query = Robot.gql("WHERE domini = :1", self.request.get('domini'))
    robot = query.get()
    if self.request.get('valid') == 'True':
      robot.valid = True
      robot.put()
    elif self.request.get('valid') == 'False':
      robot.delete()
    self.redirect('/admin')
    

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/addRobot', addRobot),
                                      ('/addRobot_Done', addRobot_Done),
                                      ('/voteRobot', voteRobot),
                                      ('/admin', admin),
                                      ('/validate', admin)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
