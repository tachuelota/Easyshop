easyshop.search Readme
======================

Overview
--------

easyshop.search is a search replacement for EasyShop (http://pypi.python.org/pypi/easyshop.core).

It provides:

   - similarity search ("summerhose" finds summerhouse) based on TextIndexNG3 (http://pypi.python.org/pypi/Products.TextIndexNG3)
   - extended live search: displaying images of products 
   - filtering of the search results by categories
   
Installation
------------

To get started you will simply need to add the package to your "eggs" and "zcml" sections, run buildout, restart your Plone instance and install the "easyshop.search" package via the "Add-on Products" section in "Site Setup".

Then go to portal_properties -> site_properties and fill in the easyshop_path. This is the shop which should be searched. If your shop has the id "acme-shop" then you have to enter /acme-shop.

Note
----

Please note that easyshop.search is not as smart as it could be (and will be soon). At the moment the package only works for one shop (which should be enough for the most use cases) and it has impact on the whole Plone site as only
products will be found - even if the user searches not within a shop.
