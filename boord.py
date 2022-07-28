#### BAZEB00RD ####
# - - - - - - - - #
#  Balance Board  #
#  API to commun  #
#  icate with it  #
###################
# Need help?  vvv #
# xpazr@yaani.com #
# @e.timur.trn IG #
###################

version = "0.1"

CONTINUOUS_REPORTING     = "04"
COMMAND_LIGHT            = "11"
COMMAND_REPORTING        = "12"
COMMAND_REQUEST_STATUS   = "15"
COMMAND_REGISTER         = "16"
COMMAND_READ_REGISTER    = "17"
INPUT_STATUS             = "20"
INPUT_READ_DATA          = "21"
EXTENSION_8BYTES         = "32"
TOPRIGHT = 0
TOPLEFT = 2
BOTLEFT = 3
BOTRIGHT = 1
BT_NAME                  = "Nintendo RVL-WBC-01"
LOCAL_CALIBRATION_SAMPLE = ["a1210000f000240bc54c890b66075f1286533c12410e12", ""] # First packet, second packet will be entered later.
LOCAL_DATA_SAMPLE        = "a13200000aa54c9c0b3b0630"

import bluetooth
import sys
import time
import logging
from textwrap import wrap
import binascii

if sys.argv[1]:
	logging.basicConfig(format='D [ %(levelname)s ] %(message)s', level=logging.DEBUG) # If you run it with "python3 boord.py debug" it will just debug it.
else:
	logging.basicConfig(format='D [ %(levelname)s ] %(message)s', level=logging.INFO)

def fetch_data(data, type):
		# The data given should be either like LOCAL_DATA_SAMPLE or should go like \x00\x11\x22 (example)
		# For just a string (11223344aabb), use "DECRYPT"
		# For a hex string (\x11\x22\xab), use "ENCODED"
		
		# This will create an array like ["00", "11", "22"], each value representing a byte.
		end_value = ""
		if type == "DECRYPT":
			if data[0:2] == "a1":
				end_value = wrap(data[2:], 2)
				# If the values start with a1, it's most likely in a receive loop. We do not need the first byte.
				# We would only need the first byte to determine what type the data is and the rest.
			else:
				end_value = wrap(data, 2)
				# This is just common wrapping
			return end_value
		elif type == "ENCODED":
			# This is a string that goes like \x11\x22\x33
			value = data.hex()
			return fetch_data(value, "DECRYPT")
		elif type == "TO_STRING":
			# This is just for converting it to a sting
			return data.hex()

def hex2int(data):
	return int(str(data), 16)
	# Very simple hex to decimal function

