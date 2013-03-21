from network import TCPHandler
from socket import error
import struct
from threading import Thread


def start_client(addr):
    tcphandler = TCPHandler(addr, None, False)
    with tcphandler:
        tcphandler.send(struct.pack("!B", 1))
        data = tcphandler.recieve(2)
        (cmd, name) = struct.unpack("!2B", data)
        print("Connected to Eyetracker %d" % name)
        
        while True:
            data = tcphandler.recieve(25)
            print("Data Recieved!\n")
            if len(data) < 25:
                continue
            etdata = struct.unpack("!B2dq", data)
            print("ETData %s\n" % str(etdata))


if __name__ == "__main__":

    import sys, traceback
    
    addr = ("localhost", 3031)
    print("HAI\n")
    print("CAN I HAS NETWORK?\n")
    print("PLZ OPEN 2 TCP " + str(addr) + "?\n")
    print("\tAWSUM THX\n")
    print("\t\tDO_STUFFS!\n")
    try:
        start_client(addr)

    except:
        print("\tO NOES\n")
        print("\t\tPANIC!\n")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("\t\tLOOKZ! KITTY!")
        try:
            with open("stderr_client.out", "a") as f:
                f.write("KITTY! IT HID " + datetime.datetime.now().isoformat(' ') + "\n")
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=5, file=f)
                f.write("\n\n")
                print("\t\tAWWW.. IT HID IN BOX " + f.name)
        
        except:
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=5)
            print("\t\tAWWW.. IT WANTED TO PLAY...")
        
        
    finally:
        print("KTHXBYE!\n")
