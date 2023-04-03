import simplepyble
from time import sleep

UUID_SPS = "2456e1b9-26e2-8f83-e744-f34f01e9d701"
UUID_FIFO = "2456e1b9-26e2-8f83-e744-f34f01e9d703"


def main():
    
    adapter = simplepyble.Adapter.get_adapters()[0]
    adapter.set_callback_on_scan_start(lambda: print("Scan started."))
    adapter.set_callback_on_scan_stop(lambda: print("Scan complete."))
    
    while(True):

        adapter.scan_for(10000)

        peripheral_list = adapter.scan_get_results()

        print("Please select a peripheral:")
        device_list = []
        for peripheral in peripheral_list:
            if "NINA" in peripheral.identifier():
                device_list.append(peripheral)

        if len(device_list):
            for index, device in enumerate(device_list):
                print(f"{index}: [{device.address()}] {device.identifier()}")
            break
        else:
            while(True):
                print("No connectable devices found. Try again? (Y/n)")
                cmd = input()
                if cmd == "" or cmd == "Y" or cmd == "y":
                    cmd = True
                    break
                elif cmd == "n" or cmd == "N":
                    cmd = False
                    break

        if not cmd:
            exit()

    choice = int(input("Select a device: "))
    device = device_list[choice]

    print(f"Connecting to: {device.identifier()} [{device.address()}]")
    device.connect()

    device.notify(UUID_SPS, UUID_FIFO, lambda data: print(f"Notification: {data.decode('ascii')}"))

    while(True):
        try:
            print("Select command:")
            print(" 0 - Write")
            print(" 1 - Read")
            print(" 2 - Get services")
            print(" q - Exit")
            cmd = input()

            if cmd == "0":
                data = input("Enter content to write: ")
                device.write_request(UUID_SPS, UUID_FIFO, data.encode('ascii'))
            elif cmd == "1":
                data = device.read(UUID_SPS, UUID_FIFO)
                print(f"Read: {data.decode('ascii')}")
            elif cmd == '2':
                services = device.services()
                for srvc in services:
                    print('*' * 40)
                    print(srvc.data(), srvc.uuid())
                    characteristics = srvc.characteristics()
                    for char in characteristics:
                        print('  ', char.uuid())
                        descriptors = char.descriptors()
                        for desc in descriptors:
                            print('    ', desc.uuid())
            elif cmd == "q":
                break
            else:
                print("Invalid, try again")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)
            pass
    
    device.disconnect()
    print("\n\nExiting ... \n")
    exit()


if __name__ == "__main__":
    main()
