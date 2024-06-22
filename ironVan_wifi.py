import platform
import subprocess
import asyncio

async def asyncRun(cmd: str):
    '''
    How to call:

        asyncio.run(asyncRun(cmd))

    Replaces subprocess.run command to allow for asynchronous shell calls.

    Returns [stdout: str, stderr: str]
    '''
    process = await asyncio.create_subprocess_shell(
        cmd,
        stderr=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    return [stdout.decode(), stderr.decode()]

class Wifi():
    def __init__(self):
        '''
        ironVan_wifi.py

        PURPOSE:  Create a wifi object for either MacOS or {Raspberry Pi OS -- not yet operational}. Available variables:

        - self.operatingSystem => 'macOS' or {RPI OS} {default: current OS}
        - self.networkStatus => Dictionary with all parsed attributes of the wifi network (default: {})
            - macOS:
                - Wifi - ON/Connected
                    - Example
                        {'agrCtlRSSI': '-43',
                        'agrExtRSSI': '0',
                        'agrCtlNoise': '-91',
                        'agrExtNoise': '0',
                        'state': 'running',
                        'opmode': 'station',
                        'lastTxRate': '130',
                        'maxRate': '144',
                        'lastAssocStatus': '0',
                        '802.11auth': 'open',
                        'linkauth': 'wpa2-psk',
                        'BSSID': '',
                        'SSID': 'NETGEAR29',
                        'MCS': '15',
                        'guardInterval': '800',
                        'NSS': '2', 
                        'channel': '2'}

                - Wifi - ON/Not connected
                    - Example
                        {'agrCtlRSSI': '0',
                        'agrExtRSSI': '0',
                        'agrCtlNoise': '0',
                        'agrExtNoise': '0',
                        'state': 'init',
                        'opmode': '',
                        'lastTxRate': '0',
                        'maxRate': '0',
                        'lastAssocStatus': '0',
                        '802.11auth': 'open',
                        'linkauth': 'wpa2-psk',
                        'BSSID': '',
                        'SSID': '',
                        'MCS': '-1',
                        'guardInterval': '-1',
                        'NSS': '-1', 
                        'channel': '1'}

                - Wifi - OFF
                    - Example
                        {'AirPort': 'Off'}

        - self.availableNetworks => Dictionary containing {'SSID': [RSSI_max, PasswordProtected(T/F)]} (default: {})

        Automatically calls detectOS() and fills self.operatingSystem with name of OS. 
        '''
        # String value of either:  'macOS', ...
        self.operatingSystem = self.detectOS()

        # Dictionary with all parameters of wifi status - updated in app.statusUpdate()
        self.networkStatus = {}

        # List containing network names
        self.availableNetworks = {}
        self.listNetworks()

    def detectOS(self):
        '''
        How to call:

            self.operatingSystem = self.detectOS()

        Detects current operating system. Currently supported:

        - macOS
        - ...
    
        '''
        operatingSystem = None
        platformRaw = platform.platform()

        if('macOS' in platformRaw):
            operatingSystem = 'macOS'

        return operatingSystem
    
    def parseWifiStatus(self):
        '''
        How to Call:

            self.networkStatus = self.parseWifiStatus()

        Check and parse wifi status output for either MacOS or {Raspberry Pi OS - not yet supported}.

        Returns wifiStatus dictionary that should be stored in wifi.networkStatus. See Wifi.__init__() docstring for output format.
        '''
        wifiStatus = {}
        match self.operatingSystem:
            case 'macOS':
                networkPrintRaw = subprocess.run(
                    ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"],
                    capture_output = True,
                    text = True
                )

                networkPrint = networkPrintRaw.stdout

                lineBreak = []
                for i in range(0, len(networkPrint)):
                    if(networkPrint[i] == '\n'):
                        lineBreak.append(i)

                networkLine = ''
                for i in range(0, len(lineBreak)):
                    if(lineBreak[i] == 0):
                        continue
                    elif(i == 0):
                        networkLine = networkPrint[:lineBreak[i]]
                    else:
                        networkLine = networkPrint[lineBreak[i - 1]:lineBreak[i]]

                    lineSeparator = networkLine.find(':')

                    wifiStatus[networkLine[:lineSeparator].replace(' ', '').replace('\n', '')] = networkLine[lineSeparator + 1:].replace(' ', '').replace('\n', '')
                    
                return wifiStatus

    def listNetworks(self):
        '''

        Note:  Make asynchronous

        How to call:

            self.listNetworks()

        Initiates a search of all available networks and updates the self.availableNetworks dictionary with {'networkName': [RSSI, PasswordProtected (T/F)]}. RSSI is the signal strength metric in dB.

        Note: If multiple networks are found with the same SSID, the highest SSID will be listed.

        Returns NONE -- auto fills self.networksAvailable
        '''
        # Stores raw string printout from subprocess
        networkRaw = None

        # Stores {'networkName': RSSI} while avoiding repeats (signal names with multiple routers, such as in a hotel)
        networkDict = {}

        match self.operatingSystem:
            case 'macOS':
                networkRaw, networkError = asyncio.run(asyncRun("/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s"))
                
                separatorIndices = []
                for i in range(0, len(networkRaw)):
                    if(networkRaw[i] == '\n'):
                        separatorIndices.append(i)
                        
                for i in range(0, len(separatorIndices)):
                    if(i != len(separatorIndices) - 1):
                        networkLine = networkRaw[separatorIndices[i]:separatorIndices[i+1]]
                        
                    networkStrengthStart = networkLine.find(' -') + 1
                    networkStrengthEnd = networkLine[networkStrengthStart:].find(' ')
                    networkName = networkLine[:networkStrengthStart].replace('\n', '').replace(' ', '')

                    try:
                        networkStrength = int(networkLine[networkStrengthStart:(networkStrengthStart+networkStrengthEnd)])
                    except:
                        print(f'Unable to add {networkLine} to network listing')
                        continue

                    passwordRequired = True if networkLine[networkStrengthStart:].find('PSK') > -1 else False

                    # exception is raised if the networkName is the first of its SSID. If it is a repeat, its RSSI will be replaced with the highest value found (occurs if multiple of the same SSID are found, such as in a hotel with multiple routers)
                    try:
                        maxStrength = networkDict[networkName]
                        if(networkStrength > maxStrength):
                            networkDict[networkName] = [networkStrength, passwordRequired]
                    
                    except:
                        networkDict[networkName] = [networkStrength, passwordRequired]

                self.availableNetworks = networkDict

    def turnWifi(self, switch):
        '''
        Turns wifi on or off -> pass argument 'on' or 'off'
        '''
        match self.operatingSystem:
            case 'macOS':
                subprocess.run(
                    ["networksetup", 
                    "-setairportpower",
                    "en0",
                    switch],
                    capture_output = True,
                    text = True
                )

    def connectToNetwork(self, *args):
        '''
        How to call:

            Password-protected:
                self.connectToNetwork(ssid, password)

            Non-password-protected:
                self.connectToNetwork(ssid)

        Connects to SSID using the password provided (if applicable).

        Returns NONE
        '''
        networkSSID = ''
        networkPassword = ''

        if(len(args) > 1):
            networkSSID = args[0]
            networkPassword = args[1]
        else:
            networkSSID = args[0]

        match self.operatingSystem:
            case 'macOS':
                output = subprocess.run(
                    ["networksetup", 
                    "-setairportnetwork",
                    "en0",
                    networkSSID,
                    networkPassword],
                    capture_output = True,
                    text = True
                )

                return output.stdout
            
    def updateWifi(self, app):
        # Check/update Wi-Fi signal
        self.networkStatus = self.parseWifiStatus()
        try:
            if(self.networkStatus['SSID'] != ''):
                if(int(self.networkStatus['agrCtlRSSI']) > -50):
                    app.root.ids['wifi_quick_switch'].icon = 'wifi-strength-4'
                elif(int(self.networkStatus['agrCtlRSSI']) > -70):
                    app.root.ids['wifi_quick_switch'].icon = 'wifi-strength-3'
                elif(int(self.networkStatus['agrCtlRSSI']) > -90):
                    app.root.ids['wifi_quick_switch'].icon = 'wifi-strength-2'
                else:
                    app.root.ids['wifi_quick_switch'].icon = 'wifi-strength-1'

            else:
                app.root.ids['wifi_quick_switch'].icon = 'wifi-strength-off-outline'
            
            app.root.ids['wifi_quick_switch'].md_bg_color = app.toggleOn

            app.root.ids['wifi_quick_switch'].value = 'wifi_on'

        except TypeError:
            app.root.ids['wifi_quick_switch'].icon = 'wifi-strength-alert-outline'
            app.root.ids['wifi_quick_switch'].md_bg_color = app.toggleOn

        except KeyError:
            app.root.ids['wifi_quick_switch'].icon = 'wifi-strength-off-outline'
            app.root.ids['wifi_quick_switch'].md_bg_color = app.toggleOff
            app.root.ids['wifi_quick_switch'].value = 'wifi_off'
