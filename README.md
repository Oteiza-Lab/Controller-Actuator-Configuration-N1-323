# Controller-Actuator-Configuration-N1-323
Controller Actuator Configuration for Studying Fish Behavior in Currents

README
**CAREFULLY REVIEW THIS DOCUMENTATION BEFORE ACTUATOR USE TO ENSURE PROPER HANDLING OF THE EQUIPMENT**

Oteiza Lab Controller-Actuator Configuration
Last Updated 03/07/2024 - Daniel Durst

---------------------------------------------
OVERVIEW

This README contains information on the Oteiza Lab Controller-Actuator Configuration, including proper use and issue fix information. If you are to improve the code, include
additional functionality in this README, then update the date and name for documentation purposes.

The purpose of this setup is to create a current with which to study fish behavior. The actuator holds a metal rod with a piston head that creates the current in the transparent
piping.

The actuator (Copley Servotube Actuator STA1112) is connected to the controller (Copley Accelnet ACJ 090 09), which is connected to the DELL PC via COM Port 3. The actuator
functionality is programmed in the python file motor.py, with helper files such as position.py, listavailableports.py, and testports.py for issue fixes (outlined below). The actuator
can be run in three different ways through the terminal: running the file alone, running the file with parameters, running the file with parameters and flags (all outlined below). The
actuator reponds to the requests of the user by moving the rod/piston from the desired start boundary (we recommend 0) to the desired +UNIT boundary specified by the user. The rod/piston
oscillate between those two boundaries for the specified duration of time desired by the user. The actuator moves the rod/piston at the desired velocity, acceleration, and deceleration
specified by the user. Do not worry about responding with incorrect or dangerously high values to the prompts. The actuator's limitations have been specified by the script and will notify
you if your values are out of range, as well as being safe to use in the designated ranges.

The actuator is not used to its full power (set currently to 1/20th of its power!!!), as 5.4 m/s is dangerously fast, can short circuit, overheat, and destroy the motor and is unnecessary
for this lab. If you are requiring a higher velocity, minimize the scale_factor GRADUALLY. The limitations of the scale factor are found at .000318, but we note 1 do NOT reach this limit
and 2 the motor acts much differently with this scale factor. If at any point, the code is to have funcitonality added or changed, refer to the manuals on the controller and actuator: 
https://copleycontrols.com/wp-content/uploads/2018/02/Accelnet_Micro_Panel_CANopen-ACJ-Datasheet-Datasheet.pdf & http://www.servovision.com/copley/download/STA11.pdf respectively.
---------------------------------------------

---------------------------------------------
CURRENT ACTUATOR CAPABILITIES & IMPORTANT NOTES

    VELOCITY: .275 m/s ~ 864 Units
    ACCELERATION / DECELERATION: .625 m/s^2 ~ 100 Units **Calculated based off tested values for velocity and using same scale_factor (could be off)
    SCALE FACTOR BEING USED: .00625 (~5% of capability)

    ** IMPORTANT **
    - The acceleration / deceleration values practically stop the rod/piston instantaneously at 100 Units at the current available max speed (.275 m/s = 864 Units).
    - To actually notice the acceleration / deceleration, utilize values <40.
    - The script currently does not anticipate the boundaries, only realizing to turn around when it has detected it is past it. THEREFORE, you must anticipate the deceleration rate
    you are using and understand that the rod/piston will overshoot the boundary you have set. This is why it is important to start the rod/piston at 0, having space to overshoot on the 
    (-) side of the tube and not cause issues with the rod/piston exiting the tube.
    ** IMPORTANT **

MAX ACTUATOR CAPABILITIES **Difficult to find exact metrics due to high capability of actuator and risk of short circuit

    VELOCITY: 5.4 m/s ~ 17000 Units (calculated off of trial and error)
    ACCELERATION / DECELERATION: 378 m/s^2 ~ 1,190,397 Units **Again calculated based off velocity since we cannot test acc/dec limits easily (could be off)
---------------------------------------------

---------------------------------------------
STEPS TO RUN ACTUATOR PROPERLY

