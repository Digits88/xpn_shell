import sys
import io
import re;

class UiException(Exception):
	def __init__(self, value):
		self.value = value;

	def __str__(self):
		return repr(self.value);

class ui:
	title = """

XPN Shell - Created by XPN (http://xpnsbraindump.blogspot.com)

	\n"""

	_stdout = 0
	_stdin = 0
	_stderr = 0

	_commands = {
		"help"  : {"callback": None, "description": "Provides help on a specified command\n"},
		"set"   : {"callback": None, "description": "Sets a variable for exploit use\n"},
	}

	_exploit = 0;

	_vars = {
		"prompt" : {"description": "Shell prompt character", "required": True, "value": "> "},
	}

	_shell_running = True

	def __init__(self, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
		self._stdin = stdin
		self._stdout = stdout
		self._stderr = stderr

	def print_error(self, message):
		self._stdout.write("[x] " + message + "\n")
		
	def print_info(self, message):
		self._stdout.write("[-] " + message + "\n")
	
	def print_warn(self, message):
		self._stdout.write("[!] " + message + "\n")

	def print_raw(self, message):
		self._stdout.write(message)
	
	def read_line(self):
		return self._stdin.readline()

	def add_command(self, command, callback, description):
		self._commands[command] = {"callback": callback, "description": description}

	def remove_command(self, command):
		del self._commands[command]

	def add_exploit(self, exploit):
		if not isinstance(exploit, Exploit):
			raise UiException("exploit object used with add_exploit() is not derived from the Exploit class")

		self._exploit = exploit

	def clear_exploit(self, exploit):
		self._exploit = 0

	def add_var(self, name, description, default=None, required=True):
		self._vars[name] = {"description": description, "required": required, "value": default}

	def remove_var(self, name):
		del self._vars[name]

	def get_var(self, name):
		if self._vars.has_key(name):
			return self._vars[name]["value"]
		else:
			raise UiException("We do not have a variable called " + name)

	def set_var(self, name, value):
		if self._vars.has_key(name):
			self._vars[name]["value"] = value
		else:
			raise UiException("We do not have a variable called " + name)

	def run(self):
		prompt = ""
		line = ""

		self._shell_running = True

		self.print_raw(self.title)

		while self._shell_running:
			try:
				prompt = self.get_var("prompt")
			except UiException as ex:
				self.print_raw("No prompt variable set, using default \">\"")
				self.add_var("prompt", "Shell prompt character", ">", True);
				prompt = self.get_var("prompt")
			
			self.print_raw(prompt + " ")
			line = self.read_line()

			self._process_command(line)

	def stop(self):
		self._shell_running = False

	def _help_command(self, params):
		pass;

	def _set_command(self, params):
		pass;

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
			raise UiException("Command: %s does not exist" % (command))

		self._commands[command]["callback"](params)
			


	
		
		
		

	

	
if __name__ == "__main__":
	main_ui = ui()
	main_ui.run()
