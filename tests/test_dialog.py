import pytest

import json

from django.core.management import call_command

from common.entities import EventCommandReceived, EventCommandToSend, Callback
from bot.dialog import Dialog


with open('tests/dialog_content.json', 'r') as f:
    string = f.readline()
    lines = json.loads(string)


greet_cases = (
    (
        EventCommandReceived.Schema().loads(lines['greet_input']),
        EventCommandToSend.Schema().loads(lines['greet_answer']),
    ),
)

category_cases = (
    (
        EventCommandReceived.Schema().loads(lines['category_input']),
        EventCommandToSend.Schema().loads(lines['category_answer']),
    ),
)

product_cases = (
    (
        EventCommandReceived.Schema().loads(lines['product_input']),
        EventCommandToSend.Schema().loads(lines['product_answer']),
    ),
)

desc_cases = (
    (
        EventCommandReceived.Schema().loads(lines['desc_input']),
        EventCommandToSend.Schema().loads(lines['desc_answer']),
    ),
)

confirm_cases = (
    (
        EventCommandReceived.Schema().loads(lines['confirm_input']),
        EventCommandToSend.Schema().loads(lines['confirm_answer']),
    ),
)

order_cases = (
    (
        EventCommandReceived.Schema().loads(lines['order_input']),
        EventCommandToSend.Schema().loads(lines['order_answer']),
    ),
)


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker) -> None:  # type: ignore
    with django_db_blocker.unblock():
        call_command('loaddata', 'tests/test_data.json')


def load(data: str) -> Callback:
    return Callback.Schema().loads(data)


@pytest.mark.parametrize(['input_', 'expected'], greet_cases)
def test_form_greeting(input_: EventCommandReceived, expected: EventCommandToSend) -> None:

    result = Dialog()._form_greeting(input_)
    assert result == expected
    assert len(result.inline_buttons) == len(expected.inline_buttons)
    for i in range(len(result.inline_buttons)):
        assert load(result.inline_buttons[i].action.payload) == load(expected.inline_buttons[i].action.payload)


@pytest.mark.django_db
@pytest.mark.parametrize(['input_', 'expected'], category_cases)
def test_form_category_list(input_: EventCommandReceived, expected: EventCommandToSend) -> None:

    result = Dialog().form_category_list(input_)
    assert result == expected
    assert len(result.inline_buttons) == len(expected.inline_buttons)
    for i in range(len(result.inline_buttons)):
        assert load(result.inline_buttons[i].action.payload) == load(expected.inline_buttons[i].action.payload)


@pytest.mark.django_db
@pytest.mark.parametrize(['input_', 'expected'], product_cases)
def test_form_product_list(input_: EventCommandReceived, expected: EventCommandToSend) -> None:

    dialog = Dialog()
    dialog.callback = Callback.Schema().loads(input_.payload.command)
    result = dialog.form_product_list(input_)
    assert result == expected
    assert len(result.inline_buttons) == len(expected.inline_buttons)
    for i in range(len(result.inline_buttons)):
        assert load(result.inline_buttons[i].action.payload) == load(expected.inline_buttons[i].action.payload)


@pytest.mark.django_db
@pytest.mark.parametrize(['input_', 'expected'], desc_cases)
def test_form_product_desc(input_: EventCommandReceived, expected: EventCommandToSend) -> None:

    dialog = Dialog()
    dialog.callback = Callback.Schema().loads(input_.payload.command)
    result = dialog.form_product_desc(input_)
    assert result == expected
    assert len(result.inline_buttons) == len(expected.inline_buttons)
    for i in range(len(result.inline_buttons)):
        assert load(result.inline_buttons[i].action.payload) == load(expected.inline_buttons[i].action.payload)


@pytest.mark.django_db
@pytest.mark.parametrize(['input_', 'expected'], confirm_cases)
def test_form_order_confirmation(input_: EventCommandReceived, expected: EventCommandToSend) -> None:

    dialog = Dialog()
    dialog.callback = Callback.Schema().loads(input_.payload.command)
    result = dialog.form_order_confirmation(input_)
    assert result == expected
    assert len(result.inline_buttons) == len(expected.inline_buttons)
    for i in range(len(result.inline_buttons)):
        assert load(result.inline_buttons[i].action.payload) == load(expected.inline_buttons[i].action.payload)


# @pytest.mark.django_db
# @pytest.mark.parametrize(['input_', 'expected'], order_cases)
# def test_make_order(input_: EventCommandReceived, expected: EventCommandToSend):
#
#     dialog = Dialog()
#     dialog.callback = Callback.Schema().loads(input_.payload.command)
#     result = dialog.make_order(input_)
#     assert result.payload.text.find(
#         'https://b98b84b2aa73.ngrok.io/billing/stripe_redirect/cs_test_') >= 0
