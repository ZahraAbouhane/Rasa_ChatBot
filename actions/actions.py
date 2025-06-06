from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction



class ActionBookFlight(Action):
    def name(self) -> str:
        return "action_book_flight"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Get current slot values
        departure_city = tracker.get_slot("departure_city")
        arrival_city = tracker.get_slot("arrival_city")
        departure_date = tracker.get_slot("departure_date")
        flight_class = tracker.get_slot("flight_class")
        flight_type = tracker.get_slot("flight_type")
        return_date = tracker.get_slot("return_date")

        # Extract entities from current message
        entities = tracker.latest_message.get("entities", [])
        events = []

        # Update slots from entities
        for entity in entities:
            entity_type = entity["entity"]
            entity_value = entity["value"]
            if entity_type in ["departure_city", "arrival_city", "departure_date", "flight_class", "flight_type",
                               "return_date"]:
                events.append(SlotSet(entity_type, entity_value))
                # Update local variables
                if entity_type == "departure_city":
                    departure_city = entity_value
                elif entity_type == "arrival_city":
                    arrival_city = entity_value
                elif entity_type == "departure_date":
                    departure_date = entity_value
                elif entity_type == "flight_class":
                    flight_class = entity_value
                elif entity_type == "flight_type":
                    flight_type = entity_value
                elif entity_type == "return_date":
                    return_date = entity_value

        # Check what's missing and ask for it
        if not departure_city:
            dispatcher.utter_message(response="utter_ask_departure_city")
            return events

        if not arrival_city:
            dispatcher.utter_message(response="utter_ask_arrival_city")
            return events

        if not departure_date:
            dispatcher.utter_message(response="utter_ask_departure_date")
            return events

        if not flight_class:
            dispatcher.utter_message(response="utter_ask_flight_class")
            return events

        if not flight_type:
            dispatcher.utter_message(response="utter_ask_flight_type")
            return events

        # If round trip, ask for return date
        if flight_type == "ذهاب-إياب" and not return_date:
            dispatcher.utter_message(response="utter_ask_return_date")
            return events

        # All required info collected, search for flights
        events.append(SlotSet("search_type", "flight"))
        events.append(FollowupAction("action_search_flights"))

        return events


class ActionBookHotel(Action):
    def name(self):
        return "action_book_hotel"

    def run(self, dispatcher, tracker, domain):
        # Get current slot values
        hotel_city = tracker.get_slot("hotel_city")
        neighborhood = tracker.get_slot("neighborhood")
        hotel_category = tracker.get_slot("hotel_category")
        num_people = tracker.get_slot("num_people")

        # Extract entities from current message
        entities = tracker.latest_message.get("entities", [])
        events = []

        # Update slots from entities
        for entity in entities:
            entity_type = entity["entity"]
            entity_value = entity["value"]
            if entity_type in ["hotel_city", "neighborhood", "hotel_category", "num_people"]:
                events.append(SlotSet(entity_type, entity_value))
                # Update local variables
                if entity_type == "hotel_city":
                    hotel_city = entity_value
                elif entity_type == "neighborhood":
                    neighborhood = entity_value
                elif entity_type == "hotel_category":
                    hotel_category = entity_value
                elif entity_type == "num_people":
                    num_people = entity_value

        # Check what's missing and ask for it
        if not hotel_city:
            dispatcher.utter_message(response="utter_ask_hotel_city")
            return events

        if not neighborhood:
            dispatcher.utter_message(response="utter_ask_neighborhood")
            return events

        if not hotel_category:
            dispatcher.utter_message(response="utter_ask_hotel_category")
            return events

        if not num_people:
            dispatcher.utter_message(response="utter_ask_num_people")
            return events

        # All required info collected, search for hotels
        events.append(SlotSet("search_type", "hotel"))
        events.append(FollowupAction("action_search_hotels"))

        return events


class ActionSearchFlights(Action):
    def name(self):
        return "action_search_flights"

    def run(self, dispatcher, tracker, domain):
        departure_city = tracker.get_slot("departure_city")
        arrival_city = tracker.get_slot("arrival_city")
        departure_date = tracker.get_slot("departure_date")
        flight_class = tracker.get_slot("flight_class")
        flight_type = tracker.get_slot("flight_type")
        return_date = tracker.get_slot("return_date")

        # Create flight options based on the search
        flight_info = f"من {departure_city} إلى {arrival_city} نهار {departure_date}"
        if flight_type == "ذهاب-إياب" and return_date:
            flight_info += f" والرجوع {return_date}"

        dispatcher.utter_message(
            text=f"لقيت ليك رحلات {flight_info} ف درجة {flight_class}:\n\n"
                 f"1️⃣ الخطوط الملكية المغربية - الإقلاع 8:00 صباح - 2500 درهم\n"
                 f"2️⃣ طيران العربية - الإقلاع 14:00 بعد الظهر - 1800 درهم\n"
                 f"3️⃣ أطلس بلو - الإقلاع 18:00 مساء - 2200 درهم\n\n"
                 f"أي رحلة بغيتي تختار؟ قول 'أكد' باش نأكد ليك الحجز الأول."
        )
        return []


