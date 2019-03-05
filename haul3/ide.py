#!/usr/bin/python
# -*- coding: utf-8

import wxversion
#wxversion.select("2.8")
import wx, wx.html, wx.stc
import sys

import thread
import time


from haul.utils import *

from haul.langs.py.reader_py import *

from haul.langs.asm.writer_asm import *
from haul.langs.bas.writer_bas import *
from haul.langs.c.writer_c import *
from haul.langs.java.writer_java import *
from haul.langs.js.writer_js import *
from haul.langs.json.writer_json import *
from haul.langs.lua.writer_lua import *
from haul.langs.opl.writer_opl import *
from haul.langs.pas.writer_pas import *
from haul.langs.py.writer_py import *
from haul.langs.vbs.writer_vbs import *

from haul.project import HAULProject, HAULSource
from haul.builder import HAULTranslator

LANGS = [
	HAULWriter_asm,
	HAULWriter_bas,
	HAULWriter_c,
	HAULWriter_java,
	HAULWriter_js,
	HAULWriter_json,
	HAULWriter_lua,
	HAULWriter_opl,
	HAULWriter_pas,
	HAULWriter_py,
	HAULWriter_vbs,
]


def put(txt):
	print('ide:\t' + str(txt))



#STARTUP_FILE = 'examples/hello.py'
#STARTUP_FILE = 'examples/small.py'
STARTUP_FILE = 'examples/shellmini.py'


if wx.Platform == '__WXMSW__':
	faces = { 'times': 'Times New Roman',
			  'mono' : 'Courier New',
			  'helv' : 'Arial',
			  'other': 'Comic Sans MS',
			  'size' : 10,
			  'size2': 8,
			 }
elif wx.Platform == '__WXMAC__':
	faces = { 'times': 'Times New Roman',
			  'mono' : 'Monaco',
			  'helv' : 'Arial',
			  'other': 'Comic Sans MS',
			  'size' : 12,
			  'size2': 10,
			 }
else:
	faces = { 'times': 'Times',
			  'mono' : 'Courier',
			  'helv' : 'Helvetica',
			  'other': 'new century schoolbook',
			  'size' : 12,
			  'size2': 10,
			 }

aboutText = """<p>Sorry, there is no information about this program. It is
running on version %(wxpy)s of <b>wxPython</b> and %(python)s of <b>Python</b>.
See <a href="http://wiki.wxpython.org">wxPython Wiki</a></p>""" 


class HtmlWindow(wx.html.HtmlWindow):
	def __init__(self, parent, id, size=(600,400)):
		wx.html.HtmlWindow.__init__(self,parent, id, size=size)
		if "gtk2" in wx.PlatformInfo:
			self.SetStandardFonts()
	
	def OnLinkClicked(self, link):
		wx.LaunchDefaultBrowser(link.GetHref())
	
class AboutBox(wx.Dialog):
	def __init__(self):
		wx.Dialog.__init__(self, None, -1, "About <<project>>",
			style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.RESIZE_BORDER|
				wx.TAB_TRAVERSAL)
		hwin = HtmlWindow(self, -1, size=(400,200))
		vers = {}
		vers["python"] = sys.version.split()[0]
		vers["wxpy"] = wx.VERSION_STRING
		hwin.SetPage(aboutText % vers)
		btn = hwin.FindWindowById(wx.ID_OK)
		irep = hwin.GetInternalRepresentation()
		hwin.SetSize((irep.GetWidth()+25, irep.GetHeight()+10))
		self.SetClientSize(hwin.GetSize())
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

