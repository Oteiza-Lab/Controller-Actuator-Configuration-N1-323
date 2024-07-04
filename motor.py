import logging
import argparse
import serial
import time
import sys
from typing import Optional

PORT = 'COM3'

class CopMotorError(Exception):
    pass

class CopMotorError(Exception):
    pass

class CopMotor:
    def __init__(self, port) -> None:
        self._dev = serial.Serial(timeout=15)  # 15 second timeout
        self._scale_factor = 0.00625

        try:
            if port is not None:
                self._dev.port = port
                self.open()
            else:
                self._port = ''
        except serial.SerialException as e:
            logging.error(f" Failed to open serial port {port}: {e}")
            raise

    def _log_str(self, data) -> str:
        return data

    def open(self) -> None:
        self._dev.open()

    def write(self, data: str) -> None:
        logging.debug('write: %s', data)
        self._dev.write(data.encode() + b'\r')

    def read(self) -> str:
        data = self._dev.read_until(b'\r').decode().strip()
        logging.debug('read: %s', data)
        return data

    def set(self, data: str) -> None:
        self.write('s ' + data)
        response = self.read()
        if response != 'ok' and response != 'k':
            raise CopMotorError(f" Failed to set command: {data}. Response: {response}")

    def get(self, data: str) -> Optional[str]:
        self.write('g ' + data)
        response = self.read()
        if response.startswith('v '):
            return response.split(' ')[1]
        else:
            logging.error(f" Unexpected response: {response}")
            return None

    def check_response(self, command: str) -> None:
        response = self.read()
        if response != 'ok':
            raise CopMotorError(f" Failed command: {command}. Response: {response}")

    def trajectory(self) -> None:
        self.write('t 1')
        self.check_response('t 1')

    def set_mode_relative_move(self):
        logging.info(self._log_str(" Set mode relative move"))
        self.set('r0xC8 256')

    def set_mode_programmed_position(self):
        logging.info(self._log_str(" Set mode programmed position"))
        self.set('r0xC4 21')

    def set_relative_move(self, data, direction=1):
        x = int(data / self._scale_factor)
        x *= direction  # Adjust the move based on direction
        # logging.info(self._log_str(f"set relative move: {x}"))
        self.set(f"r0xCA {x}")

    def set_profile_velocity(self, data: float):
        x = int(data / self._scale_factor)
        # logging.info(self._log_str(f" Set profile velocity: {x}"))
        self.set(f"r0xCB {x}")

    def set_profile_acceleration(self, data: float):
        x = int(data / self._scale_factor)
        # logging.info(self._log_str(f" Set profile acceleration: {x}"))
        try:
            self.set(f"r0xCC {x}")
        except CopMotorError as e:
            logging.error(f" Failed to set profile acceleration: {e}")
            raise

    def set_profile_deceleration(self, data: float):
        x = int(data / self._scale_factor)
        # logging.info(self._log_str(f" Set profile deceleration: {x}"))
        try:
            self.set(f"r0xCD {x}")
        except CopMotorError as e:
            logging.error(f" Failed to set profile deceleration: {e}")
            raise

    def get_motor_position(self) -> Optional[float]:
        try:
            response = self.get('r0x32')
            if response is not None:
                data = float(response) * self._scale_factor
                logging.info(self._log_str(f" Motor position: {data: .5f}"))
                return data
            else:
                logging.error(" Failed to get motor position.")
                return None
        except Exception as e:
            logging.error(f" Error getting motor position: {e}")
            return None

    def get_load_position(self) -> Optional[float]:
        try:
            response = self.get('r0x17')
            if response is not None:
                data = float(response) * self._scale_factor
                logging.info(self._log_str(f" Load position: {data}"))
                return data
            else:
                logging.error(" Failed to get load position.")
                return None
        except Exception as e:
            logging.error(f" Error getting load position: {e}")
            return None

    def get_following_error(self) -> Optional[float]:
        try:
            response = self.get('r0x35')
            if response is not None:
                data = float(response) * self._scale_factor
                logging.info(self._log_str(f" Following error: {data}"))
                return data
            else:
                logging.error(" Failed to get following error.")
                return None
        except Exception as e:
            logging.error(f" Error getting following error: {e}")
            return None

    def get_event_register(self) -> Optional[int]:
        try:
            response = self.get('r0xA0')
            if response is not None:
                data = int(response)
                logging.info(self._log_str(f" Event register: {data}"))
                return data
            else:
                logging.error(" Failed to get event register.")
                return None
        except Exception as e:
            logging.error(f" Error getting event register: {e}")
            return None

    def get_trajectory_status(self) -> Optional[int]:
        try:
            response = self.get('r0xC9')
            if response is not None:
                data = int(response)
                logging.info(self._log_str(f" Trajectory status register: {data}"))
                return data
            else:
                logging.error(" Failed to get trajectory status register.")
                return None
        except Exception as e:
            logging.error(f" Error getting trajectory status register: {e}")
            return None

    def enable_drive(self) -> None:
        logging.info(self._log_str(" Enable drive"))
        try:
            self.set("r0x24 21")
            logging.info(" Motor enabled successfully.")
        except CopMotorError as e:
            logging.error(f" Failed to enable drive: {e}")
            raise  # Raise the exception to propagate the error

    def disable_drive(self) -> None:
        logging.info(self._log_str(" Disabling drive."))
        try:
            self.set("r0x24 0")
            time.sleep(1)
        except CopMotorError as e:
            logging.error(f" Failed to disable drive: {e}")
            raise  # Raise the exception to propagate the error

