# zope imports
from zope.interface import implements
from zope.component import adapts

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# easyshop imports
from easyshop.core.interfaces import ICustomerManagement
from easyshop.core.interfaces import ITaxes
from easyshop.core.interfaces import IShippingManagement
from easyshop.core.interfaces import ICartManagement
from easyshop.core.interfaces import IItemManagement
from easyshop.core.interfaces import IValidity
from easyshop.core.interfaces import IShop
from easyshop.catalog.content.product import Product
from easyshop.core.interfaces import IShopManagement

class ShippingManagement:
    """An adapter, which provides shipping management for shop content objects.
    """    
    implements(IShippingManagement)
    adapts(IShop)

    def __init__(self, context):
        """
        """
        self.context = context
        self.prices  = self.context.shippingprices
        self.methods = self.context.shippingmethods
        
    def getSelectedShippingMethod(self):
        """
        """
        cm = ICustomerManagement(IShopManagement(self.context).getShop())
        customer = cm.getAuthenticatedCustomer()        
        shipping_method_id = customer.selected_shipping_method
        
        return self.getShippingMethod(shipping_method_id)
        
    def getShippingPrice(self, id):
        """
        """        
        try:
            return self.prices[id]
        except KeyError:
            return None
            
    def getShippingPrices(self):
        """
        """
        return self.prices.objectValues()
        
        shop = IShopManagement(self.context).getShop()
        
        # Todo: By interface
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog.searchResults(
            portal_type = ("ShippingPrice", "DemmelhuberShippingPrice"),
            path = "/".join(self.prices.getPhysicalPath()),
            sort_on = "getObjPositionInParent",
        )

        # Todo: Optimize
        return [brain.getObject() for brain in brains]

    def getShippingMethod(self, id):
        """
        """
        try:
            return self.methods[id]
        except KeyError:
            return None    

    def getShippingMethods(self):
        """
        """
        # Todo: By interface
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog.searchResults(
            portal_type = ("ShippingMethod",),
            path = "/".join(self.methods.getPhysicalPath()),
            sort_on = "getObjPositionInParent",
        )

        # Todo: Optimize
        return [brain.getObject() for brain in brains]

    # Todo: Optimize. The next methods are the same as for pending tax
    # calculations
    def getPriceGross(self):
        """
        """
        for price in self.getShippingPrices():
            if IValidity(price).isValid() == True:
                return price.getPriceGross()
        
        return 0
        
    def getTaxRate(self):
        """
        """
        temp_shipping_product = self.createTemporaryShippingProduct()
        return ITaxes(temp_shipping_product).getTaxRate()

    def getTaxRateForCustomer(self):
        """
        """
        temp_shipping_product = self.createTemporaryShippingProduct()
        return ITaxes(temp_shipping_product).getTaxRateForCustomer()

    def getTax(self):
        """
        """
        temp_shipping_product = self.createTemporaryShippingProduct()
        return ITaxes(temp_shipping_product).getTax()

    def getTaxForCustomer(self):
        """
        """
        # If there a no items the shipping tax is 0
        cart_manager = ICartManagement(self.context)
        cart = cart_manager.getCart()
        
        if cart is None:
            return 0
            
        cart_item_manager = IItemManagement(cart)
        if cart_item_manager.hasItems() == False:
            return 0

        temp_shipping_product = self.createTemporaryShippingProduct()        
        return ITaxes(temp_shipping_product).getTaxForCustomer()

    def getPriceNet(self):
        """
        """
        return self.getPriceGross() - self.getTax()

    def getPriceForCustomer(self):
        """
        """
        # If there a no items the shipping price is 0        
        cart_manager = ICartManagement(self.context)
        cart = cart_manager.getCart()        
        
        if cart is None:
            return 0
                    
        cart_item_manager = IItemManagement(cart)
        if cart_item_manager.hasItems() == False:
            return 0
        
        return self.getPriceNet() + self.getTaxForCustomer()

    def createTemporaryShippingProduct(self):
        """
        """
        temp_shipping_product = Product("shipping")
        temp_shipping_product.setPriceGross(self.getPriceGross())
        temp_shipping_product.context = self.context
        
        return temp_shipping_product
