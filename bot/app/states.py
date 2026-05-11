from aiogram.fsm.state import State, StatesGroup

class MainMenu(StatesGroup):
    main_menu = State()
    profile = State()
    my_offers = State()
    offers_search = State()

class Admin(StatesGroup):
    panel = State()
    stats_overview = State()

    reports = State()
    report_details = State()

class Auth(StatesGroup):
    ask_to_auth = State()

    name = State()
    age = State()
    city = State()
    smoking = State()
    children = State()
    pets = State()
    descr = State()
    media_files = State()

class OfferCreate(StatesGroup):
    type = State()
    city = State()
    district = State()
    smoking = State()
    children = State()
    pets = State()
    title = State()
    price = State()
    description = State()
    media = State()
    finalize = State()

class Offer(StatesGroup):
    active_offer_interact = State()
    inactive_offer_interact = State()
    offer_deact = State()
    offer_del = State()
    view_likes = State()

class SearchOffers(StatesGroup):
    city = State()
    choice = State()
    offer_not_found = State()

    report_reason = State()