1 Set the metal rod in the actuator with the piston attached to the end.
2 Place the piston in the transparent tubing.
3 **ALWAYS Align the black line on the piston head with the line labelled 0 (advised) before running the actuator.**
4 If you find yourself in the wrong directory, follow these steps in the terminal window
 (replace daniel.durst with personal account name). Otherwise move to step 5:
    PS C:\Users\daniel.durst\Downloads\Actuator_OteizaLab> cd /
    PS C:\> cd Users
    PS C:\Users> cd daniel.durst
    PS C:\Users\daniel.durst> cd Downloads
    PS C:\Users\daniel.durst\Downloads> cd Actuator_OteizaLab
5 Run Commands:
    1 Running the file alone:
        PS C:\Users\daniel.durst\Downloads\Actuator_OteizaLab> python motor.py
        ___ (follow prompts: 5)
        ___ (output, enable drive)
    2 Running the file with parameters [VELOCITY] [ACCELERATION] [DECELERATION] [TIME] [DELTA]:
        PS C:\Users\daniel.durst\Downloads\Actuator_OteizaLab> python motor.py 100 10 10 15 150
        ___ (output, enable drive)
    3 Running the file with parameters and flags [-v][VELOCITY] [-a][ACCELERATION] [-d][DECELERATION] [-t][TIME] [-dist][DELTA]:
        PS C:\Users\daniel.durst\Downloads\Actuator_OteizaLab> python motor.py -v 3 -a 10 -d 10 -t 15 -dist 150
        ___ (output, enable drive)
    - Method (2) requires precise ordering of specified parameters. Method (3)'s ordering is insignificant as long as the flag is provided before the value.
    - If the parameters in methods (2) and (3) are incomplete, the script will default to method (1) and run the 5 prompts for value specification.
6 **IF AT ANY TIME THE ACTUATOR MUST BE STOPPED IMMEDIATELY:
    1 Hold down CTRL + C:
        INFO:root: Motor position: -320.12500
        INFO:root: Motor position: -316.30000
        INFO:root: Motor position: -312.45000
        INFO:root: Interrupt detected. Attempting to disable drive...
        INFO:root: Disabling drive.
        INFO:root: Drive disabled successfully.
    2 Reset rod/piston positioning and ensure safety of hardware.
---------------------------------------------

---------------------------------------------
IMPORTANT CONSIDERATIONS FOR PROPER ACTUATOR FUNCTIONALITY AND ISSUE FIXES

1 Actuator Enabled, Positioning Stagnanat, Event Register 40e000:
    PS C:\Users\daniel.durst\Downloads\Actuator_OteizaLab> python motor.py -v 300 -a 10 -d 10 -dist 150 -t 15
    ELOCITY set to: 0.095 m/s (300.000 Units)
    ACCELERATION set to: 0.062 m/s2 (10.000 Units)
    DECELERATION set to: 0.062 m/s2 (10.000 Units)
    TIME set to: 15.000 seconds (187 Units)
    DELTA set to: 150.000 Units
    INFO:root: Motor position: -285.29375
    INFO:root: Load position: -285.2875
    INFO:root: Following error: 0.0
    INFO:root: Set mode relative move
    INFO:root: Set mode programmed position
    INFO:root: Enable drive
    INFO:root: Motor enabled successfully.
    INFO:root: Event register: 4251648
    INFO:root: Motor position: -285.28750
    INFO:root: Motor position: -285.28750
    INFO:root: Motor position: -285.28750
    INFO:root: Motor position: -285.28750
    INFO:root: Motor position: -285.28750

    STEPS TO FIX:
    1 Run in Terminal (Ensure proper issue):
        PS C:\Users\daniel.durst\Downloads\Actuator_OteizaLab> python position.py
        INFO:root: Motor position: -285.28750
        INFO:root: Following error: 0.0
        INFO:root: Enable drive
        INFO:root: Event register: 40e000
        INFO:root: Motor position: -285.28750
        INFO:root: Disable drive

        C:\Users\daniel.durst\AppData\Local\Microsoft\WindowsApps\python.exe: can't open file 'C:\\Users\\daniel.durst\\Downloads\\Actuator_OteizaLab\\listavailable': [Errno 2] No such file or directory
        PS C:\Users\daniel.durst\Downloads\Actuator_OteizaLab> python listavailableports.py
        Available serial ports: ['COM1', 'COM3']

        PS C:\Users\daniel.durst\Downloads\Actuator_OteizaLab> python testports.py
        INFO:root:Opened port COM1 successfully.
        INFO:root:Response from COM1: 
        Port COM1 did not respond.
        INFO:root:Opened port COM3 successfully.
        INFO:root:Response from COM3: ok
        Port COM3 responded: ok

        - Here we see that the issue is detailed in the event register 40e000 (most likely due to hyperextension of the rod),
        translating to a fault configuration error (): Drive fault. 22: A drive fault that was configured as latching has occurred.
        For information on latching faults, see the CME 2 User Guide. If you see this event register, move on to step 2. We also
        understand that the actuator is running through Port COM3 as it returned the 'ok' when asked to respond.
    2 Open CME on this PC
    3 In the Copley Neighborhood folder, there should be 1 Virtual Amplifier and 2 COM3: N1-323
        - If COM3 is not in this folder: N1-323, open Tools-->Communications Wizard-->Serial Ports-->Next-->Add COM3-->Remove COM1-->Next-->Finish
        - If COM3 is not available to add, ensure it is not being utilized by another device.
    4 Click on the Control Panel (tab next to settings gear)
    5 Click Enable & Clear Faults
    6 Close CME (opening COM3 port for actuator use)
    7 Run Commands and Check Functionality

