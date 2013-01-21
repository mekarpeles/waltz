#!/usr/bin/env python

"""
   ballroom.treasury
   ~~~~~~~~~~~~~~~~~

   The treasury contains several modules which, when joined, provide shopping cart function.

   Product:
   A Product is a generic interface which one may extend or inherit in order to
   represent a physical or digital e-commerce product.

   Item:
   A wrapper which encapsulates and functions upon the base Product
   class's attributes in order to interface as a unit of the Cart object.
   Items can be bound to a coupon which may modify or adjust the total
   item price according to the Item.qty (quantity), as well as the 
   specifications of the coupon.

   Cart:
   A shopping Cart is a collection of Items.

       Coupon Calculation:
       The cart has a property() called 'total' which caclulate the
       cart total, with coupons applied, in realtime. First, the
       procedure iterates over each Item within the cart and invoke
       the Item's total property (thus getting the adjusted price for
       the Item, according to the item qty and coupons). After the
       subtotal has been calculated for all Items, any cart level
       coupons are then applied to this subtotal in order to yield the
       final total. Taxes, fees, and commissions are applies at this
       point.

   Coupon:
   Coupons can be applied at both the Cart and the Item level. If
   applied at the Cart level, the coupon will have the effect of a
   value or percentage off of the entire Cart.value. If a Coupon is
   applied to an Item, a 'limit' parameter may be specified as a
   modifier to limit the max number of applications the Coupon can be
   applied to an Item's products (e.g. given an Item having quantity
   5, (i.e. Item.qty == 5) bound to a Coupon having a limit=3 may/can
   only adjust (apply to) 3 of the 5 instances of the Product this
   Item represents.

"""

__author__  = ["Michael E. Karpeles", "Stephen Balaban"]
__email__   = ["michael.karpeles@gmail.com", "mail@stephenbalaban.com"]
__version__ = "0.0.3"

from decimal import Decimal 
from utils import Storage

class Coupon(object):
    def __init__(self, cid, code, percent_off=0, value_off="0.00", pids=None, limit=1):
        """
        params:
            value_off - either a string or a Decimal dollar value with precision of 2 digits
            pids - a list of product ids for which the coupon applies.
                   The default action is for the coupon to apply to the entire 
                   cart / purchase.
            limit - the number of times this coupon should be applied to a product
        """
        self.id = cid # database identifier of the coupon
        self.pids = pids
        self.code = code # coupon code which the user supplies
        self.percent_off = percent_off
        self.value_off = Decimal(value_off)
        self.applications = limit

    @classmethod
    def apply(cls, coupon, price):
        """Applies a coupon to a single unit of an item (an item can
        have a qty > 1) and returns the adjusted price for that
        unit. In terms of order of operations, first subtracts any
        monetary value off discount and then afterwards applies the
        percentage off (if any specified in coupon) to the updated
        subtotal
        """
        if not coupon:
            return price
        dprice = Decimal(.01 * (100.0 - coupon.percent_off)) * (price - coupon.value_off)
        qdprice = (dprice).quantize(Decimal('.01'), rounding='ROUND_DOWN')
        if qdprice <= 0:
            return Decimal('0.00')

class Product(object):
    """Necessary scaffolding for a Product in order to interface with
    the Cart. Feel free to extend this object to fit your needs

    params:
        upc (optional) - Standard UPC-A (see encoding - http://en.wikipedia.org/wiki/Universal_Product_Code#Encoding)
    """
    def __init__(self, pid, label, desc="", price="9.99", currency="USD", phash=None, upc=None):
        self.id = pid
        self.name = label
        self.description = desc
        self.price = Decimal(price)
        self.hash = phash # still needs to be standardized (perhaps see web.py utils for hash ideas)
        self.upc = upc