def valid_input(prompt, min, max):
    while True:
        try:
            unit_value = float(input(prompt))
            if min <= unit_value <= max:
                return unit_value
            else:
                print(f" Invalid Input ERROR: Enter a value between {min} and {max: .3f}: ")
        except ValueError:
            print(f" Invalid Input ERROR: Please Enter a numerical value between {min} and {max: .3f}: ")

def safe_abort(dev):
    try:
        dev.disable_drive()
        logging.info(" Drive disabled safely.")
    except Exception as e:
        logging.error(f" Error occurred while disabling drive: {e}")
    finally:
        logging.info(" Exiting program due to interrupt.")
        exit()

def validate_args(args):
    try:
        # Validate each argument against its valid range
        assert 0 <= args.VELOCITY <= MAX_VELOCITY_MpS, f"ERROR: VELOCITY must be between 0 and {MAX_VELOCITY_UNITS_SCALED} Units (0 - {MAX_VELOCITY_MpS * CAP_FACTOR: .3f} m/s"
        assert 0 <= args.ACCELERATION <= MAX_ACCELERATION_MpS2, f"ERROR: ACCELERATION must be between 0 and {SET_ACCELERATION_UNITS_FIXED} Units (0 - {SET_ACCELERATION_UNITS_MpS2} m/s^2"
        assert 0 <= args.DECELERATION <= MAX_DECELERATION_MpS2, f"ERROR: DECELERATION must be between 0 and {SET_DECELERATION_UNITS_FIXED} Units (0 - {SET_DECELERATION_UNITS_MpS2} m/s^2"
        assert 0 <= args.DESIRED_TIME <= MAX_DESIRED_TIME_S, f"ERROR: DESIRED_TIME must be between 0 and {MAX_DESIRED_TIME_S} seconds"
        assert 0 <= args.DELTA <= MAX_DELTA_UNITS, f"ERROR: DELTA must be between 0 and {MAX_DELTA_UNITS} Units"
    except AssertionError as e:
        print(f"Error: {e}")
        sys.exit(1)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Motor Control')

    # Positional arguments
    parser.add_argument('VELOCITY', type=float, nargs='?', help=f'Motor VELOCITY (0 - {MAX_VELOCITY_UNITS_SCALED} Units (0 - {MAX_VELOCITY_MpS * CAP_FACTOR: .3f} m/s)')
    parser.add_argument('ACCELERATION', type=float, nargs='?', help=f'Motor ACCELERATION (0 - {SET_ACCELERATION_UNITS_FIXED} Units (0 - {SET_ACCELERATION_UNITS_MpS2} m/s^2)')
    parser.add_argument('DECELERATION', type=float, nargs='?', help=f'Motor DECELERATION (0 - {SET_DECELERATION_UNITS_FIXED} Units (0 - {SET_DECELERATION_UNITS_MpS2} m/s^2)')
    parser.add_argument('DESIRED_TIME', type=float, nargs='?', help=f'Motor RUN TIME (0 - {MAX_DESIRED_TIME_S} s)')
    parser.add_argument('DELTA', type=float, nargs='?', help=f'Motor LOWER BOUND (+0 - +{MAX_DELTA_UNITS} Units)')

    # Optional arguments with flags
    parser.add_argument('-v', '--velocity', type=float, help=f'Motor VELOCITY (0 - {MAX_VELOCITY_UNITS_SCALED} Units (0 - {MAX_VELOCITY_MpS * CAP_FACTOR: .3f} m/s)')
    parser.add_argument('-a', '--acceleration', type=float, help=f'Motor ACCELERATION (0 - {SET_ACCELERATION_UNITS_FIXED} Units (0 - {SET_ACCELERATION_UNITS_MpS2} m/s^2)')
    parser.add_argument('-d', '--deceleration', type=float, help=f'Motor DECELERATION (0 - {SET_DECELERATION_UNITS_FIXED} Units (0 - {SET_DECELERATION_UNITS_MpS2} m/s^2)')
    parser.add_argument('-t', '--desired-time', type=float, help=f'Motor RUN TIME (0 - {MAX_DESIRED_TIME_S} s)')
    parser.add_argument('-dist', '--delta', type=float, help=f'Motor LOWER BOUND (+0 - +{MAX_DELTA_UNITS} Units)')

    args = parser.parse_args()

    # Use values from flags if provided; otherwise, fallback to positional arguments
    velocity = args.velocity if args.velocity is not None else args.VELOCITY
    acceleration = args.acceleration if args.acceleration is not None else args.ACCELERATION
    deceleration = args.deceleration if args.deceleration is not None else args.DECELERATION
    desired_time = args.desired_time if args.desired_time is not None else args.DESIRED_TIME
    delta = args.delta if args.delta is not None else args.DELTA

    return velocity, acceleration, deceleration, desired_time, delta

