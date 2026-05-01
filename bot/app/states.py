from aiogram.fsm.state import State, StatesGroup

class Auth(StatesGroup):
    ask_to_auth = State()

    name = State()
    age = State()
    city = State()
    descr = State()
    media_files = State()

class OfferCreate(StatesGroup):
    type = State()
    city = State()
    district = State()
    title = State()
    price = State()
    description = State()
    media = State()

class Offer(StatesGroup):
    offer_interact = State()
    offer_deact = State()