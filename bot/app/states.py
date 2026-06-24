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
    name = State()
    city = State()
    descr = State()
    media_files = State()

class OfferCreate(StatesGroup):
    city = State()
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
