# import sys
# from PyQt5 import QtCore, QtGui, QtWidgets
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *
# # from PyQt5.QtWebKit import *
# # from PyQt5.QtWebKitWidgets import *
# from PyQt5.QtWebEngineWidgets import *
#
# from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
#
# app = QApplication(sys.argv)
#
# web = QWebEngineView()
# web.load(QUrl("http://jeffreyfarnworth.com/calculator.html"))
#
# # web.page().runJavaScript("document.title", "[](const QVariant &v) { qDebug() << v.toString(); }")
#
#
# web.show()
# sys.exit(app.exec_())







#http://stackoverflow.com/questions/5885290/how-to-call-javascript-function-from-pyqt

# I'm trying to interact with a google map using python. I've built an application in PyQT with a QWebView. The QWebView loads a local html page as shown here:

# browser = QwebView()
# browser.load(QUrl("file:///c:/main.html"))
# frame = browser.page().currentFrame()
# frame.evaluateJavaScript(QString("addMarker(-33.89, 151.275)"))
# The html page is as follows:
#
# <!DOCTYPE html>
# <html>
# <head>
# <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
# <style type="text/css">
#   html { height: 100% }
#   body { height: 100%; margin: 0px; padding: 0px }
#   #map_canvas { height: 100% }
# </style>
# <script type="text/javascript"
#   src="http://maps.google.com/maps/api/js?sensor=false">
# </script>
# <script type="text/javascript">
# var map;
# function initialize() {
#     var latlng = new google.maps.LatLng(-34.397, 150.644);
#     var myOptions = {
#                     zoom: 8,
#                     center: latlng,
#                     mapTypeId: google.maps.MapTypeId.ROADMAP
#                     };
#      map = new google.maps.Map(document.getElementById("map_canvas"),
#                                myOptions);
#  }
#
#  function addMarker(lat, lng) {
#   var myLatLng = new google.maps.LatLng(lat, lng);
#       var beachMarker = new google.maps.Marker({position: myLatLng,
#                                                 map: map
#                                                });
#  }
#
# </script>
# </head>
# <body onload="initialize();">
#     <div id="map_canvas" style="width:100%; height:100%"></div>
# </body>
# </html>
# How can I call addMarker from Python?
#
# I have tried calling addMarker from the HTML (added the call to the onload call) and I tried using a simple javascript expression from the python (frame.evaluateJavaScript("alert(5)")). Both of those worked, so I know that addMarker and evaluateJavaScript can work, I just don't know how.
#
# I also tried calling evaluateJavaScript("addMarker(-33.89,151.275)") on the frame.documentElement() object and that didn't work either.
#
# The error was that I needed to wait for the page to load. I added a button that was connected to the  evaluateJavaScript("addMarker(-33.89,151.275)") call. When I clicked the button (after the page loaded), the marker was added as expected.











# import sys
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *
# # from PyQt5.QtWebKit import *
# # from PyQt5.QtWebKitWidgets import *
# from PyQt5.QtWebEngineWidgets import *
#
#
# class MyBrowser(QWidget):
#     def __init__(self, parent = None):
#         super(MyBrowser, self).__init__(parent)
#         self.createLayout()
#         self.createConnection()
#
#     def search(self):
#         address = str(self.addressBar.text())
#         if address:
#             if address.find('://') == -1:
#                 address = 'http://' + address
#             url = QUrl(address)
#             self.webEngineView.load(url)
#
#     def createLayout(self):
#         self.setWindowTitle("keakon’s browser")
#         self.addressBar = QLineEdit()
#         self.goButton = QPushButton("&GO")
#         bl = QHBoxLayout()
#         bl.addWidget(self.addressBar)
#         bl.addWidget(self.goButton)
#         self.webEngineView = QWebEngineView()
#         layout = QVBoxLayout()
#         layout.addLayout(bl)
#         layout.addWidget(self.webEngineView)
#         self.setLayout(layout)
#
#     def createConnection(self):
#         self.addressBar.returnPressed.connect(self.search)
#         self.addressBar.returnPressed.connect(self.addressBar.selectAll)
#         self.goButton.clicked.connect(self.search)
#         self.goButton.clicked.connect(self.addressBar.selectAll)
#
#
# app = QApplication(sys.argv)
# browser = MyBrowser()
# browser.show()
# sys.exit(app.exec_())