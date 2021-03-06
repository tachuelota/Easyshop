# Five imports
from Products.Five.browser import BrowserView

# CMFPlone imports
from Products.CMFPlone.utils import safe_unicode

# Easyshop imports
from easyshop.catalog.adapters.property_management import getTitlesByIds
from easyshop.core.interfaces import ICartManagement
from easyshop.core.interfaces import ICurrencyManagement
from easyshop.core.interfaces import ICustomerManagement
from easyshop.core.interfaces import IItemManagement
from easyshop.core.interfaces import IImageManagement
from easyshop.core.interfaces import IPrices
from easyshop.core.interfaces import IProductVariant
from easyshop.core.interfaces import IPropertyManagement
from easyshop.core.interfaces import IShippingMethodManagement
from easyshop.core.interfaces import IShopManagement

class AddedToCartView(BrowserView):
    """
    """
    def getProducts(self):
        """Returns the last products, which are added to the cart.
        """
        cm = ICurrencyManagement(self.context)
        
        result = []
        for cart_item_id in self.request.SESSION.get("added-to-cart", []):

            cart = ICartManagement(self.context).getCart()
            cart_item = IItemManagement(cart).getItem(cart_item_id)
            if cart_item is None:
                continue

            product = cart_item.getProduct()
            if product is None:
                continue
                
            # Price
            price = IPrices(product).getPriceForCustomer()
        
            # Image
            product = cart_item.getProduct()
            image = IImageManagement(product).getMainImage()
            if image is not None:
                image_url = image.absolute_url()
            else:
                image_url = None
        
            # Get selected properties
            properties = []
            pm = IPropertyManagement(product)
        
            for selected_property in cart_item.getProperties():
                property_price = pm.getPriceForCustomer(
                    selected_property["id"], 
                    selected_property["selected_option"]) 

                # Get titles of property and option
                titles = getTitlesByIds(
                    product,
                    selected_property["id"], 
                    selected_property["selected_option"])
                
                if titles is None:
                    continue

                if (property_price == 0.0) or \
                   (IProductVariant.providedBy(product)) == True:
                    show_price = False
                else:
                    show_price = True
                
                properties.append({
                    "id" : selected_property["id"],
                    "selected_option" : titles["option"],
                    "title" : titles["property"],
                    "price" : cm.priceToString(property_price),
                    "show_price" : show_price,
                })
            
                price += property_price
        
            total = cart_item.getAmount() * price
                        
            result.append({
                "title"      : product.Title(),
                "url"        : product.absolute_url(),
                "amount"     : cart_item.getAmount(),
                "total"      : cm.priceToString(total),
                "price"      : cm.priceToString(price),
                "image_url"  : image_url,
                "properties" : properties,
            })
        
        # Update selected shipping method. TODO: This should be factored out and
        # made available via a event or similar. It is also used within 
        # ajax/cart/_refresh_cart
        customer = ICustomerManagement(self.context).getAuthenticatedCustomer()
            
        shop = IShopManagement(self.context).getShop()
        shipping_methods = IShippingMethodManagement(shop).getShippingMethods(check_validity=True)
        shipping_methods_ids = [sm.getId() for sm in shipping_methods]
        selected_shipping_method = self.request.get("selected_shipping_method")

        # Set selected shipping method
        if selected_shipping_method in shipping_methods_ids:
            customer.selected_shipping_method = \
                safe_unicode(self.request.get("selected_shipping_method"))
        else:
            customer.selected_shipping_method = shipping_methods_ids[0]
        
        # Reset session
        if self.request.SESSION.has_key("added-to-cart"):
            del self.request.SESSION["added-to-cart"]
        return result
    
    def getShopURL(self):
        """
        """
        return IShopManagement(self.context).getShop().absolute_url()