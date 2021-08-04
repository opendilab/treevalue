import colorsys
import random
import re
from typing import Optional, Union

from .func import post_process, raising


class GetSetProxy:
    def __init__(self, getter, setter=None):
        self.__getter = getter
        self.__setter = setter or raising(lambda x: NotImplementedError)

    def set(self, value):
        return self.__setter(value)

    def get(self):
        return self.__getter()


class RGBColorProxy:
    def __init__(self, r: GetSetProxy, g: GetSetProxy, b: GetSetProxy):
        self.__rp = r
        self.__gp = g
        self.__bp = b

    @property
    def red(self) -> float:
        return self.__rp.get()

    @red.setter
    def red(self, new: float):
        self.__rp.set(new)

    @property
    def green(self) -> float:
        return self.__gp.get()

    @green.setter
    def green(self, new: float):
        self.__gp.set(new)

    @property
    def blue(self) -> float:
        return self.__bp.get()

    @blue.setter
    def blue(self, new: float):
        self.__bp.set(new)

    def __iter__(self):
        yield self.red
        yield self.green
        yield self.blue

    def __repr__(self):
        return '<{cls} red: {red}, green: {green}, blue: {blue}>'.format(
            cls=self.__class__.__name__,
            red='%.3f' % (self.red,),
            green='%.3f' % (self.green,),
            blue='%.3f' % (self.blue,),
        )


class HSVColorProxy:
    def __init__(self, h: GetSetProxy, s: GetSetProxy, v: GetSetProxy):
        self.__hp = h
        self.__sp = s
        self.__vp = v

    @property
    def hue(self) -> float:
        return self.__hp.get()

    @hue.setter
    def hue(self, new: float):
        self.__hp.set(new)

    @property
    def saturation(self) -> float:
        return self.__sp.get()

    @saturation.setter
    def saturation(self, new: float):
        self.__sp.set(new)

    @property
    def value(self) -> float:
        return self.__vp.get()

    @value.setter
    def value(self, new: float):
        self.__vp.set(new)

    def __iter__(self):
        yield self.hue
        yield self.saturation
        yield self.value

    def __repr__(self):
        return '<{cls} hue: {hue}, saturation: {saturation}, value: {value}>'.format(
            cls=self.__class__.__name__,
            hue='%.3f' % (self.hue,),
            saturation='%.3f' % (self.saturation,),
            value='%.3f' % (self.value,),
        )


_ratio_to_255 = lambda x: int(round(x * 255))
_ratio_to_hex = post_process(lambda x: '%02x' % (x,))(_ratio_to_255)
_hex_to_255 = lambda x: int(x, base=16) if x is not None else None
_hex_to_ratio = post_process(lambda x: x / 255.0 if x is not None else None)(_hex_to_255)

_RGB_COLOR_PATTERN = re.compile(r'^#?([a-zA-Z\d]{2})([a-zA-Z\d]{2})([a-zA-Z\d]{2})([a-zA-Z\d]{2}|)$')


class Color:
    def __init__(self, c, alpha: float = None):
        if isinstance(c, tuple):
            self.__r, self.__g, self.__b = c
            self.__alpha = alpha
        elif isinstance(c, str):
            _finding = _RGB_COLOR_PATTERN.findall(c)
            if _finding:
                _first = _finding[0]
                rs, gs, bs, as_ = _first
                as_ = None if not as_ else as_

                r, g, b, a = map(_hex_to_ratio, (rs, gs, bs, as_))
                if alpha is not None:
                    a = a * alpha if a is not None else alpha

                self.__init__((r, g, b), a)
            else:
                raise ValueError("Invalid string color, matching of pattern {pattern} "
                                 "expected but {actual} found.".format(pattern=repr(_RGB_COLOR_PATTERN.pattern),
                                                                       actual=repr(c), ))
        else:
            raise TypeError('Unknown color value - {c}.'.format(c=repr(c)))

    def __set_r(self, new):
        self.__r = new

    def __set_g(self, new):
        self.__g = new

    def __set_b(self, new):
        self.__b = new

    @property
    def rgb(self) -> RGBColorProxy:
        return RGBColorProxy(
            GetSetProxy(lambda: self.__r, self.__set_r),
            GetSetProxy(lambda: self.__g, self.__set_g),
            GetSetProxy(lambda: self.__b, self.__set_b),
        )

    def __get_hsv(self):
        return colorsys.rgb_to_hsv(self.__r, self.__g, self.__b)

    def __set_hsv(self, h=None, s=None, v=None):
        ch, cs, cv = self.__get_hsv()
        self.__r, self.__g, self.__b = colorsys.hsv_to_rgb(h or ch, s or cs, v or cv)

    @property
    def hsv(self) -> HSVColorProxy:
        return HSVColorProxy(
            GetSetProxy(
                post_process(lambda x: x[0])(self.__get_hsv),
                lambda x: self.__set_hsv(h=x),
            ),
            GetSetProxy(
                post_process(lambda x: x[1])(self.__get_hsv),
                lambda x: self.__set_hsv(s=x),
            ),
            GetSetProxy(
                post_process(lambda x: x[2])(self.__get_hsv),
                lambda x: self.__set_hsv(v=x),
            ),
        )

    @property
    def alpha(self) -> Optional[float]:
        return self.__alpha if self.__alpha is not None else 1.0

    @alpha.setter
    def alpha(self, new: Optional[float]):
        self.__alpha = new

    def __repr__(self):
        if self.__alpha is not None:
            return '<{cls} r: {r}, g: {g}, b: {b}, a: {a}>'.format(
                cls=self.__class__.__name__,
                r='%.3f' % (self.__r,),
                g='%.3f' % (self.__g,),
                b='%.3f' % (self.__b,),
                a='%.3f' % (self.__alpha,),
            )
        else:
            return '<{cls} r: {r}, g: {g}, b: {b}>'.format(
                cls=self.__class__.__name__,
                r='%.3f' % (self.__r,),
                g='%.3f' % (self.__g,),
                b='%.3f' % (self.__b,),
            )

    def __str__(self):
        rs, gs, bs = _ratio_to_hex(self.__r), _ratio_to_hex(self.__g), _ratio_to_hex(self.__b)
        as_ = _ratio_to_hex(self.__alpha) if self.__alpha is not None else ''

        return '#' + rs + gs + bs + as_

    @classmethod
    def random(cls, rnd=None, alpha: Union[bool, None, int, float] = None):
        rnd = rnd or random
        r, g, b = rnd.random(), rnd.random(), rnd.random()
        if isinstance(alpha, (float, int)):
            a = alpha
        else:
            a = rnd.random() if alpha else None
        return cls((r, g, b), a)

    @classmethod
    def from_hsv(cls, h, s, v, alpha=None):
        return cls(colorsys.hsv_to_rgb(h, s, v), alpha)
