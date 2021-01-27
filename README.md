# YZXStudio USB Meter Reader

## Serial Port

| Via       | Band rate |
| --------- | --------- |
| USB       | 115200    |
| Bluetooth | 9600      |

## Packet layout

| Field |      Type | Note       |
| ----: | --------: | ---------- |
|   STX |    3 byte | `AB 00 06` |
|  Volt |  int32 LE | / 10, mV   |
|   Amp |  int32 LE | / 10, mA   |
|   A·h | uint32 LE | / 10, mA·h |
|   W·h | uint32 LE | / 10, mW·h |
| Delta | uint32 LE | ms         |
|    D- | uint16 LE | mV         |
|    D+ | uint16 LE | mV         |
