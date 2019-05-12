import wx, sys, time, requests, datetime,  re
import serial, serial.tools.list_ports
from ft_settings import GUI_settings as settings
from ft_settings import CfgParser as parser

class HttpClient:

	url = ft_settings.UPLOAD_TO['URL']
	
	def __init__(self, par):
		self.par = par
		self.url = self.check_url(par)
		return

	def send_file(self, path_to_file):
		self.file = path_to_file
		print self.file
		self.url = self.check_url(self.par)
		print "Uploading to:", self.url
		files = {'file' : ('record', open(self.file,'rb'), 'text/plain', 'form-data; name=\"document\"; filename=\"testcsv.txt\"')}
		try: 	
			response = requests.post(url = self.url, data={'upload_type': 'standard', 'upload_to': '0' }, files = { 'record': open(self.file,'rb') })
			print response.text
			print response.status_code
		except:
			print "Error:", sys.exc_info()[0]

	def check_url(self, parser):
		url_and_path = parser.fetch_url_and_path()
		print "Validating url: ", url_and_path['UPLOAD_TO']
		return url_and_path['UPLOAD_TO']

class SerialCom:

        baudrate = None
        port = "/dev/ttyUSB0"
        sp = None
        timeout = None

        def __init__(self, baudrate):
                self.baudrate = baudrate
		self.timeout = 5
                self.sp = serial.Serial(timeout = self.timeout)
                self.sp.baudrate = self.baudrate
                self.sp.port = self.port
                try:
                        self.sp.open()
                        print "Opening serial port..."
                        time.sleep(2)
                except:
                        print "Error:", sys.exc_info()[0]


        def send_cmd(self, cmd):
                if self.sp.isOpen:
                        self.sp.write(cmd)
                else:
                        print "Open serial port!!!"

                return

        def read_line(self):
		print "reading line..."
                return  self.sp.readline()

	def read_log(self):
                line = ""
                while "EOM" not in line:
                        line += self.sp.readline()
                
                return line


	def change_port(self, port):
		self.sp.close()
		self.sp.port = port
                try:
                        self.sp.open()
                        print "Opening serial port..."
                        #time.sleep(2)
                except:
                        print "Error:", sys.exc_info()[0]


