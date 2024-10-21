# Copyright (c) 2017-2023 Analog Devices Inc.
# All rights reserved.
# www.analog.com

#
# SPDX-License-Identifier: Apache-2.0
#

# Release Notes -----------------------------------------------------------
# This script uses the Aardvark from Total Phase drivers to communicate with ADM1266.
# If you would like to use other devices, please comment out the Aardvark sections below.
# Open PMBus_I2C.py and replace aardvark_py APIs with the dongle APIs that you are using.
# No other modification is required

import ADM1266_Lib
import PMBus_I2C
import sys
import time
import hex_file_chopper

if sys.version_info.major < 3:
    input = raw_input

# Print telemetry information

def Status_Print():
    print('\n')
    print('-------------------------------------------------------------------------')
    print("Rails")
    print('-------------------------------------------------------------------------')
    if len(ADM1266_Lib.OV_I_Rails) != 0:
        print('\n'.join(ADM1266_Lib.OV_I_Rails))
        print('-------------------------------------------------------------------------')
    if len(ADM1266_Lib.UV_I_Rails) != 0:
        print('\n'.join(ADM1266_Lib.UV_I_Rails))
        print('-------------------------------------------------------------------------')
    if len(ADM1266_Lib.OVW_I_Rails) != 0:
        print('\n'.join(ADM1266_Lib.OVW_I_Rails))
        print('-------------------------------------------------------------------------')
    if len(ADM1266_Lib.UVW_I_Rails) != 0:
        print('\n'.join(ADM1266_Lib.UVW_I_Rails))
        print('-------------------------------------------------------------------------')
    if len(ADM1266_Lib.Normal_I_Rails) != 0:
        print('\n'.join(ADM1266_Lib.Normal_I_Rails))
        print('-------------------------------------------------------------------------')
    if len(ADM1266_Lib.Disabled_I_Rails) != 0:
        print('\n'.join(ADM1266_Lib.Disabled_I_Rails))
        print('-------------------------------------------------------------------------')
    if len(ADM1266_Lib.Signals_I_Status) != 0:
        print("Signals")
        print('-------------------------------------------------------------------------')
        print('\n'.join(ADM1266_Lib.Signals_I_Status))
        print('-------------------------------------------------------------------------')

def MFR_Rev_Read(device_addr, len):
    if (len < 0 or len > 9):
        print("Invalid Length. 0 < LEN < 9. Max len is 8 + 1 PEC byte")

    crcData = [hex(device_addr), hex(0x9B), hex(0x1), hex(0x8), hex(0x41)]

    # len + length byte + PEC
    inData = PMBus_I2C.PMBus_BlockWR(device_addr, [0x9B, 1, len], len+2)
    inData = inData.tolist()
    for i in range(0, len+2):
        inData[i] = hex(inData[i])
        crcData.append(inData[i])

    print(*inData)
    print("PEC: " + str(inData[-1]))
    print("CRC Data:")
    print(*crcData)

    return inData

if __name__ == '__main__':

    # Open Connection to Aardvark (Comment this section out for using other devices other than Aardvark)
    # If no dongle ID is passed into the function an auto scan will be performed and the first dongle found will be used
    # For using a specific dongle pass the unique ID number, as shown in example below.
    # Example: PMBus_I2C.Open_Aardvark(1845957180)
    PMBus_I2C.Open_Aardvark()

    # PMBus address of all ADM1266 in this design. e.g: [0x40, 0x42]
    if len(sys.argv) > 1:
        #All trailing arguments are treated as addresses in hex
        ADM1266_Lib.ADM1266_Address = [int(a,16) for a in sys.argv[1:]]
    else:
        #Default to [0x40, 0x42]
        # ADM1266_Lib.ADM1266_Address = [0x40, 0x42]
        ADM1266_Lib.ADM1266_Address = [0x40]

    # Check if all the devices listed in ADM1266_Lib.ADM1266_Address above is present.
    # If all the devices are not present the function will throw an exception and will not procced with the remaining code.
    ADM1266_Lib.device_present()

    # Lists to convert status to a readable format
    Rail_Status = ["Normal", "Disabled", "Under Voltage Warning", "Over Voltage Warning", "Under Voltage Fault", "Over Voltage Fault"]
    Signal_Status = ["Low", "High"]

    # Dynamically initialize nested lists to store system and telemetry data
    ADM1266_Lib.Init_Lists()

    if ADM1266_Lib.refresh_status() == True:
        print("Memory refresh is currently running, please try after 10 seconds.")

    else:
        # Get raw data and parse it for system information
        ADM1266_Lib.System_Parse()

        read_type = int(input("Type 0 for reading back the status of all rails and signals,\n1 for reading back a specific Rail,\n2 for reading back a specific Signal, \n3 to read back MFR_REVISION.\n "))

        # Readback all data
        if read_type == 0 :
            # Get current telemetry values
            ADM1266_Lib.Get_Current_Data()
            # Parse current Rails telemetry values
            ADM1266_Lib.Rails_I_Status()
            # Parse current Signals telemetry values
            ADM1266_Lib.Signals_I_Status_Fill()
            # Print Telemetry data
            Status_Print()

        # Readback data for a single Rail
        if read_type == 1 :
            address = input("Enter device address (e.g. 0x40): ")
            address = int(address, 16)
            address = ADM1266_Lib.ADM1266_Address.index(address)
            channel = input("Enter channel name (e.g. VH1, VP1): ")
            page = ADM1266_Lib.VX_Names.index(channel)
            # Function that returns the value, status and name of the voltage monitoring pin for a particular device
            (value, status, name) = ADM1266_Lib.Get_Rail_Current_Data(address, page)
            status = Rail_Status[status]
            if name == 0 :
                name = "Pin not assigned to any rail"
            print(str(name) + " - " + str(status) + " - " + str(value) +"V")

        # Readback data for a single digital signal
        if read_type == 2 :
            address = input("Enter device address (e.g. 0x40): ")
            address = int(address, 16)
            address = ADM1266_Lib.ADM1266_Address.index(address)
            channel = input("Enter channel name (e.g. PDIO1, GPIO1): ")
            index = ADM1266_Lib.PDIO_GPIO_Names.index(channel)
            # Function that returns the status and name of the digital pin for a particular device
            (status, name) = ADM1266_Lib.Get_Signal_Current_Data(address, index)
            status = Signal_Status[status]
            if name == 0 :
                name = "Pin not assigned to any signal"
            print(name + " - " + status)

        if read_type == 3 :
            address = input("Enter device address (e.g. 0x40): ")
            address = int(address, 16)
            print("Reading MFR_Revision...\n")
            MFR_Rev = MFR_Rev_Read(int(address, 16), 8)
            time.sleep(0.1) # wait 100 ms

    # Close Connection to Aardvark ( Comment this section out for using other devices other than Aardvark)
    PMBus_I2C.Close_Aardvark()
