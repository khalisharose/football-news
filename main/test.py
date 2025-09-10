from django.test import TestCase
from .models import Item

class ItemTest(TestCase):
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