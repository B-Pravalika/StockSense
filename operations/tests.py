from decimal import Decimal

from django.test import TestCase

from inventory.models import Category, Product, Stock
from warehouse.models import Warehouse, Location

from operations.models import (
    Supplier,
    Receipt,
    ReceiptItem,
    Delivery,
    DeliveryItem,
    InternalTransfer,
    TransferItem,
    InventoryAdjustment,
    AdjustmentItem,
    StockLedger,
)

from operations.services.stock_service import (
    increase_stock,
    decrease_stock,
    transfer_stock,
    adjust_stock,
)

from operations.services.operation_service import (
    validate_receipt,
    validate_delivery,
    validate_transfer,
    validate_adjustment,
)


class StockServiceTestCase(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name="Raw Materials",
            description="Test category"
        )

        self.product = Product.objects.create(
            name="Steel Rod",
            sku="STEEL-001",
            category=self.category,
            unit_of_measure="kg"
        )

        self.warehouse = Warehouse.objects.create(
            name="Main Warehouse",
            address="Hyderabad"
        )

        self.location_a = Location.objects.create(
            warehouse=self.warehouse,
            name="Rack A"
        )

        self.location_b = Location.objects.create(
            warehouse=self.warehouse,
            name="Rack B"
        )

    def test_increase_stock(self):
        stock = increase_stock(
            product=self.product,
            location=self.location_a,
            quantity=100,
            reference="REC-001"
        )

        self.assertEqual(stock.quantity, Decimal("100"))

        ledger = StockLedger.objects.get(
            reference="REC-001"
        )

        self.assertEqual(ledger.quantity, Decimal("100"))
        self.assertEqual(ledger.operation, "RECEIPT")

    def test_decrease_stock(self):
        increase_stock(
            product=self.product,
            location=self.location_a,
            quantity=100,
            reference="REC-002"
        )

        stock = decrease_stock(
            product=self.product,
            location=self.location_a,
            quantity=20,
            reference="DEL-001"
        )

        self.assertEqual(stock.quantity, Decimal("80"))

        ledger = StockLedger.objects.get(
            reference="DEL-001"
        )

        self.assertEqual(ledger.quantity, Decimal("-20"))
        self.assertEqual(ledger.operation, "DELIVERY")

    def test_transfer_stock(self):
        increase_stock(
            product=self.product,
            location=self.location_a,
            quantity=100,
            reference="REC-003"
        )

        result = transfer_stock(
            product=self.product,
            source_location=self.location_a,
            destination_location=self.location_b,
            quantity=30,
            reference="TRF-001"
        )

        self.assertTrue(result)

        source_stock = Stock.objects.get(
            product=self.product,
            location=self.location_a
        )

        destination_stock = Stock.objects.get(
            product=self.product,
            location=self.location_b
        )

        self.assertEqual(
            source_stock.quantity,
            Decimal("70")
        )

        self.assertEqual(
            destination_stock.quantity,
            Decimal("30")
        )

        ledger_entries = StockLedger.objects.filter(
            reference="TRF-001"
        )

        self.assertEqual(ledger_entries.count(), 2)

    def test_adjust_stock(self):
        increase_stock(
            product=self.product,
            location=self.location_a,
            quantity=100,
            reference="REC-004"
        )

        stock = adjust_stock(
            product=self.product,
            location=self.location_a,
            counted_quantity=97,
            reference="ADJ-001",
            notes="3 kg damaged"
        )

        self.assertEqual(
            stock.quantity,
            Decimal("97")
        )

        ledger = StockLedger.objects.get(
            reference="ADJ-001"
        )

        self.assertEqual(
            ledger.quantity,
            Decimal("-3")
        )

        self.assertEqual(
            ledger.operation,
            "ADJUSTMENT"
        )

    def test_cannot_deliver_more_than_available(self):
        increase_stock(
            product=self.product,
            location=self.location_a,
            quantity=50,
            reference="REC-005"
        )

        with self.assertRaises(ValueError):
            decrease_stock(
                product=self.product,
                location=self.location_a,
                quantity=60,
                reference="DEL-002"
            )

        stock = Stock.objects.get(
            product=self.product,
            location=self.location_a
        )

        self.assertEqual(
            stock.quantity,
            Decimal("50")
        )

    def test_negative_quantity_is_not_allowed(self):
        with self.assertRaises(ValueError):
            increase_stock(
                product=self.product,
                location=self.location_a,
                quantity=-10,
                reference="REC-006"
            )

    def test_ledger_created_for_stock_operations(self):
        increase_stock(
            product=self.product,
            location=self.location_a,
            quantity=100,
            reference="REC-007"
        )

        decrease_stock(
            product=self.product,
            location=self.location_a,
            quantity=20,
            reference="DEL-003"
        )

        transfer_stock(
            product=self.product,
            source_location=self.location_a,
            destination_location=self.location_b,
            quantity=30,
            reference="TRF-002"
        )

        adjust_stock(
            product=self.product,
            location=self.location_b,
            counted_quantity=25,
            reference="ADJ-002"
        )

        self.assertEqual(
            StockLedger.objects.count(),
            5
        )