class Item(object):
    """
    usage:
        >>> p = Product(1, 'shoes', desc='new pair of shoes',
        ...             price='13.37', phash='d81hda8z')
        >>> item = Item(product=p)
        >>> item.total
        '13.37'
    """
    def _verify(self, product=None, qty=1, coupon=None, **kwags):
        """Throws an exception if any of the parameters fail to pass
        verification. A failure may be the result of several
        occurrences, including unexpected types, undesired value
        ranges, signs (i.e. signed versus unsigned), etc.
        """
        #note refid is a user's id and default, -1, is nobody
        if product and not isinstance(product, Product):
            raise TypeError('product argument must inherit from the ' \
                                'Product class.')
        if coupon and not isinstance(coupon, Coupon):
            raise TypeError("Coupon was expected, instead encountered:" \
                                "<type: '%s'>" % type(coupon))
        if type(qty) is not int:
            qty = 1

    def __init__(self, product=None, qty=1, coupon=None, ref=None):
        """
        params:
            product - an instance of an object which subclasses Product
            ref - referral id, for affiliates or referrers
        """
        # need to direclty set to avoid infinite loop
        self._verify(product, qty, coupon)
        object.__setattr__(self, 'qty', qty)
        object.__setattr__(self, 'price', Decimal('0.00'))

        if not ref:
            ref = self.get_empty_ref()
        self.product = product
        self.coupon = coupon
        self.id = product.id
        self.qty = qty
        self.price = getattr(self.product, "price")
        self.currency = getattr(self.product, "currency", "USD")
        self.ref = ref

    def __repr__(self):
        result = "<Item id: "+ str(self.id) + ", total: " + str(self.total) \
                + ", qty: " + str(self.qty) \
                + ", price: " + str(self.price) \
                + ", currency: " + str(self.currency) \
                + ", ref: " + str(self.ref) \
                + ", coupon: " + str(self.coupon) \
                + ", products: " + str(self.product) + " >"
        return unicode(result)

    def __setattr__(self, name, value):
        kwarg = {name: value}
        self._verify(**kwarg)
        object.__setattr__(self, name, value)

    @property
    def total(self):
        ttl = Decimal('0.00')
        applications = self.coupon.applications if self.coupon else 0
        if applications >= self.qty:            
            return Coupon.apply(self.coupon, self.price) * self.qty
        return (Coupon.apply(self.coupon, self.price) * applications) + \
               (self.price * (self.qty - applications))
                
    @classmethod
    def get_empty_ref(self):
        """
        returns an empty ref, free to use!

        >>> Item.get_empty_bag()
        """
        default_refid = -1
        empty_ref = Storage({'id': default_refid,
                             'username': None,
                             'time': None,
                             'uri': None,
                             'tag': None })
        return empty_ref

