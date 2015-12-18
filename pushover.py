#!/usr/bin/python

'''
        Pushover.py

        License:
        This work is licensed under a Creative Commons Attribution-ShareAlike 3.0 Unported License.
        http://creativecommons.org/licenses/by-sa/3.0/deed.en_US
        
        What it does:
        Send push notification requests to Pushover.

        Can be used as either a module or as a command-line tool.
        This is a very simple implementation of the Pushover v1 API. It doesn't do anything fancy, such as
        monitor high-priority notification receipts.

        I am not a professional, but merely a hobbyist. The code, I'm sure, isn't deployment-quality but it
        works. I mainly wrote it to send my phone notifications when certain tasks on my machine have finished.

        Module usage:
                import pushover

                po = Pushover("Application Token", "User Token", echo = True/False)

                po.send(device = You device (optional),
                        sound = "Select a notification sound (optional)",
                        priority = "Priority level (optional)",
                        title = "Notification title (optional)",
                        message = "Notification message (required)",
                        url = "Send a link with the notification (optional)",
                        url_title = "Human-readable text to assing to link (optional)")
                        
                If request was sent successfully, the method will return True (if echo is enabled, it will print
                "Notification sent successfully"

        CLI usage:
                Just type -h or --help for instructions.
                
'''


import httplib
import urllib
import json


PUSHOVER_URLS = { 
			'base' : u'api.pushover.net:443',
        		'validate_device' : u'/1/users/validate.json',
        		'send_notification' : u'/1/messages.json',
			'get_sounds' : u'/1/sounds.json' 
		}

CHAR_LIMITS = {
			'msg_title' : 250,
			'msg_body' : 1024,
			'sup_title' : 100,
			'sup_url' : 250
		}


class Pushover:
        def __init__(self, app_token, user_token, echo = False):
                self.APP_TOKEN = app_token
                self.USER_TOKEN = user_token

                self.ECHO = echo


        '''
                _echo(msg)

                Arguments:
                        msg - The message to print

                Returns:
                        String

                _echo will print a given message if the object has been called with echo turned on.
        '''
        def _echo(self, msg):
                if self.ECHO: print msg


        '''
                _trim(incoming, length)

                Arguments:
                        incoming - Incoming string that needs to be ananlyzed and trimmed if
                        necessary.

                        length - Maximum length a string can be.

                Returns:
                        String

                Pushover has certain requirements for string length (titles can only be 50 characters, messages
                can be 512, etc.) _trim is called to make sure strings are in spec, and if they're too long, they're
                truncated and have a "..." append for looks.
        '''
        def _trim(self, incoming, length):
                if incoming is None:
                        return ""
                
                if len(incoming) > length:
                        return incoming[:length - 3] + "..."

                else:
                        return incoming


        '''
                _send_request(method, url, data)

                Arguments:
                        method - The HTTP method, ie POST or GET.
                        
                        url - The URL to send the request.
                        
                        data - Data being sent, encoded with urllib.urlencode().

                Returns:
                        httplib.getresponse() object
                
                This method will send the request, through SSL, to Pushover using httplib. If the request
                was sent successfully, it will return a httplib response object. If the request fails,
                the method will return None.
        '''
        def _send_request(self, method, url, data):
                try:
                        conn = httplib.HTTPSConnection(PUSHOVER_URLS['base'])

                except:
                        self._echo("Could not connect")

                        return None

                try:
                        conn.request(method, url, data, { "Content-type": "application/x-www-form-urlencoded" })

                        return conn.getresponse()

                except:
                        self._echo("An error occured")

                        return None

	
	def getSoundsList(self):
                if self.APP_TOKEN:
                        response = self._send_request('GET',
                                                        PUSHOVER_URLS['get_sounds'],
                                                        urllib.urlencode({'token' : self.APP_TOKEN}))

                        if response is not None:
                                response_dump = json.loads(response.read())

                                if response_dump['status'] == 1:
                                        for item in response_dump['sounds']:
                                                print item
                                                
                                else:
                                        self._echo("Error(s) from Pushover:")

                                        for item in response_dump['errors']:
                                                self._echo(item)
                                
                                        return False
                        else:
                                self._echo("An unknown error occured trying to reach Pushovers servers.")

                                return False
                                
                else:
                        self._echo("A Pushover application token is required for this request.")

                        return False

		

        '''
                sendNotification(device, sound, priority, title, message, url, url_title)

                Arguments:
                        device - A string value containg the name of the device you wish to notify.
                        If left empty, the notification will be sent to all devices associated with the
                        account. If a device is specified, and not found, the method will return false.

                        sound - A string value of the notification sound you would like to use. If left
                        blank, the default notification sound will be used. Use "none" to send a silent
                        notification

                        priority - An integer value that will change the notifications priority level.
                        -1 is low priority, 0 is normal, 1 is high.

                        title - A string value for the optional title.

                        message - A string value for the notification message. This is required.

                        url - A string value used to attach a link to the notification

                        url_title - A string value used to give the previous mentioned link a human-readable
                        text value, so instead of it showing up as "http://www.google.com" in the notification,
                        it as "Google".

                Returns:
                        Boolean

                This method is the where the message will be configured and sent to Pushover. The method first
                verifies that the tokens provided are valid, checks if the device name given (if any) is
                associated with the account, and then will proceed to send the request if no validation errors
                have been established. If the request was accepted, the method will return True. 
                        
        '''                                           
        def sendNotification(self, device = "", sound = "", priority = 0, title = "", message = "", url = "", url_title = "", enable_html = False):
                verify_response = self._send_request('POST',
                                         PUSHOVER_URLS['validate_device'],
                                         urllib.urlencode({
                                                'token' : self.APP_TOKEN,
                                                'user' : self.USER_TOKEN,
                                                'device' : device
                                        }))

                if verify_response is not None:
                        verify_response_dump = json.loads(verify_response.read())
                        
                        if verify_response_dump['status'] == 1:
                                if message is None:
                                        self._echo("Must supply a notification message. Terminating request.")
                                        return False
                                
                                send_response = self._send_request('POST',
                                                          PUSHOVER_URLS['send_notification'],
                                                          urllib.urlencode({
                                                                'token' : self.APP_TOKEN,
                                                                'user' : self.USER_TOKEN,
                                                                'device' : device,
                                                                'priority' : priority,
                                                                'sound' : sound,
                                                                'title' : self._trim(title, CHAR_LIMITS['msg_title']),
                                                                'message' : self._trim(message, CHAR_LIMITS['msg_body']),
                                                                'url' : self._trim(url, CHAR_LIMITS['sup_url']),
                                                                'url_title' : self._trim(url_title, CHAR_LIMITS['sup_title']),
                                                                'html' : 1 if enable_html else 0
                                                        }))

                                if send_response is not None and send_response.status == 200:
                                        if json.loads(send_response.read())['status'] == 1:
                                                self._echo("Notification was sent successfully!")
                                
                                                return True
                                        else:
                                                self._echo("Notification was not sent. An error occured")

                                                return False

                                elif send_response.status == 429:
                                        self._echo("Notification cap has been reached. Notification not sent.")

                                        return False

                        else:
                                self._echo("Error(s) from Pushover:")

                                for item in verify_response_dump['errors']:
                                        self._echo(item)
                                
                                return False
                        
                else:
                        self._echo("An error occured when connecting to Pushover. Request terminated.")

                        return False

	def sendEmergencyNotification(self):
		return False  


