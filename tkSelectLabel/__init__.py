import tkinter as tk

#SelectLabel, a tkinter widget that extends Text.  This widget is meant to have similar functionality to a Label, but with highlightable text.
class SelectLabel(tk.Text):
	def __init__(self, root, text="", justify=tk.CENTER, relief=tk.FLAT, wrap="none", shrink=True, **kwargs):
		if 'state' in kwargs.keys(): #intercept '-state', which is an option for Text, but not for SelectLabel
			raise tk.TclError('unknown option "-state"') #raise exception

		self.shrink = shrink #If shrink is true, then the widget's height and width will automatically be reduced to fit the text contents.  Else, the user may specify dimensions.
		super().__init__(root, relief=relief, wrap=wrap, **kwargs)
		super().tag_add(tk.ALL, '1.0', tk.END) #Add a Text tag to control text justification for all contents
		super().tag_config(tk.ALL, justify=justify)
		super().insert(tk.END, text, tk.ALL) #Add text contents
		super().delete('end - 1c') #delete trailing newline which is always added by insert()
		super().config(state=tk.DISABLED) #Keep the widget permanently disabled, which will keep the user from modifying the text contents
		if self.shrink:
			self.shrinkLabelToText()

	#configure, or config, is used to edit the widget's properties.  Overrides Text method
	def configure(self, **kwargs):
		if 'state' in kwargs.keys(): #intercept '-state', which is an option for Text, but not for SelectLabel
			raise tk.TclError('unknown option "-state"') #raise exception

		if 'text' in kwargs.keys(): #intercept '-text', , which is an option for SelectLabel, but not for Text
			text = kwargs.pop('text') #remove and get justify parameter
		else:
			text = super().get('1.0', tk.END) #get current text parameter

		if 'justify' in kwargs.keys(): #intercept '-justify', , which is an option for SelectLabel, but not for Text
			justify = kwargs.pop('justify') #remove and get justify parameter
		else:
			justify = super().tag_cget(tk.ALL, 'justify') #get current justify parameter

		if 'shrink' in kwargs.keys(): #intercept '-shrink', , which is an option for SelectLabel, but not for Text
			self.shrink = kwargs.pop('shrink') #update attribute

		super().config(state=tk.NORMAL, **kwargs) #enable text modification, and pass all other arguments
		super().delete("1.0", tk.END) #clear existing text
		super().insert(tk.END, text, tk.ALL) #add new text
		super().delete('end - 1c') #delete trailing newline which is always added by insert()
		super().tag_config(tk.ALL, justify=justify) #update justification
		super().config(state=tk.DISABLED) #disable text modification
		if self.shrink:
			self.shrinkLabelToText()

	config = configure #alternate function name

	#shrinkLabelToText, internal method to resize the widget to fit only the text contents
	def shrinkLabelToText(self):
		lines = super().get('1.0', tk.END).split('\n')
		height = len(lines) - 1
		width = max([len(line) for line in lines])
		super().config(height=height, width=width)