class Cart(object):
    """
    main atributes:
        total       - total value of cart denominated in cart.currency
        qty         - total number of items in cart
        currency    - cart currency symbol-code tuple ("$", "USD")
        taxrate     - current taxrate of cart (regional basis)
        itemsdict   - list containing current items
    main methods: 
        add(product)
        remove(pid)
        empty()
    usage:
        >>> cart = Cart(itemsdict=[], 
        >>>           taxrate=0, 
        >>>           currency=('$','USD'))
        >>> cart.add(product) # adds a product object to the bar + recalculates
        >>> cart.empty()  # empties cart, resets totals
        >>> cart.total # returns the total cost of all items in cart + tax
        >>> cart.qty # recalculates and returns qty of items in cart
        >>> cart.itemsdict[pid] #returns item object <Item qty: 1, total: blah, product...
        >>> cart.__dict__ # dict representation
        >>> cart.get(product_object) # blah
    
    """
    def _verify(self):
        pass

    def __init__(self, taxrate=Decimal('0.00'), currency=("$", "USD"),
                 qty=0, total=Decimal('0.00'), coupon=None):
        if taxrate > Decimal('1.00') or taxrate < Decimal('0.00'):
            raise ValueError('taxrate is a decimal between 0.00 and 1.00')
        self.taxrate = taxrate
        self.currency = currency
        self.itemsdict = {}
        self.coupon = coupon

    def __repr__(self):
        result = '<Cart total: ' + str(self.total) \
                + ', currency: ' + str(self.currency) \
                + ', itemsdict: ' + str(map(self._repr_wrap, self.itemsdict.keys())) \
                + ', qty: ' + str(self.qty) \
                + ', taxrate: ' + str(self.taxrate) \
                + ', coupon: ' + (str(self.coupon.id) if getattr(self, 'coupon', None) else 'None') \
                + ', pythonid: ' + str(id(self)) + '>'
        return unicode(result)

    def _repr_wrap(self, thing):
        return "<Item " + str(thing) + ">"
    
    def __setattr__(self, name, value):
        """
        controls attribute settings
        """
        if name == 'qty':
            try:
                value = int(value)
            except ValueError as details: 
                raise ValueError("please provide an int for qty")
            if value < 0:
                raise ValueError("qty cannot be less than zero")

        object.__setattr__(self, name, value)

    @property
    def currency_code(self):
        """returns currency code
            >>> cart.currency_code
            "USD"
        """
        return self.currency[1]

    @property
    def currency_symbol(self):
        """returns currency symbol
            >>> cart.currency_symbol
            "$"
        """
        return self.currency[0]

    def add(self, product=None, qty=1, ref=None):
        """ 
        adds product object, sets quantity and refid to cart

        plain vanilla product add
            >>> cart.add(product) 

        add with kwargs:
            >>> cart.add(product=product, qty=3, ref=<Storage ...>)

        """
        if not product: return self
        if self.itemsdict.has_key(product.id):
            #if item exists, increment
            self.itemsdict[product.id].qty += qty

        else:
            item = Item(product=product, qty=qty, ref=ref)
            self.itemsdict[item.id] = item
        self.invariants()
        return self

    @property
    def total(self):
        """Dynamically calculates an up-to-date total in a piecewise
        fashion by traversing each each item in the cart and
        dynamically calculating the totals of each of the cart's
        items. C"""
        subtotal = sum([item.total for k, item in self.itemsdict.items()])
        return Coupon.apply(self.coupon, subtotal)

    @property
    def qty(self):
        """Returns the number of unique items within the cart ignoring the
        quantity of the items, itself.

        XXX Make sure len is working correctly over list of tuples
        returned by itemsdict.items()
        """
        return sum([item.qty for k, item in self.itemsdict.items()])

    def remove(self, pid, amt=None):
        """removes ALL of an item from cart based on product id 

        >>> #using id
        >>> cart.remove(2) #pid = 2, an item in cart
        2
        >>> cart.remove(2) # an item no longer in cart raises KeyError
        Traceback (most recent call last):
            File "<stdin>", line 1, in <module>
            File "cart/cart.py", line 149, in remove
                raise KeyError('no item found')
            KeyError: 'no item found'

        Note: if you only want to remove some of the items in the cart,
        use the cart.set(id, qty) method instead.
        """
        if type(pid) is not (long or int):
            raise TypeError("Product ID must be an int or long; " \
                                "Instead received value: %s of " \
                                "type %s" % (pid, type(pid)))
        if not self.itemsdict.has_key(pid):
            raise KeyError('no item found')
        else:
            del self.itemsdict[pid]
        self.invariants()
        return self

    def get(self, pid=None, slug=None):
        """
        gets an Item based on product_id
            >>> cart.get(pid) #pid = 2 (an item not in cart)
            Traceback (most recent call last):
                File "<stdin>", line 1, in <module>
                File "cart/cart.py", line 171, in get
                    return self.itemsdict[key]
                KeyError: 2
            >>> cart.get(2) #an item in cart
            <Item id: 2, total: ... >
        """
        pid = long(pid)
        key = -1
        if pid == None and slug == None:
            raise ValueError("please supply an pid or slug")
        if pid == None:
            # slug search O(n)
            for k,v in self.itemsdict.items():
                if v.product.name == slug:
                    key = k
        else:
            # pid O(1)
            key = pid
        return self.itemsdict[key]

    def contains(self, pid=None):
        """
        returns boolean if itemsdict contains product id (pid)

        consider:
           extend this function s.t. you provide a key and a value to
           search for.

        usage:
            >>> cart.add(product) # product.id = 3, product.slug = "Slug Text"
            >>> cart.contains(3)
            True
        """
        if pid:
            raise ValueError("please supply an pid or slug")
        return self.itemsdict.has_key(pid)

    @property
    def tax(self):
        return Decimal(self.total * self.taxrate).quantize(Decimal('.01'), rounding='ROUND_DOWN')

    def invariants(self):
        """tests cart invariants -- TODO"""
        pass

    def empty(self):
        """
        empties this cart, keeps taxrate, currency, returns copy
            >>> cart.empty()
            <Cart total: 0.00, currency: ('$', 'USD'), qty: 0, itemsdict: {},
            taxrate: 0.00, coupon: None>
        """
        return self.nullify()

    def nullify(self):
        """
        Purges all new carts directly after being issued to a session
        """
        self.coupon = None
        self.itemsdict = {} 
    
    def make_receipt(self):
        """ 
        Return a string detailing all of the items in the cart
        and their costs to be used as a receipt.
        """
        desc = ""
        for index, item in enumerate(self.itemsdict):
            if index == 0:
                desc = "item #%s - %s - $%s" % (self.itemsdict[item].product.hash,
                                                self.itemsdict[item].product.name,
                                                self.itemsdict[item].price)
            else:
                desc = "%s, item #%s - %s - $%s" % (desc, self.itemsdict[item].product.hash,
                                                    self.itemsdict[item].product.name,
                                                    self.itemsdict[item].price)
        return desc

