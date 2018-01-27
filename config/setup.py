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

menu = {}
menu['1']="Create %s user & Configure system security." % (gd.shotgun_user)
menu['2']="Extract & load [shotgun app image] [transcoder images]."
menu['3']="Setup shotgun enterprise console."
menu['4']="Configure production yml [app] [db] [dbops] [transcoder services]."
menu['5']="Start shotgun enterprise production server."
menu['6']="Configure staging yml."
menu['7']="Reset shotgun server password to %s" % (gd.SHOTGUN_ADMIN_PW)
menu['8']="Setup basic monitor"
menu['0']="Exit"
while True: 
    os.system('clear')
    options=menu.keys()
    options.sort()
    for entry in options: 
        p.printend(entry + ': ' + menu[entry])

    selection=raw_input("Please Select:") 
    if selection =='1': 
        '''Create shotgun user & Configure system security.'''
        os.system('clear')
        c.createshotgunuser()
        c.systemsecurity()
        selection=raw_input("\nPress any key ...") 
    elif selection == '2':
        '''Extract & load [shotgun app image] [transcoder images].'''
        os.system('clear')
        c.tempfolder()
        a.loadappimage()
        t.loadimages()
        selection=raw_input("\nPress any key ...") 
    elif selection == '3':
        '''Setup shotgun enterprise console.'''
        os.system('clear')
        c.tempfolder()
        s.setup()
        selection=raw_input("\nPress any key ...") 
    elif selection == '4':
        '''Configure production yml [app] [db] [dbops] [transcoder services].'''
        os.system('clear')
        a.setupproduction()
        t.editproductionyml()
        selection=raw_input("\nPress any key ...") 
    elif selection == '5':
        '''Start shotgun enterprise production server.'''
        os.system('clear')
        a.startserver()
        selection=raw_input("\nPress any key ...") 
    elif selection == '6':
        '''Configure staging yml.'''
        os.system('clear')
        a.setupstaging()
        t.editstagingyml()
        selection=raw_input("\nPress any key ...") 
    elif selection == '7':
        '''Reset production server password'''
        os.system('clear')
        a.setpassword()
        selection=raw_input("\nPress any key ...") 
    elif selection == '8':
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
