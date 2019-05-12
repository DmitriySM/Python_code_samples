import wx, sys, time, requests, datetime, re, os
from sys import platform as _platform
import ConfigParser


# link to the website loader script
# UPLOAD_TO = { 'URL': 'http://localhost:8000/loaded/'}
# Path to the folder where workouts are stored
DEFAULT_WORKOUT_FOLDER = { 'PATH' : '' }


class GUI_settings(wx.Frame):
        def __init__(self, parent):
                # frames
                wx.Frame.__init__(self, None, size=(550,500), title='Personals')
                self.parent = parent
                ppnl = wx.Panel(self)
                stbtn = wx.Button(ppnl, label='Set', pos=(220,10))
                vbtn = wx.Button(ppnl, label='View', pos=(330,10))
                cbtn = wx.Button(ppnl, label='  Close  ', pos=(440,10))

                self.url_text = wx.TextCtrl(ppnl, -1, pos=(0,10), size=(100,20), style=wx.DEFAULT)
                self.path_text = wx.TextCtrl(ppnl, -1, pos=(0,40), size=(100,20), style=wx.DEFAULT)

                self.UID_label = wx.StaticText(ppnl, -1, label="Loader URL", pos=(120,10), size=(100,20), style=wx.DEFAULT)
                self.weight_label = wx.StaticText(ppnl, label="Local path", pos=(120,40), size=(100,20), style=wx.DEFAULT)

                # binds
                cbtn.Bind(wx.EVT_BUTTON, self.OnClose)
                stbtn.Bind(wx.EVT_BUTTON, self.OnSet)
                vbtn.Bind(wx.EVT_BUTTON, self.OnView)
		
		#config parser
		self.config = CfgParser()

        def OnSet(self, e):
		self.url = self.url_text.GetValue()
		self.path = self.path_text.GetValue()
		self.config.set_url_and_path(self.url, self.path)

        def OnView(self, e):
		self.url_text.write(self.config.get_url())
		self.path_text.write(self.config.get_path())

        def OnClose(self, e):
                self.Close(True)

	def fetch_url_and_path(self):
		print "fetching", self.config.get_url_and_path()
		return self.config.get_url_and_path()

class CfgParser:
	def __init__(self):
		self.config = ConfigParser.RawConfigParser()
	        # Config parser
                # Checking if file exist and filled
                self.isEmptyFile = True
		self.configfile = 'ft_config.cfg'
		self.default_folder = self.detect_default_folder()
		print "#2 Default path: " , self.default_folder

                try:
                        if (os.stat(self.configfile).st_size == 0):
                                self.isEmptyFile = True
                        else:
                                self.isEmptyFile = False
                except:
                        self.config.add_section('Link_and_Path')
                        self.config.set('Link_and_Path','url','https://localhost:8000')
                        self.config.set('Link_and_Path','path', self.default_folder)
                        with open(self.configfile,'wb') as configfile:
                                self.config.write(configfile)
                        configfile.close()


                if self.isEmptyFile == True:
                        #self.config.add_section('Link_and_Path')
                        self.config.set('Link_and_Path','url','https://localhost:8000')
                        self.config.set('Link_and_Path','path', self.default_folder)
                        with open(self.configfile,'wb') as configfile:
                                self.config.write(configfile)
                        configfile.close()


	def set_url_and_path(self, url, path):
		print url, path
		self.config.set('Link_and_Path','url', url)
                self.config.set('Link_and_Path','path', path)
                with open(self.configfile,'wb') as configfile:
                	self.config.write(configfile)
                        configfile.close()

	
	def get_url_and_path(self):
		self.url_and_path = {}
		self.config.read('ft_config.cfg')
                self.url_and_path['UPLOAD_TO'] = self.config.get('Link_and_Path','url')
		self.url_and_path['PATH'] = self.config.get('Link_and_Path','path')
		return self.url_and_path		

	def get_url(self):
		return self.config.get('Link_and_Path','url')

	def get_path(self):
		return self.config.get('Link_and_Path','path')

	def detect_default_folder(self):
		if _platform == "linux" or _platform == "linux2": # Linux
			default_path = os.path.dirname(os.path.abspath(__file__)) + "/"
		elif _platform == "darwin": # MacOs
			default_path = os.path.dirname(os.path.abspath(__file__)) + "/"
		elif _platform == "win32" or _platform == "win64": # Win
			default_path = os.path.dirname(os.path.abspath(__file__)) + "\\"

		print "Default folder: ", default_path
		return default_path
