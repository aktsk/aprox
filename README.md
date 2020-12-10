# aprox

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/aktsk/aprox/blob/master/LICENSE)

Android PROXy setting tool

## Motivation
In the security test for android apps, we can specify a local proxy server or local DNS server from the Wifi settings and use a proxy tool to check request and response.
Since it is troublesome to configure this from the GUI, we created this tool so that it can be configured from the CUI.

## Requirements
- adb
- Android Device

## Installation

```
$ pip install git+ssh://git@github.com/aktsk/aprox.git
```

## Usage

Subcommands are assigned with alias, which is useful.

|subcommand  |alias  |desc  |
|---|---|---|
|`proxy` |`p` | Set local proxy server |
|`dns` | `d` | Set local DNS server(rooted device only) |
|`clear` |`c`, `cl`  | Clear local proxy/DNS setting |
|`manual` |`m` | Access WiFi settings page on GUI|


### Set Proxy Server
`proxy` subcommand set the local proxy Server.

```
$ aprox proxy 192.168.100.10:8080
Local proxy has been set up
```

### Set DNS Server (rooted device only)
`dns` subcommand set the local DNS Server. This only works on rooted devices.

Fake DNS servers can be set up using [PacketProxy](https://github.com/DeNA/PacketProxy).

```
$ aprox dns 192.168.100.10
200 0 Resolver command succeeded
```

### Clear Settings
`clear` subcommand clear local proxy/DNS setting.

```
$ aprox clear
Local proxy is not configured...
Cleared local DNS settings!!
```

### Access Wifi settings page
`manual` subcommand access WiFi settings page on GUI.

```
$ aprox manual
Starting: Intent { act=android.settings.WIRELESS_SETTINGS flg=0x4000000 }
```

## License
MIT License