class ActionSearchHotels(Action):
    def name(self):
        return "action_search_hotels"

    def run(self, dispatcher, tracker, domain):
        hotel_city = tracker.get_slot("hotel_city")
        neighborhood = tracker.get_slot("neighborhood")
        hotel_category = tracker.get_slot("hotel_category")
        num_people = tracker.get_slot("num_people")

        dispatcher.utter_message(
            text=f"لقيت ليك أوتيلات ف{hotel_city} - {neighborhood} - {hotel_category} ل{num_people}:\n\n"
                 f"1️⃣ فندق الأطلس - 800 درهم/ليلة\n"
                 f"2️⃣ نوفوتيل - 1200 درهم/ليلة\n"
                 f"3️⃣ ريكسوس - 1800 درهم/ليلة\n\n"
                 f"أي أوتيل بغيتي تختار؟ قول 'أكد' باش نأكد ليك الحجز الأول."
        )
        return []


class ActionConfirmFlightReservation(Action):
    def name(self):
        return "action_confirm_flight_reservation"

    def run(self, dispatcher, tracker, domain):
        departure_city = tracker.get_slot("departure_city")
        arrival_city = tracker.get_slot("arrival_city")
        departure_date = tracker.get_slot("departure_date")
        return_date = tracker.get_slot("return_date")
        flight_class = tracker.get_slot("flight_class")
        flight_type = tracker.get_slot("flight_type")

        # Get selected flight option (you might want to add a slot for this)
        selected_flight = tracker.get_slot("selected_flight") or "1"

        # Flight details based on selection (you can make this dynamic)
        flight_details = {
            "1": {"airline": "الخطوط الملكية المغربية", "price": "2500", "time": "8:00 صباح"},
            "2": {"airline": "طيران العربية", "price": "1800", "time": "14:00 بعد الظهر"},
            "3": {"airline": "أطلس بلو", "price": "2200", "time": "18:00 مساء"}
        }

        selected_details = flight_details.get(selected_flight, flight_details["1"])

        confirmation_text = f"🎉 تأكد الحجز ديال الطيارة!\n\n"
        confirmation_text += f"✈️ من: {departure_city}\n"
        confirmation_text += f"✈️ إلى: {arrival_city}\n"
        confirmation_text += f"📅 تاريخ السفر: {departure_date}\n"

        if flight_type == "round_trip" and return_date:
            confirmation_text += f"📅 تاريخ الرجوع: {return_date}\n"

        confirmation_text += f"🎫 الدرجة: {flight_class}\n"
        confirmation_text += f"✈️ الطيران: {selected_details['airline']}\n"
        confirmation_text += f"🕐 وقت الإقلاع: {selected_details['time']}\n"
        confirmation_text += f"💰 السعر: {selected_details['price']} درهم\n"
        confirmation_text += f"🎫 رقم الحجز: FL2024{selected_flight}01\n\n"
        confirmation_text += f"تبارك الله عليك! رحلة سعيدة! 🌟"

        dispatcher.utter_message(text=confirmation_text)

        # Clear flight-related slots
        return [
            SlotSet("departure_city", None),
            SlotSet("arrival_city", None),
            SlotSet("departure_date", None),
            SlotSet("flight_class", None),
            SlotSet("flight_type", None),
            SlotSet("return_date", None),
            SlotSet("selected_flight", None)
        ]


class ActionConfirmHotelReservation(Action):
    def name(self):
        return "action_confirm_hotel_reservation"

    def run(self, dispatcher, tracker, domain):
        hotel_city = tracker.get_slot("hotel_city")
        neighborhood = tracker.get_slot("neighborhood")
        hotel_category = tracker.get_slot("hotel_category")

        dispatcher.utter_message(
            text=f"🎉 تأكد الحجز ديال الأوتيل!\n\n"
                 f"🏨 المدينة: {hotel_city}\n"
                 f"📍 الحي: {neighborhood}\n"
                 f"⭐ الفئة: {hotel_category}\n"
                 f"💰 السعر: 800 درهم/ليلة\n"
                 f"🎫 رقم الحجز: HT2024001\n\n"
                 f"تبارك الله عليك! إقامة سعيدة! 🌟"
        )

        # Clear hotel-related slots
        return [
            SlotSet("hotel_city", None),
            SlotSet("neighborhood", None),
            SlotSet("hotel_category", None),
            SlotSet("num_people", None)
        ]