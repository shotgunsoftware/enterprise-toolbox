#!/usr/bin/python
'''Basic setup'''
import os
from dc import base, config, app, trc, sec, monitor

gd = base.global_data()
p = base.pub()
c=config.Conf(gd, p)
a=app.App(gd, p)
t=trc.TranscoderService(gd, p)
s=sec.SEC(gd, p)
m=monitor.Monitor()

sg = "Shotgun"

def ToolsMenu():
    menu = {}
    menu['0']="Back to main menu"
    menu['0-']="--------------------------------"
    menu['1']="Setup Basic Monitor"

    while True: 
        os.system('clear')
        options=menu.keys()
        options.sort()
        for entry in options:
            if entry == "0-":
                print menu[entry]
            else: 
                p.printend(entry + ': ' + menu[entry])

        selection=raw_input("Please Select: ") 
        if selection =='1': 
            '''Setup basic monitor'''
            os.system('clear')
            m.setup()
            selection=raw_input("\nPress any key ...") 
        elif selection == '0': 
            os.system('clear')
            break
        else: 
            os.system('clear')
            #print "\nUnknown Option Selected!\n" 
            #selection=raw_input("\nPress any key ...") 

def RakeCommandsMenu():
    menu = {}
    menu['0']="Back to main menu"
    menu['0-']="--------------------------------"
    menu['1']="Reset Production Server Password to %s" % (gd.SHOTGUN_ADMIN_PW)
    menu['2']="Reset Staging Server Password to %s" % (gd.SHOTGUN_ADMIN_PW)
    menu['3']="Upgrade Production Server"
    menu['4']="Upgrade Staging Server"
    menu['5']="Scale Production Transcoder Worker"

    while True: 
        os.system('clear')
        options=menu.keys()
        options.sort()
        for entry in options: 
            if entry == "0-":
                print menu[entry]
            else:
                p.printend(entry + ': ' + menu[entry])

        selection=raw_input("Please Select: ") 
        if selection =='1': 
            '''Reset shotgun server password'''
            os.system('clear')
            a.setpassword('production')
            selection=raw_input("\nPress any key ...") 
        if selection =='2': 
            '''Reset shotgun server password'''
            os.system('clear')
            a.setpassword('staging')
            selection=raw_input("\nPress any key ...") 
        if selection =='3': 
            '''upgrade'''
            os.system('clear')
            a.rakeupgrade('production')
            selection=raw_input("\nPress any key ...") 
        if selection =='4': 
            '''upgrade staging'''
            os.system('clear')
            a.rakeupgrade('staging')
            selection=raw_input("\nPress any key ...") 
        if selection =='5': 
            '''scale transcoder'''
            os.system('clear')
            a.setpassword('production')
            selection=raw_input("\nPress any key ...") 
        elif selection == '0': 
            os.system('clear')
            break
        else: 
            os.system('clear')
            #print "\nUnknown Option Selected!\n" 
            #selection=raw_input("\nPress any key ...") 

def DockerCommandsMenu():
    menu = {}
    menu['0']="Back to main menu"
    menu['0-']="--------- Docker Commands -----------"
    menu['1']="Show All Containers"
    menu['2']="Show All Images"

    while True: 
        os.system('clear')
        options=menu.keys()
        options.sort()
        for entry in options: 
            if entry == "0-":
                print menu[entry]
            else:
                p.printend(entry + ': ' + menu[entry])

        selection=raw_input("Please Select: ") 
        if selection =='1': 
            '''All containers'''
            os.system('clear')
            p.dockerps()
            selection=raw_input("\nPress any key ...") 
        if selection =='2': 
            '''All images'''
            os.system('clear')
            p.dockerimages()
            selection=raw_input("\nPress any key ...") 
        if selection =='3': 
            '''Reset shotgun server password'''
            os.system('clear')
            p.dockersystemprune()
            selection=raw_input("\nPress any key ...") 
        elif selection == '0': 
            os.system('clear')
            break

