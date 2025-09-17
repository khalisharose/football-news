from django.test import TestCase
from .models import News
from django.test import TestCase, Client
from .models import News
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from django.contrib.auth.models import User

class MainTest(TestCase):
    def test_main_url_is_exist(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

    def test_main_using_main_template(self):
        response = self.client.get('')
        self.assertTemplateUsed(response, 'main.html')

    def test_nonexistent_page(self):
        response = self.client.get('/nonexistent_page/')
        self.assertEqual(response.status_code, 404)

    def test_item_creation(self):
        item = Item.objects.create(
            name="Official Merch T-Shirt",
            price=1500000,
            description="High-quality official merch",
            category="clothing",
            stock=50,
            rating=4.5,
            is_featured=True,
            is_official_merch=True
        )
        self.assertEqual(item.name, "Official Merch T-Shirt")
        self.assertEqual(item.category, "clothing")
        self.assertTrue(item.is_featured)
        self.assertTrue(item.is_official_merch)

    def test_item_default_values(self):
        item = Item.objects.create(
            name="Default Product",
            price=1000000,
            description="Default product description"
        )
        self.assertEqual(item.category, "electronics")
        self.assertEqual(item.stock, 0)
        self.assertEqual(item.rating, 0.0)
        self.assertFalse(item.is_featured)
        self.assertFalse(item.is_official_merch)
        self.assertTrue(item.is_high_demand)

    def test_increment_stock(self):
        item = Item.objects.create(
            name="Test Product",
            price=500000,
            description="Test product"
        )
        initial_stock = item.stock
        item.increment_stock()
        self.assertEqual(item.stock, initial_stock + 1)

    def test_is_high_demand_threshold(self):
        # Test item with stock >= 10 (not high demand)
        item_not_high = Item.objects.create(
            name="Low Demand Product",
            price=700000,
            description="Low demand product",
            stock=15
        )
        self.assertFalse(item_not_high.is_high_demand)

        # Test item with stock < 10 (high demand)
        item_high = Item.objects.create(
            name="High Demand Product",
            price=750000,
            description="High demand product",
            stock=5
        )
        self.assertTrue(item_high.is_high_demand)
        
class FootballNewsFunctionalTest(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create single browser instance for all tests
        cls.browser = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Close browser after all tests complete
        cls.browser.quit()

    def setUp(self):
        # Create user for testing
        self.test_user = User.objects.create_user(
            username='testadmin',
            password='testpassword'
        )

    def tearDown(self):
        # Clean up browser state between tests
        self.browser.delete_all_cookies()
        self.browser.execute_script("window.localStorage.clear();")
        self.browser.execute_script("window.sessionStorage.clear();")
        # Navigate to blank page to reset state
        self.browser.get("about:blank")

    def login_user(self):
        """Helper method to login user"""
        self.browser.get(f"{self.live_server_url}/login/")
        username_input = self.browser.find_element(By.NAME, "username")
        password_input = self.browser.find_element(By.NAME, "password")
        username_input.send_keys("testadmin")
        password_input.send_keys("testpassword")
        password_input.submit()

    def test_login_page(self):
        # Test login functionality
        self.login_user()

        # Check if login is successful
        wait = WebDriverWait(self.browser, 120)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Football News")

        logout_link = self.browser.find_element(By.PARTIAL_LINK_TEXT, "Logout")
        self.assertTrue(logout_link.is_displayed())

    def test_register_page(self):
        # Test register functionality
        self.browser.get(f"{self.live_server_url}/register/")

        # Check if register page opens
        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Register")

        # Fill register form
        username_input = self.browser.find_element(By.NAME, "username")
        password1_input = self.browser.find_element(By.NAME, "password1")
        password2_input = self.browser.find_element(By.NAME, "password2")

        username_input.send_keys("newuser")
        password1_input.send_keys("complexpass123")
        password2_input.send_keys("complexpass123")
        password2_input.submit()

        # Check redirect to login page
        wait = WebDriverWait(self.browser, 120)
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Login"))
        login_h1 = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(login_h1.text, "Login")

    def test_create_news(self):
        # Test create news functionality (requires login)
        self.login_user()

        # Go to create news page
        add_button = self.browser.find_element(By.PARTIAL_LINK_TEXT, "+ Add News")
        add_button.click()

        # Fill form
        title_input = self.browser.find_element(By.NAME, "title")
        content_input = self.browser.find_element(By.NAME, "content")
        category_select = self.browser.find_element(By.NAME, "category")
        thumbnail_input = self.browser.find_element(By.NAME, "thumbnail")
        is_featured_checkbox = self.browser.find_element(By.NAME, "is_featured")

        title_input.send_keys("Test News Title")
        content_input.send_keys("Test news content for selenium testing")
        thumbnail_input.send_keys("https://example.com/image.jpg")

        # Set category (select 'match' from dropdown)

        select = Select(category_select)
        select.select_by_value("match")

        # Check is_featured checkbox
        is_featured_checkbox.click()

        # Submit form
        title_input.submit()

        # Check if returned to main page and news appears
        wait = WebDriverWait(self.browser, 120)
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Football News"))
        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Football News")

        # Check if news title appears on page
        wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Test News Title")))
        news_title = self.browser.find_element(By.PARTIAL_LINK_TEXT, "Test News Title")
        self.assertTrue(news_title.is_displayed())

    def test_news_detail(self):
        # Test news detail page

        # Login first because of @login_required decorator
        self.login_user()

        # Create news for testing
        news = News.objects.create(
            title="Detail Test News",
            content="Content for detail testing",
            user=self.test_user
        )

        # Open news detail page
        self.browser.get(f"{self.live_server_url}/news/{news.id}/")

        # Check if detail page opens correctly
        self.assertIn("Detail Test News", self.browser.page_source)
        self.assertIn("Content for detail testing", self.browser.page_source)

    def test_logout(self):
        # Test logout functionality
        self.login_user()

        # Click logout button - text is inside button, not link
        logout_button = self.browser.find_element(By.XPATH, "//button[contains(text(), 'Logout')]")
        logout_button.click()

        # Check if redirected to login page
        wait = WebDriverWait(self.browser, 120)
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Login"))
        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Login")

    def test_filter_main_page(self):
        # Test filter functionality on main page
        #         
        # Create news for testing
        News.objects.create(
            title="My Test News",
            content="My news content",
            user=self.test_user
        )
        News.objects.create(
            title="Other User News", 
            content="Other content",
            user=self.test_user  # Same user for simplicity
        )

        self.login_user()

        # Test filter "All Articles"
        wait = WebDriverWait(self.browser, 120)
        wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "All Articles")))
        all_button = self.browser.find_element(By.PARTIAL_LINK_TEXT, "All Articles")
        all_button.click()
        self.assertIn("My Test News", self.browser.page_source)
        self.assertIn("Other User News", self.browser.page_source)

        # Test filter "My Articles"  
        my_button = self.browser.find_element(By.PARTIAL_LINK_TEXT, "My Articles")
        my_button.click()
        self.assertIn("My Test News", self.browser.page_source)