class OperationValidationTestCase(TestCase):

    def setUp(self):
        # Category
        self.category = Category.objects.create(
            name="Test Category"
        )

        # Product
        self.product = Product.objects.create(
            name="Steel Rod",
            sku="STEEL-TEST-001",
            category=self.category,
            unit_of_measure="kg"
        )

        # Warehouse
        self.warehouse = Warehouse.objects.create(
            name="Test Warehouse",
            address="Hyderabad"
        )

        # Locations
        self.location_a = Location.objects.create(
            warehouse=self.warehouse,
            name="Main Store"
        )

        self.location_b = Location.objects.create(
            warehouse=self.warehouse,
            name="Production Floor"
        )

        # Supplier
        self.supplier = Supplier.objects.create(
            name="ABC Steel Suppliers",
            contact_person="Test Person",
            phone="9999999999",
            email="supplier@example.com"
        )

    def test_validate_receipt(self):
        """
        READY receipt should increase stock
        and become DONE.
        """

        receipt = Receipt.objects.create(
            reference="REC-TEST-001",
            supplier=self.supplier,
            destination=self.location_a,
            status="READY"
        )

        ReceiptItem.objects.create(
            receipt=receipt,
            product=self.product,
            quantity=100
        )

        result = validate_receipt(receipt)

        self.assertEqual(
            result.status,
            "DONE"
        )

        stock = Stock.objects.get(
            product=self.product,
            location=self.location_a
        )

        self.assertEqual(
            stock.quantity,
            Decimal("100")
        )

        ledger = StockLedger.objects.get(
            reference="REC-TEST-001"
        )

        self.assertEqual(
            ledger.operation,
            "RECEIPT"
        )

        self.assertEqual(
            ledger.quantity,
            Decimal("100")
        )

    def test_validate_delivery(self):
        """
        PACK delivery should decrease stock
        and become DONE.
        """

        increase_stock(
            product=self.product,
            location=self.location_a,
            quantity=100,
            reference="REC-TEST-002"
        )

        delivery = Delivery.objects.create(
            reference="DEL-TEST-001",
            destination="Customer A",
            source_location=self.location_a,
            status="PACK"
        )

        DeliveryItem.objects.create(
            delivery=delivery,
            product=self.product,
            quantity=20
        )

        result = validate_delivery(delivery)

        self.assertEqual(
            result.status,
            "DONE"
        )

        stock = Stock.objects.get(
            product=self.product,
            location=self.location_a
        )

        self.assertEqual(
            stock.quantity,
            Decimal("80")
        )

        ledger = StockLedger.objects.get(
            reference="DEL-TEST-001"
        )

        self.assertEqual(
            ledger.operation,
            "DELIVERY"
        )

        self.assertEqual(
            ledger.quantity,
            Decimal("-20")
        )

    def test_validate_transfer(self):
        """
        READY transfer should move stock
        from source to destination.
        """

        increase_stock(
            product=self.product,
            location=self.location_a,
            quantity=100,
            reference="REC-TEST-003"
        )

        transfer = InternalTransfer.objects.create(
            reference="TRF-TEST-001",
            source_location=self.location_a,
            destination_location=self.location_b,
            status="READY"
        )

        TransferItem.objects.create(
            transfer=transfer,
            product=self.product,
            quantity=30
        )

        result = validate_transfer(transfer)

        self.assertEqual(
            result.status,
            "DONE"
        )

        source_stock = Stock.objects.get(
            product=self.product,
            location=self.location_a
        )

        destination_stock = Stock.objects.get(
            product=self.product,
            location=self.location_b
        )

        self.assertEqual(
            source_stock.quantity,
            Decimal("70")
        )

        self.assertEqual(
            destination_stock.quantity,
            Decimal("30")
        )

        ledger_entries = StockLedger.objects.filter(
            reference="TRF-TEST-001"
        )

        self.assertEqual(
            ledger_entries.count(),
            2
        )

    def test_validate_adjustment(self):
        """
        DRAFT adjustment should set stock
        to the physical counted quantity.
        """

        increase_stock(
            product=self.product,
            location=self.location_a,
            quantity=100,
            reference="REC-TEST-004"
        )

        adjustment = InventoryAdjustment.objects.create(
            reference="ADJ-TEST-001",
            location=self.location_a,
            status="DRAFT",
            reason="Physical stock count"
        )

        AdjustmentItem.objects.create(
            adjustment=adjustment,
            product=self.product,
            counted_quantity=97
        )

        result = validate_adjustment(adjustment)

        self.assertEqual(
            result.status,
            "DONE"
        )

        stock = Stock.objects.get(
            product=self.product,
            location=self.location_a
        )

        self.assertEqual(
            stock.quantity,
            Decimal("97")
        )

        ledger = StockLedger.objects.get(
            reference="ADJ-TEST-001"
        )

        self.assertEqual(
            ledger.quantity,
            Decimal("-3")
        )

    def test_receipt_must_be_ready(self):
        """
        A DRAFT receipt cannot be validated.
        """

        receipt = Receipt.objects.create(
            reference="REC-TEST-005",
            supplier=self.supplier,
            destination=self.location_a,
            status="DRAFT"
        )

        ReceiptItem.objects.create(
            receipt=receipt,
            product=self.product,
            quantity=50
        )

        with self.assertRaises(ValueError):
            validate_receipt(receipt)

        self.assertFalse(
            Stock.objects.filter(
                product=self.product,
                location=self.location_a
            ).exists()
        )

    def test_delivery_must_be_pack(self):
        """
        A READY delivery cannot be directly validated.
        """

        increase_stock(
            product=self.product,
            location=self.location_a,
            quantity=100,
            reference="REC-TEST-006"
        )

        delivery = Delivery.objects.create(
            reference="DEL-TEST-002",
            destination="Customer B",
            source_location=self.location_a,
            status="READY"
        )

        DeliveryItem.objects.create(
            delivery=delivery,
            product=self.product,
            quantity=20
        )

        with self.assertRaises(ValueError):
            validate_delivery(delivery)

        stock = Stock.objects.get(
            product=self.product,
            location=self.location_a
        )

        self.assertEqual(
            stock.quantity,
            Decimal("100")
        )

    def test_canceled_transfer_cannot_be_validated(self):
        """
        A canceled transfer cannot change stock.
        """

        increase_stock(
            product=self.product,
            location=self.location_a,
            quantity=100,
            reference="REC-TEST-007"
        )

        transfer = InternalTransfer.objects.create(
            reference="TRF-TEST-002",
            source_location=self.location_a,
            destination_location=self.location_b,
            status="CANCELED"
        )

        TransferItem.objects.create(
            transfer=transfer,
            product=self.product,
            quantity=30
        )

        with self.assertRaises(ValueError):
            validate_transfer(transfer)

        source_stock = Stock.objects.get(
            product=self.product,
            location=self.location_a
        )

        self.assertEqual(
            source_stock.quantity,
            Decimal("100")
        )

        self.assertFalse(
            Stock.objects.filter(
                product=self.product,
                location=self.location_b
            ).exists()
        )

    def test_operation_with_no_items_fails(self):
        """
        An operation without items cannot be validated.
        """

        receipt = Receipt.objects.create(
            reference="REC-TEST-008",
            supplier=self.supplier,
            destination=self.location_a,
            status="READY"
        )

        with self.assertRaises(ValueError):
            validate_receipt(receipt)

        self.assertEqual(
            receipt.status,
            "READY"
        )