def LoadImagesMenu():
    menu = {}
    menu['0']="Back to main menu"
    menu['0-']="--------------------------------"
    menu['1']="Setup Shotgun Images Folder"
    menu['2']="Load Shotgun App Image (production, staging, emailnotifier, memcache, dbops, buildin pgsql)"
    menu['3']="Load Shotgun Transcoder Service Image (transcoder server, transcoder workder)"
    menu['4']="Load Shotgun Enterprise Console Image"

    while True: 
        os.system('clear')
        print '-  Your images folder is ', gd.temp_folder
        options=menu.keys()
        options.sort()
        for entry in options: 
            if entry == "0-":
                print menu[entry]
            else:
                p.printend(entry + ': ' + menu[entry])

        selection=raw_input("Please Select: ") 
        if selection =='1': 
            '''Setup Shotgun Images Folder'''
            os.system('clear')
            c.tempfolder()
            selection=raw_input("\nPress any key ...") 
        elif selection =='2': 
            '''Load Shotgun App Image '''
            os.system('clear')
            a.loadappimage()
            selection=raw_input("\nPress any key ...") 
        elif selection =='3': 
            '''Load Shotgun Transcoder Service Image '''
            os.system('clear')
            t.loadimages()
            selection=raw_input("\nPress any key ...") 
        elif selection =='4': 
            '''Load Shotgun Enterprise Console Image '''
            os.system('clear')
            s.loadimage()
            selection=raw_input("\nPress any key ...") 
        elif selection == '0': 
            os.system('clear')
            break
        else: 
            os.system('clear')
            #print "\nUnknown Option Selected!\n" 
            #selection=raw_input("\nPress any key ...") 

def StartStopServicesMenu():
    menu = {}
    menu['0']="Back to main menu"
    menu['0-']="---------------- Start ----------------"
    menu['1']="Start Shotgun Production Server"
    menu['2']="Start Shotgun Staging Server"
    menu['3']="Start Shotgun Enterprise Console"
    menu['3-']="---------------- Stop -----------------"
    menu['4']="Stop Shotgun Production Server"
    menu['5']="Stop Shotgun Staging Server"
    menu['6']="Stop Shotgun Enterprise Console"
    menu['6-']="---------------- Status ---------------"
    menu['7']="Status of Shotgun Production Server"
    menu['8']="Status Shotgun Staging Server"

    while True: 
        os.system('clear')
        options=menu.keys()
        options.sort()
        for entry in options: 
            if entry == "0-" or entry == "3-" or entry == "3-" or entry == "6-":
                print menu[entry]
            else:
                p.printend(entry + ': ' + menu[entry])

        selection=raw_input("Please Select: ") 
        if selection =='1': 
            '''Start Shotgun Production Server'''
            os.system('clear')
            a.startserver('production')
            selection=raw_input("\nPress any key ...") 
        elif selection =='2': 
            '''Start Shotgun Staging Server'''
            os.system('clear')
            a.startserver('staging')
            selection=raw_input("\nPress any key ...") 
        elif selection =='3': 
            '''Start Shotgun Enterprise Console'''
            os.system('clear')
            s.startup()
            selection=raw_input("\nPress any key ...") 
        elif selection =='4': 
            '''Stop Shotgun Production Server'''
            os.system('clear')
            a.stopserver('production')
            selection=raw_input("\nPress any key ...") 
        elif selection =='5': 
            '''Stop Shotgun Staging Server'''
            os.system('clear')
            a.stopserver('staging')
            selection=raw_input("\nPress any key ...") 
        elif selection =='6': 
            '''Stop Shotgun Enterprise Console'''
            os.system('clear')
            s.stopserver()
            selection=raw_input("\nPress any key ...") 
        elif selection =='7': 
            '''Status of Production'''
            os.system('clear')
            a.dockercomposestatus('production')     
            selection=raw_input("\nPress any key ...") 
        elif selection =='8': 
            '''Status of Staging'''            
            os.system('clear')
            a.dockercomposestatus('staging')
            selection=raw_input("\nPress any key ...") 
        elif selection == '0': 
            os.system('clear')
            break
        else: 
            os.system('clear')
            #print "\nUnknown Option Selected!\n" 
            #selection=raw_input("\nPress any key ...") 

