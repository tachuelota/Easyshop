# Zope imports
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser

# zope imports
from zope.interface import implements
from zope.component import adapts
from zope.event import notify

# CMF imports
from Products.CMFCore.utils import getToolByName

# EasyShop import
from easyshop.core.interfaces import IItemManagement 
from easyshop.core.interfaces import IOrderManagement
from easyshop.core.interfaces import ICartManagement
from easyshop.core.interfaces import ICopyManagement
from easyshop.core.interfaces import ICustomerManagement
from easyshop.core.interfaces import IShippingManagement
from easyshop.core.interfaces import IPaymentPrices
from easyshop.core.interfaces import IShop

from easyshop.order.events import OrderSubmitted

class UnrestrictedUser(BaseUnrestrictedUser):
    """Unrestricted user that still has an id."""
    def getId(self):
        """Return the ID of the user."""
        return self.getUserName()

class OrderManagement:
    """An adapter, which provides order management for shop content objects.
    """
    implements(IOrderManagement)
    adapts(IShop)

    def __init__(self, context):
        """
        """
        self.context = context
        self.orders = context.orders

    def addOrder(self, customer=None, cart=None, notify_=True):
        """Adds a new order on base of the current customer and current cart.        
           It should be called after the payment process is completed.
        """
        cartmanager = ICartManagement(self.context)
        if customer is None:
            cm = ICustomerManagement(self.context)
            customer = cm.getAuthenticatedCustomer()

        if cart is None:
            cart = cartmanager.getCart()

        portal = getToolByName(self.context, 'portal_url').getPortalObject()

        ## The current user may not be allowed to create an order, so we
        ## temporarily change the security context to use a temporary
        ## user with manager role.
        old_sm = getSecurityManager()
        tmp_user = UnrestrictedUser(
            old_sm.getUser().getId(),
            '', ['Manager'], 
            ''
        )
        
        tmp_user = tmp_user.__of__(portal.acl_users)
        newSecurityManager(None, tmp_user)
  
        # Add a new order
        new_id = self.createOrderId()
        self.orders.invokeFactory("Order", id=new_id)
        new_order = getattr(self.orders, new_id)

        # Add shipping values to order
        sm = IShippingManagement(self.context)
        new_order.setShippingPriceNet(sm.getPriceNet())
        new_order.setShippingPriceGross(sm.getPriceGross())
        new_order.setShippingTax(sm.getTaxForCustomer())
        new_order.setShippingTaxRate(sm.getTaxRateForCustomer())

        # Add cart items to order
        IItemManagement(new_order).addItemsFromCart(cart)

        # Add payment price values to order 
        pp = IPaymentPrices(self.context)
        new_order.setPaymentPriceGross(pp.getPriceGross())
        new_order.setPaymentPriceNet(pp.getPriceNet())
        new_order.setPaymentTax(pp.getTaxForCustomer())
        new_order.setPaymentTaxRate(pp.getTaxRateForCustomer())
        
        # Copy Customer to Order
        customer = ICustomerManagement(self.context).getAuthenticatedCustomer()
        cm = ICopyManagement(customer)
        cm.copyTo(new_order)
            
        # Delete cart
        cartmanager.deleteCart(cart.getId())

        ## Reset security manager
        setSecurityManager(old_sm)
        
        # Index with customer again
        new_order.reindexObject()
        
        # Fire up event
        if notify_ == True:
            notify(OrderSubmitted(new_order))
                    
        return new_order

    def getOrders(self, filter=None, sorting="created", sort_order="reverse"):
        """Returns orders filtered by given filter.
        """
        catalog = getToolByName(self.orders, "portal_catalog")
        path = "/".join(self.orders.getPhysicalPath())
        
        query = {
            "path" : path,
            "portal_type" : "Order",
            "sort_on"     : sorting,
            "sort_order"  : sort_order,
        }
                
        if filter is not None:
            query["review_state"] = filter
                        
        brains = catalog.searchResults(query)
        return [brain.getObject() for brain in brains]

    def getOrdersForAuthenticatedCustomer(self):
        """Returns all orders for the actual customer.
        """
        # get authenticated customer        
        customer = ICustomerManagement(self.context).getAuthenticatedCustomer()

        orders = []
        for order in self.getOrders():
            if order.getCustomer().getId() == customer.getId():
                orders.append(order)

        return orders

    def getOrdersForCustomer(self, customer_id):
        """
        """
        orders = []
        for order in self.getOrders():
            if order.getCustomer().getId() == customer_id:
                orders.append(order)

        return orders
        
    def createOrderId(self):
        """Creates a new unique order id
        """
        from DateTime import DateTime;
        now = DateTime()

        return str(now.millis())
        
    def getOrderByUID(self, uid):
        """Returns order by given uid.        
        """
        uid_catalog = getToolByName(self.context, 'uid_catalog')
        lazy_cat = uid_catalog(UID=uid)
        o = lazy_cat[0].getObject()
        return o
        
    def _copyCustomerToOrder(self, customer, order):
        """NOT USED AT THE MOMENT
        """
        ## The current user may not be allowed to copy and paste, so we
        ## temporarily change the security context to use a temporary
        ## user with manager role.
        portal = getToolByName(self.context, 'portal_url').getPortalObject()

        old_sm = getSecurityManager()
        tmp_user = UnrestrictedUser(
            old_sm.getUser().getId(),
            '', ['Manager'], 
            ''
        )
        
        tmp_user = tmp_user.__of__(portal.acl_users)
        newSecurityManager(None, tmp_user)

        # Copy Customer to Order         
        data = self.context.customers.manage_copyObjects(ids=[customer.getId()])
        order.manage_pasteObjects(data)        

        ## Reset security manager
        setSecurityManager(old_sm)