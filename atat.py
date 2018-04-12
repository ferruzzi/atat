#!/usr/bin/python
# coding: utf-8

from pysnmp.hlapi import *

##########################
#    VARIABLES
##########################

WHID = "location"
CommunityString = "secret"
Printers = ["printer1", "printer2","printer3", "plotter1", "printer4"]

##########################
#   SNMP Code Descriptions
##########################

#   .1.3.6.1.2.1.43.11.1.1.5.1.1 = product [6="inkCartridge", 21="tonerCartridge", 15="fuser", 18="cleanerUnit", 20="transferUnit"]
#productIndex = 5
#productCodes = {"6" : "inkCartridge", "21" : "tonerCartridge", "15" : "fuser", "18" : "cleanerUnit", "20" : "transferUnit"}

#   .1.3.6.1.2.1.43.11.1.1.3.1.1 = color
#      toner: [1="Black", 2="Cyan", 3="Magenta", 4="Yellow"]
#      ink:   [1="Cyan", 2="Magenta", 3="Yellow", 4="Gray", 5="Matte Black", 6="Photo Black"]
#colorIndex = 3
#colorTonerCodes = {"1" : "black" , "2" : "cyan" , "3" : "magenta" , "4" : "yellow"}
#colorInkCodes = {"1" : "cyan" , "2" : "magenta" , "3" : "yellow" , "4" : "gray" , "5" : "matte black", "6" : "photo black"}

#   .1.3.6.1.2.1.43.11.1.1.7.1.1 = units [19="percent", 15="tenthsOfMilliliters"]
#unitIndex = 7
#unitCodes = {"19" : "percent" , "15" : "tenthsOfMilliliters"}

#   .1.3.6.1.2.1.43.11.1.1.8.1.1 = max [int]
#maxValueIndex = 8
#maxValue = ""


class Printer:
    short_name = ""
    hostname = ""
    is_mono = 0
    style = "laser"
    supplies_list = []

def buildPrinter(short_name, hostname):
    printer = Printer()
    printer.short_name = short_name
    printer.hostname = hostname
    printer.style = getStyle(printer.hostname)
    if printer.style =="none":
        return printer;
    printer.is_mono = getMono(printer.hostname, printer.style)
    printer.colors = []
    
    if printer.style == "laser":
        printer.supplies_list = ["fuser", "cleaner", "transfer"]
        if printer.is_mono:
            printer.colors_list = ["black"]
        else:
            printer.colors_list = ["black", "cyan", "magenta", "yellow"]
    elif printer.style == "plotter":
        printer.colors_list = ["gray", "photo black", "matte black", "yellow", "magenta", "cyan"]

    printer.colors = [[cl,""] for cl in printer.colors_list]
    printer.supplies = [[su,""] for su in printer.supplies_list]
        
    return printer   


def getStyle(hostname):
    errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
            CommunityData(CommunityString, mpModel=0),
            UdpTransportTarget((hostname, 161)),
            ContextData(),
            ObjectType(ObjectIdentity('.1.3.6.1.2.1.43.11.1.1.5.1.1')))
        )
    
    try: 
        if (varBinds[0][1] == 21):
            return "laser"
        elif (varBinds[0][1] == 6):
            return "plotter"
    except IndexError:
        print "Hostname %s not found" % hostname
        return "none"


def getMono(hostname, style):    
    if style == "laser":
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
            CommunityData(CommunityString, mpModel=0),
            UdpTransportTarget((hostname, 161)),
            ContextData(),
            ObjectType(ObjectIdentity('.1.3.6.1.2.1.43.11.1.1.5.1.2')))
            )
        if (varBinds[0][1] == 21):
            return False
        return True


def loadColors(thisPrinter):
    for x in range (1, len(thisPrinter.colors)+1):
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
            CommunityData(CommunityString, mpModel=0),
            UdpTransportTarget((thisPrinter.hostname, 161)),
            ContextData(),
            ObjectType(ObjectIdentity('.1.3.6.1.2.1.43.11.1.1.9.1.%s' % x)))
        )
    
        try:
            thisPrinter.colors[x-1][1] = int(varBinds[0][1])
        except ValueError:
            print "ValueError based on: %s" % str((varBinds[0][1]))
        except IndexError:
            print "Hostname %s not found" % thisPrinter.hostname
            
    return


def loadSupplies(thisPrinter):
    for x in range (len(thisPrinter.colors)+1, len(thisPrinter.colors)+len(thisPrinter.colors)+1):
        
        errorIndication, errorStatus, errorIndex, supplyType = next(
            getCmd(SnmpEngine(),
            CommunityData(CommunityString, mpModel=0),
            UdpTransportTarget((thisPrinter.hostname, 161)),
            ContextData(),
            ObjectType(ObjectIdentity('.1.3.6.1.2.1.43.11.1.1.5.1.%s' % x)))
        )
        
        errorIndication, errorStatus, errorIndex, supplyValue = next(
                getCmd(SnmpEngine(),
                CommunityData(CommunityString, mpModel=0),
                UdpTransportTarget((thisPrinter.hostname, 161)),
                ContextData(),
                ObjectType(ObjectIdentity('.1.3.6.1.2.1.43.11.1.1.8.1.%s' % x)))
            )
        supplyType = int(supplyType[0][1])
        supplyValue = int(supplyValue[0][1])
        
        # printer.supplies = ["fuser", "cleaner", "transfer"]
        # 15="fuser", 18="cleanerUnit", 20="transferUnit"
        if (supplyType == 1):
            return
        if (supplyType == 20):
            thisPrinter.supplies[2][1] = supplyValue
            continue
        if (supplyType == 18):
            thisPrinter.supplies[1][1] = supplyValue
            continue
        if (supplyType == 15):              
            thisPrinter.supplies[0][1] = supplyValue
            continue
        else:
            print supplyType
        
    return


for i in Printers:
    short_name = "%s-prt-%s" % (WHID.lower(), i.lower())
    hostname = "%s.%s.amazon.com" % (short_name, WHID.lower())
    
    thisPrinter = buildPrinter(short_name, hostname)
    if thisPrinter.style=="none":
        continue
    else:
        loadColors(thisPrinter)
        if thisPrinter.style != "plotter":
            loadSupplies(thisPrinter)
    
            
    print "%s is a %s %s" % (thisPrinter.short_name, "mono" if thisPrinter.is_mono else "color", thisPrinter.style)
    for x in range(0,len(thisPrinter.colors)):
        if thisPrinter.style == "plotter":
            thisPrinter.colors[x][1] = int(thisPrinter.colors[x][1]/1.3)
        print "\t", thisPrinter.colors[x]
    for x in range(0,len(thisPrinter.supplies)):
        if thisPrinter.style != "plotter":
            if not(isinstance(thisPrinter.supplies[x][1], basestring)):
                print "\t", thisPrinter.supplies[x]
