using System;
using System.Dynamic;
using Windows.Devices.Bluetooth;
using Windows.Devices.Bluetooth.GenericAttributeProfile;
using Windows.Devices.Enumeration;
using System.Threading;
using System.Threading.Tasks;
using Windows.Storage.Streams;
using System.Collections.Generic;

namespace BleTaskWin
{
    public class BleTask: DynamicObject
    {
        public BluetoothLEDevice bus;
        public bool verbose = false;
        public string uuid;
        
        private List<DeviceInformation> modiDevices = new List<DeviceInformation>();
        private GattCharacteristic targetChar;
        private Queue<string> recv_q = new Queue<string>();

        public BleTask(bool verbose = false, string uuid = "")
        {
            this.verbose = verbose;
            this.uuid = uuid;
        }

        public List<string> list_modi_devices()
        {
            modiDevices.Clear();
            Scan();
            List<string> device_names = new List<string>();
            foreach(DeviceInformation info in modiDevices)
            {
                device_names.Add(info.Name.ToUpper());
            }
            return device_names;
        }
        public void open_conn()
        {
            if (modiDevices.Count == 0)
            {
                Scan();
            }
            DeviceInformation targetInfo = null;
            if (uuid.Length > 0) {
                foreach (DeviceInformation info in modiDevices)
                {
                    if (info.Name.ToUpper().Contains(uuid))
                    {
                        targetInfo = info;
                        break;
                    }
                }
            }
            else
            {
                targetInfo = modiDevices[0];
            }
            if(targetInfo == null)
            {
                throw new Exception(string.Format("MODI network module of uuid {0} not found", uuid));
            }
            ConnectDevice(targetInfo).Wait();
        }

        public void close_conn()
        {
            Disconnect().Wait();
        }

        private async Task Disconnect()
        {
            GattCommunicationStatus status = await targetChar.WriteClientCharacteristicConfigurationDescriptorAsync(
                         GattClientCharacteristicConfigurationDescriptorValue.None);
            if (status == GattCommunicationStatus.Success)
            {
                targetChar.ValueChanged -= on_receive;
            }
            bus.Dispose();
        }

        public void send(byte[] pkt)
        {
            write_char(pkt).Wait();
        }

        private async Task write_char(byte[] pkt)
        {
            var writer = new DataWriter();
            writer.WriteBytes(pkt);

            GattCommunicationStatus write_result = await targetChar.WriteValueAsync(writer.DetachBuffer());
        }

        public string recv()
        {
            if (recv_q.Count > 0)
            {
                return recv_q.Dequeue();
            }
            else
            {
                return null;
            }
        }

        private void Scan()
        {
            // Query for extra properties you want returned
            string[] requestedProperties = { "System.Devices.Aep.DeviceAddress", "System.Devices.Aep.IsConnected" };

            DeviceWatcher deviceWatcher =
                        DeviceInformation.CreateWatcher(
                                BluetoothLEDevice.GetDeviceSelectorFromPairingState(false),
                                requestedProperties,
                                DeviceInformationKind.AssociationEndpoint);
         
            deviceWatcher.Added += on_added;
            deviceWatcher.Updated += DeviceWatcher_Updated;
            deviceWatcher.Removed += DeviceWatcher_Removed;
            deviceWatcher.Start();
            Thread.Sleep(1000);
            deviceWatcher.Stop();
        }

        private void on_added(DeviceWatcher watcher, DeviceInformation info)
        {
            if (info.Name.Contains("MODI"))
            {
                modiDevices.Add(info);
            }
        }

        static void DeviceWatcher_Updated(DeviceWatcher dev, DeviceInformationUpdate info)
        {
            // Console.WriteLine(info.Properties);
        }

        static void DeviceWatcher_Removed(DeviceWatcher dev, DeviceInformationUpdate info)
        {
            // Console.WriteLine(info.Properties);
        }

        private async Task ConnectDevice(DeviceInformation deviceInfo)
        {
            bus = await BluetoothLEDevice.FromIdAsync(deviceInfo.Id);
            GattDeviceServicesResult result = await bus.GetGattServicesAsync();
            if (result.Status == GattCommunicationStatus.Success)
            {
                var services = result.Services;
                foreach (GattDeviceService serv in services)
                {
                    GattCharacteristicsResult char_result = await serv.GetCharacteristicsAsync();

                    if (char_result.Status == GattCommunicationStatus.Success)
                    {
                        var characteristics = char_result.Characteristics;
                        foreach (GattCharacteristic ch in characteristics)
                        {
                            if (ch.Uuid.ToString() == "00008421-0000-1000-8000-00805f9b34fb")
                            {
                                targetChar = ch;
                                break;
                            }
                        }
                    }
                }
            }
            GattCommunicationStatus status = await targetChar.WriteClientCharacteristicConfigurationDescriptorAsync(
                        GattClientCharacteristicConfigurationDescriptorValue.Notify);
            if (status == GattCommunicationStatus.Success)
            {
                targetChar.ValueChanged += on_receive;
            }
        }

        private void on_receive(GattCharacteristic sender, GattValueChangedEventArgs args)
        {
            var reader = DataReader.FromBuffer(args.CharacteristicValue);
            byte[] buffer = new byte[16];
            reader.ReadBytes(buffer);
            recv_q.Enqueue(ble_to_json(buffer));
        }

        private string ble_to_json(byte[] ble_msg)
        {
            string json_msg = "{";
            json_msg += string.Format("\"c\":{0},", ble_msg[0] | ble_msg[1] << 8);
            json_msg += string.Format("\"s\":{0},", ble_msg[2] | ble_msg[3] << 8);
            json_msg += string.Format("\"d\":{0},", ble_msg[4] | ble_msg[5] << 8);
            int length = ble_msg[6] | ble_msg[7] << 8;
            json_msg += string.Format("\"l\":{0},", length);
            byte[] data = new byte[length];
            for (int i = 0; i < length; i++)
            {
                data[i] = ble_msg[8 + i];
            }
            json_msg += string.Format("\"b\":\"{0}\"", Convert.ToBase64String(data));
            json_msg += "}";
            return json_msg;
        }
    }
}
