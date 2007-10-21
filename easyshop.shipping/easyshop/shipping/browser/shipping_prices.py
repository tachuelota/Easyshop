# zope imports
from zope.interface import Interface
from zope.interface import implements

# Five imports
from Products.Five.browser import BrowserView

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# EasyShop imports
from Products.EasyShop.interfaces import ICurrencyManagement
from Products.EasyShop.interfaces import IShippingManagement
from Products.EasyShop.interfaces import IShopManagement

class IShippingPricesView(Interface):    
    """
    """
    def getShippingPrices():
        """Returns the shipping prices of the shop.
        """
    
class ShippingPricesView(BrowserView):
    """
    """
    implements(IShippingPricesView)

    def getShippingPrices(self):
        """
        """
        shop = IShopManagement(self.context).getShop()        
        sm = IShippingManagement(shop)        
        cm = ICurrencyManagement(shop)
                
        result = []
        for shipping_price in sm.getShippingPrices():
            
            price = cm.priceToString(shipping_price.getPriceGross())
            
            result.append({
                "id"       : shipping_price.getId(),            
                "title"    : shipping_price.Title(),
                "price"    : price,
                "url"      : shipping_price.absolute_url(),
                "up_url"   : "%s/es_folder_position?position=up&id=%s" % (self.context.absolute_url(), shipping_price.getId()),
                "down_url" : "%s/es_folder_position?position=down&id=%s" % (self.context.absolute_url(), shipping_price.getId()),
                "amount_of_criteria" : self._getAmountOfCriteria(shipping_price.getId())
            })

        return result
        
    def _getAmountOfCriteria(self, id):
        """Returns amount of criteria for tax with given id.
        """
        try:
            tax = self.context[id]
        except IndexError:
            return 0
            
        return len(tax.objectIds())
    