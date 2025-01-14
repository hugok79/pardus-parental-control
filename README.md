# pardus-parental-control
Parental Control application for Pardus.

![screenshots/main-active.png](screenshots/main-active.png)

## Features
- 📑 Application Filtering
  - **Allow Only** List
  - **Deny Only** List
- 🔗 Domain Filtering
  - **Allow Only** List
  - **Deny Only** List
- ⏰ Session Time Limit
  - Limit Session Times

## Installation
Download the .deb file and install it with Pardus Package Installer.

or

```
sudo apt install ./pardus-parental-control_0.1.0_amd64.deb
```
## How to run?
1. Open application with non restricted user
2. Edit Profile and add your own domains and applications
3. Start/Stop Parental Control Service with On/Off Button

## How does it work?
- [Application Filtering](doc/ApplicationFiltering.md)
- [Website Filtering](doc/WebsiteFiltering.md)
- [Session Time Limit](doc/SessionTimeLimit.md)

## How to create a .deb package from source?
Install required development packages:
```
sudo apt install devscripts git-buildpackage
```
Install dependencies & create .deb package from source code:
```
sudo mk-build-deps -ir
gbp buildpackage --git-export-dir=/tmp/build/pardus-parental-control -us -uc
```
