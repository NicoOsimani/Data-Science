# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import math
import datetime

class ActionBooking(Action):

    def name(self) -> Text:
        return "action_booking"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        num_rooms = tracker.get_slot("num_rooms")
        room_type = tracker.get_slot("room_type")

        dispatcher.utter_message(text=f'You have chosen to book {num_rooms} {room_type} rooms.')

        return [SlotSet("num_rooms"), SlotSet("room_type"), SlotSet("num_rooms_res", num_rooms), SlotSet("room_type_res", room_type)]

class ActionSetNumRooms(Action):

    def name(self) -> Text:
        return "action_set_num_rooms"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        num_persons = tracker.get_slot("num_people")
        people_per_room = tracker.get_slot("people_per_room")

        # If unable to extract num persons set num rooms to 1, else calc num rooms
        if num_persons is None:
            num_rooms = "1"
        else:
            num_rooms = str(math.ceil(int(num_persons)/int(people_per_room)))
        
        return [SlotSet("num_people"), SlotSet("people_per_room"), SlotSet("num_rooms", num_rooms)] 

class ActionSeeReservations(Action):

    def name(self) -> Text:
        return "action_see_reservations"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        num_rooms_res = tracker.get_slot("num_rooms_res")
        room_type_res = tracker.get_slot("room_type_res")

        if ((num_rooms_res is None) or (room_type_res is None)):
            dispatcher.utter_message(response='utter_no_reservations')
        else:
            dispatcher.utter_message(text=f'You have booked {num_rooms_res} {room_type_res} rooms.') 

        return []

class ActionSeeCleaningSchedule(Action):

    def name(self) -> Text:
        return "action_see_cleaning_schedule"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        h = tracker.get_slot("hour")
        m = tracker.get_slot("minute")
        suff = tracker.get_slot("suff")

        if ((h is None) or (m is None) or (suff is None)):
            dispatcher.utter_message(response='utter_no_cleaning_scheduled')
        else:
            dispatcher.utter_message(text=f'We have scheduled a cleaning for {h}:{m} {suff}.') 

        return []

class ActionScheduleCleaning(Action):

    def name(self) -> Text:
        return "action_schedule_cleaning"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dur = tracker.get_slot("duration")
        unit = tracker.get_slot("time_unit")

        if dur is None:
            dispatcher.utter_message(text='Sure, i will send someone to your room right away.')
            return [SlotSet("time_unit"), SlotSet("hour"), SlotSet("minute"), SlotSet("suff")]

        if unit is None:
            dispatcher.utter_message(text='Sure, sending a cleaner to your room.')
            return [SlotSet("duration"), SlotSet("hour"), SlotSet("minute"), SlotSet("suff")]


        time_tuple = datetime.datetime.now().timetuple()
        h = time_tuple[3]
        m = time_tuple[4]

        if unit == "min":
            m += int(dur)
            if m > 60:
                h += int(m/60)
                m = m % 60

        elif unit == "hour":
            h += int(dur)

        h = h % 24
        if h > 12:
            h = h - 12
            suff = 'PM'
        else:
            suff = 'AM'
        m = "%02d" % m
        dispatcher.utter_message(text=f'Sure, i have scheduled a cleaning for {h}:{m} {suff}.') 

        return [SlotSet("duration"), SlotSet("time_unit"), SlotSet("hour", h), SlotSet("minute", m), SlotSet("suff", suff)]