class GUI(wx.Frame):
	def __init__(self, *args, **kwargs):
		super(GUI, self).__init__(*args, **kwargs)
		self.parser = settings(0)
		self.url_and_path = self.parser.fetch_url_and_path()
		print self.url_and_path
		self.wk_path = self.url_and_path['PATH']
		self.InitUI()
		self.http = HttpClient(self.parser)
		self.port = None
		self.sp = SerialCom(9600)		


	def  InitUI(self):
		pnl = wx.Panel(self)
		# ports combo box

		self.portBox = wx.BoxSizer(wx.VERTICAL)
		self.label = wx.StaticText(pnl, label="Available ports", pos=(150,285), style = wx.ALIGN_CENTRE)
		self.portBox.Add(self.label, 0, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 20)
		self.ports = serial.tools.list_ports.comports()
		choice = []
		
		for port in self.ports:
			choice.append(port.device)

		self.combo = wx.ComboBox(pnl, choices = choice, pos=(20,280))
		self.portBox.AddStretchSpacer()

		# buttons
		rbtn = wx.Button(pnl, label='  Read  ', pos=(20,20))
		ubtn = wx.Button(pnl, label=' Upload ', pos=(20,70))
		pbtn = wx.Button(pnl, label='Personals', pos=(20,130))
		sbtn = wx.Button(pnl, label='Settings', pos=(20,180))
		cbtn = wx.Button(pnl, label='  Close  ', pos=(20,230))
		# menu bar
		menubar = wx.MenuBar()
		# menus
		menuBar = wx.MenuBar()
        	fileMenu = wx.Menu()
        	exitMenuItem = fileMenu.Append(wx.NewId(), "Exit", "Exit the application")
        	menuBar.Append(fileMenu, "&File")
        	self.Bind(wx.EVT_MENU, self.OnClose, exitMenuItem)
        	self.SetMenuBar(menuBar)
		# binds	
		cbtn.Bind(wx.EVT_BUTTON, self.OnClose)
		pbtn.Bind(wx.EVT_BUTTON, self.OnPersonals)		
		rbtn.Bind(wx.EVT_BUTTON, self.OnRead)
		ubtn.Bind(wx.EVT_BUTTON, self.OnUpload)
		sbtn.Bind(wx.EVT_BUTTON, self.OnSettings)
		self.combo.Bind(wx.EVT_COMBOBOX, self.OnCombo)
		# sizes
		self.SetSize((550, 500))
		self.SetTitle('wx.Button')
		self.Centre()
		self.Show(True)

	def OnClose(self, e):
		self.Close(True)

	def OnRead(self, e):
		print "performing on read"
		sorter = Sorter(self.parser)
		print "Send command"
		self.sp.send_cmd('133\r\n')
		log =  self.sp.read_log()
		print "Log: ", log
		sorter.write_to_csv(log)
		return 0
	
	def OnPersonals(self, e):
		ppnl = GUI_personals(self, self.sp)
		ppnl.Show()

	def OnCombo(self, e):
		self.sp.change_port(self.combo.GetValue())

	def OnUpload(self, e):
		print "On Upload"
		pnl = wx.Frame(None, -1, 'win.py')
		pnl.SetDimensions(0,0,200,50)
		openFileDialog = wx.FileDialog(pnl, "Upload file", "", "", "CSV files (*.csv)|*.csv", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
		openFileDialog.ShowModal()
		upload_file = openFileDialog.GetPath()
		openFileDialog.Destroy()
		self.http.send_file(upload_file)

	def OnSettings(self, e):
		self.parser.Show()


class GUI_personals(wx.Frame):
	def __init__(self, parent, serial_port):
		# frames
		wx.Frame.__init__(self, None, size=(550,500), title='Personals')
		self.parent = parent
		ppnl = wx.Panel(self)
		spbtn = wx.Button(ppnl, label='Set Details', pos=(220,10))
		stbtn = wx.Button(ppnl, label='Set Time', pos=(330,10))	
		cbtn = wx.Button(ppnl, label='  Close  ', pos=(440,10))

		self.UID_text = wx.TextCtrl(ppnl, -1, pos=(0,10), size=(100,20), style=wx.DEFAULT)
		self.weight_text = wx.TextCtrl(ppnl, -1, pos=(0,40), size=(100,20), style=wx.DEFAULT)
		self.height_text = wx.TextCtrl(ppnl, -1, pos=(0,70), size=(100,20), style=wx.DEFAULT)
		self.heartrate_text = wx.TextCtrl(ppnl, -1, pos=(0,100), size=(100,20), style=wx.DEFAULT)	
		self.appointment_text = wx.TextCtrl(ppnl, -1, pos=(0,130), size=(100,20), style=wx.DEFAULT)
		
		self.UID_label = wx.StaticText(ppnl, -1, label="User ID", pos=(120,10), size=(100,20), style=wx.DEFAULT)
		self.weight_label = wx.StaticText(ppnl, label="Weight", pos=(120,40), size=(100,20), style=wx.DEFAULT)
		self.height_label = wx.StaticText(ppnl, label="Height", pos=(120,70), size=(100,20), style=wx.DEFAULT)
		self.heartrate_label = wx.StaticText(ppnl, label="Heart Rate", pos=(120,100), size=(100,20), style=wx.DEFAULT)	
		self.appointment_label = wx.StaticText(ppnl, label="Appointment", pos=(120,130), size=(100,20), style=wx.DEFAULT)
		
		# binds
		cbtn.Bind(wx.EVT_BUTTON, self.OnClose)
		stbtn.Bind(wx.EVT_BUTTON, self.OnSetTime)
		spbtn.Bind(wx.EVT_BUTTON, self.OnSetPersonals)
		# additional
		self.sp = serial_port
	
	def OnSetPersonals(self, e):
		cmd = "150," + self.UID_text.GetValue() + ":" +  self.height_text.GetValue() + ":" + self.weight_text.GetValue() + ":" + self.heartrate_text.GetValue() + ":" + self.appointment_text.GetValue() + ":"+ "\r\n"
		cmd.encode('ascii')
		print cmd
		try:
			self.sp.send_cmd(bytearray(cmd, 'ascii'))
		except:
			warn = GUI_Warning(self)
			warn.Show()

	def OnSetTime(self, e):
		weekday = datetime.datetime.today().isoweekday()
		tm = time.strftime("%H:%M:%S")
		dt = time.strftime("%d:%m:%Y")
		cmd = "254," + tm + ":" + str(weekday) + ":" + dt + "\r\n"
		cmd.encode('ascii')
		print cmd
		try:
			self.sp.send_cmd(bytearray(cmd, 'ascii'))
		except:
			warn = GUI_Warning(self)
			warn.Show()

	def OnClose(self, e):		
		self.Close(True)

class GUI_Warning(wx.Frame):
	
	def __init__(self, parent):
		wx.Frame.__init__(self, None, size=(300,200), title='Error')
		self.parent = parent
		epnl = wx.Panel(self)
		cbtn = wx.Button(epnl, label= ' Close ', pos=(100,100))
		self.message_label = wx.StaticText(epnl, -1, label="The device is not connected", pos=(10,10), size=(280,20), style=wx.DEFAULT)

		cbtn.Bind(wx.EVT_BUTTON, self.OnClose)

	def OnClose(self,e):
		self.Close(True)

class Sorter:
	
	def __init__(self, par):
		self.received_data = ""
		self.parser = par
		self.path = self.check_path(self.parser)

	def check_path(self, parser):
		url_and_path = parser.fetch_url_and_path()
		print "Validating path: ", url_and_path['PATH']
		return url_and_path['PATH']

	def detect_filename(self, str_list):
		for st in str_list:	
			if ("0x0A" not in st) and ("EOM" not in st) and (st != "") and ("0xAA" in st):
				q = re.split(',',st)
				self.out_filename = self.path + q[1] + "_" + time.strftime("%d_%m_%Y") + ".csv"
				return
			else:
				print "No file name found!"

	def sort_to_csv(self, st):
		if ("0xAA" not in st) and ("EOM" not in st) and (st != "") and ("0x0A" in st):
			q = re.split(',', st)
			s = re.split('-', q[1])
			values = []
			for i, val in enumerate(s):
				values.append(int(val))

			
			s1 = ((values[2] << 8) + values[1])
			s2 = ((values[6] << 24) + (values[5] << 16) + (values[4] << 8) + values[3])
			
			output = {}			
			wkCount = values[0]
			output['wk_type'] = (s1 >> 9) & 0xf
        		output['wk_duration'] = s1 & 0x1ff;
       			output['wk_steps'] = s2 & 0xffff;
        		output['wk_month'] = (s2 >> 16) & 0xf;
        		output['wk_day'] = (s2 >> 20) & 0x1f;
			output['wk_year'] = 0
			if output['wk_month'] <= datetime.date.today().month:
				output['wk_year'] = datetime.date.today().year
			else:
				output['wk_year'] = datetime.date.today().year - 1

			wk_type = ""
			if output['wk_type'] == 1:
				wk_type = "Running"
			elif output['wk_type'] == 2:
				wk_type = "Walking"
			elif output['wk_type'] == 3:
				wk_type = "Cycling"
			elif output['wk_type'] == 4:
				wk_type = "Rope Jumping"
			elif output['wk_type'] == 5:
				wk_type = "Swimming"
			elif output['wk_type'] == 6:
				wk_type = "Tennis"
			elif output['wk_type'] == 7:
				wk_type = "Team"
			elif output['wk_type'] == 8:
				wk_type = "Other"

			return wk_type + "," + str(output['wk_duration']) + "," + str(output['wk_year']) + "-" + str(output['wk_month']) + "-" +  str(output['wk_day']) + "," + str(output['wk_steps']) + "\n"


	def write_to_csv(self, str_list):
		csv_list = re.split(r'[\n\r]+', str_list)
		self.out_filename = "csvout.csv"
		print csv_list 
		print "\n Seraching for filename: "
		
		self.detect_filename(csv_list)

		print "Filename: " + self.out_filename 

		with open(self.out_filename, 'wb') as file:
			for s in csv_list:
				print "for s in csv_list:" , s
				if ("0x0A" in s):
					file.write(self.sort_to_csv(s))
					


class Commander:

	def __init__(self, serial_com):
		self.cmd = ["254", "133", "150", "222"] # set current time, read personal data, set personal data, erase memory
		self.sp = serial_com		

	def set_current_time(self):
		
		return -1
		
	def set_personal_data(self):
		return -1

	def read_personal_data(self):
		return -1

	def erase_memory(self):
		return -1

app = wx.App()
GUI(None)

#http = HttpClient()
#http.send_file()

#frame = wx.Frame(None, -1, 'ft_pro')
#frame.Show()

app.MainLoop()





