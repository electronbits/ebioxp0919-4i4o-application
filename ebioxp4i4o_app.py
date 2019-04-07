#!/usr/bin/python3
"""
ElectronBits 2020
The script hadles commnads send to EBIOXP0910-4I4O board 
from a Raspberry Pi which sits on EBRPIH1118 board. 
To read input status and energize/de-energize power relays.
It uses smbus/smbus2 module to connect to the board. 
"""


try:
    import smbus as smbus
except Exception as e:
    try:
        import smbus2 as smbus
    except:
        err_text = "There is no smubs/smbus2 module available on your system\nPlease\
 consider installing smbus/smbus2 module for python3"
        print(Colors.colored_text(err_text,'FAIL'))
from sys import exit,argv,stderr
import argparse
from enum import IntEnum

class RelayState(IntEnum):
    OFF = 0,
    ON = 1,


class Colors:
    color_codes= {
    'HEADER' : '\033[95m',
    'OKBLUE' : '\033[94m',
    'OKGREEN' : '\033[92m',
    'WARNING' : '\033[93m',
    'FAIL' : '\033[91m',
    'ENDC' : '\033[0m',
    'BOLD' : '\033[1m',
    'UNDERLINE' : '\033[4m',
    }

    @classmethod
    def colored_text(cls,text:str,color_code:str)->str:
        color = cls.color_codes.get(color_code)
        if color is not None:
            return color+text+cls.color_codes['ENDC']
        else:
            return text

def get_bus()->smbus.SMBus:
    "It will return smbus.SMBus object"
    try:
        return smbus.SMBus(1)
    except Exception as e:
        print(Colors.colored_text(e.__str__(),'FAIL'))
        exit(0)

def cleanup(bus):
    bus.close()
    print(Colors.colored_text("Clean up Done.",'OKGREEN'))
    exit(0)

def is_already_init(bus,chip_address,cfg_reg,expected_value)->bool:
    ret = read_from_board(bus,chip_address,cfg_reg)
    return ret == expected_value

def init_board(bus,chip_address,cfg_reg,wr_reg,expected_value)->bool:
    try:
        bus.write_byte_data(chip_address,cfg_reg,0xf0)
        bus.write_byte_data(chip_address,wr_reg,0x0)
    except OSError as e:
        print(Colors.colored_text(e.__str__(),'FAIL'))
        exit(0)

def read_from_board(bus,chip_address,target_reg):
    "reads target register value which can be either config register or read register"
    return bus.read_byte_data(chip_address,target_reg)

def read_input_state(bus,chip_address,target_reg,input_number):
    expected_values = {1:0x1,2:0x2,3:0x4,4:0x8}
    ret = read_from_board(bus,chip_address,target_reg)>>4 #to move data from LSB to MSB: 0xf0 to 0xf
    #shift >> pin state to the most right position. for example for input number two the value would be 0x2
    # and by shifting >> 1 (input_number - 1), it will show its value correctly.
    return (ret&expected_values[input_number]) >> (input_number-1)

def relay_handler(bus,chip_address,wr_reg,rd_reg,relay_number,state:RelayState):
    former_relays_status = (read_from_board(bus,chip_address,rd_reg)) & 0xf
    
    if state == RelayState.OFF:
        new_relays_status = former_relays_status & (0xf ^ (1<<relay_number-1))
    elif state == RelayState.ON:
        new_relays_status = former_relays_status | (1<<relay_number-1)
    bus.write_byte_data(chip_address,wr_reg,new_relays_status)




if __name__ == "__main__":
    RD_REGISTER = 0x00 
    WR_REGISTER = 0x01
    CFG_REGISTER = 0x03
    CFG_VALUE = 0xf0
    
    parser = argparse.ArgumentParser(description="Handles command for IO board")
    pins_group = parser.add_mutually_exclusive_group()
    pins_group.add_argument("-r","--relay",type=int,default=None,metavar='',help="Relay number for energize/de-energize")
    pins_group.add_argument("-di","--digital_input",type=int,default=None,help="Digital input number for read digital input state.")
    parser.add_argument('--on',action='store_true',default=False,required=False,help="When -r/--relay called this switch can be specified to energize the relay")
    parser.add_argument('--off',action='store_true',default=False,required=False,help="When -r/--relay called this switch can be specified to de-energize the relay")
    parser.add_argument('--addr',action='store',type=int,default=0x3f,help="It specifies the chip address, default value: 0x3f (63 in decimal)")
    args = parser.parse_args()
    
    CHIP_ADDR = args.addr
    bus = get_bus()

    if not is_already_init(bus,CHIP_ADDR,CFG_REGISTER,CFG_VALUE):
        print(Colors.colored_text("Initilizing Board...",'UNDERLINE'))
        init_board(bus,CHIP_ADDR,CFG_REGISTER,WR_REGISTER,CFG_VALUE)

    if args.digital_input is not None:
        if args.digital_input in (1,2,3,4):
            print(read_input_state(bus,CHIP_ADDR,RD_REGISTER,args.digital_input))
        else:
            print(Colors.colored_text("Invalid digital input number.",'FAIL'))
        
        pass
    elif (args.relay is not None and (args.on or args.off)) :
        if args.relay in (1,2,3,4):
            state = RelayState.OFF if args.off else RelayState.ON
            relay_handler(bus,CHIP_ADDR,WR_REGISTER,RD_REGISTER,args.relay,state)
        else:
            print(Colors.colored_text("Invalid Relay number.",'FAIL'))
        
    else:
        parser.print_help(stderr)
        print("\n\nExample: python3 %s -r1 --on "%(argv[0]),"\tIt will energize relay#1\n")

    print(Colors.colored_text("main function has been finished, cleaning up...",'OKGREEN'))
    cleanup(bus)
