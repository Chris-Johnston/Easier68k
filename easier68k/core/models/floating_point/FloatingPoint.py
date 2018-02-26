"""
Abstract class definition of a floating point
number
defines the interface
"""

class FloatingPoint():

    def isZero(self):
        """
        Returns true if the value
        represents +0.0 or -0.0

        sign of mantissa can be anything
        exponent and mantissa = 0
        :return:
        """
        pass

    def isInfinite(self):
        """
        Returns true if the value is
        + or - infinity

        sign of mantissa can be anything
        exponent is maximum
        mantissa is 0
        :return:
        """
        pass

    def isNaN(self):
        """
        Returns true if the value is
        +/- NaN

        Sign of mantissa 0 or 1
        If the exponent is maximum
        Mantissa any non zero pattern
        :return:
        """
        pass