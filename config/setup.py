#!/usr/bin/python
'''Basic setup'''
import os
from dc import base, config, app, trc, sec

gd = base.global_data()
p = base.pub()
c=config.Conf(gd, p)
a=app.App(gd, p)
t=trc.TranscoderService(gd, p)
s=sec.SEC(gd, p)

menu = {}
menu['1']="Create %s user & Configure system security.\n" % (gd.shotgun_user)
menu['2']="Extract & load [shotgun app image] [transcoder images].\n"
menu['3']="Setup shotgun enterprise console.\n"
menu['4']="Configure production yml [app] [db] [dbops] [transcoder services].\n"
menu['5']="Start shotgun enterprise production server.\n"
menu['6']="Configure staging yml.\n"
menu['7']="Re-configure standalone postgresql for production server.\n"
menu['8']="Reset production server password to %s\n" % (gd.SHOTGUN_ADMIN_PW)
menu['0']="Exit\n"
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
        '''Re-configure standalone for production server.'''
        os.system('clear')
        a.setupdb()
        selection=raw_input("\nPress any key ...") 
    elif selection == '8':
        '''Reset production server password'''
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
