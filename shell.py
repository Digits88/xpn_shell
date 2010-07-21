"""XPN Shell for python exploit developers.

http://xpnsbraindump.blogspot.com

email.xpn@gmail.com

This module provides exploit developers with a shell like environment 
without worrying about having to write a UI each time they develop an
exploit.

The implimentation is very simple, and is easily extended with commands
and variables.

THIS IS NOT A REPLACEMENT FOR METASPLOIT
========================================

As if ;). Metasploit is a full framework, this is just a simple UI for exploit
developers. The reason for its creation is my need for creating portable
exploits without taking the full metasploit framework with me.

This module can be imported or the exploit can be added to the end of the module
and distributed as one file (see example at the tail of this file)

Example:

# Typical usage for this module should be as follows:

class my_l33t_exploit(Exploit):
	def __init__(self.....)
		self.name = "My L33t Exploit"
		self.description = "A description of my L33T Exploit"

	def run(self, ui):
		param1 = ui.get_var("param1")
		param2 = ui.get_var("param2")

		# Leet exploit stuff here #

		ui.print_info("Host Exploited")

		# More leet stuff here #

		ui.print_warning("Unable to gain r00t")

exploit_obj = my_l33t_exploit()
exploit_ui = ui()
exploit_ui.title = "L33T Exploit!"
exploit_ui.add_var("param1", "Hostname to target", "127.0.0.1", required=True)
exploit_ui.add_var("param2", "TCP port to target", 8080, required=True)
exploit_ui.add_exploit(exploit_obj)
exploit_ui.run()

"""

import sys
import io
import re;

class UiException(Exception):
	def __init__(self, value):
		self.value = value;

	def __str__(self):
		return repr(self.value);

