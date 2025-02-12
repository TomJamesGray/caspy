import logging
import copy
import caspy.pattern_match
import caspy.numeric.numeric as num
import caspy.functions.function as funcs
from caspy.numeric.fraction import Frac, Fraction
from caspy.printing.latex_numeric import latex_numeric_str as lns

logger = logging.getLogger(__name__)


class Symbol:
    """Represents a product of symbols and their powers"""

    def __init__(self, val, coeff: Frac):
        # Store value as a list of pair lists, ie
        # [[value1,power1],[value2,power2]] so x^2*y would be
        # [['x',Numeric(2)],['y',Numeric(1)]]
        # The value part can be a string like 'x' or a Numeric object
        # like (1+x)
        if val == 1:
            self.val = [[coeff, 1]]
            # self.coeff = 1
        else:
            self.val = [[val, num.Numeric(1, "number")], [coeff, 1]]
            # self.coeff = 1

    def __mul__(self, other):
        if type(other) == Symbol:
            if self.val == [[1, 1]]:
                logger.debug("current sym val is [[1,1]] so ignore it completely")
                self.val = other.val
            else:
                logger.debug("Multiply {} by {}".format(lns(num.Numeric(self)), lns(num.Numeric(other))))

                for j in range(0, len(other.val)):
                    sym_added = False
                    for i in range(0, len(self.val)):
                        if self.val[i][0] == other.val[j][0] and self.val[i][0] != 1:
                            # Symbols match so increment the powers
                            if type(self.val[i][1]) == num.Numeric:
                                # Check it's numeric type, otherwise items like
                                # 2*2^2 error
                                self.val[i][1] += other.val[j][1]
                            else:
                                # Make it a numeric type then increment it
                                self.val[i][1] = num.Numeric(self.val[i][1], "number")
                                self.val[i][1] += other.val[j][1]

                            sym_added = True
                            # Leave this loop
                            break
                    if not sym_added and other.val[j] != [1, 1]:
                        self.val.append(other.val[j])

            # self.coeff *= other.coeff
            logger.debug("Result of symbol mul {}".format(lns(num.Numeric(self))))
            return self

    def __truediv__(self, other):
        if type(other) == Symbol:
            self * other.recip()
            return self

    def __pow__(self, power):
        """
        Raises this symbol to the power x
        :param power: Numeric object
        :return: self
        """
        if type(power) == num.Numeric:
            logger.debug("{} to the power {}".format(self, power))
            for i in range(0, len(self.val)):
                tmp_pow = copy.deepcopy(power)
                if type(self.val[i][1]) == num.Numeric:
                    self.val[i][1] = self.val[i][1].mul(tmp_pow)
                elif self.val[i][0] != 1:
                    # Check that the first term isn't one. If it is then it's pointless
                    # raising it's power and will only confusing the formatting
                    # of the output
                    self.val[i][1] = tmp_pow.mul(num.Numeric(self.val[i][1], "number"))
            return self

    def mul(self, y):
        return self * y

    def pow(self, x):
        """
        Raises this symbol to the power x
        :param x: Numeric object
        :return: self
        """
        return self ** x

    @property
    def coeff(self) -> Frac:
        index = self.get_coeff_index()
        if index != -1:
            return self.val[index][0]
        # This can occur in some cases like 2^2
        logger.info("No coefficient index found for object {} so treating "
                    "coeff as 1".format(self))
        return Fraction(1, 1)

    def get_coeff_index(self) -> int:
        """
        Finds the index of the coefficient term for this symbol
        :return: -1 if no such term found, otherwise returns the index
        """
        for i in range(0, len(self.val)):
            if type(self.val[i][0]) == Fraction and self.val[i][1] == 1:
                # We have found the index of the coefficient term
                return i
        # Don't return False since 0 == False
        return -1

    def add_coeff(self, x: Frac) -> None:
        logger.debug("Adding coefficient {} to {}".format(x, self))
        coeff_index = self.get_coeff_index()
        if coeff_index != -1:
            # Increment the coefficient by x
            self.val[coeff_index][0] += x
        else:
            logger.info("No coefficient index found for object {}".format(self))
            # Introduce a coefficient term and add x
            self.val.append([Fraction(1, 1) + x, 1])

    def neg(self):
        """Negates this symbol"""
        coeff_index = self.get_coeff_index()
        if coeff_index != -1:
            # Multiply the coefficient index by 1
            self.val[coeff_index][0] *= -1
        else:
            logger.warning("No coefficient index found for object {} so "
                           "adding one as -1".format(self))
            self.val.append([Fraction(-1, 1), 1])

    def recip(self):
        """Makes this symbol the reciprocal of itself"""
        for i in range(0, len(self.val)):
            if type(self.val[i][1]) == num.Numeric:
                self.val[i][1] = self.val[i][1].neg()
            else:
                self.val[i][1] = - self.val[i][1]
        # self.coeff = self.coeff.recip()
        return self

    def __repr__(self):
        return "<Symbol {}>".format(self.val)

    def len_no_coeff(self) -> int:
        l = 0
        for (sym_name, pow) in self.val:
            if type(sym_name) == Fraction and pow == 1:
                continue
            elif isinstance(sym_name, caspy.pattern_match.ConstPlaceholder):
                continue
            else:
                l += 1
        return l

    def __eq__(self, other):
        """
        Defines equality for the symbol class. The order of the terms
        in the value property doesn't matter. Ignores the coefficient
        property
        """
        # Simplify this object and the other value
        if type(other) == Symbol:
            self.simplify()
            other.simplify()
            # logger.critical("CHECKING {} == {}".format(self,other))

            if self.is_exclusive_numeric() and other.is_exclusive_numeric():
                return True
            for (sym_name, pow) in self.val:
                eq = False
                # Ignoring the coefficient 'property'
                if type(sym_name) == Fraction and pow == 1:
                    # logger.warning("IGNORING COEFF PROPERTY {} {}".format(sym_name,pow))
                    continue
                if isinstance(sym_name, caspy.pattern_match.PlaceholderVal):
                    # logger.warning("IGNORING PLACEHOLDER VAL {} {}".format(sym_name, pow))
                    continue
                for (sym_name_o,pow_o) in other.val:
                    if sym_name == sym_name_o and pow == pow_o:
                        eq = True
                        # logger.warning("FOUND TERM {} {}".format(sym_name,pow_o))
                        break

                if not eq:
                    return False

            logger.debug("Length no coeffs self {} and other {}".format(
                self.len_no_coeff(), other.len_no_coeff()))
            return True and self.len_no_coeff() == other.len_no_coeff()
        else:
            return False

    def simplify(self, simp_pows=True):
        """
        Simplifies this symbol by looking for the simple numeric aspects eg
        [2,1] and [4,-1] in the value class represents 2 * 4^(-1) which can
        be simplified to 1/2
        :return: none
        """
        # logger.debug("Simplifying symbol {}".format(self))
        if self.is_zero():
            logger.debug("Value is zero so remove all other parts")
            self.val = [[Fraction(0, 1), 1]]
            return
        acc = Fraction(1, 1)
        to_remove = []
        for i in range(0, len(self.val)):
            # Deal with the case when the power is zero
            # By removing it we get rid of terms like x^0
            if type(self.val[i][1]) == num.Numeric:
                if type(self.val[i][0]) == Fraction and \
                        self.val[i][1].is_exclusive_numeric() and simp_pows:
                    try:
                        pow_val = self.val[i][1].frac_eval()
                        if int(pow_val.to_real()) != pow_val.to_real():
                            continue
                        new_val = copy.deepcopy(self.val[i][0]) ** int(pow_val.to_real())
                        # if new_val.is_int_frac():
                        acc *= new_val
                        to_remove.append(i)
                    except ValueError:
                        pass

                if self.val[i][1].is_zero():
                    to_remove.append(i)
                    continue
            elif isinstance(self.val[i][0], funcs.Function):
                self.val[i][0].simplify()
                continue
            # Deal with numeric 'coefficient terms'
            if type(self.val[i][0]) == Fraction and self.val[i][1] == 1:
                # Multiply accumulator by this fraction
                acc *= self.val[i][0]
                to_remove.append(i)
            elif type(self.val[i][0]) == Fraction and self.val[i][1] == -1:
                # Multiply accumulator by reciprocal of this fraction
                acc *= self.val[i][0].recip()
                to_remove.append(i)

        if to_remove == []:
            return
        # Remove the indexes that have been factored into the acc
        new_val = []
        for (j, sym_part) in enumerate(self.val):
            if j not in to_remove:
                new_val.append(sym_part)

        self.val = new_val + [[acc, 1]]

    def is_exclusive_numeric(self) -> bool:
        """
        Determines if a numeric object is exclusively numeric, ie doesn't
        contain symbols like 'x'
        :return: Boolean
        """
        for (sym_name, sym_pow) in self.val:
            if type(sym_name) == Fraction:
                if type(sym_pow) == num.Numeric:
                    if not sym_pow.is_exclusive_numeric():
                        return False
            elif isinstance(sym_name, funcs.Function):
                if type(sym_name.arg) == num.Numeric:
                    if not sym_name.arg.is_exclusive_numeric():
                        return False
                if type(sym_pow) == num.Numeric:
                    if not sym_pow.is_exclusive_numeric():
                        return False
            elif not (isinstance(sym_name, caspy.pattern_match.ConstPlaceholder)
                      or isinstance(sym_name, caspy.pattern_match.ConstPlaceHolderNonZero)):
                # Not a constant value placeholder
                return False
            else:
                return False
        return True

    def sym_frac_eval(self) -> Frac:
        """
        Attempts to get a floating point representation of this symbol. If this
        is not possible it raises an exception
        :return: Fraction
        """
        ret = Fraction(1, 1)
        for (sym_name, sym_pow) in self.val:
            if type(sym_pow) == num.Numeric:
                sym_pow_frac = sym_pow.frac_eval()
            elif type(sym_pow) == Fraction:
                sym_pow_frac = sym_pow
            elif type(sym_pow) in (int,float):
                sym_pow_frac = sym_pow
            else:
                raise Exception("Can't get fraction representation of {}".format(sym_pow))

            if type(sym_name) == Fraction:
                ret *= sym_name ** sym_pow_frac
            elif isinstance(sym_name, funcs.Function):
                if sym_name.fname != "re":
                    ret *= sym_name.to_frac() ** sym_pow_frac
                else:
                    continue
            else:
                raise Exception("Can't get fraction representation of {}".format(self))

        return ret

    def replace(self, x, y):
        """
        Replaces some variable like 'x' with y
        :param x: Thing to be removed
        :param y: Thing to be added inplace of x
        :return: self
        """
        for i in range(0, len(self.val)):
            if self.val[i][0] == x:
                self.val[i][0] = y
            if type(self.val[i][1]) == num.Numeric:
                self.val[i][1] = self.val[i][1].replace(x, y)
            if isinstance(self.val[i][0],funcs.Function):
                self.val[i][0].arg = self.val[i][0].arg.replace(x, y)

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
        MAX_DIVS = 10
        MAX_MULTS = 10
        vars_to_remove = x.get_variables_in()
        sym_args_done = copy.deepcopy(self)
        for (sym_fact_name, sym_fact_pow) in sym_args_done.val:
            if isinstance(sym_fact_name,funcs.Function):
                # deal with the function argument
                result = sym_fact_name.arg.try_replace_numeric_with_var(x, copy.deepcopy(y))
                if result is not None:
                    sym_fact_name.arg = result

        if sym_args_done.get_variables_in().intersection(vars_to_remove) == set():
            # Don't need to try multiplication or division on this as it is
            # already done
            return caspy.numeric.numeric.Numeric(sym_args_done,"sym_obj")

        sym_try_divs = copy.deepcopy(sym_args_done)
        # Try repeated division to remove the numeric object in question
        new_sym_num = caspy.numeric.numeric.Numeric(sym_try_divs,"sym_obj")
        for i in range(1,MAX_DIVS):
            new_sym_num / copy.deepcopy(x)
            new_sym_num.simplify()
            logger.info("New sym num {} vars {} x {}".format(new_sym_num,new_sym_num.get_variables_in(),x))
            if new_sym_num.get_variables_in().intersection(vars_to_remove) == set():
                power = caspy.numeric.numeric.Numeric(i,"number")
                new_sym_num * (copy.deepcopy(y) ** power)
                return new_sym_num

        # Try repeated multiplication to remove the numeric object
        sym_try_mults = copy.deepcopy(sym_args_done)
        new_sym_num = caspy.numeric.numeric.Numeric(sym_try_mults, "sym_obj")
        for i in range(1,MAX_MULTS):
            new_sym_num * copy.deepcopy(x)
            new_sym_num.simplify()
            logger.info("New sym num {} vars {} x {}".format(new_sym_num,new_sym_num.get_variables_in(),x))
            if new_sym_num.get_variables_in().intersection(vars_to_remove) == set():
                power = caspy.numeric.numeric.Numeric(i,"number")
                new_sym_num / (copy.deepcopy(y) ** power)
                return new_sym_num

        # Haven't been able to replace the numeric with the variable
        return None

    def get_variables_in(self):
        """
        Makes a set of all the variable names that are in this symbol
        :return: Set
        """
        vars_in = set()
        for (sym_fact_name,sym_fact_pow) in self.val:
            if type(sym_fact_name) == str:
                vars_in.add(sym_fact_name)
            elif type(sym_fact_name) == caspy.numeric.numeric.Numeric:
                vars_in = vars_in.union(sym_fact_name.get_variables_in())
            elif isinstance(sym_fact_name, funcs.Function):
                vars_in = vars_in.union(sym_fact_name.arg.get_variables_in())

            if type(sym_fact_pow) == caspy.numeric.numeric.Numeric:
                vars_in = vars_in.union(sym_fact_pow.get_variables_in())

        return vars_in

    def contains_sym(self, x) -> bool:
        """
        Checks if this symbol contains another. Ignoring coefficients
        For instance x*y would contain x
        :param x: Symbol object
        :return: Boolean
        """
        i = 0
        if x.is_exclusive_numeric():
            return False
        for (sym_name_x, sym_pow_x) in x.val:
            fnd = False
            if i == x.get_coeff_index():
                # Skip coefficient
                continue
            i += 1
            for (sym_name, sym_pow) in self.val:
                if sym_name_x == sym_name and sym_pow_x == sym_pow:
                    fnd = True
                    break
            if not fnd:
                return False

        return True

    def has_variable_in(self, x: str) -> bool:
        """
        Checks if this symbol has a term in 'x'. For instance the symbol
        x*y^2 has a term in y
        :param x: String representing some variable
        :return: boolean
        """
        for (sym_name,sym_pow) in self.val:
            if sym_name == x:
                return True
            if type(sym_name) == num.Numeric:
                if sym_name.has_variable_in(x):
                    return True
            if type(sym_pow) == num.Numeric:
                if sym_pow.has_variable_in(x):
                    return True
            if isinstance(sym_name,funcs.Function):
                if sym_name.arg.has_variable_in(x):
                    return True
        return False

    def is_zero(self) -> bool:
        """Checks if this symbol is equal to zero"""
        for (sym_name, sym_pow) in self.val:
            if sym_name == 0:
                return True