2 Position Stagnanat, Event Register e3:
    PS C:\Users\daniel.durst\Downloads\Actuator_OteizaLab> python motor.py 400 10 10 15 150
    VELOCITY set to: 0.127 m/s (400.000 Units)
    ACCELERATION set to: 0.062 m/s2 (10.000 Units)
    DECELERATION set to: 0.062 m/s2 (10.000 Units)
    TIME set to: 15.000 seconds (187 Units)
    DELTA set to: 150.000 Units
    ERROR:root: Unexpected response: e 3
    ERROR:root: Failed to get motor position.
    INFO:root: Load position: 340.91875000000005
    INFO:root: Following error: 0.0
    INFO:root: Set mode relative move
    INFO:root: Set mode programmed position
    INFO:root: Disabling drive.
    INFO:root: Drive disabled safely.
    INFO:root: Exiting program due to interrupt.

    STEPS TO FIX:
    1 Run in Terminal (Ensure proper issue):
        PS C:\Users\daniel.durst\Downloads\Actuator_OteizaLab> python position.py
        INFO:root: Motor position: -285.28750
        INFO:root: Following error: 0.0
        INFO:root: Enable drive
        INFO:root: Event register: e 3
        INFO:root: Motor position: -285.28750
        INFO:root: Disable drive

        - Here we see issue is detailed in the event register e3 (most likely due to overworking the motor at dangerously high speeds).
        This translates to a short circuit amongst other issues: Short circuit detected, Drive over temperature, Over voltage, Under voltage,
        Current output limited.
    2 Stop any running program and unplug the actuator (black cable)
    3 Be careful not to touch any of the electrical boxes or open circuits, if any
    4 Let the actuator cool down for 30 minutes and test it again
    5 If e3 error still there, contact help due to potential short circuit damage
        

3 PISTON OVERSHOOTS DESIRED +DELTA AT HIGH SPEEDS
    1 This is normal due to several factors:
        - Communication Delays: The controller sends the actuator a signal to reverse the direction when the boundary is reached.
        This signal, however, takes time to send and be received, and therefore this delay is more pronounced at higher speeds, leading
        to overshooting the desired boundary.
        - Processing Delay: The signals sent by the controller also take time to be processed and understood, contributing to the delay
        seen at higher velocities.
    2 TO FIX:
        - Utilize lower speeds.
        - Implement a PID Controller to handle dynamic delay.
        - Adjust acceleration / deceleration profile to reduce momentum at boundaries.

4 "FAILED TO DISABLE DRIVE" IN TERMINAL
    1 The commands CTRL + C will disable the drive and stop the motion of the rod/piston
        - Since the actuator is in the process of disabling the drive (it is not instantaneous) while looking for an exception e,
        it might throw out this message.

    2 TO FIX:
        - Ensure that you give time to the def disable_drive method after setting the register self.set("r0x24 0") AKA to stop. This
        is done by adding: time.sleep(1) after the register set.
        ** This line is already in the code, but is an important note if this code is improved and this functionality is lost.
