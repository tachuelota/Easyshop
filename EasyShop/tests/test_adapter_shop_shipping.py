# Zope imports
from DateTime import DateTime

# zope imports
from zope.component import getMultiAdapter

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# EasyShop imports 
from base import EasyShopTestCase
from Products.EasyShop.tests import utils
from Products.EasyShop.interfaces import IShippingManagement

class TestShopShippingManagement(EasyShopTestCase):
    """
    """
    def afterSetUp(self):
        """
        """
        utils.createTestEnvironment(self)
        self.shop.taxes.invokeFactory("CustomerTax", id="customer", rate=10.0)
        self.sm = IShippingManagement(self.shop)
        
    def testGetShippingPrice(self):
        """
        """
        price = self.sm.getShippingPrice("default")
        self.assertEqual(price.getPriceGross(), 10.0)
                
    def testGetShippingPrices(self):
        """
        """
        self.shop.shippingprices.invokeFactory("EasyShopShippingPrice", "s1")
        self.shop.shippingprices.invokeFactory("EasyShopShippingPrice", "s2")
        self.shop.shippingprices.invokeFactory("EasyShopShippingPrice", "s3")
        self.shop.shippingprices.invokeFactory("EasyShopShippingPrice", "s4")
        
        ids = [p.getId() for p in self.sm.getShippingPrices()]
        self.assertEqual(ids, ["default", "s1", "s2", "s3", "s4"])
                
    def getShippingMethods(self):
        """
        """
        # Todo: Added test when implemented

    def testGetPriceGross(self):
        """
        """
        self.assertEqual(self.sm.getPriceGross(), 10.0)
                
    def testGetTaxRate(self):
        """
        """
        self.assertEqual(self.sm.getTaxRate(), 19.0)
        
    def testGetTaxRateForCustomer(self):
        """
        """
        self.assertEqual(self.sm.getTaxRateForCustomer(), 10.0)
        
    def testGetTax(self):
        """
        """
        self.assertEqual("%.2f" % self.sm.getTax(), "1.60")
                
    def testGetTaxForCustomer_1(self):
        """
        """
        self.assertEqual(self.sm.getTaxForCustomer(), 0)

    def testGetTaxForCustomer_2(self):
        """
        """
        self.login("newmember")
        view = getMultiAdapter((self.product_1, self.product_1.REQUEST), name="addToCart")
        view.addToCart()
        
        self.assertEqual("%.2f" % self.sm.getTaxForCustomer(), "0.84")

    def testGetPriceNet(self):
        """
        """
        self.assertEqual("%.2f" % self.sm.getPriceNet(), "8.40")
        
    def testGetPriceForCustomer_1(self):
        """
        """
        self.assertEqual(self.sm.getPriceForCustomer(), 0.0)

    def testGetPriceForCustomer_2(self):
        """
        """
        self.login("newmember")
        view = getMultiAdapter((self.product_1, self.product_1.REQUEST), name="addToCart")
        view.addToCart()
        
        self.assertEqual("%.2f" % self.sm.getPriceForCustomer(), "9.24")
        
    def testCreateTemporaryShippingProduct(self):
        """
        """
        product = self.sm.createTemporaryShippingProduct()
        self.assertEqual(product.getPriceGross(), 10.0)
        self.assertEqual(product.getId(), "shipping")
                
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestShopShippingManagement))
    return suite