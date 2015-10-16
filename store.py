"""Assignment 1 - Grocery Store Models (Task 1)

This file should contain all of the classes necessary to model the entities
in a grocery store.
"""
# This module is used to read in the data from a json configuration file.
import json
from event import Checkout_Begins, Checkout_Finish, Line_Close, New_Customer

class GroceryStore:
    """A grocery store.

    A grocery store should contain customers and checkout lines.

    TODO: make sure you update the documentation for this class to include
    a list of all public and private attributes, in the style found in
    the Class Design Recipe.
    """
    def __init__(self, filename):
        """Initialize a GroceryStore from a configuration file <filename>.

        @type filename: str
            The name of the file containing the configuration for the
            grocery store.
        @type checkout_line: list[Event]
            a list of all events that will take place in the store
        @type time: int
            keeps track of timestamps and where they are (choronologically)
        @rtype: None
        """

        with open(filename, 'r') as file:
            self.config = json.load(file)

        # <config> is now a dictionary with the keys 'cashier_count',
        # 'express_count', 'self_serve_count', and 'line_capacity'.
        self.time = 0
        self.checkout_line = []

        num_of_Checkoutlines = int(self.config['cashier_count']) + int(self.config['express_count']) + int(self.config['self_serve_count'])

        # sets up checkline
        for index in range(0, num_of_Checkoutlines):
            self.checkout_line.append([])

    def new_customer(self, imported_event):
        """handles new cutomer events

        customer always joins line with most open space.
        also the line with least index
        @type index: int
            indicates which line new customer will join
        @type length: int
        @type imported_event: Event
        @type new_eve: Event
        @rtype: list
        """

        # DEBUGGED, REFER TO MAIN BELOW

        line = -1
        length = self.config['line_capacity']
        # checks every line and sees which line has shortest line

        for i in range(len(self.checkout_line)):

            # if empty space in line is greater than current emptiest line proceed
            # also if item greated than 8 and express line is ready to be checkeds, skip all express lines

            if imported_event.item_carried >= 8 and (i > self.config['cashier_count'] - 1 and i < self.config['cashier_count'] + self.config['express_count']):
                pass
            else:
                #print('length of checkout line ' + str(i) + ' is ' + str(len(self.checkout_line[i])))
                #print('current length: ' + str(length))
                if len(self.checkout_line[i]) < self.config['line_capacity'] and len(self.checkout_line[i]) < length:
                    line = i
                    length = len(self.checkout_line[i])


        # for loop ends
        # create a check out begin event and add it to end of check out line
        new_event = Checkout_Begins(imported_event.timestamp)
        new_event.distribute_info(imported_event.name, imported_event.item_carried, 0, line)
        self.checkout_line[line].append(new_event)
        return new_event

    def checkout_begins(self, imported_event):
        """Handles events from the Checkout_Begins subclass objects

        calculations will be preformed here to see how long will it
        take for the customer to checkout items.
        then using that time a new Checkout_Finish event will be
        created and returned.
        @type imported_event: Event
        @type timestamp: int
        @rtype: list
        """

        # cashier checkout line is number of item + 7 seconds
        if imported_event.line < self.config['cashier_count']:
            timestamp = imported_event.item_carried + 7
        # express line is number of item + 4 seconds
        elif imported_event.line < self.config['express_count']:
            timestamp = imported_event.item_carried + 4
        else: #self serve line is 2n + 1
            timestamp = 2*imported_event.item_carried + 1

        # create a new checkout_finish event and return it
        # the timestamp given to checout_finishes is for keeping track of the max waittime
        new_event = Checkout_Finish(timestamp + imported_event.timestamp)
        new_event.distribute_info(imported_event.name, imported_event.item_carried, timestamp, imported_event.line)

        # replace the old event at the front of the line with the new one
        # since the old one must be checkout_begins
        # as it begins and changes into checkout_finish, it must remain there, at the front
        # for however long the timestamp indicates

        self.checkout_line[imported_event.line].append(new_event)
        return new_event

    def checkout_finish(self, imported_event):
        """handles events from the Checkout_Finish subclass

        when a checkout_finish event is reached in terms of the timestamp
        it will be passed here, where the wait time for that specific event
        will be returned and the event should be removed in sim

        @type imported_event: Checkout_Finish
        @rtype: list
        """
        # removes the customer in that line so length can be
        # properly calculated in new customer

        self.checkout_line[imported_event.line].pop(0)
        return imported_event.time_waited

    def line_close(self, imported_event):
        """handles events from the Line_close subclass

        when line_close event is passed here, customers remaining in the line
        will be reversly re-organized into a new list of new_customer events
        with intervals of one second
        the line it self will be filled with 0s, indicating that it has closed.
        then the list of new_customer events will be returned.

        @type imported_event: Event (it is a line_close event)
        @type line_length: int
        @type temp_line: list[Event]
            this list is where all the customer events in the line
            will be store and returned
        @rtype: list[Event]
        """

        temp_event_list = []
        line_length =  len(self.checkout_line[imported_event.line_index])

        # take the element in line of index: line_index, and put them in list
        # this is a stack thingy ish thing
        # this for loop is used to put item into a new list in reverse order
        for index in range(line_length):
            temp_event_list.append(self.checkout_line[imported_event.line_index][line_length - index - 1])

        """ ====== TODO, NEED TO CHANGE THE EVENT TO NEW CUSTOMER EVENTS WITH 1 SEC INTERVALS!!!!!!!! ====== """

        """ =============================================================
        To keep track of time waited and keep on recording when line closes
        for checkout_begin:
            it has its initial timestamp and time that it is supposed to wait
        for checkout_finish:
            it has a time-waited attribute that is the time that the event should trigger
            so just take the checkout_finish timestamp + time to wait - timestamp of line_close
            that would be the time waited currently when the line is closed for that one event
            ==============================================================
        """

        # clearing the line and fill it with 0 to indicate it is closed
        self.checkout_line[imported_event.line_index].clear()
        for index in range(self.config['line_capacity']):
            self.checkout_line[imported_event.line_index].append(0)

        return temp_event_list


