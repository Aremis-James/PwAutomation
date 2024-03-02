import pytest
import re
from playwright.sync_api import Page, expect
from faker import Faker


# def test_has_title(page: Page):
#     page.goto("https://playwright.dev/")
#     expect(page).to_have_title(re.compile('Playwright'))
#     pass

# def test_get_started_link(page: Page):
#     page.goto('"https://playwright.dev/"')
#     expect(page.get_by_role('heading', name='Installation')).to_be_visible()
#     pass
