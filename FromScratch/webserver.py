from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create session and connect to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id = restaurantIDPath).one()

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
        
                output = ""
                output += "<html><body>"
                output += "<h1> Are you sure want to delete %s?</h1>" % restaurant.name
                output += "<form method = 'POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>" % restaurantIDPath
                output += "<input type='submit' value='Delete'>"
                output += "</form></body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/edit"):
                restaurantIDPath = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id = restaurantIDPath).one()

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
        
                output = ""
                output += "<html><body>"
                output += "<h1> %s </h1>" % restaurant.name
                output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurants/%s/edit'>" % restaurantIDPath
                output += "<input name = 'renamedRestaurantName' type = 'text' placeholder = '%s'>" % restaurant.name
                output += "<input type='submit' value='Rename'>"
                output += "</form></body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Make a New Restaurant</h1>"
                output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurants/new'>"
                output += "<input name = 'newRestaurantName' type = 'text' placeholder = 'New Restaurant Name' > "
                output += "<input type='submit' value='Create'>"
                output += "</form></body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/restaurants"):
                restaurants = session.query(Restaurant).all()
                output = ""
                output += "<a href = '/restaurants/new' > Make a New Restaurant Here </a></br></br>"

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output += "<html><body>"
                for restaurant in restaurants:
                    output += restaurant.name
                    output += "</br>"
                    output += "<a href ='/restaurants/%d/edit'> Edit </a>" % restaurant.id
                    output += "</br>"
                    output += "<a href ='/restaurants/%d/delete'> Delete </a>" % restaurant.id
                    output += "</br></br></br>"

                output += "</body></html>"
                self.wfile.write(output)
                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')

                    newRestaurant = Restaurant(name = messagecontent[0])
                    session.add(newRestaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('renamedRestaurantName')

                    restaurantIDPath = self.path.split("/")[2]
                    restaurant = session.query(Restaurant).filter_by(id = restaurantIDPath).one()
                    restaurant.name = messagecontent[0]

                    session.add(restaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id = restaurantIDPath).one()

                session.delete(restaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
        except:
            pass


def main():
    try:
        server = HTTPServer(('', 8080), webServerHandler)
        print 'Web server running...\nOpen localhost:8080/restaurants in your browser'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()