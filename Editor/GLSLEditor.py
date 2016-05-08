import wx
import wx.lib.dialogs
import wx.stc as stc
import keyword
import os
from xml.dom.minidom import parse
import xml.dom.minidom

if wx.Platform == '__WXMSW__':
	faces = { 'times' : 'Times New Roman',
			  'mono' : 'Courier New',
			  'helv' : 'Arial',
			  'size' : 10,
			  'size2' : 8,
			}
else:
	faces = { 'times' : 'Times',
			  'mono' : 'Courier',
			  'helv' : 'Helvetica',
			  'size' : 12,
			  'size2' : 10,
			}

class MainWindow(wx.Frame):
	def __init__(self, parent, title):
		self.dirname = ''
		self.filename= ''

		# editor options
		self.lineNumbersEnabled = True
		self.leftMartinWidth = 25

		# application frame
		wx.Frame.__init__(self, parent, title=title, size=(800, 600))
		self.control = stc.StyledTextCtrl(self, style = wx.TE_MULTILINE | wx.TE_WORDWRAP)

		# text zoom in and out
		self.control.CmdKeyAssign(ord('='), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMIN)
		self.control.CmdKeyAssign(ord('-'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMOUT)

		# text control
		self.control.SetViewWhiteSpace(False)
		self.control.SetProperty("fold", "1")
		self.control.SetProperty("tab.timmy.whinge.level", "1")

		# margins
		self.control.SetMargins(5, 0)
		self.control.SetMarginType(1, stc.STC_MARGIN_NUMBER)
		self.control.SetMarginWidth(1, self.leftMartinWidth)

		self.CreateStatusBar()
		self.UpdateLineCol(self)
		self.StatusBar.SetBackgroundColour((220, 220, 220))

		# file menu items
		fileMenu = wx.Menu()
		menuNew = fileMenu.Append(wx.ID_NEW, "&New", "Create new file")
		menuOpen = fileMenu.Append(wx.ID_OPEN, "&Open", "Open existing file")
		menuSave = fileMenu.Append(wx.ID_SAVE, "&Save", "Save current file")
		menuSaveAs = fileMenu.Append(wx.ID_SAVEAS, "Save &As", "Save to a new file")
		fileMenu.AppendSeparator()
		menuClose = fileMenu.Append(wx.ID_EXIT, "&Close", "Close the editor")

		# edit menu
		editMenu = wx.Menu()
		menuUndo = editMenu.Append(wx.ID_UNDO, "&Undo", "Undo last action")
		menuRedo = editMenu.Append(wx.ID_REDO, "&Redo", "Redo last action")
		editMenu.AppendSeparator()
		menuSelectAll = editMenu.Append(wx.ID_SELECTALL, "&Select All", "Select entire file content")
		menuCopy = editMenu.Append(wx.ID_COPY, "&Copy", "Copy selection")
		menuCut = editMenu.Append(wx.ID_CUT, "C&ut", "Cut selection")
		menuPaste = editMenu.Append(wx.ID_PASTE, "&Paste", "Paste from clipboard")

		# preferences menu
		prefMenu = wx.Menu()
		menuLineNumbers = prefMenu.Append(wx.ID_ANY, "&Line Numbers", "Toggle line numbers")

		# help menu
		helpMenu = wx.Menu()
		menuAbout = helpMenu.Append(wx.ID_ANY, "&About", "About the editor")

		# menubar
		menuBar = wx.MenuBar()
		menuBar.Append(fileMenu, "&File")
		menuBar.Append(editMenu, "&Edit")
		menuBar.Append(prefMenu, "&Preferences")
		menuBar.Append(helpMenu, "&Help")
		self.SetMenuBar(menuBar)

		# file menu events
		self.Bind(wx.EVT_MENU, self.OnNew, menuNew)
		self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
		self.Bind(wx.EVT_MENU, self.OnSave, menuSave)
		self.Bind(wx.EVT_MENU, self.OnSaveAs, menuSaveAs)
		self.Bind(wx.EVT_MENU, self.OnClose, menuClose)

		# edit menu events
		self.Bind(wx.EVT_MENU, self.OnUndo, menuUndo)
		self.Bind(wx.EVT_MENU, self.OnRedo, menuRedo)
		self.Bind(wx.EVT_MENU, self.OnSelectAll, menuSelectAll)
		self.Bind(wx.EVT_MENU, self.OnCopy, menuCopy)
		self.Bind(wx.EVT_MENU, self.OnCut, menuCut)
		self.Bind(wx.EVT_MENU, self.OnPaste, menuPaste)

		# preferences menu events
		self.Bind(wx.EVT_MENU, self.OnToggleLineNumbers, menuLineNumbers)

		# help menu events
		self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)

		# key events
		self.control.Bind(wx.EVT_CHAR, self.OnCharEvent)
		self.control.Bind(wx.EVT_KEY_UP, self.UpdateLineCol)
		self.control.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)

		self.Show()

		# styling
		#self.control.SetKeyWords(0, " ".join(["uniform", "if"]))
		self.Style()

	def Style(self):
		self.control.StyleSetSpec(stc.STC_STYLE_LINENUMBER, "back:#C0C0C0,face:%(helv)s,size:%(size2)d" % faces)

		self.control.StyleSetBackground(stc.STC_STYLE_DEFAULT, "#222222")
		self.control.SetSelBackground(True, "#666666")

		self.control.StyleSetSpec(stc.STC_P_DEFAULT, "fore:%s,back:%s" % ("#EEEEEE", "#222222"))
		self.control.StyleSetSpec(stc.STC_P_DEFAULT, "face:%(mono)s,size:%(size)d" % faces)

		self.control.SetCaretForeground("#FFFFFF")
		self.control.SetCaretLineBackground("#111111")
		self.control.SetCaretLineVisible(True)

	def OnNew(self, e):
		self.filename = ""
		self.control.SetValue("")

	def OnOpen(self, e):
		try:
			dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.FD_OPEN)
			if (dlg.ShowModal() == wx.ID_OK):
				self.filename = dlg.GetFilename()
				self.dirname = dlg.GetDirectory()
				f = open(os.path.join(self.dirname, self.filename), 'r')
				self.control.SetValue(f.read())
				f.close()
			dlg.Destroy()
		except:
			dlg = wx.MessageDialog(self, "Couldn't open file", "Error", wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()

	def OnSave(self, e):
		try:
			f = open(os.path.join(self.dirname, self.filename), 'w')
			f.write(self.control.GetValue())
			f.close()
		except:
			try:
				dlg = wx.FileDialog(self, "Save file as", self.dirname, "Untitled", "*.*", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
				if (dlg.ShowModal() == wx.ID_OK):
					self.filename = dlg.GetFilename()
					self.dirname = dlg.GetDirectory()
					f = open(os.path.join(self.dirname, self.filename), 'w')
					f.write(self.control.GetValue())
					f.close()
				dlg.Destroy()
			except:
				pass

	def OnSaveAs(self, e):
		try:
			dlg = wx.FileDialog(self, "Save file as", self.dirname, self.filename, "*.*", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
			if (dlg.ShowModal() == wx.ID_OK):
				self.filename = dlg.GetFilename()
				self.dirname = dlg.GetDirectory()
				f = open(os.path.join(self.dirname, self.filename), 'w')
				f.write(self.control.GetValue())
				f.close()
			dlg.Destroy()
		except:
			pass

	def OnClose(self, e):
		self.Close(True)

	def OnUndo(self, e):
		self.control.Undo()

	def OnRedo(self, e):
		self.control.Redo()

	def OnSelectAll(self, e):
		self.control.SelectAll()

	def OnCopy(self, e):
		self.control.Copy()

	def OnCut(self, e):
		self.control.Cut()

	def OnPaste(self, e):
		self.control.Paste()

	def OnToggleLineNumbers(self, e):
		if (self.lineNumbersEnabled):
			self.control.SetMarginWidth(1, 0)
			self.lineNumbersEnabled = False
		else:
			self.control.SetMarginWidth(1, self.leftMartinWidth)
			self.lineNumbersEnabled = True

	def OnAbout(self, e):
		dlg = wx.MessageDialog(self, "Simple GLSL editor written in Python.\nVersion 0.1 (BETA)", "About", wx.OK)
		dlg.ShowModal()
		dlg.Destroy()

	def UpdateLineCol(self, e):
		line = self.control.GetCurrentLine() + 1
		col = self.control.GetColumn(self.control.GetCurrentPos())
		stat = "Line %s, Column %s" % (line, col)
		self.StatusBar.SetStatusText(stat, 0)

	def OnLeftUp(self, e):
		self.UpdateLineCol(self)
		e.Skip()

	def OnCharEvent(self, e):
		keycode = e.GetKeyCode()
		controlDown = e.CmdDown()
		altDown = e.AltDown()
		shiftDown = e.ShiftDown()

		if (keycode == 14): # Ctrl + N
			self.OnNew(self)
		elif (keycode == 15): # Ctrl + O
			self.OnOpen(self)
		elif (keycode == 19): # Ctrl + S
			self.OnSave(self)
		elif (altDown and (keycode == 115)): # Alt + S
			self.OnSaveAs(self)
		elif (keycode == 23): # Ctrl + W
			self.OnClose(self)
		elif (keycode == 1): # Ctrl + A
			self.OnSelectAll(self)
		elif (keycode == 340): # F1
			self.OnAbout(self)
		else:
			e.Skip()

app = wx.App()
frame = MainWindow(None, "GLSL Editor")
app.MainLoop()
