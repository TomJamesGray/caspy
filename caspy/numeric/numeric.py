import copy
import logging
from caspy.numeric.symbol import Symbol
from caspy.numeric.fraction import Fraction,Frac
from typing import TypeVar, Generic

Num = TypeVar("Num")
logger = logging.getLogger(__name__)


class Numeric(Generic[Num]):
    """Represents a linear combination of numbers and symbols"""

    def __init__(self, val, typ: str):
        """Initialises a numeric class with a single value"""
        self.val = []
        if typ == "sym":
            # val represents the letter of the symbol, such as x,y,..
            self.val.append(Symbol(val, Fraction(1, 1)))
        elif typ == "number":
            # in this case the 1 represents that this value is just a number
            if type(val) == Fraction:
                self.val.append(Symbol(1,val))
            else:
                self.val.append(Symbol(1, Fraction(float(val), 1)))
        elif typ == "sym_obj":
            self.val.append(val)

    def __repr__(self):
        return "<Numeric class {}>".format(self.val)

    def __add__(self, other):
        if type(other) == Numeric:
            return self.add(other)
        elif type(other) in (int,float):
            return self.add(Numeric(other, "number"))

    def __mul__(self, other):
        if type(other) == Numeric:
            return self.mul(other)

    def __sub__(self, other):
        if type(other) == Numeric:
            return self.add(other.neg())

    def __truediv__(self, other):
        if type(other) == Numeric:
            if other.is_zero():
                logger.critical("Division by zero")
                raise ZeroDivisionError("Trying to divide {} by zero".format(self))
            return self.mul(other.recip())

    def __pow__(self, power, modulo=None):
        if type(power) == Numeric:
            return self.pow(power)

    def sym_in(self,key):
        """
        Checks if a symbol such as 'x' already exists in this. Used
        for multiplication of terms like x and x^2
        :param key: symbol such as x
        :return: False if not found, otherwise returns coresponding
        key for this object
        """
        for key_x in self.val:
            if key_x == key:
                return key_x
        return False

    def sym_and_pow_match(self,sym):
        """
        Checks if a symbol is in this numeric class
        :param key: symbol object in this class
        :return:
        """
        for sym_self in self.val:
            sym_self.simplify()
            if sym_self == sym:
                return sym_self

        return False

    def add(self, y: Num) -> Num:
        """
        Adds y to this number
        :param y: Another numeric class
        :return: self
        """
        if self.is_zero():
            self.val = y.val
            return self
        elif y.is_zero():
            return self

        for sym_y in y.val:
            sym_y.simplify()
            lookup = self.sym_and_pow_match(sym_y)
            if lookup:
                # A term with the same symbols already exists in this numeric expression
                # so just add coeffs
                logger.debug("sym_and_pow match on {} and {}".format(self,sym_y))
                # Find coefficient for sym_y
                sym_y_coeff_index = sym_y.get_coeff_index()
                if sym_y_coeff_index != -1:
                    lookup.add_coeff(sym_y.val[sym_y_coeff_index][0])
                else:
                    logger.debug("No coefficient for symbol {} so adding '1' as coeff".format(sym_y))
                    sym_y.val.append([Fraction(1,1),1])
                    lookup.add_coeff(sym_y.val[sym_y_coeff_index][0])
            else:
                self.val.append(sym_y)

        return self

    def neg(self) -> Num:
        """
        Negates this number
        :return: self
        """
        for sym in self.val:
            sym.neg()

        return self

    def recip(self) -> Num:
        if len(self.val) == 1:
            self.val[0] = self.val[0].recip()
            return self
        else:
            return self.pow(Numeric(-1,"number"))

    def pow(self,x: Num) -> Num:
        """
        Raises this number to the power x
        :param x: Numeric object
        :return: self
        """
        if len(self.val) == 1:
            self.val[0] = self.val[0].pow(x)
            return self
        else:
            # Make a copy of this object for later use
            pre_exp = copy.copy(self)
            # Redefine this object as a list of length 1 with the previous
            # info stored as a symbol type and raise that to the power x
            self.val = [Symbol(pre_exp, Fraction(1, 1))]
            self.val[0].val[0][1] = x
            return self

    def mul(self, x: Num) -> Num:
        """
        Multiplies this number by x. If this number or x is made up
        of a linear combination of terms, eg (1+x) then we don't
        expand the product
        :param x: Numeric object
        :return: self
        """
        if len(self.val) > 1 or len(x.val) > 1:
            pre_self = copy.copy(self)
            pre_x = copy.copy(x)
            # Redefine this numeric object as having just one symbol
            # that is the product of it's prior self and x
            self.val = [Symbol(pre_self, Fraction(1, 1))]
            self.val[0].val.append([pre_x, Numeric(1, "number")])
        else:
            self.val[0].mul(x.val[0])
        return self

    def div(self,x: Num) -> Num:
        """
        Divides this number by x
        :param x: Numeric object
        :return: self
        """
        return self.__truediv__(x)

    def __eq__(self, other):
        if type(other) == Numeric:
            # Simplify this object and the other value
            self.simplify()
            other.simplify()
            # for sym in self.val:
            #     if sym.val != self
            for sym in self.val:
                fnd = False
                for sym_o in other.val:
                    if sym_o.val == sym.val and sym_o.coeff == sym.coeff:
                        fnd = True
                if not fnd:
                    return False
            return True

    def all_syms_eq(self,other):
        """
        Checks all symbols in this numeric object have a corresponding symbol
        in the other numeric object. Just uses the equaltiy operator for symbols.
        Therefore this ignores differing coefficients for example
        :param other: Numeric object
        :return: Boolean
        """
        used_terms = []
        for sym_self in self.val:
            fnd = False
            for i,sym_other in enumerate(other.val):
                if sym_self == sym_other and i not in used_terms:
                    used_terms.append(i)
                    fnd = True
            if not fnd:
                return False
        return True

    def simplify(self):
        """
        Simplifies all symbol objects stored in self.val
        :return: self
        """
        for val in self.val:
            val.simplify()
        return self

    def is_exclusive_numeric(self) -> bool:
        """
        Determines if a numeric object is exclusively numeric, ie doesn't
        contain symbols like 'x'
        :return: Boolean
        """
        for sym in self.val:
            if not sym.is_exclusive_numeric():
                return False
        return True

    def frac_eval(self) -> Frac:
        """
        Attempts to get a floating point representation of this symbol. If this
        is not possible it raises an exception
        :return: float
        """
        logger.warning("Frac eval on {}".format(self))
        ret = Fraction(0,1)
        for sym in self.val:
            x = sym.sym_frac_eval()
            ret += x
        return ret

    def replace(self,x,y):
        """
        Replaces some variable like 'x' with y
        :param x: Thing to be removed
        :param y: Thing to be added inplace of x
        :return: self
        """
        for sym in self.val:
            sym.replace(x,y)
        return self

    def try_replace_numeric_with_var(self, x, y):
        """
        Trys to replace some term (x) in this symbol with another variable. For
        instance we could try and replace the term x^2 in the symbol sin(x^2)
        with a variable u. So sin(x^2) would become sin(u)
        :param x: Numeric object
        :param y: Numeric object
        :return: Another numeric object if it has been successful, otherwise None
        """
        new_val = Numeric(0,"number")
        for sym in self.val:
            new_val += sym.try_replace_numeric_with_var(x, copy.deepcopy(y))
        return new_val

    def get_variables_in(self):
        """
        Makes a set of all the variable names that are in this symbol
        :return: Set
        """
        vars_in = set()
        for sym in self.val:
            vars_in = vars_in.union(sym.get_variables_in())

        return vars_in

    def is_zero(self) -> bool:
        """Checks if this numeric object is equal to zero"""
        for sym in self.val:
            if not sym.is_zero():
                return False
        return True

    def mul_expand(self, x: Num):
        """
        Multiplies this object by another numeric object term by term. So
        (x+1)*(x+2) will be evaluated to x^2+3x+2
        :param x: Numeric object
        :return: Numeric object
        """
        # Initialise object to act as the accumulator
        cur_val = copy.deepcopy(self)
        acc = Numeric(0,"number")
        for sym_cur_val in copy.deepcopy(cur_val.val):
            for sym_mul in x.val:
                logger.debug("{} mul {}".format(sym_cur_val, sym_mul))
                tmp = copy.deepcopy(sym_mul)
                acc.add(Numeric(tmp.mul(sym_cur_val), "sym_obj"))

        # self.val = acc
        return acc

    def has_variable_in(self, x: str) -> bool:
        """
        Checks if this symbol has a term in 'x'. For instance the symbol
        x*y^2 has a term in y
        :param x: String representing some variable
        :return: boolean
        """
        for sym in self.val:
            if sym.has_variable_in(x):
                return True
        return False
