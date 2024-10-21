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

CRC_LUT = [0x00, 0x07, 0x0e, 0x09, 0x1c, 0x1b, 0x12, 0x15,
0x38, 0x3f, 0x36, 0x31, 0x24, 0x23, 0x2a, 0x2d,
0x70, 0x77, 0x7e, 0x79, 0x6c, 0x6b, 0x62, 0x65,
0x48, 0x4f, 0x46, 0x41, 0x54, 0x53, 0x5a, 0x5d,
0xe0, 0xe7, 0xee, 0xe9, 0xfc, 0xfb, 0xf2, 0xf5,
0xd8, 0xdf, 0xd6, 0xd1, 0xc4, 0xc3, 0xca, 0xcd,
0x90, 0x97, 0x9e, 0x99, 0x8c, 0x8b, 0x82, 0x85,
0xa8, 0xaf, 0xa6, 0xa1, 0xb4, 0xb3, 0xba, 0xbd,
0xc7, 0xc0, 0xc9, 0xce, 0xdb, 0xdc, 0xd5, 0xd2,
0xff, 0xf8, 0xf1, 0xf6, 0xe3, 0xe4, 0xed, 0xea,
0xb7, 0xb0, 0xb9, 0xbe, 0xab, 0xac, 0xa5, 0xa2,
0x8f, 0x88, 0x81, 0x86, 0x93, 0x94, 0x9d, 0x9a,
0x27, 0x20, 0x29, 0x2e, 0x3b, 0x3c, 0x35, 0x32,
0x1f, 0x18, 0x11, 0x16, 0x03, 0x04, 0x0d, 0x0a,
0x57, 0x50, 0x59, 0x5e, 0x4b, 0x4c, 0x45, 0x42,
0x6f, 0x68, 0x61, 0x66, 0x73, 0x74, 0x7d, 0x7a,
0x89, 0x8e, 0x87, 0x80, 0x95, 0x92, 0x9b, 0x9c,
0xb1, 0xb6, 0xbf, 0xb8, 0xad, 0xaa, 0xa3, 0xa4,
0xf9, 0xfe, 0xf7, 0xf0, 0xe5, 0xe2, 0xeb, 0xec,
0xc1, 0xc6, 0xcf, 0xc8, 0xdd, 0xda, 0xd3, 0xd4,
0x69, 0x6e, 0x67, 0x60, 0x75, 0x72, 0x7b, 0x7c,
0x51, 0x56, 0x5f, 0x58, 0x4d, 0x4a, 0x43, 0x44,
0x19, 0x1e, 0x17, 0x10, 0x05, 0x02, 0x0b, 0x0c,
0x21, 0x26, 0x2f, 0x28, 0x3d, 0x3a, 0x33, 0x34,
0x4e, 0x49, 0x40, 0x47, 0x52, 0x55, 0x5c, 0x5b,
0x76, 0x71, 0x78, 0x7f, 0x6a, 0x6d, 0x64, 0x63,
0x3e, 0x39, 0x30, 0x37, 0x22, 0x25, 0x2c, 0x2b,
0x06, 0x01, 0x08, 0x0f, 0x1a, 0x1d, 0x14, 0x13,
0xae, 0xa9, 0xa0, 0xa7, 0xb2, 0xb5, 0xbc, 0xbb,
0x96, 0x91, 0x98, 0x9f, 0x8a, 0x8d, 0x84, 0x83,
0xde, 0xd9, 0xd0, 0xd7, 0xc2, 0xc5, 0xcc, 0xcb,
0xe6, 0xe1, 0xe8, 0xef, 0xfa, 0xfd, 0xf4, 0xf3]

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

    crc = 0x00
    crcData = [hex(device_addr << 1), hex(0x9B), hex(0x1), hex(0x8), hex((device_addr << 1) | 1)]

    # len + length byte + PEC
    inData = PMBus_I2C.PMBus_BlockWR(device_addr, [0x9B, 1, len], len+2)
    inData = inData.tolist()
    for i in range(0, len+2):
        inData[i] = hex(inData[i])
        if i != len+1:
            crcData.append(inData[i]) # don't append the PEC byte itself

    # Print data from MFR_Rev command
    print("INDATA:")
    print(*inData)
    print("PEC: " + str(inData[-1] + "\n"))
    print("CRCDATA:")
    print(*crcData)

    # Validate PEC Byte with CRC Lookup Table
    print("\nCRC CHECK (should match last byte of inData):")
    for crcVal in crcData:
        crc = CRC_LUT[crc ^ int(crcVal, 16)]
    print(str(hex(crc)))

    # return MFR_Rev command
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
            MFR_Rev = MFR_Rev_Read(address, 8)
            time.sleep(0.1) # wait 100 ms

    # Close Connection to Aardvark ( Comment this section out for using other devices other than Aardvark)
    PMBus_I2C.Close_Aardvark()
