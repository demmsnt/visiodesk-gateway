class BACnetWriter:

    @staticmethod
    def create_bacwi(devices):
        """
        example of file format
        ;Device   MAC (hex)            SNET  SADR (hex)           APDU
        ;-------- -------------------- ----- -------------------- ----
          200     0A:15:50:0C:BA:C0    0     00                   480
          300     0A:15:50:0D:BA:C0    0     00                   480
          400     0A:15:50:0E:BA:C0    0     00                   480
          500     0A:15:50:0F:BA:C0    0     00                   480
          600     0A:15:50:10:BA:C0    0     00                   480
        ;
        ; Total Devices: 5
        """
        lines = []
        lines.append(";Device   MAC (hex)            SNET  SADR (hex)           APDU")
        lines.append(";-------- -------------------- ----- -------------------- ----")
        for device in devices:
            id = device['id']
            host = device['host'].split(".")
            port = device['port']
            mac = "{:02X}:{:02X}:{:02X}:{:02X}:{}:{}".format(int(host[0]), int(host[1]), int(host[2]), int(host[3]),
                                                             hex(port)[2:4].upper(), hex(port)[4:6].upper())
            apdu = device['apdu']
            line = "{:<9} {:<20} {:<5} {:<20} {:<4}".format(
                device['id'],
                mac,
                0,
                '00',
                apdu
            )
            lines.append(line)
        lines.append(";")
        lines.append("; Total Devices: {}".format(len(devices)))
        return "\n".join(lines)

    @staticmethod
    def write_bacwi(self, devices, path):
        text = BACnetWriter.create_bacwi(devices)
        f = open(path, "+w")
        f.write(text)
        f.close()