# You can run a basic test here using the default 'config.json'
# file we provided.
if __name__ == '__main__':
    store = GroceryStore('config.json')
    # Execute some methods here

    #checkout_begins debug
    event1 = New_Customer(2)
    event1.distribute_info('Powell', 1, 0, 0)
    event1 = store.new_customer(event1)
    returned_event = store.checkout_begins(event1)
    print('line ' + str(returned_event.line + 1) + ' wait time is ' + str(returned_event.time_waited))

    event2 = New_Customer(5)
    event2.distribute_info('Jason', 7, 0, 0)
    event2 = store.new_customer(event2)
    returned_event = store.checkout_begins(event2)
    print('line ' + str(returned_event.line + 1) + ' wait time is ' + str(returned_event.time_waited))

    event3 = New_Customer(6)
    event3.distribute_info('Jason', 12, 0, 0)
    event3 = store.new_customer(event3)
    returned_event = store.checkout_begins(event3)
    print('line ' + str(returned_event.line + 1) + ' wait time is ' + str(returned_event.time_waited))

    event4 = New_Customer(6)
    event4.distribute_info('Jason', 2, 0, 0)
    event4 = store.new_customer(event4)
    returned_event = store.checkout_begins(event4)
    print('line ' + str(returned_event.line + 1) + ' wait time is ' + str(returned_event.time_waited))


    """new_customer method test cases

    event1 = New_Customer(2)
    event1.distribute_info('Powell', 9, 0, 0)

    return_event = store.new_customer(event1)
    print('event1 begins check out at line ' + str(return_event.line))
    print('')

    event2 = New_Customer(5)
    event2.distribute_info('Jason', 7, 0, 0)

    return_event = store.new_customer(event2)
    print('event2 begins check out at line ' + str(return_event.line))
    print('')

    event3 = New_Customer(6)
    event3.distribute_info('Jason', 9, 0, 0)

    return_event = store.new_customer(event3)
    print('event3 begins check out at line ' + str(return_event.line))
    print('')

    event4 = New_Customer(6)
    event4.distribute_info('Jason', 9, 0, 0)

    return_event = store.new_customer(event4)
    print('event4 begins check out at line ' + str(return_event.line))
    print('')
    """
