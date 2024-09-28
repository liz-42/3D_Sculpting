# 3D_Sculpting
Code for CSC 513 Assignment 1

- sculpting_script.blend: blend file with icospehre object that can be manipulated with the RotationOperatorSerial script
- SetupSerial.py: Run after opening the blend file to install pyserial library
- RotationOperatorSerial.py: code to read input from accelerometer and ultrasonic range sensor, and move the blender object accordingly. This code should be added as a shortcut under preferences for the 3D view, and run using control + return
- ultrasonicranging.ino: arduino code to read data from the ultrasonic range sensor, and write that data to serial output
- https://makecode.microbit.org/S80537-16376-80285-14576: link to Microsoft MakeCode project for the micro:bit accelerometer code
