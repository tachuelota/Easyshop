# Zope imports
from DateTime import DateTime

# zope imports
from zope.component import getMultiAdapter

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# easyshop imports 
from base import EasyShopTestCase
from iqpp.easyshop.tests import utils
from iqpp.easyshop.interfaces import I

class Test(EasyShopTestCase):
    """
    """
    def afterSetUp(self):
        """
        """
        utils.createTestEnvironment(self)

        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(Test))
    return suite
                                               