class EditorControl(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		box = wx.BoxSizer(wx.HORIZONTAL)
		
		monospace_font = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		#tc = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)
		#tc = wx.TextCtrl(parent, wx.ID_ANY, size=(300,100), style=wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
		#tc = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_MULTILINE|wx.HSCROLL|wx.VSCROLL)
		tc = wx.stc.StyledTextCtrl(self, wx.ID_ANY, style=wx.TE_MULTILINE|wx.HSCROLL|wx.VSCROLL)
		#tc.SetValue('# The quick brown fox jumps over the lazy dog.\n' * 50)
		#tc.SetFont(monospace_font)
		#tc.SetSizeHints(128,24, 1024,64)
		#tc.SetToolTip(wx.ToolTip('Human readable sample name'))
		#tc.Bind(wx.EVT_TEXT_ENTER, self.details_on_change, self.name_entry)
		
		tc.SetViewWhiteSpace(True)
		#tc.SetViewEOL(True)
		tc.SetProperty("fold", "1")
		tc.SetProperty("tab.timmy.whinge.level", "1")
		tc.SetMargins(0,0)
		
		
		# Line numbers
		tc.SetMarginType(0, wx.stc.STC_MARGIN_NUMBER)
		tc.SetMarginWidth(0, 32)
		
		
		tc.SetMarginType(1, wx.stc.STC_MARGIN_SYMBOL)
		tc.SetMarginMask(1, wx.stc.STC_MASK_FOLDERS)
		tc.SetMarginSensitive(1, True)
		tc.SetMarginWidth(1, 12)
		
		
		# Global default styles for all languages
		tc.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT,     "face:%(mono)s,size:%(size)d" % faces)
		tc.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER,  "back:#C0C0C0,face:%(helv)s,size:%(size2)d" % faces)
		tc.StyleSetSpec(wx.stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces)
		tc.StyleSetSpec(wx.stc.STC_STYLE_BRACELIGHT,  "fore:#FFFFFF,back:#0000FF,bold")
		tc.StyleSetSpec(wx.stc.STC_STYLE_BRACEBAD,    "fore:#000000,back:#FF0000,bold")
		#tc.StyleClearAll()  # Reset all to be like the default
		
		# Python styles
		# Default 
		tc.StyleSetSpec(wx.stc.STC_P_DEFAULT, "fore:#000000,face:%(mono)s,size:%(size)d" % faces)
		# Comments
		tc.StyleSetSpec(wx.stc.STC_P_COMMENTLINE, "fore:#007F00,face:%(other)s,size:%(size)d" % faces)
		# Number
		tc.StyleSetSpec(wx.stc.STC_P_NUMBER, "fore:#007F7F,size:%(size)d" % faces)
		# String
		tc.StyleSetSpec(wx.stc.STC_P_STRING, "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces)
		# Single quoted string
		tc.StyleSetSpec(wx.stc.STC_P_CHARACTER, "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces)
		# Keyword
		tc.StyleSetSpec(wx.stc.STC_P_WORD, "fore:#00007F,bold,size:%(size)d" % faces)
		# Triple quotes
		tc.StyleSetSpec(wx.stc.STC_P_TRIPLE, "fore:#7F0000,size:%(size)d" % faces)
		# Triple double quotes
		tc.StyleSetSpec(wx.stc.STC_P_TRIPLEDOUBLE, "fore:#7F0000,size:%(size)d" % faces)
		# Class name definition
		tc.StyleSetSpec(wx.stc.STC_P_CLASSNAME, "fore:#0000FF,bold,underline,size:%(size)d" % faces)
		# Function or method name definition
		tc.StyleSetSpec(wx.stc.STC_P_DEFNAME, "fore:#007F7F,bold,size:%(size)d" % faces)
		# Operators
		tc.StyleSetSpec(wx.stc.STC_P_OPERATOR, "bold,size:%(size)d" % faces)
		# Identifiers
		tc.StyleSetSpec(wx.stc.STC_P_IDENTIFIER, "fore:#000000,face:%(helv)s,size:%(size)d" % faces)
		# Comment-blocks
		tc.StyleSetSpec(wx.stc.STC_P_COMMENTBLOCK, "fore:#7F7F7F,size:%(size)d" % faces)
		# End of line where string is not closed
		tc.StyleSetSpec(wx.stc.STC_P_STRINGEOL, "fore:#000000,face:%(mono)s,back:#E0C0E0,eol,size:%(size)d" % faces)
		
		tc.SetCaretForeground("BLUE")
		
		
		
		
		
		# setup some markers
		#tc.SetMarginType(1, wx.stc.STC_MARGIN_SYMBOL)
		#tc.MarkerDefine(0, wx.stc.STC_MARK_ROUNDRECT, "#CCFF00", "GREEN")
		#tc.MarkerDefine(1, wx.stc.STC_MARK_CIRCLE, "FOREST GREEN", "SIENNA")
		#tc.MarkerDefine(2, wx.stc.STC_MARK_SHORTARROW, "blue", "blue")
		#tc.MarkerDefine(3, wx.stc.STC_MARK_ARROW, "#00FF00", "#00FF00")
		tc.MarkerDefine(0, wx.stc.STC_MARK_ARROW, "YELLOW", "GREEN")
		tc.MarkerDefine(1, wx.stc.STC_MARK_ARROW, "WHITE", "RED")
		
		"""
		# put some markers on some lines
		tc.MarkerAdd(17, 0)
		tc.MarkerAdd(18, 1)
		tc.MarkerAdd(19, 2)
		tc.MarkerAdd(20, 3)
		tc.MarkerAdd(20, 0)
		
		
		# and an indicator or two
		tc.IndicatorSetStyle(0, wx.stc.STC_INDIC_SQUIGGLE)
		tc.IndicatorSetForeground(0, wx.RED)
		tc.IndicatorSetStyle(1, wx.stc.STC_INDIC_DIAGONAL)
		tc.IndicatorSetForeground(1, wx.BLUE)
		tc.IndicatorSetStyle(2, wx.stc.STC_INDIC_STRIKE)
		tc.IndicatorSetForeground(2, wx.RED)
		
		tc.StartStyling(836, wx.stc.STC_INDICS_MASK)
		tc.SetStyling(10, wx.stc.STC_INDIC0_MASK)
		tc.SetStyling(8, wx.stc.STC_INDIC1_MASK)
		tc.SetStyling(10, wx.stc.STC_INDIC2_MASK | wx.stc.STC_INDIC1_MASK)
		
		# add some annotations
		tc.AnnotationSetText(23, "\nThis is an annotaion, it is not part of \nthe document's text.\n")
		tc.AnnotationSetVisible(wx.stc.STC_ANNOTATION_BOXED)
		tc.AnnotationSetStyle(23, 5)  # line number, style number
		"""
		
		
		tc.EmptyUndoBuffer()
		tc.Colourise(0, -1)
		
		self.tc = tc
		
		box.Add(tc, proportion=1, flag=wx.ALL | wx.EXPAND, border=0)
		self.SetSizer(box)
		self.Layout()
		
	def set_data(self, text):
		#self.tc.StyleClearAll()
		self.tc.SetValue(text)
		#self.tc.AddText(text)
	
	def get_data(self):
		return self.tc.GetValue()
	
	def set_cursor(self, p, scroll=True):
		#self.tc.SetCurrentPos(p)
		
		#self.tc.StyleClearAll()
		self.tc.MarkerDeleteAll(0)
		
		self.tc.SetEmptySelection(p)
		
		# Mark the line
		l = self.tc.GetCurrentLine()
		self.tc.MarkerAdd(l, 0)
		
		if scroll:
			self.tc.ScrollToLine(l)
	
	def show_error(self, message, p):
		self.tc.MarkerDeleteAll(0)
		self.tc.SetEmptySelection(p)
		l = self.tc.GetCurrentLine()
		
		self.tc.MarkerAdd(l, 1)
		self.tc.AnnotationSetText(l, '\n' + message + '\n')
		self.tc.AnnotationSetVisible(wx.stc.STC_ANNOTATION_BOXED)
		#self.tc.AnnotationSetStyle(l, 0)  # line number, style number
		
		self.tc.ScrollToLine(l)


class TreeControl(wx.TreeCtrl):
	def __init__(self, parent, id, pos, size, style):
		wx.TreeCtrl.__init__(self, parent, id, pos, size, style)
		
		self.root = self.AddRoot('ROOT')
		#self.SetPyData(self.root, ('key', 'value'))
		
		osi = self.AppendItem(self.root, 'Some entry')
		
		self.Expand(self.root)
	
	def clear(self):
		#self.DeleteAllItems()
		self.DeleteChildren(self.root)
	
	def render(self, m):
		self.clear()
		
		mi = self.add_module(self.root, m)
		self.Expand(mi)
		
	
	
	def select_object(self, o, selectednode=None):
		"Search for the item that has the given object as PyData"
		
		if selectednode == None:
			selectednode = self.root
		
		#put('Searching in ' + str(selectednode))
		
		# First perform the action on the first object separately
		childcount = self.GetChildrenCount(selectednode, False)
		#put('Childcount: {}'.format(childcount))
		if childcount == 0:
			return None
		
		(item,cookie) = self.GetFirstChild(selectednode)
		#put('A	' + str(self.GetPyData(item)))
		if self.GetPyData(item) == o:
			#put('Found! ' + str(item))
			self.Expand(item)
			self.SelectItem(item, True)
			return item
		
		r = self.select_object(o, item)
		if r is not None: return r
		
		while childcount > 1:
			childcount = childcount - 1
			# Then iterate over the rest of objects
			(item,cookie) = self.GetNextChild(item, cookie)
			if self.GetPyData(item) == o:
				#put('Found! ' + str(item))
				self.Expand(item)
				self.SelectItem(item, True)
				return item
			
			r = self.select_object(o, item)
			if r is not None: return r
		return None
	
	def add_id(self, parent, id):
		ii = self.AppendItem(parent, 'id "{}"'.format(id.name))
		self.SetPyData(ii, id)
		# kind
		# data
		# value
		# parentNamespace
		return ii
	
	def add_name(self, parent, name):
		ni = self.AppendItem(parent, 'name: "{}"'.format(name))
		return ni
	
	def add_module(self, parent, m):
		mi = self.AppendItem(parent, 'module "{}"'.format(m.name))
		self.SetPyData(mi, m)
		self.add_name(mi, m.name)
		
		# imports
		
		self.add_namespace(mi, m.namespace)
		
		# classes
		
		if (len(m.funcs) > 0):
			fsi = self.AppendItem(mi, 'funcs[{}]'.format(len(m.funcs)))
			for f in m.funcs:
				self.add_func(fsi, f)
		
		self.add_block(mi, m.block)
		return mi
	
	def add_namespace(self, parent, ns):
		nsi = self.AppendItem(parent, 'namespace "{}"'.format(ns.name))
		self.SetPyData(nsi, ns)
		#self.add_name(nsi, ns.name)
		
		if (len(ns.ids) > 0):
			nsii = self.AppendItem(nsi, 'ids[{}]'.format(len(ns.ids)))
			for id in ns.ids:
				self.add_id(nsii, id)
		
		# nss
		if (len(ns.nss) > 0):
			nssi = self.AppendItem(nsi, 'sub-namespaces[{}]'.format(len(ns.nss)))
			"""
			for cns in ns.nss:
				self.add_namespace(nssi, cns)
			"""
		
		return nsi
	
	def add_block(self, parent, b):
		bi = self.AppendItem(parent, 'block "{}"'.format(b.name))
		self.SetPyData(bi, b)
		#self.add_name(bi, b.name)
		
		if BLOCKS_HAVE_LOCAL_NAMESPACE:
			self.add_namespace(bi, b.namespace)	# If using block namespaces
		
		if (len(b.instrs) > 0):
			isi = self.AppendItem(bi, 'instrs[{}]'.format(len(b.instrs)))
			for i in b.instrs:
				self.add_instruction(isi, i)
		
		return bi
	
	def add_func(self, parent, f):
		fi = self.AppendItem(parent, 'func "{}"'.format(f.id.name))
		self.SetPyData(fi, f)
		self.add_id(fi, f.id)
		
		self.add_type(fi, f.returnType)
		self.add_args(fi, f.args)
		
		self.add_namespace(fi, f.namespace)
		self.add_block(fi, f.block)
		
		return fi
	
	def add_instruction(self, parent, instr):
		#ii = self.AppendItem(parent, 'instr {}')
		
		if (instr.call):
			ii = self.AppendItem(parent, 'instr (call) {}'.format(instr.call.id.name))
			self.add_call(ii, instr.call)
		elif (instr.control):
			ii = self.AppendItem(parent, 'instr (control) {}'.format(instr.control.controlType))
			self.add_control(ii, instr.control)
		else:
			ii = self.AppendItem(parent, 'instr')
		
		self.SetPyData(ii, instr)
		
		if (instr.comment):
			self.AppendItem(ii, 'comment: "{}"'.format(instr.comment))
		
		return ii
	
	def add_control(self, parent, c):
		ci = self.AppendItem(parent, 'control: {}'.format(c.controlType))
		self.SetPyData(ci, c)
		#self.AppendItem(ci, 'controlType: "{}"'.format(c.controlType))
		
		if (len(c.exprs) > 0):
			cei = self.AppendItem(ci, 'exprs[{}]'.format(len(c.exprs)))
			for e in c.exprs:
				self.add_expression(cei, e)
		
		if (len(c.blocks) > 0):
			cbi = self.AppendItem(ci, 'blocks[{}]'.format(len(c.blocks)))
			for b in c.blocks:
				self.add_block(cbi, b)
		
		return ci
	
	def add_call(self, parent, c):
		ci = self.AppendItem(parent, 'call "{}"'.format(c.id.name))
		self.SetPyData(ci, c)
		self.add_id(ci, c.id)
		
		#self.add_args(ci, c.args)
		ai = self.AppendItem(ci, 'args[{}]'.format(len(c.args)))
		for a in c.args:
			self.add_expression(ai, a)
		
		return ci
	
	def add_expression(self, parent, e):
		ei = self.AppendItem(parent, 'expression')
		self.SetPyData(ei, e)
		
		if (e.value): self.add_value(ei, e.value)
		if (e.var): self.add_id(ei, e.var)
		if (e.call): self.add_call(ei, e.call)
		if (e.returnType): self.add_type(ei, e.returnType)
		# call
		# return
		return ei
	
	def add_args(self, parent, args):
		ai = self.AppendItem(parent, 'args[{}]'.format(len(args)))
		for arg in args:
			#self.add_variable(ai, arg)
			self.add_id(ai, arg)
		return ai
	
	def add_variable(self, parent, v):
		return self.add_id(parent, v)
	
	def add_value(self, parent, v):
		vi = self.AppendItem(parent, 'value "{}"'.format(str(v)))
		# type, data?
		return vi
	
	def add_type(self, parent, t):
		ti = self.AppendItem(parent, 'type "{}"'.format(t))
		return ti


class MainFrame(wx.Frame):
	def __init__(self):
		#wx.Frame.__init__(self, None, -1, title='HAUL Editor', pos=wx.DefaultPosition, size=wx.DefaultSize)
		wx.Frame.__init__(self, None, -1, title='HAUL Editor', pos=(0,0), size=(1280,960))
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		
		menuBar = wx.MenuBar()
		menu = wx.Menu()
		m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
		self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
		menuBar.Append(menu, "&File")
		menu = wx.Menu()
		m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
		self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
		menuBar.Append(menu, "&Help")
		self.SetMenuBar(menuBar)
		
		self.statusbar = self.CreateStatusBar()
		self.statusbar.SetStatusText('Ready')
		
		self.filename = '?'
		self.module = None
		#self.WriterClass = HAULWriter_asm
		#self.WriterClass = HAULWriter_bas
		#self.WriterClass = HAULWriter_c
		#self.WriterClass = HAULWriter_java
		self.WriterClass = HAULWriter_js
		#self.WriterClass = HAULWriter_json
		#self.WriterClass = HAULWriter_lua
		#self.WriterClass = HAULWriter_opl
		#self.WriterClass = HAULWriter_pas
		#self.WriterClass = HAULWriter_py
		#self.WriterClass = HAULWriter_vbs
		
		
		"""
		panel = wx.Panel(self)
		box = wx.BoxSizer(wx.VERTICAL)
		
		m_text = wx.StaticText(panel, -1, "Hello World!")
		m_text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		m_text.SetSize(m_text.GetBestSize())
		box.Add(m_text, 0, wx.ALL, 10)
		
		m_close = wx.Button(panel, wx.ID_CLOSE, "Close")
		m_close.Bind(wx.EVT_BUTTON, self.OnClose)
		box.Add(m_close, 0, wx.ALL, 10)
		
		panel.SetSizer(box)
		panel.Layout()
		"""
		
		sizer_main = wx.BoxSizer(wx.HORIZONTAL)
		"""
		self.splitter = wx.SplitterWindow(self, wx.ID_ANY)
		self.splitter.SetMinimumPaneSize(20)
		
		self.panel_editor1 = wx.Panel(self.splitter, wx.ID_ANY)
		self.panel_editor2 = wx.Panel(self.splitter, wx.ID_ANY)
		self.panel_tree = wx.Panel(self.splitter, wx.ID_ANY)
		
		
		self.editor1 = EditorControl(self.panel_editor1)
		sizer_editor1 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_editor1.Add(self.editor1, 1, wx.EXPAND, 0)
		self.panel_editor1.SetSizer(sizer_editor1)
		
		self.editor2 = EditorControl(self.panel_editor2)
		sizer_editor2 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_editor2.Add(self.editor2, 1, wx.EXPAND, 0)
		self.panel_editor2.SetSizer(sizer_editor2)
		
		self.tree = TreeControl(self.panel_tree, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_HAS_BUTTONS)    
		sizer_tree = wx.BoxSizer(wx.HORIZONTAL)
		sizer_tree.Add(self.tree, 1, wx.EXPAND, 0)
		self.panel_tree.SetSizer(sizer_tree)
		
		#self.splitter.SplitVertically(sizer_editor1, self.panel_tree, sizer_editor2)
		self.splitter.SplitVertically(self.panel_editor1, self.panel_tree)
		
		
		sizer_main.Add(self.splitter, 1, wx.EXPAND, 0)
		"""
		
		
		self.editor1 = EditorControl(self)
		self.editor1.tc.SetLexer(wx.stc.STC_LEX_PYTHON)
		self.editor1.Bind(wx.stc.EVT_STC_MARGINCLICK, self.editor1_on_click)
		self.editor1.Bind(wx.stc.EVT_STC_DOUBLECLICK, self.editor1_on_click)
		
		panel2 = wx.Panel(self, wx.ID_ANY)
		panel2_sizer = wx.BoxSizer(wx.VERTICAL)
		
		
		choices = []
		i = 0
		s = 0
		for W in LANGS:
			if (W == self.WriterClass):
				s = i
			label = str(W.__name__)
			#self.choice2.SetString(i, label)
			choices.append(label)
			i += 1
		self.choice2 = wx.Choice(panel2, wx.ID_ANY, choices=choices)
		self.choice2.Bind(wx.EVT_CHOICE, self.choice2_on_choice)
		self.choice2.SetSelection(s)
		panel2_sizer.Add(self.choice2, 0, wx.EXPAND, 0)
		
		self.editor2 = EditorControl(panel2)
		self.editor2.Bind(wx.stc.EVT_STC_MARGINCLICK, self.editor2_on_click)
		self.editor2.Bind(wx.stc.EVT_STC_DOUBLECLICK, self.editor2_on_click)
		panel2_sizer.Add(self.editor2, 1, wx.EXPAND, 0)
		panel2.SetSizer(panel2_sizer)
		
		self.tree = TreeControl(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_HAS_BUTTONS)    
		self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.tree_on_select)
		
		
		
		sizer_main.Add(self.editor1, 3, wx.EXPAND, 0)
		sizer_main.Add(panel2, 3, wx.EXPAND, 0)
		sizer_main.Add(self.tree, 1, wx.EXPAND, 0)
		
		self.SetSizer(sizer_main)
		self.Layout()
		
	
	def OnClose(self, event):
		self.Destroy()
		sys.exit(0)
		
	
	def OnAbout(self, event):
		dlg = AboutBox()
		dlg.ShowModal()
		dlg.Destroy()
	
	
	def choice2_on_choice(self, event):
		i = self.choice2.GetSelection()
		put('Switching to #{}...'.format(i))
		self.WriterClass = LANGS[i]
		put('Selected new WriterClass {}'.format(str(self.WriterClass)))
		self.translate()
		
	
	def editor1_on_click(self, event):
		# Get source cursor pos
		p = self.editor1.tc.GetCurrentPos()
		
		# Now find something close to it
		o, best = self.get_object_at(p, dest=False)
		
		# Show in tree
		self.tree.select_object(o)
		
		# Select it in both editors
		if o.origin is not None:
			self.editor1.set_cursor(o.origin, scroll=False)
		
		if o.destination is not None:
			self.editor2.set_cursor(o.destination, scroll=True)
		
	
	def editor2_on_click(self, event):
		# Get source cursor pos
		p = self.editor2.tc.GetCurrentPos()
		
		# Now find something close to it
		o, best = self.get_object_at(p, dest=True)
		
		# Show in tree
		self.tree.select_object(o)
		
		# Select it in both editors
		if o.origin is not None:
			self.editor1.set_cursor(o.origin, scroll=True)
		
		if o.destination is not None:
			self.editor2.set_cursor(o.destination, scroll=False)
		
	
	def get_object_at(self, p, dest):
		return self.get_object_at_block(dest, p, self.module, self.module, self.module.origin)
	
	def get_object_at_block(self, dest, p, o_check, o0, best0):
		# Check the object itself
		o, best = self.get_object_at_check(dest, p, o_check, o0, best0)
		
		# Check its functions (if exist)
		if hasattr(o_check, 'funcs'):
			for f in o_check.funcs:
				o, best = self.get_object_at_block(dest, p, f, o, best)
		
		if hasattr(o_check, 'block'):
			o, best = self.get_object_at_block(dest, p, o_check.block, o, best)
		
		if hasattr(o_check, 'blocks'):
			for b in o_check.blocks:
				o, best = self.get_object_at_block(dest, p, b, o, best)
		
		if hasattr(o_check, 'instrs'):
			for i in o_check.instrs:
				o, best = self.get_object_at_check(dest, p, i, o, best)
		
		return o, best
	
	def get_object_at_check(self, dest, p, o, o0, best0):
		if dest:
			if (o.destination <= p) and (o.destination >= best0):
				return o, o.destination
		else:
			if (o.origin <= p) and (o.origin >= best0):
				return o, o.origin
		return o0, best0
	
	
	def tree_on_select(self, event):
		"Double-click on tree item"
		
		# Get tree item
		i = self.tree.GetFocusedItem()
		
		# Check what it is
		#data = self.tree.GetItemData(i)
		data = self.tree.GetPyData(i)
		#put('data=' + str(data))
		
		if (hasattr(data, 'origin') and data.origin is not None):
			put('origin={}'.format(data.origin))
			self.editor1.set_cursor(data.origin)
		
		if (hasattr(data, 'destination') and data.destination is not None):
			put('destination={}'.format(data.destination))
			self.editor2.set_cursor(data.destination)
		
	
	def load_file(self, filename):
		self.filename = filename
		with open(filename, 'rb') as h:
			self.editor1.set_data(h.read())
		
		
		self.translate()
	
	def translate(self):
		input_filename = self.filename
		text = self.editor1.get_data().encode('ascii','ignore')
		
		stream_in = StringReader(text)
		
		stream_out = StringWriter()
		
		"""
		# Read it
		reader = HAULReader_py(stream=stream_in, filename=input_filename)
		
		# Translate it
		writer = self.WriterClass(stream_out)
		
		monolithic = True	# Use simple (but good) monolithic version (True) or a smart multi-pass streaming method (False)
		reader.seek(0)
		"""
		
		put('Translating using {}...'.format(str(self.WriterClass)))
		try:
			#self.module = writer.stream(reader, namespace=ns, monolithic=monolithic)	# That's where the magic happens!
			
			"""
			# Translate it (old, without HAULTranslator)
			t = HAULTranslator(HAULReader_py, self.WriterClass)
			t.process_lib('hio', FileReader('libs/hio.py'))
			self.module = t.translate(name=input_filename, stream_in=stream_in, stream_out=stream_out)
			"""
			
			# Translate it (using HAULProject / HAULTranslator)
			p = HAULProject('example')
			p.sources_path = 'examples'
			
			p.add_lib('hio')
			
			#p.add_source('small')
			#p.add_source('bastest')
			#p.add_source(input_filename)
			#p.add_source_stream(stream_in, uri=input_filename)
			
			t = HAULTranslator(HAULReader_py, self.WriterClass)	#, dialect=DIALECT_MS)
			#t.translate_project(p, output_path='build', dest_extension='bas')
			
			# Only translate one source/stream
			for l in p.libs:
				t.process_lib(l.name, l.stream, l.uri)
			
			source = HAULSource(name=input_filename, stream=stream_in, uri=input_filename)
			self.module = t.translate_source(source, stream_out, close_stream=True)
			
			
			
		except HAULParseError as e:
			put('Parse error: ' + e.message + ' in ' + str(e.token))
			self.editor1.show_error(e.message, e.token.originByte)
		else:
			# Show it
			self.tree.render(self.module)
			
		
		self.editor2.set_data(stream_out.r)
		
		

class MainApp(wx.App):
	def OnInit(self):
		self.frame = MainFrame()
		self.frame.Show()
		
		self.frame.load_file(STARTUP_FILE)
		
		return True

if __name__ == '__main__':
	
	put('Start...')
	app = MainApp(redirect=not True)	# Without that, the window will not show when starting the script as a child process under Windows
	put('MainLoop...')
	app.MainLoop()
	
