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

CONTINUOUS_REPORTING     = b"\x04"
COMMAND_LIGHT            = b"\x11"
COMMAND_REPORTING        = b"\x12"
COMMAND_REQUEST_STATUS   = b"\x15"
COMMAND_REGISTER         = b"\x16"
COMMAND_READ_REGISTER    = b"\x17"
INPUT_STATUS             = "20"
INPUT_READ_DATA          = "21"
EXTENSION_8BYTES         = "32"
BT_NAME                  = "Nintendo RVL-WBC 01"
LOCAL_CALIBRATION_SAMPLE = ["a1210000f000240bc54c890b66075f1286533c12410e12", ""] # First packet, second packet will be entered later.
LOCAL_DATA_SAMPLE        = "a13200000aa54c9c0b3b0630"

import bluetooth
import sys
import logging

logging.basicConfig(format='%(levelname)s ] %(message)s', level=logging.INFO) # Change this to logging.DEBUG to debug the module.


class Boord:
  def __init__(self):
    self.receivesocket = None
		self.controlsocket = None
		self.calibration = []
		self.calibrationRequested = False
		self.LED = False
		self.address = None
		self.buttonDown = False
		for i in range(3):
			self.calibration.append([])
			for j in range(4):
				self.calibration[i][j].append(10000)  # high dummy value so events with it don't register

		self.connect = False
    try:
			self.receivesocket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
			self.controlsocket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
		except ValueError:
			logging.critical("Bluetooth could not be located.")
      logging.debug("L2CAP couldn't be enabled")
     
  def discover(self, sec=6, autoconnect=False):
    if self.connect:
      logging.info("Already connected to boord. No need to discover again.")
      logging.debug("If it's not, try restarting the app.")
    else:
      adress = None
      logging.info("Press the red (or black, if you're too cool) sync button in the battery slot of the board.")
      logging.info("I will start scanning now, make sure your boord will still be in sync mode for 6 seconds.")
      bluetooth_address = bluetooth.discover_devices(duration=sec, lookup_names=True) 
      logging.debug(f"List of devices: {bluetooth_address}")
      for device in bluetooth_address:
			  if device[1] == BT_NAME:
				  address = device[0]
				  logging.info(f"Got it! A boord was found. ({address})")for bluetoothdevice in bluetoothdevices:
			if bluetoothdevice[1] == BLUETOOTH_NAME:
				address = bluetoothdevice[0]
				print(f"Found Wiiboard at address {address}")
          if autoconnect:
            self.connect(address)
          else:
            pass
        else
          logging.error("Hm... Couldn't find a boord. Trying again in 3 seconds.")
          time.sleep(2.9727) # Troll wwwww
          self.discover()
          
  def connect(address):
    if self.connect:
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
  def fetch_data(self, data):
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
      else
        end_value = wrap(data, 2)
        # This is just common wrapping
      return end_value
    elif type == "ENCODED":
      # This is a string that goes like \x11\x22\x33
      value = data.hex()
      fetch_data(value, "DECRYPT")
    elif type == "TO_STRING":
      # This is just for converting it to a sting
      return data.hex()

  def hex2int(self, data):
    return int(str(data), 16)
    # Very simple hex to decimal function
    
  def recieve_loop(self):
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
            self.calibration = [fetch_data(fetch_data(data, "TO_STRING")[0:8]), "DECODED"), fetch_data(fetch_data(data, "TO_STRING")[8:16]), "DECODED"), [1e4]*4)]
          elif packet_length < 16:
            self.calibration[2] = [fetch_data(fetch_data(data, "TO_STRING")[0:8]), "DECODED")]
          else:
            logging.error("Something went wrong with the calibration...")
            logging.debug(f"Here's what the data was: {data}")
          # I should've explained this earlier:
          # calibration[0] is calibration values for 0kg
          # calibration[1] is calibration values for 17kg
          # and calibration[2] is calibration values for 37kg
        elif f_data == EXTENSION_8BYTES or f_data == "32":
          self.button_check(fetch_data(data[6:], "ENCODED")[0])
          # The above code checks for the button press. If the value is 80 then the button is pressed.
          # If it's 00, it's not pressed.
          
          self.parse_cal(fetch_data(data[6:], "ENCODED").remove(fetch_data(data[6:], "ENCODED")[0]))
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

          
 # Rest will be written when I switch to local files, I wrote all of these in GitHub, without any debugging.