def validate_args(velocity, acceleration, deceleration, desired_time, delta):
    try:
        assert 0 <= velocity <= MAX_VELOCITY_UNITS_SCALED, f"ERROR: VELOCITY must be between 0 and {MAX_VELOCITY_UNITS_SCALED} Units (0 - {MAX_VELOCITY_MpS * CAP_FACTOR: .3f}) m/s"
        assert 0 <= acceleration <= SET_ACCELERATION_UNITS_FIXED, f"ERROR: ACCELERATION must be between 0 and {SET_ACCELERATION_UNITS_FIXED} Units (0 - {SET_ACCELERATION_UNITS_MpS2}) m/s^2"
        assert 0 <= deceleration <= SET_DECELERATION_UNITS_FIXED, f"ERROR: DECELERATION must be between 0 and {SET_DECELERATION_UNITS_FIXED} Units (0 - {SET_DECELERATION_UNITS_MpS2}) m/s^2"
        assert 0 <= desired_time <= MAX_DESIRED_TIME_S, f"ERROR: DESIRED_TIME must be between 0 and {MAX_DESIRED_TIME_S} seconds"
        assert 0 <= delta <= MAX_DELTA_UNITS, f"ERROR: DIST must be between 0 and {MAX_DELTA_UNITS} Units"
    except AssertionError as e:
        logging.error(f"Validation error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Model STA1112 Limitations
    MAX_VELOCITY_MpS = 5.4
    MAX_ACCELERATION_MpS2 = 378
    MAX_DECELERATION_MpS2 = 378
    MAX_DESIRED_TIME_S = 100000
    MAX_DELTA_UNITS = 300
    SCALE_FACTOR = .00625
    CAP_FACTOR = .05088
    TIME_FACTOR = 12.5

    MAX_VELOCITY_UNITS_SCALED = MAX_VELOCITY_MpS / SCALE_FACTOR
    SET_ACCELERATION_UNITS_FIXED = 100
    SET_DECELERATION_UNITS_FIXED = 100
    SET_ACCELERATION_UNITS_MpS2 = SET_ACCELERATION_UNITS_FIXED * SCALE_FACTOR
    SET_DECELERATION_UNITS_MpS2 = SET_DECELERATION_UNITS_FIXED * SCALE_FACTOR
    

    try:
        velocity, acceleration, deceleration, desired_time, delta = parse_arguments()

        # If any required argument is missing, prompt user for input
        if None in (velocity, acceleration, deceleration, desired_time, delta):
            velocity = valid_input(f" Motor VELOCITY (0 - {MAX_VELOCITY_UNITS_SCALED} Units (0 - {MAX_VELOCITY_MpS * CAP_FACTOR: .3f} m/s)): ", 0, MAX_VELOCITY_UNITS_SCALED)
            acceleration = valid_input(f" Motor ACCELERATION (0 - {SET_ACCELERATION_UNITS_FIXED} Units (0 - {SET_ACCELERATION_UNITS_MpS2} m/s^2): ", 0, SET_ACCELERATION_UNITS_FIXED)
            deceleration = valid_input(f" Motor DECELERATION (0 - {SET_DECELERATION_UNITS_FIXED} Units (0 - {SET_DECELERATION_UNITS_MpS2} m/s^2): ", 0, SET_DECELERATION_UNITS_FIXED)
            desired_time = valid_input(f" Motor RUN TIME (0 - {MAX_DESIRED_TIME_S} s): ", 0, MAX_DESIRED_TIME_S)
            delta = valid_input(f" Motor LOWER BOUND (+0 - +{MAX_DELTA_UNITS} Units): +", 0, MAX_DELTA_UNITS)

        # Validate input arguments
        validate_args(velocity, acceleration, deceleration, desired_time, delta)

        # Initialize CopMotor object
        dev = CopMotor(PORT)

        # Perform motor control operations
        given_velocity = velocity * SCALE_FACTOR * CAP_FACTOR
        given_acceleration = acceleration * SCALE_FACTOR
        given_deceleration = deceleration * SCALE_FACTOR
        given_seconds_units = int(desired_time * TIME_FACTOR)
        print(f" VELOCITY set to: {given_velocity:.3f} m/s ({velocity:.3f} Units)")
        print(f" ACCELERATION set to: {given_acceleration:.3f} m/s2 ({acceleration:.3f} Units)")
        print(f" DECELERATION set to: {given_deceleration:.3f} m/s2 ({deceleration:.3f} Units)")
        print(f" TIME set to: {desired_time:.3f} seconds ({given_seconds_units} Units)")
        print(f" DELTA set to: {delta:.3f} Units")
        dev.get_motor_position()
        dev.get_load_position()
        dev.get_following_error()

        

        try:
            dev.set_profile_acceleration(acceleration)
            dev.set_profile_deceleration(deceleration)
            dev.set_profile_velocity(velocity)
            dev.set_mode_relative_move()
            dev.set_mode_programmed_position()

            time.sleep(1)

            dev.enable_drive()
            event_register_before = dev.get_event_register()

            current_direction = 1
            initial_motor_position = dev.get_motor_position()
            specified_lower_bound = initial_motor_position + delta

            start_time = time.time()
            while True:
                dev.set_relative_move(delta, current_direction)
                dev.trajectory()
                motor_position = dev.get_motor_position()
                if current_direction == 1 and motor_position >= specified_lower_bound:
                    current_direction = -1
                elif current_direction == -1 and motor_position <= initial_motor_position:
                    current_direction = 1
                if time.time() - start_time >= desired_time:
                    break

            elapsed_time = time.time() - start_time
            logging.info(f" Elapsed time: {elapsed_time:.2f} seconds")

        except KeyboardInterrupt:
            logging.info(" Interrupt detected. Attempting to disable drive...")
            try:
                dev.disable_drive()
                logging.info(" Drive disabled successfully.")
                drive_disabled = True
            except Exception as e:
                logging.error(f" Error occurred while disabling drive: {e}")
        except Exception as e:
            logging.error(f" An error occurred: {e}")
        finally:
            if not drive_disabled:
                try:
                    dev.disable_drive()
                    logging.info(" Drive disabled successfully.")
                except Exception as e:
                    logging.error(f" Error occurred while disabling drive: {e}")


    except Exception as e:
        logging.error(f" An error occurred: {e}")
