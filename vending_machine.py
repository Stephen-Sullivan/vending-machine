"""
Stephen Sullivan 100526624
TPRG 2131
November 16th 2023
This module controls a vending machine's operations through a GUI interface using PySimpleGUI
and a servo motor connected to the Raspberry Pi GPIO for physical item dispensing. It includes
a state machine to manage the vending process, taking input from the GUI and controlling the hardware.
"""

import PySimpleGUI as sg
import RPi.GPIO as GPIO
from time import sleep

# Set up the GPIO pins and PWM for the servo motor
servo_pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)
pwm = GPIO.PWM(servo_pin, 50)  # Initialize PWM with 50Hz frequency for the servo

def set_servo_angle(angle):
    """
    Sets the servo motor to the specified angle.

    param angle: The angle to which the servo motor should turn.
    """
    duty_cycle = angle / 18.0 + 2  # Convert angle to duty cycle
    pwm.ChangeDutyCycle(duty_cycle)  # Apply the duty cycle to the servo
    sleep(0.5)  # Wait for the servo to reach the set angle
    pwm.ChangeDutyCycle(0)  # Reset the duty cycle to prevent jitter

# Check if the hardware-specific gpiozero library is available
hardware_present = False
try:
    from gpiozero import Button
    hardware_present = True
except ImportError:
    print("gpiozero library not found. Ensure you are running this on a Raspberry Pi with gpiozero installed.")

# Set the theme for the GUI
sg.theme('Dark Grey 13')

def calculate_change(total_amount, item_price):
    """
    Calculates the change to be returned to the customer.

    param total_amount: The total amount of money inserted.
    param item_price: The price of the selected item.
    return: The calculated change.
    """
    return total_amount - item_price

# Define the values of coins and prices of items available in the vending machine
coin_values = {'5': 5, '10': 10, '25': 25, '100': 100, '200': 200}
item_prices = {'surprise': 150, 'pop': 50, 'chips': 75, 'choc': 50, 'beer': 200}

class State:
    """
    Represents a base state for the vending machine state machine.
    """
    def __init__(self):
        self.name = "initial"

    def on_entry(self, machine, event):
        """
        Handles the actions to be performed when entering a state.

        param machine: The state machine instance.
        param event: The event that triggered the state transition.
        """
        pass

    def on_exit(self, machine, event):
        """
        Handles the actions to be performed when exiting a state.

        param machine: The state machine instance.
        param event: The event that triggered the state transition.
        """
        pass

class WaitingForMoneyState(State):
    """
    Represents the state of waiting for money to be inserted into the vending machine.
    """
    def on_entry(self, machine, event):
        """
        Adds the value of the inserted coin to the total amount when entering this state.

        param machine: The state machine instance.
        param event: The coin that was inserted.
        """
        if event in coin_values:
            machine.total_amount += coin_values[event]
            window['-TOTAL-'].update(f'Total Amount: {machine.total_amount}')

class ItemSelectedState(State):
    """
    Represents the state when an item has been selected for purchase.
    """
    def on_entry(self, machine, event):
        """
        Processes the item selection, calculates change, and completes the purchase if sufficient funds have been provided.

        param machine: The state machine instance.
        param event: The item that was selected.
        """
        if event in item_prices:
            change = calculate_change(machine.total_amount, item_prices[event])
            if change >= 0:
                window['-CONSOLE-'].update(f"Bought {event}. Your change is: {change}\n", append=True)
                machine.total_amount = 0  # Reset total amount after purchase
                window['-TOTAL-'].update(f'Total Amount: {machine.total_amount}')
            else:
                window['-CONSOLE-'].update(f"Not enough money for {event}. Insert more coins.\n", append=True)

class StateMachine:
    """
    Manages the states of the vending machine, handling transitions and actions associated with each state.
    """
    def __init__(self):
        """
        Initializes the state machine with defined states and sets the initial state to 'initial'.
        """
        self.states = {'initial': State(), 'waiting_for_money': WaitingForMoneyState(), 'item_selected': ItemSelectedState()}
        self.state = self.states['initial']
        self.total_amount = 0

    def update(self, event):
        """
        Updates the state machine based on the incoming event.

        param event: An event that can trigger state transitions such as coin insertion or item selection.
        """
        self.state.on_exit(self, event)
        if event in coin_values:
            self.state = self.states['waiting_for_money']
        elif event in item_prices:
            self.state = self.states['item_selected']
        self.state.on_entry(self, event)

    def return_money(self):
        """
        Returns the inserted money and resets the state to the initial state.
        """
        window['-CONSOLE-'].update(f"Returning {self.total_amount} cents\n", append=True)
        self.total_amount = 0
        window['-TOTAL-'].update(f'Total Amount: {self.total_amount}')
        self.state = self.states['initial']

    def deliver_product(self):
        """
        Simulates the delivery of a product by controlling a servo motor.
        """
        set_servo_angle(90)  # Dispense the product
        sleep(0.5)  # Wait for motion
        set_servo_angle(0)  # Return to the resting position
        sleep(0.5)  # Wait for motion

    # Alternate deliver_product method with error handling
    def deliver_product(self):
        print("Attempting to deliver product...")
        try:
            set_servo_angle(90)  # Dispensing position
            sleep(0.5)
            set_servo_angle(0)  # Return to rest position
            sleep(0.5)
        except Exception as e:
            print(f"An error occurred while controlling the servo: {e}")
        finally:
            print("Product delivery attempted.")

# Define layout for the GUI including coin and item buttons
coin_buttons = [
    [sg.Button('5')],
    [sg.Button('10')],
    [sg.Button('25')],
    [sg.Button('100')],
    [sg.Button('200')],
]

item_buttons = [
    [sg.Button('suprise')],
    [sg.Button('pop')],
    [sg.Button('chips')],
    [sg.Button('choc')],
    [sg.Button('beer')],
]

# Create display elements for total amount and console output
total_amount_display = sg.Text('Total Amount: 0', key='-TOTAL-')
output_console = sg.Multiline('Welcome to the Vending Machine\n', size=(45, 5), key='-CONSOLE-', autoscroll=True, disabled=True)

# Define the overall layout of the GUI
layout = [
    [sg.Text('ENTER COINS', size=(15, 1), justification='center'), sg.Text('SELECT ITEM', size=(15, 1), justification='center')],
    [sg.Column(coin_buttons, element_justification='center', expand_x=True), 
     sg.VSeparator(pad=(0, 0)), 
     sg.Column(item_buttons, element_justification='center', expand_x=True)],
    [sg.Column([[total_amount_display]], element_justification='center', expand_x=True)],
    [sg.Column([[sg.Button('Return')]], element_justification='center', expand_x=True)],
    [output_console]
]

# Initialize the window and state machine
window = sg.Window('Vending Machine', layout, size=(280, 400), resizable=False)
machine = StateMachine()

# Setup for hardware return button if gpio is available
if hardware_present:
    # Configure the 'Return' button on the hardware
    return_button_hardware = Button(5, pull_up=True)

    # Define action for hardware return button press
    def hardware_return_press():
        print("Hardware return button pressed.")
        machine.return_money()

    # Attach the action to the button press event
    return_button_hardware.when_pressed = hardware_return_press

# Event loop to handle GUI interactions
try:
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == 'Return':
            machine.return_money()
        else:
            machine.update(event)
            if machine.state.name == "item_selected" and event in item_prices:
                machine.deliver_product()  
except Exception as e:
    print(f"Caught exception: {e}")
finally:
    # Cleanup GPIO and stop PWM signal on program exit
    pwm.stop()
    GPIO.cleanup()

# Close the window
window.close()
