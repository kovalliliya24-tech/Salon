from aiogram.fsm.state import StatesGroup, State

class Registration(StatesGroup):
    name = State()
    phone = State()

class Booking(StatesGroup):
    service = State()
    master = State()
    date = State()
    time = State()
    confirm = State()

class Admin(StatesGroup):
    add = State()
    delete = State()

class AdminAction(StatesGroup):
    waiting_for_delete_id = State()
    waiting_for_add_booking = State()

class AdminBooking(StatesGroup):
    service = State()
    master = State()
    date = State()
    time = State()
    client_name = State()
    client_phone = State()

class Review(StatesGroup):
    text = State()