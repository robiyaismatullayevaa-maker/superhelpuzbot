"""
SUPER ASSISTANT - FSM Holatlari (States)
"""
from aiogram.fsm.state import State, StatesGroup

class AIStates(StatesGroup):
    waiting_for_prompt = State()

class WeatherStates(StatesGroup):
    waiting_for_city = State()

class TranslateStates(StatesGroup):
    target_lang = State()
    waiting_for_text = State()

class CalculatorStates(StatesGroup):
    waiting_for_expression = State()
    waiting_for_percent = State()

class ReminderStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_time = State()

class CurrencyStates(StatesGroup):
    waiting_for_amount = State()

class AdminStates(StatesGroup):
    waiting_for_broadcast = State()
