import PySimpleGUI as sg

sg.theme('Dark Grey 13')

# Utility Function Definitions
def calculate_change(total_amount, item_price):
    return total_amount - item_price

# Define coin values and item prices
coin_values = {'5': 5, '10': 10, '25': 25, '100': 100, '200': 200}
item_prices = {'suprise': 150, 'pop': 50, 'chips': 75, 'choc': 50, 'beer': 200}

# Class Definitions
class State:
    def __init__(self):
        self.name = "initial"

    def on_entry(self, machine, event):
        pass

    def on_exit(self, machine, event):
        pass

class WaitingForMoneyState(State):
    def __init__(self):
        super().__init__()
        self.name = "waiting_for_money"

    def on_entry(self, machine, event):
        if event in coin_values:
            machine.total_amount += coin_values[event]
            # Update the GUI element instead of printing
            window['-TOTAL-'].update(f'Total Amount: {machine.total_amount}')

    def on_exit(self, machine, event):
        pass
        
        
class ItemSelectedState(State):
    def __init__(self):
        super().__init__()
        self.name = "item_selected"

    def on_entry(self, machine, event):
        if event in item_prices:
            change = calculate_change(machine.total_amount, item_prices[event])
            if change >= 0:
                print(f"Bought {event}. Your change is: {change}")
                machine.total_amount = 0  # reset total amount after purchase
                # Update the GUI element to show the new total amount
                window['-TOTAL-'].update(f'Total Amount: {machine.total_amount}')
            else:
                print(f"Not enough money for {event}. Insert more coins.")
                
class StateMachine:
    def __init__(self):
        self.states = {'initial': State(), 'waiting_for_money': WaitingForMoneyState(), 'item_selected': ItemSelectedState()}
        self.state = self.states['initial']
        self.total_amount = 0

    def update(self, event):
        self.state.on_exit(self, event)
        if event in coin_values:
            self.state = self.states['waiting_for_money']
        elif event in item_prices:
            self.state = self.states['item_selected']
        self.state.on_entry(self, event)

    def return_money(self):
        print(f"Returning {self.total_amount} cents")
        self.total_amount = 0
        self.state = self.states['initial']
        
    def return_money(self):
        # Update the GUI element instead of printing
        window['-TOTAL-'].update(f'Total Amount: 0')
        self.total_amount = 0
        self.state = self.states['initial']

# Modified layout
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

return_button = [sg.Button('Return')]

total_amount_display = sg.Text('Total Amount: 0', key='-TOTAL-')

layout = [
    [sg.Text('ENTER COINS', size=(15, 1), justification='center'), sg.Text('SELECT ITEM', size=(15, 1), justification='center')],
    [sg.Column(coin_buttons, element_justification='center', expand_x=True), 
     sg.VSeparator(pad=(0, 0)), 
     sg.Column(item_buttons, element_justification='center', expand_x=True)],
    [sg.Column([[total_amount_display]], element_justification='center', expand_x=True)],
    [sg.Column([[sg.Button('Return')]], element_justification='center', expand_x=True)]
]

window = sg.Window('Vending Machine', layout, resizable=True)


machine = StateMachine()

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break
    elif event == 'Return':
        machine.return_money()
    else:
        machine.update(event)

window.close()