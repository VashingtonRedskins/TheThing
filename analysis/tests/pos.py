# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

class pos(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://127.0.0.1:8000/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_login(self):
        driver = self.driver
        driver.get(self.base_url + "/accounts/login/")
        driver.find_element_by_id("inputLogin").clear()
        driver.find_element_by_id("inputLogin").send_keys("admin")
        driver.find_element_by_id("inputPassword").clear()
        driver.find_element_by_id("inputPassword").send_keys("admin")
        driver.find_element_by_xpath("//button[@type='submit']").click()

    def test_add_repos(self):
        driver = self.driver
        driver.get(self.base_url + "/octonyan/add/repo/")
        driver.find_element_by_id("id_repository_url").clear()
        driver.find_element_by_id("id_repository_url").send_keys("https://github.com/olgaItis/Livebook.git")
        driver.find_element_by_css_selector("input[type=\"submit\"]").click()

    def test_login_add_repos(self):
        driver = self.driver
        driver.get(self.base_url + "/accounts/login/")
        driver.find_element_by_id("inputLogin").clear()
        driver.find_element_by_id("inputLogin").send_keys("admin")
        driver.find_element_by_id("inputPassword").clear()
        driver.find_element_by_id("inputPassword").send_keys("admin")
        driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.get(self.base_url + "/octonyan/add/repo/")
        driver.find_element_by_id("id_repository_url").clear()
        driver.find_element_by_id("id_repository_url").send_keys("https://github.com/olgaItis/Livebook.git")
        driver.find_element_by_css_selector("input[type=\"submit\"]").click()

    def test_login_my_repos(self):
        driver = self.driver
        driver.get(self.base_url + "/accounts/login/")
        driver.find_element_by_id("inputLogin").clear()
        driver.find_element_by_id("inputLogin").send_keys("admin")
        driver.find_element_by_id("inputPassword").clear()
        driver.find_element_by_id("inputPassword").send_keys("admin")
        driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.get(self.base_url + "/octonyan/")
        driver.find_element_by_css_selector("div.ripple-wrapper").click()
        driver.get(self.base_url + "/octonyan/repo/TheThing/")
        driver.find_element_by_link_text("Back").click()

    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException, e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
