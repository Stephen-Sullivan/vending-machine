import PySimpleGUI as sg


# Define the coin buttons layout
coin_buttons = [
    [sg.Button('5')],
    [sg.Button('10')],
    [sg.Button('25')],
    [sg.Button('100')],
    [sg.Button('200')],
]

# Define the item buttons layout
item_buttons = [
    [sg.Button('suprise')],
    [sg.Button('pop')],
    [sg.Button('chips')],
    [sg.Button('choc')],
    [sg.Button('beer')],
]

# Main Program layout
layout = [
    [sg.Text('ENTER COINS', size=(15, 1), justification='center'), sg.VSeparator(), sg.Text('SELECT ITEM', size=(15, 1), justification='center')],
    [sg.Column(coin_buttons, element_justification='left', expand_x=True), 
     sg.VSeparator(), 
     sg.Column(item_buttons, element_justification='left', expand_x=True)]
]

window = sg.Window('Vending Machine', layout, resizable=True, size=(322,200))


while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        print("Shutting down...")
        break
    else:
        machine.update(event)

window.close()
