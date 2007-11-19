# zope imports
from zope.interface import implements
from zope.component import adapts

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# easyshop imports
from easyshop.core.interfaces import ITaxes
from easyshop.core.interfaces import IProduct
from easyshop.core.interfaces import IShopManagement

class ProductTaxCalculator:
    """Provides ITaxes for product content objects.
    """
    implements(ITaxes)
    adapts(IProduct)

    def __init__(self, context):
        """
        """
        self.context = context
        shop = IShopManagement(self.context).getShop()
        self.taxes = ITaxes(shop)

    def getTaxRate(self):
        """
        """
        tax = self.taxes.getTaxRate(self.context)
        return tax

    def getTaxRateForCustomer(self):
        """
        """
        tax = self.taxes.getTaxRateForCustomer(self.context)
        return tax

    def getTax(self):
        """
        """
        tax = self.taxes.getTax(self.context)
        return tax

    def getTaxForCustomer(self):
        """
        """
        tax = self.taxes.getTaxForCustomer(self.context)
        return tax