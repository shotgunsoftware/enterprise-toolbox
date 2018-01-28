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
                p.printend(menu[entry])
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
            print "\nUnknown Option Selected!\n" 
            selection=raw_input("\nPress any key ...") 

def RakeCommandsMenu():
    menu = {}
    menu['0']="Back to main menu"
    menu['0-']="--------------------------------"
    menu['1']="Reset shotgun server password to %s" % (gd.SHOTGUN_ADMIN_PW)

    while True: 
        os.system('clear')
        options=menu.keys()
        options.sort()
        for entry in options: 
            if entry == "0-":
                p.printend(menu[entry])
            else:
                p.printend(entry + ': ' + menu[entry])

        selection=raw_input("Please Select: ") 
        if selection =='1': 
            '''Reset shotgun server password'''
            os.system('clear')
            a.setpassword()
            selection=raw_input("\nPress any key ...") 
        elif selection == '0': 
            os.system('clear')
            break
        else: 
            os.system('clear')
            print "\nUnknown Option Selected!\n" 
            selection=raw_input("\nPress any key ...") 

def DockerCommandsMenu():
    menu = {}
    menu['0']="Back to main menu"
    menu['0-']="--------------------------------"
    menu['1']="Show All Containers"
    menu['2']="Show All Images"
    menu['3']="Docker System Prune"

    while True: 
        os.system('clear')
        options=menu.keys()
        options.sort()
        for entry in options: 
            if entry == "0-":
                p.printend(menu[entry])
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
        options=menu.keys()
        options.sort()
        for entry in options: 
            if entry == "0-":
                p.printend(menu[entry])
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
            print "\nUnknown Option Selected!\n" 
            selection=raw_input("\nPress any key ...") 

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

    while True: 
        os.system('clear')
        options=menu.keys()
        options.sort()
        for entry in options: 
            if entry == "0-" or entry == "3-":
                p.printend(menu[entry])
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
        elif selection == '0': 
            os.system('clear')
            break
        else: 
            os.system('clear')
            print "\nUnknown Option Selected!\n" 
            selection=raw_input("\nPress any key ...") 

def ConfigYMLMenu():
    menu = {}
    menu['0']="Back to main menu"
    menu['0-'] ="----------------- Production Server -----------------"
    menu['1']="Reset %s Production Site Config YML" % (sg)
    menu['2']="Setup %s Production App" % (sg)
    menu['3']="Setup Standalone Postgresql Production Server"
    menu['4']="Enable Email-Notifier on %s Production" % (sg)
    menu['5']="Enable Transcoder Services on %s Production" % (sg)
    menu['5-'] ="----------------- Staging Server --------------------"
    menu['6']="Reset %s Staging Site Config YML" % (sg)
    menu['7']="Setup %s Staging App" % (sg)
    menu['8']="Enable Email-Notifier on %s Staging" % (sg)
    menu['9']="Enable Transcoder Services on %s Staging" % (sg)

    while True: 
        os.system('clear')
        options=menu.keys()
        options.sort()
        for entry in options: 
            if entry == "5-" or entry == "0-":
                p.printend(menu[entry])
            else:
                p.printend(entry + ': ' + menu[entry])

        selection=raw_input("Please Select: ") 
        if selection =='1': 
            '''Reset Site Config YML'''
            os.system('clear')
            a.startover('production')
            selection=raw_input("\nPress any key ...") 
        elif selection =='2': 
            '''Setup %s Production App'''
            os.system('clear')
            a.setupproduction()
            selection=raw_input("\nPress any key ...") 
        elif selection =='3': 
            '''Setup database'''
            os.system('clear')
            a.setupdb()
            selection=raw_input("\nPress any key ...") 
        elif selection =='4': 
            '''Enable Email-Notifier'''
            os.system('clear')
            a.setupemailer('production')
            selection=raw_input("\nPress any key ...") 
        elif selection =='5': 
            '''Enable Transcoder Services'''
            os.system('clear')
            t.editproductionyml()
            selection=raw_input("\nPress any key ...") 
        elif selection =='6': 
            '''Reset Site Config YML'''
            os.system('clear')
            a.startover('staging')
            selection=raw_input("\nPress any key ...") 
        elif selection =='7': 
            '''Setup Staging App'''
            os.system('clear')
            a.setupstaging()
            selection=raw_input("\nPress any key ...") 
        elif selection =='8': 
            '''Enable Email-Notifier'''
            os.system('clear')
            a.setupemailer('staging')
            selection=raw_input("\nPress any key ...") 
        elif selection =='9': 
            '''Enable Transcoder Services'''
            os.system('clear')
            t.editstagingyml()
            selection=raw_input("\nPress any key ...") 
        elif selection == '0': 
            os.system('clear')
            break
        else: 
            os.system('clear')
            print "\nUnknown Option Selected!\n" 
            selection=raw_input("\nPress any key ...") 

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
                p.printend(menu[entry])
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
            print "\nUnknown Option Selected!\n" 
            selection=raw_input("\nPress any key ...") 



