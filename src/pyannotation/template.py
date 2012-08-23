"""This module illustrates how to write your docstring in OpenAlea
and other projects related to OpenAlea."""

__license__ = "Cecill-C"
__revision__ = " $Id: actor.py 1586 2009-01-30 15:56:25Z cokelaer $ "
__docformat__ = 'reStructuredText'

class MainClass1(object):
    """This class docstring shows how to use sphinx and rst syntax

    The first line is brief explanation, which may be completed with 
    a longer one. For instance to discuss about its methods. The only
    method here is :func:`function1`'s. The main idea is to document
    the class and methods's arguments with.


    Here below is the results of the :func:`function1` docstring.

    """

    def function1(self, arg1, arg2, arg3):
        """returns (arg1 / arg2) + arg3

    
        """
        return arg1/arg2 + arg3