if __name__ == "__main__":
        from optparse import OptionParser, OptionGroup
        from sys import exit

        parser = OptionParser(usage = "Usage: %prog [options]")

        
        parser.add_option("", "--user-token",
                          type = "string",
                          dest = "user_token",
                          default = 0,
                          help = "User token for Pushover service.")

        parser.add_option("", "--app-token",
                          type = "string",
                          dest = "app_token",
                          default = 0,
                          help = "App token for Pushover service.")

        parser.add_option("-e", "--echo",
                          action = "store_true",
                          dest = "echo",
                          default = False,
                          help = "Turn command line echo on.")

	parser.add_option("", "--list-sounds",
			  action = "store_true",
			  dest = "action_list_sounds",
			  default = False,
			  help = "Get a current list of supported sounds from Pushover.")


	group_notification = OptionGroup(parser, "Notification Options",
					"These options can be used to send a standard notification to Pushover.")

	group_notification.add_option("-m", "--message",
			  type = "string",
			  dest = "message",
			  default = "",
			  help = "Body of the notification to be sent. Max length is 1024 characters and supports limited HTML styling.")

	group_notification.add_option("-d", "--device",
			  type = "string",
			  dest = "device",
			  default = "",
			  help = "Define to which device this notification gets sent to. Default is all registered devices.")

	group_notification.add_option("-p", "--priority",
			  type = "int",
			  dest = "priority",
			  default = "0",
			  help = "Set notification priority. -1 low priority, 0 normal priority, 1 high priority.")

	group_notification.add_option("-s", "--sound",
			  type = "string",
			  dest = "sound",
			  default = "",
			  help = "Set notification sound.")

	group_notification.add_option("-t", "--title",
			  type = "string",
			  dest = "title",
			  default = "",
			  help = "Set notification title.")

	group_notification.add_option("-u", "--url",
			  type = "string",
			  dest = "url",
			  default = "",
			  help = "Set URL for notification.")

	group_notification.add_option("-l", "--url-title",
			  type = "string",
			  dest = "url_title",
			  default = "",
			  help = "Set title for URL.")

	group_notification.add_option("", "--enable-html",
			  action = "store_true",
			  dest = "enable_html",
			  default = True,
			  help = "Enable HTML formatting.")


	parser.add_option_group(group_notification)

        (options, args) = parser.parse_args()


        if options.app_token is None or options.user_token is None:
                print "User or application tokens are required for this request."

                exit()

	po = Pushover(options.app_token, options.user_token, options.echo)

	if options.action_list_sounds:
		po.getSoundsList()
		exit()

	

##        print "Message to be sent: %s" % options.message

        res = po.sendNotification(device = options.device,
                      priority = options.priority,
                      sound = options.sound,
                      title = options.title,
                      message = options.message,
                      url = options.url,
                      url_title = options.url_title,
                      enable_html = options.enable_html)

        if res:
                exit()
        else:
                print "An error occured. Use the '--echo' flag and rerun the script for more information."