def ConfigYMLMenu():
    menu = {}
    menu['0']="Back to main menu"
    menu['0-'] ="--------- Standalone Production Server --------------"
    menu['1']="Setup %s Production App" % (sg)
    menu['2']="Setup Standalone Postgresql for Production Server"
    menu['2-'] ="--------- Standalone Staging Server -----------------"
    menu['3']="Setup %s Staging App" % (sg)
    menu['3-0']="----- Production & Staging Mixed Server -------------"
    menu['3-1']="This will configure haproxy when Production and Staging running on same machine."
    menu['3-2']="Please make sure you have setup standalone Production and Staging server on the same machine."
    menu['3-3']="And all services have been stopped."
    menu['4']="Edit Production & Staging YML and Enable Haproxy"

    while True: 
        os.system('clear')
        options=menu.keys()
        options.sort()
        for entry in options: 
            if entry == "2-" or entry == "0-" or entry == "3-0" or entry == "3-1" or entry == "3-2" or entry == "3-3":
                print menu[entry]
            else:
                p.printend(entry + ': ' + menu[entry])

        selection=raw_input("Please Select: ") 
        if selection =='1': 
            '''Setup %s Production App'''
            os.system('clear')
            a.startover('production')
            a.setupproduction()
            a.setupemailer('production')
            t.editproductionyml()
            selection=raw_input("\nPress any key ...") 
        elif selection =='2': 
            '''Setup database'''
            os.system('clear')
            a.setupdb()
            selection=raw_input("\nPress any key ...") 
        elif selection =='3': 
            '''Setup Staging App'''
            os.system('clear')
            a.startover('staging')
            a.setupstaging()
            a.setupemailer('staging')
            t.editstagingyml()
            selection=raw_input("\nPress any key ...") 
        elif selection =='4': 
            '''Haproxy'''
            os.system('clear')
            a.setupproxy()
            selection=raw_input("\nPress any key ...") 
        elif selection == '0': 
            os.system('clear')
            break
        else: 
            os.system('clear')
            #print "\nUnknown Option Selected!\n" 
            #selection=raw_input("\nPress any key ...") 

if __name__=="__main__":
    menu = {}
    menu['0']="Exit"
    menu['0-']="-------------- System  ------------------"
    menu['1']="Create %s user & Configure system security." % (gd.shotgun_user)
    menu['1-']="-------------- Configuration  -----------"
    menu['2']="Extract & Load Shotgun Images"
    menu['3']="Configure Shotgun Configuration YML"
    menu['4']="Start/Stop Shotgun Services"
    menu['4-']="-------------- Helper -------------------"
    menu['5']="Shotgun Rake Commands"
    menu['6']="Tools"
    menu['7']="Docker Commands"
    while True: 
        os.system('clear')
        options=menu.keys()
        options.sort()
        for entry in options: 
            if entry == "4-" or entry == "0-" or entry == "1-":
                print menu[entry]
            else:
                p.printend(entry + ': ' + menu[entry])
                
        selection=raw_input("Please Select: ") 
        if selection =='1': 
            '''Create shotgun user & Configure system security.'''
            os.system('clear')
            c.createshotgunuser()
            c.systemsecurity()
            selection=raw_input("\nPress any key ...") 
        elif selection == '2':
            '''Extract & Load Shotgun Images'''
            os.system('clear')
            LoadImagesMenu()
        elif selection == '3':
            '''Configure Shotgun Configuration YML'''
            os.system('clear')
            ConfigYMLMenu()
        elif selection == '4':
            '''Start/Stop Shotgun Services'''
            os.system('clear')
            StartStopServicesMenu()
        elif selection == '5':
            '''Rake commands'''
            os.system('clear')
            RakeCommandsMenu()
        elif selection == '6':
            '''Setup basic monitor'''
            os.system('clear')
            ToolsMenu()
        elif selection == '7':
            '''Docker Commands'''
            os.system('clear')
            DockerCommandsMenu()
        elif selection == '0': 
            os.system('clear')
            break
        else: 
            os.system('clear')
            #print "\nUnknown Option Selected!\n" 
            #selection=raw_input("\nPress any key ...") 



