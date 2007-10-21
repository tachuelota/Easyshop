# Zope imports
from zope.interface import implements
from zope.component import adapts

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# EasyShop imports
from Products.EasyShop.interfaces import IPaymentProcessing
from Products.EasyShop.interfaces import IItemManagement
from Products.EasyShop.interfaces import IAddressManagement
from Products.EasyShop.interfaces import IProductManagement
from Products.EasyShop.interfaces import IPrices
from Products.EasyShop.interfaces import IPayPal
from Products.EasyShop.interfaces import ICompleteness
from Products.EasyShop.interfaces import IType
from Products.EasyShop.interfaces import IShopManagement

class PayPalType:
    """Provides IType for paypal content objects.
    """
    implements(IType)
    adapts(IPayPal)

    def __init__(self, context):
        self.context = context                  

    def getType(self):
        """Returns type of EasyShopPrepayment.
        """
        return "paypal"
                
class PayPalCompleteness:
    """Provides ICompleteness for paypal content objects.
    """
    implements(ICompleteness)
    adapts(IPayPal)
        
    def __init__(self, context):
        """
        """
        self.context = context                  

    def isComplete(self):
        """For PayPal no information is needed
        """        
        return True
        
class PayPalPaymentProcessor:
    """Provides IPaymentProcessing for paypal content objects.
    Passes the whole cart to paypal. (There can be a problem because the
    content is passed via GET-REQUEST)
    """
    implements(IPaymentProcessing)
    adapts(IPayPal)

    def __init__(self, context):
        """
        """
        self.context = context
        
    def process(self, order):
        """
        """
        info = dict()

        pc = IPrices(order)
        
        url = "https://www.sandbox.paypal.com/cgi-bin/webscr"
        
        customer = order.getCustomer()

        am = IAddressManagement(customer)
        invoice_address  = am.getInvoiceAddress()
        shipping_address = am.getShippingAddress()
                
        info = {
            "cmd" : "_cart",
            "upload" : "1",
            "business" : "heinz@haendler.de",
            "currency_code" : "EUR",
            "notify_url" : "",
            "return" : "",
            "last_name" : shipping_address.getName(),
            "address1" : shipping_address.getAddress1(),
            "address2" : shipping_address.getAddress2(),
            "city" : shipping_address.getCity(),
            "state" : shipping_address.getCountry(),
            "zip" : shipping_address.getZipCode(),
            "shipping_1" : order.getShippingPriceNet(),
            "tax_1" : pc.getPriceGross() - pc.getPriceNet()
        }
        
        im = IItemManagement(order)
        for i, item in enumerate(im.getItems()):
            j = i + 1
            name     = "item_name_%s" % j
            quantity = "quantity_%s" % j
            amount   = "amount_%s" % j
            
            product = item.getProduct()
            
            info[name]     = product.Title()
            info[quantity] = str(int(item.getProductQuantity()))
            info[amount]   = str(item.getProductPriceGross())
            
        # redirect to paypal    
        parameters = "&".join(["%s=%s" % (k, v) for (k, v) in info.items()])                
        
        url = url + "?" + parameters
        self.context.REQUEST.RESPONSE.redirect(url)
        
        return "NOT_PAYED"
        
class PayPalSimplePaymentProcessor:
    """Provides IPaymentProcessing for paypal content objects.    
    Passes just a value for the whole cart to papal.
    """
    implements(IPaymentProcessing)
    adapts(IPayPal)

    def __init__(self, context):
        """
        """
        self.context = context
        
    def process(self, order):
        """
        """    
        info = dict()

        shop = IShopManagement(self.context).getShop()                        
        notify_url = "%s/paypal?order=%s" % (shop.absolute_url(), order.UID())
        return_url = "%s/check-out-thanks" % shop.absolute_url()
        
        pc = IPrices(order)
        price_net = "%.2f" % pc.getPriceNet()
        tax = "%.2f" % (pc.getPriceGross() - float(price_net))
        
        url = shop.getPayPalUrl()
        
        customer = order.getCustomer()
        am = IAddressManagement(customer)
        invoice_address  = am.getInvoiceAddress()
        shipping_address = am.getShippingAddress()
        
        info = {
            "cmd" : "_xclick",
            "upload" : "1",
            "business" : shop.getPayPalId(),
            "currency_code" : "EUR",
            "notify_url" : notify_url,
            "return" : return_url,
            "first_name" : invoice_address.getFirstname(),
            "last_name" : invoice_address.getLastname(),
            "address1" : invoice_address.getAddress1(),
            "address2" : invoice_address.getAddress2(),
            "city" : invoice_address.getCity(),
            "state" : invoice_address.getCountry(),
            "zip" : invoice_address.getZipCode(),
            "no_shipping" : "1",
            "item_name" : "Demmelhuber",           
            "amount" : price_net,
            "tax" : tax,
        }

        # redirect to paypal    
        parameters = "&".join(["%s=%s" % (k, v) for (k, v) in info.items()])                
        
        url = url + "?" + parameters
        self.context.REQUEST.RESPONSE.redirect(url)
        
        return "NOT_PAYED"        