from scanners.base import BaseScanner

class Scanner(BaseScanner):

    devices_url_file = ("http://app.vadix.io/devices.json", "../assets/devices.json")

    def __init__(self, *args, **kwargs):
        self.known_devices = self._get_json_url_or_file(self.devices_url_file)
    
    def filter_known_devices(self, source_data):
        print("Source data: %s" % self.cf_json(source_data))

        detected_known_devices = {}
        for ip, ip_data in source_data.items():
            known_device = self.is_device_known(ip_data)
            if known_device:
                detected_known_devices[ip] = known_device

        print("Matched known devices: %s" % detected_known_devices)
        for ip, known_device in detected_known_devices.items():
            del(source_data[ip])
            source_data[known_device] = {}


    def is_device_known(self, ip_data):
        mac = ip_data.get('mac')
        open_ports = ip_data.get('open_ports', [])

        for device, device_heuristic in self.known_devices.items():
            heuristic_keys = device_heuristic.keys()
            # Test if a mac Address matches
            if mac and 'mac' in heuristic_keys:
                if not max([mac.startswith(vmac) for vmac in device_heuristic.get("mac")]):
                    continue
            # Test a port groups match
            if open_ports and 'open_ports' in heuristic_keys:
                if not max([sorted(open_ports) == sorted(dev_op) for dev_op in device_heuristic.get("open_ports")]):
                    continue
            # Must be known
            return device


    def generate_pipeline_steps(self):
        steps = []
        steps.append({
            "func": self.filter_known_devices,
            "end_text": "Filtering known devices"
        })
        return steps