class Boord:
	def __init__(self):
		self.receivesocket = None
		self.controlsocket = None
		self.calibration = []
		self.calibrated = False
		self.LED = False
		self.address = None
		self.connection = False
		try:
			self.receivesocket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
			self.controlsocket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
		except ValueError:
			logging.critical("Bluetooth could not be located.")
			logging.debug("L2CAP couldn't be enabled")
		 
	def discover(self, sec=6):
		address = None
		if self.connection:
			logging.info("Already connected to boord. No need to discover again.")
			logging.debug("If it's not, try restarting the app.")
		else:
			logging.info("Press the red (or black, if you're too cool) sync button in the battery slot of the board.")
			logging.info(f"I will start scanning now, make sure your boord will still be in sync mode for {sec} seconds.")
			bluetooth_address = bluetooth.discover_devices(duration=sec, lookup_names=True) 
			logging.debug(f"Address list: {bluetooth_address}")
			for device in bluetooth_address:
				if device[1] == BT_NAME or device[1] == "Nintendo RVL-WBC-01":
					address = device[0]
					logging.info(f"A boord has been found! ({address})")
			if address is None:
				logging.info("Couldn't find any boords. Trying again in 3 seconds.")
				time.sleep(2.9727) # I rewrote this but the troll is still here wwwww
		return address
			# I did it the wrong way				
					
	def connect(self, address):
		if address is None:
			logging.error("Non-existant address. Check the input")
			return
		if self.connection:
			logging.info("Already connected to boord. No need to connect again.")
		else:
			logging.info("Trying to etablish connection...")
			logging.debug("Connecting control socket first")
			try:
				self.controlsocket.connect((address, 0x11))
				logging.debug("Connection successful!")
			except Exception as err:
				logging.error("Couldn't connect with the control socket... Try again.")
				logging.debug(f"Error: {err}")
			logging.debug("Connecting receive socket now")
			try:
				self.receivesocket.connect((address, 0x13))
				logging.debug("Connection successful!")
			except Exception as err:
				logging.error("Couldn't connect with the receive socket... Try again.")
				logging.debug(f"Error: {err}")
			logging.info("Sucessfully connected both the control and receive socket!")
			self.send_data(COMMAND_READ_REGISTER, "04a400240018") # Sends calibration data
		
	def receive_loop(self):
		if self.connect:
			while self.connect:
				data = self.receivesocket.recv(25)
				f_data = fetch_data(data, "ENCODED")[0] # This is the determining data I talked about earlier
				if f_data == INPUT_STATUS or f_data == "20": # Just in case, I check it as a string too.
					self.send_data(COMMAND_REPORTING, CONTINUOUS_REPORTING, EXTENSION_8BYTES)
					# I think this is only about the battery life, but I am not sure what this does.
					# I've taken this from skorokithakis/gr8w8upd8m8
				elif f_data == INPUT_READ_DATA or f_data == "21":
					# Now this is kinda confusing. I will explain it through
					# 21 is basically about calibration so we have to calibrate it
					# The boord sends 2 different packets for us to put in the calibration variable.
					# One's length is 16 and one's length is smaller
					# We already have the length given in the packet itself, it's the 5th byte.
					# Refer to the local calibration sample in the variables. There is the first packet
					# The 4th byte of it is f0 which translates to 240. We now divide this value with 16.
					# We get 15. When we add 1 to this we end up with what we need. This identifies the first
					# packet. We can now work with it.
					packet_length = int(hex2int(fetch_data(data, "ENCODED")[3]) / 16 + 1)
					need = fetch_data(data, "TO_STRING")[7:7 + packet_length]
					# Sorry if some of my variable naming is confusing, I usually name stuff "need" because
					# I can't find anything else lol
					# And also, I don't really know what the 7 is about, I will research it further.
					if packet_length == 16:
						self.calibration = [fetch_data(fetch_data(data, "TO_STRING")[0:8], "DECODED"), fetch_data(fetch_data(data, "TO_STRING")[8:16], "DECODED"), [1e4]*4]
					elif packet_length < 16:
						self.calibration[2] = [fetch_data(fetch_data(data, "TO_STRING")[0:8], "DECODED")]
					else:
						logging.error("Something went wrong with the calibration...")
						logging.debug(f"Here's what the data was: {data}")
					# I should've explained this earlier:
					# calibration[0] is calibration values for 0kg
					# calibration[1] is calibration values for 17kg
					# and calibration[2] is calibration values for 37kg
				elif f_data == EXTENSION_8BYTES or f_data == "32":
					self.button_check(fetch_data(data, "ENCODED")[6:][0])
					# The above code checks for the button press. If the value is 80 then the button is pressed.
					# If it's 00, it's not pressed.
					
					self.parse_cal(fetch_data(data, "TO_STRING")[8:])
					report = self.report(fetch_data(data, "TO_STRING")[8:])
					return report
					# This might seem a bit confusing... it is!
					# Let me show this with an example:
					# "a13200000aa54c9c0b3b0630"
					#  112233445555555555555555
					#          1122334455667788
					# 1 > Unused byte (? unconfirmed)
					# 2 > Identifier
					# 3 > Unused byte (? unconfirmed)
					# 4 > Button byte [80 = pressed, 00 = none]
					# 5 > Mass data
					#   1 > Top    right
					#   2 > Top    right
					#   3 > Bottom right
					#   4 > Bottom right
					#   5 > Top    left
					#   6 > Top    left
					#   7 > Bottom left
					#   8 > Bottom left
					# So we would just need it after the 6th character, split it up to 8 (or maybe 4) and work with that!

	def send_data(self, *data):
		temp_data = ""
		for n in data:
			temp_data += n
		end_str = b"\x52" + binascii.unhexlify(temp_data)
		self.controlsocket.send(end_str)

	def button_check(self, data):
		if data == "80":
			logging.info("The button is being pressed down.")
		else:
			pass

	def parse_cal(self, data):
		index = 0
		if self.calibrated:
			pass
		else:
			byte = wrap(data, 4)
			if len(data) == 16:
				for a in range(2):
					for b in range(4):
						self.calibration[a][b] = (int(byte[index], 16) << 8)
						index += 1
			elif len(data) < 16:
				for b in range(4):
					self.calibration[2][b] = (int(byte[index], 16) << 8)
					index +=1
			self.calibrated = True

		# Explanation:
		# We split the mass data to 4, one for each part of the board
		# We assign those values to the calibrations.
		# The for loops are for assigning all 4 sides in 2 ways (both 0kg and 17kg)
		# If the data is less than 16 bytes then we assign it all to 34kg

	def calc_mass(self, raw, pos):
		val = 0.0
		kg0 = self.calibration[0][pos]
		kg17 = self.calibration[1][pos]
		kg34 = self.calibration[2][pos]
		kg = [kg0, kg17, kg34]
		# Easy accesibilyiyı9tjwol (I don't know how to spell it)
		if raw < kg[0]:
			return 0.0
		elif raw < kg[1]:
			return 17 * ((raw - kg[0]) / float((kg[1] - kg[0])))
		elif raw > kg[1]:
			return 34 * ((raw - kg[1]) / float((kg[2] - kg[1])))
		else:
			logging.critical("Something went wrong while calculating mass...")
			logging.debug("Calibration values:\nKG0 {kg0}\nKG17{kg17}\nKG34 {kg34}\nALL {self.calibration}")

	def report(self, data):
		byte = wrap(data, 4)

		TR = self.calc_mass(hex2int(byte[0]), TOPRIGHT)
		BR = self.calc_mass(hex2int(byte[1]), BOTRIGHT)
		TL = self.calc_mass(hex2int(byte[2]), TOPLEFT)
		BL = self.calc_mass(hex2int(byte[3]), BOTLEFT)

		return {
			"top_right": tr,
			"bottom_right": br,
			"top_left": tl,
			"bottom_left": bl,
			"left": (tl + bl) / 2, # Avg. left value
			"right": (tr + br) / 2, # Avg. right value
			"total": (tr + br + tl + bl) / 4, # Avg. of all values
			"total_weight": tr + br + tl + bl, # Total of all weighs
		}

# Time to write some code to try it out.

def test():
	b00rd = Boord()
	found = b00rd.discover(4) # This will loop until a boord has been found
	b00rd.connect(found)
	receive = b00rd.receive_loop()
	print(receive["top_right"])

if __name__ == "__main__":
	test()