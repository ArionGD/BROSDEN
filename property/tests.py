from django.test import TestCase
from django.contrib.auth import get_user_model
from property.models import Property

User = get_user_model()

class PropertyModelTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='password', role='OWNER')
        self.property = Property.objects.create(
            owner=self.owner,
            title='Test PG',
            price=5000,
            property_type='PG',
            total_capacity=5,
            current_occupancy=2
        )

    def test_available_spaces(self):
        """Test the available_spaces property."""
        self.assertEqual(self.property.available_spaces, 3)

    def test_is_vacant(self):
        """Test the is_vacant property."""
        self.assertTrue(self.property.is_vacant)
        
        self.property.current_occupancy = 5
        self.property.save()
        self.assertFalse(self.property.is_vacant)

    def test_financial_breakdown_fixed_fee(self):
        """Test that contract fee is always 2000."""
        breakdown = self.property.get_financial_breakdown()
        self.assertEqual(breakdown['contract_fee'], 2000)
        # Verify total calculation
        expected_total = (self.property.price * self.property.security_deposit_months) + 2000
        self.assertEqual(breakdown['total'], expected_total)

    def test_pg_type_exists(self):
        """Test that PG is a valid property type."""
        choices = dict(Property.PROPERTY_TYPES)
        self.assertIn('PG', choices)
        self.assertEqual(choices['PG'], 'Paying Guest')