class ui:
	"""ui class for use by python exploit developers"""
	title = """

XPN Shell - Created by XPN (http://xpnsbraindump.blogspot.com)

	\n"""

	_stdout = 0
	_stdin = 0
	_stderr = 0

	# commands that the user will enter into our shell
	_commands = {}

	# holds the object of the exploit
	_exploit = None

	# signals when the exploit is running
	_exploit_running = False

	# shell variables
	_vars = {
		"prompt" : {"description": "Shell prompt character", "required": True, "value": "> "},
	}

	# control variable to allow stopping the running shell
	# TODO: Add this throughout where using within the running exploit is not advisable
	_shell_running = True

	def __init__(self, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
		# All handles must be file objects
		# TODO: Testing to test sockets instead of file handles

		if not isinstance(stdin, file):
			raise UiException("STDIN handle passed to __init__ is not a file object")
		else:
			self._stdin = stdin

		if not isinstance(stdout, file):
			raise UiException("STDOUT handle passed to __init__ is not a file object")
		else:
			self._stdout = stdout

		if not isinstance(stderr, file):
			raise UiException("STDERR handle passed to __init__ is not a file object")
		else:
			self._stderr = stderr

		self.add_command("help", self._help_command, "Usage: help command\n\tProvides help on a specified command\n", 0, 1)
		self.add_command("set", self._set_command, "Usage set [name=val]\n\tSets a variable for exploit use. To 'unset' a variable, use 'set var1='\n", 0, 1)
		self.add_command("unset", self._unset_command, "Usage unset varname\n\tClears a variable's value\n", 1, 1)
		self.add_command("exploit", self._exploit_command, "Usage: exploit\n\tStart the exploit\n", 0, 0)
		self.add_command("info", self._info_command, "Usage: info\n\tShows info on the exploit\n", 0, 0)
		self.add_command("quit", self._quit_command, "Usage: quit\n\tQuits the shell\n", 0, 0)

	def _is_exploit_running(self):
		return True if self._exploit_running else False

	def print_error(self, message):
		"""Print an error message to the user in the format

		[X] Error Message Here"""

		self._stdout.write("[x] {0}\n".format(message))
		
	def print_info(self, message):
		"""Print an info message to the user in the format
	
		[-] Info Message Here"""

		self._stdout.write("[-] {0}\n".format(message))
	
	def print_warn(self, message):
		"""Print a warning message to the user in the format

		[!] Warning Message Here"""

		self._stdout.write("[!] {0}\n".format(message))

	def print_raw(self, message):
		"""Print a raw message to the user. This contains no formatting"""
		self._stdout.write(message)
	
	def read_line(self):
		"""Returns a line read from the user"""
		return self._stdin.readline()

	def add_command(self, command, callback, description, min_args=0, max_args=0):
		"""Add a command to the shell for use by the user:

		add_command("test_cmd", self._test_cmd, "Usage: test_cmd param1 [param2]\\nA test command", min_args=1, max_args=2)

		command - String containing command 
		callback - Function that accepts 2 params
		description - A description of the command. This is recommended to have the format:
				"Usage: USAGE INFO HERE [PARAM1]\\n\\tDescription Here\n"
		min_args - Minimum number of argumentst that need to be provided
		max_args - Maximum number of arguments that need to be provided

		callback function must accept 2 commands for example:

			test_cmd(ui, params)

		Where:

			ui - Pointer to the UI instance object
			params - An array of arguments provided by the user

		All callbacks should not raise any exceptions !

		CANNOT BE CALLED WHILE EXPLOIT IS RUNNING"""

		# adds a command to our command dictionary
		if self._is_exploit_running():
			raise UiException("Exploit is already running")

		self._commands[command] = {"callback": callback, "description": description, "min_args": min_args, "max_args": max_args}

	def remove_command(self, command):
		"""Removes a command from the shell:

		remove_command("test_cmd")

		CANNOT BE CALLED WHILE EXPLOIT IS RUNNING"""

		# remove command from our command dictionary
		if self._is_exploit_running():
			raise UiException("Exploit is already running")

		del self._commands[command]

	def add_exploit(self, exploit):
		"""Add the exploit to the shell:

		add_exploit(my_exploit_object)

		CANNOT BE CALLED WHILE EXPLOIT IS RUNNING"""

		# TODO: Add ability for Multiple Exploits to be used

		if self._is_exploit_running():
			raise UiException("Exploit is already running")


		# exploit must derive from our 'exploit' class
		if not isinstance(exploit, Exploit):
			raise UiException("exploit object used with add_exploit() is not derived from the Exploit class")

		# if is a genuine exploit object, we assign this to be our exploit
		self._exploit = exploit

	def remove_exploit(self, exploit=None):
		"""Removes the exploit from the shell:

		NOTE: Please ignore the 'exploit' param for now, this will be in a future release to support multiple exploits

		remove_exploit()

		CANNOT BE CALLED WHILE EXPLOIT IS RUNNING"""
		# TODO: Add ability for Multiple Exploits to be used

		if self._is_exploit_running():
			raise UiException("Exploit is already running")


		# remove the object instance
		self._exploit = None

	def add_var(self, name, description, default=None, required=True):
		"""Add a variable to the shell:

		required - This param sets the variable as essential. If the user doesn't set the variable then the
			   exploit will not run

		add_var("test_var", "Test Variable", default="DEFAULT_VAL", required=True)

		CANNOT BE CALLED WHILE EXPLOIT IS RUNNING"""

		# add a variable to our shell variable dictionary

		if self._is_exploit_running():
			raise UiException("Exploit is already running")

		self._vars[name] = {"description": description, "required": required, "value": default}

	def remove_var(self, name):
		"""Remove a variable from the shell:

		name - The name of the variable to remove

		remove_var("test_var")

		CANNOT BE CALLED WHILE EXPLOIT IS RUNNING"""

		# remove the variable from our shell variable dictionary

		if self._is_exploit_running():
			raise UiException("Exploit is already running")

		del self._vars[name]

	def get_var(self, name):
		"""Returns the value of the shell variable
	
		get_var("test_var")"""

		# retrieve a variable from our shell variable dictionary, if it doesn't exist we throw an exception
		if self._vars.has_key(name):
			return self._vars[name]["value"]
		else:
			raise UiException("We do not have a variable called " + name)

	def set_var(self, name, value):
		"""Sets the value of the shell variable

		set_var("test_var", "test_value")

		CANNOT BE CALLED WHILE EXPLOIT IS RUNNING"""

		# set a variable in our shell variable dictionary, if it doesn't exist we throw an exception
		if self._is_exploit_running():
			raise UiException("Exploit is already running")

		if self._vars.has_key(name):
			self._vars[name]["value"] = value
		else:
			raise UiException("We do not have a variable called " + name)

	def run(self):
		"""Starts the main shell loop which will read commands from the user

		CANNOT BE CALLED WHILE EXPLOIT IS RUNNING"""

		# Starts the main loop of our shell to read commands from the user and pass for the command to be executed

		if self._is_exploit_running():
			raise UiException("Exploit is already running")

		prompt = ""
		line = ""

		self._shell_running = True

		self.print_raw(self.title)

		self.print_info("Please use the 'info' command for information on the exploit")

		try:
			while self._shell_running:
				try:
					prompt = self.get_var("prompt")
				except UiException as ex:
					self.print_raw("No prompt variable set, using default \">\"")
					self.add_var("prompt", "Shell prompt character", ">", True);
					prompt = self.get_var("prompt")
				
				self.print_raw("{0} ".format(prompt))
				line = self.read_line()

				try:
					self._process_command(line)
				except UiException as ex:
					self.print_error(ex)
		except KeyboardInterrupt:
			self.print_raw("\n")
			self.print_error("Quitting")
			quit()

	def stop(self):
		"""Stops execution of the shell"""
		self._shell_running = False

	def _info_command(self, ui, params):
		if self._exploit == None:
			# no exploit has been set !
			self.print_error("No exploit has been loaded, please contact the exploit vendor")
			return

		self.print_raw("Exploit Information\n==================\n\n")
		self.print_raw("{0}\n{1}\n".format(self._exploit.name, self._exploit.description))
		return

	def _quit_command(self, ui, params):
		self._shell_running = False
		return

	def _help_command(self, ui, params):
		if len(params) == 0:
			for command_name, command in self._commands.iteritems():
				self.print_raw("{0} - {1}\n".format(command_name, command["description"]))
		else:
			# params[0] should be the command
			if self._commands.has_key(params[0]):
				self.print_raw("{0}: {1}".format(params[0], self._commands[params[0]]["description"]))
			else:
				self.print_error("Unknown Command: {0}".format(params[0]))
		return

	def _unset_command(self, ui, params):
		if len(params) == 0:
			return

		self._set_command(ui, ["{0}=".format(params[0])])
	
		return
		

	def _set_command(self, ui, params):
		if len(params) == 0:
			# we need to print the existing vars

			self.print_raw("Shell Variables\n----------------\n\n")

			for var_name, var in self._vars.iteritems():
				self.print_raw("{0}={1}\t\t- {2} {3}\n".format(var_name, \
									var["value"] if var["value"] != None else "", \
									var["description"], \
									"[REQUIRED]" if var["required"] == True else ""\
									))

		else:
			# we need to set a variable

			param_split = params[0].split("=")

			if len(param_split) != 2:
				return

			try:
				if len(param_split[1]) == 0:
					# we want to unset our variable
					self.set_var(param_split[0], None)
				else:
					self.set_var(param_split[0], param_split[1])
			except UiException as e:
				self.print_error("No Shell Variable Named: {0}".format(param_split[0]))
				return

	def _exploit_command(self, ui, params):
		# this is where we launch the actual exploit 

		# first we need to check to make sure all required variables are accessable

		for var_name, var in self._vars.iteritems():
			if var["required"] == True:
				if var["value"] == None or var["value"] == "":
					self.print_error("Unable to execute exploit, required param missing: [{0}]".format(var_name))
					return

		if self._exploit == None:
			self.print_error("No exploit attached to Shell, see exploit vendor")
			return;

		self.print_raw("Starting Exploit: {0}\n{1}\n".format(self._exploit.name, self._exploit.description))
		self._exploit_running = True
		self._exploit.run(self)
		self._exploit_running = False


	def _process_command(self, line):
		command = ""
		params = []

		re_matches = re.findall("([^\\s\\n\\r\\0]+)", line);

		if len(re_matches) == 0:
			# no exception as the user may have just hit the enter key
			return

		command = re_matches[0]
		params = re_matches[1:]

		if not self._commands.has_key(command):
			raise UiException("Command: {0} does not exist".format(command))

		if len(params) < self._commands[command]["min_args"] or len(params) > self._commands[command]["max_args"]:
			# invalid arguments provided so we will show the user the correct usage
			self._process_command("help {0}".format(command))
			return

		try:
			self._commands[command]["callback"](self, params)
		except Exception as e:
			# capture all unknown exceptions rather than crashing our shell
			raise UiException("Command: {0} caused an exception: {1}".format(command, e))

class Exploit:
	"""Interface that must be inherited by an exploit.

	This is a VERY simple framework allowing the exploit writer to still be as creative as possible
	but to also be able to communicate with the UI"""

	name = "Add Exploit Name Here"
	description = "Add Exploit Description Here"

	def __init__(self):
		pass;

	def run(self, ui):
		"""This is called by the UI when the user issues the 'exploit' command

		ui - This is an instance to the running UI that the exploit writer can use to retrieve vars, print messages, quit etc""" 

		pass;

##########################################################################################################################################
# EXAMPLE																 #
##########################################################################################################################################

class my_exploit(Exploit):
	name = "Test Exploit"
	description = "My Test Exploit Description"

	def __init__(self):
		pass;

	def _test_command(self, ui, params):
		ui.print_info("CALLED OUR TEST COMAMND: ECHO '{0}'".format(params[0]))

	def run(self, ui):
		host = ui.get_var("TARGET_HOST")
		ui.print_info("We would have exploited {0} if this was a real exploit".format(host))
		
		
if __name__ == "__main__":


	exploit_obj = my_exploit()
	main_ui = ui()
	main_ui.title = """\

Simple Test Exploit

Just to show the usage of the exploit ui interface

Variables Required: 
	TARGET_HOST

Example Usage:
	set TARGET_HOST=127.0.0.1
	test_command WOOP_WOOP
	exploit

"""


	main_ui.add_var("TARGET_HOST", "Host to target", "127.0.0.1", required=True)
	main_ui.add_exploit(exploit_obj)
	main_ui.add_command("test_command", exploit_obj._test_command, "Usage: test_command PARAM\n\tDoes nothing, just a test\n", 1, 1)
	main_ui.run()
