import asyncio
from bleak import BleakScanner, BleakClient
from time import sleep
import sys
from blessings import Terminal

UUID_MANUFACTURER = "00002a29-0000-1000-8000-00805f9b34fb"
UUID_SOFTWARE_REV = "00002a28-0000-1000-8000-00805f9b34fb"
UUID_MODEL_NUMBER = "00002a24-0000-1000-8000-00805f9b34fb"
UUID_FIRMWARE_REV = "00002a26-0000-1000-8000-00805f9b34fb"

UUID_FIFO = "2456e1b9-26e2-8f83-e744-f34f01e9d703"

term = Terminal()

async def discover(filter : str):
    devices = await BleakScanner.discover()
    target_devices = []
    for device in devices:
       if filter in device.name:
           target_devices.append(device)
    return target_devices

async def get_services(device):
    async with BleakClient(device.address) as client:
        
        if (not client.is_connected):
            raise "Client not connected"
        
        services = client.services
        for service in services:
            print("_" * term.width)
            print('service', service.handle, service.uuid, service.description)
            characteristics = service.characteristics
            for char in characteristics:
                print('  characteristic', char.handle, char.uuid, char.description, char.properties)
                descriptors = char.descriptors
                for desc in descriptors:
                    print('    descriptor', desc)
        print()
        
async def get_characteristics(device):
    async with BleakClient(device.address) as client:
        characteristics = client.services.characteristics
        for characteristic in characteristics:
            print(client.services.get_characteristic(characteristic))

def callback(sender, data):
    print(f"{sender}: {data}")
    sys.stdout.flush()

async def enable_notify(device, uuid):
    async with BleakClient(device.address) as client:
        await client.start_notify(uuid, callback)

async def write(device, uuid, data):
    async with BleakClient(device.address) as client:
        await client.write_gatt_char(uuid, data.encode('utf-8'))

async def read(device, uuid):
    async with BleakClient(device.address) as client:
        return await client.read_gatt_char(uuid)
    
async def print_device_info(device):
    async with BleakClient(device.address) as client:
        char_data = await client.read_gatt_char(UUID_MANUFACTURER)
        print(f"{device.name} - Manufacturer: {char_data.decode()}")
        char_data = await client.read_gatt_char(UUID_MODEL_NUMBER)
        print(f"{device.name} - Model Number: {char_data.decode()}")
        char_data = await client.read_gatt_char(UUID_SOFTWARE_REV)
        print(f"{device.name} - Software REV: {char_data.decode()}")
        char_data = await client.read_gatt_char(UUID_FIRMWARE_REV)
        print(f"{device.name} - Firwamre REV: {char_data.decode()}")

async def get_mtu_size(device):
    async with BleakClient(device) as client:
        if client.__class__.__name__ == "BleakClientBlueZDBus":
            await client._acquire_mtu()
        print(f"{device.name} - MTU Size: {client.mtu_size}")
        return client.mtu_size

def select_device(devices):
    print("Select the device:")
    counter = 0
    for device in devices:
        print(f" {counter:2} - {device.name}")
    return input()

def select_command():
    print("Select command:")
    print(" 0 - Print device info")
    print(" 1 - Print services")
    print(" 2 - Read from FIFO")
    print(" 3 - Write to FIFO")
    return input()

async def main():

    # Get target device (filter by NINA)
    target_devices = await discover("NINA")
    
    while True:
        try:
            print('=' * term.width)
            selection = int(select_device(target_devices))
            if (selection < 0) or (selection > len(target_devices) - 1):
                raise ValueError
            break
        except KeyboardInterrupt:
            print("\n\nExiting ... \n")
            exit()
        except ValueError:
            print("Please, enter a valid option")
        except Exception as e:
            print(e)

    print("\nDevice selected : ", target_devices[selection].name, "\n")
    target_device = target_devices[selection]

    async with BleakClient(target_device) as client:

        # Without enabling the notification, I could not get it to work
        await client.start_notify(UUID_FIFO, callback)

        while True:
            try:
                print()
                print('=' * term.width)
                selection = int(select_command())
                if (selection < 0) or (selection > 3):
                    raise ValueError

                # Print device info
                if selection == 0:
                    char_data = await client.read_gatt_char(UUID_MANUFACTURER)
                    print(f"{target_device.name} - Manufacturer: {char_data.decode()}")
                    char_data = await client.read_gatt_char(UUID_MODEL_NUMBER)
                    print(f"{target_device.name} - Model Number: {char_data.decode()}")
                    char_data = await client.read_gatt_char(UUID_SOFTWARE_REV)
                    print(f"{target_device.name} - Software REV: {char_data.decode()}")
                    char_data = await client.read_gatt_char(UUID_FIRMWARE_REV)
                    print(f"{target_device.name} - Firwamre REV: {char_data.decode()}")

                # Print device services, characteristics, and descriptors
                elif selection == 1:
                    
                    if (not client.is_connected):
                        raise "Client not connected"
                    
                    services = client.services
                    for service in services:
                        print("_" * term.width)
                        print('service', service.handle, service.uuid, service.description)
                        characteristics = service.characteristics
                        for char in characteristics:
                            print('  characteristic', char.handle, char.uuid, char.description, char.properties)
                            descriptors = char.descriptors
                            for desc in descriptors:
                                print('    descriptor', desc)
                    print()

                elif selection == 2:
                    data = await client.read_gatt_char(UUID_FIFO)
                    print("Read data: ", data.decode())
                elif selection == 3:
                    print("Data to write: ", end="")
                    data = input()
                    await client.write_gatt_char(UUID_FIFO, data.encode('utf-8'), response=False)

            except KeyboardInterrupt:
                print("\n\nExiting ... \n")
                exit()
            except ValueError:
                print("Please, enter a valid option")
            except Exception as e:
                print(e)

if __name__ == '__main__':
    asyncio.run(main())
