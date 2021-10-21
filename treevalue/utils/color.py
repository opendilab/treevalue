import colorsys
import math
import re
from typing import Optional, Union, Tuple

from hbutils.reflection import post_process, raising, freduce, dynamic_call, warning_


def _round_mapper(min_: float, max_: float):
    min_, max_ = min(min_, max_), max(min_, max_)
    round_ = max_ - min_

    def _func(v):
        if v < min_:
            v += math.ceil((min_ - v) / round_) * round_
        if v > max_:
            v -= math.ceil((v - max_) / round_) * round_

        return v

    return _func


def _range_mapper(min_: Optional[float], max_: Optional[float], warning=None):
    if min_ is not None and max_ is not None:
        min_, max_ = min(min_, max_), max(min_, max_)
    warning = dynamic_call(warning_(warning if warning is not None else lambda: None))

    def _func(v):
        if max_ is not None and v > max_:
            warning(v, min_, max_)
            return max_
        elif min_ is not None and v < min_:
            warning(v, min_, max_)
            return min_
        else:
            return v

    return _func


class GetSetProxy:
    def __init__(self, getter, setter=None):
        self.__getter = getter
        self.__setter = setter or raising(lambda x: NotImplementedError)

    def set(self, value):
        return self.__setter(value)

    def get(self):
        return self.__getter()


_r_mapper = _range_mapper(0.0, 1.0, lambda v, min_, max_: Warning(
    'Red value should be no less than %.3d and no more than %.3d, but %.3d found.' % (min_, max_, v)))
_g_mapper = _range_mapper(0.0, 1.0, lambda v, min_, max_: Warning(
    'Green value should be no less than %.3d and no more than %.3d, but %.3d found.' % (min_, max_, v)))
_b_mapper = _range_mapper(0.0, 1.0, lambda v, min_, max_: Warning(
    'Blue value should be no less than %.3d and no more than %.3d, but %.3d found.' % (min_, max_, v)))
_a_mapper = _range_mapper(0.0, 1.0, lambda v, min_, max_: Warning(
    'Alpha value should be no less than %.3d and no more than %.3d, but %.3d found.' % (min_, max_, v)))


class RGBColorProxy:
    def __init__(self, this: 'Color', r: GetSetProxy, g: GetSetProxy, b: GetSetProxy):
        self.__this = this
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


_hsv_h_mapper = _round_mapper(0.0, 1.0)
_hsv_s_mapper = _range_mapper(0.0, 1.0, lambda v, min_, max_: Warning(
    'Saturation value should be no less than %.3d and no more than %.3d, but %.3d found.' % (min_, max_, v)))
_hsv_v_mapper = _range_mapper(0.0, 1.0, lambda v, min_, max_: Warning(
    'Brightness(value) value should be no less than %.3d and no more than %.3d, but %.3d found.' % (min_, max_, v)))


class HSVColorProxy:
    def __init__(self, this: 'Color', h: GetSetProxy, s: GetSetProxy, v: GetSetProxy):
        this.__this = this
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


_hls_h_mapper = _round_mapper(0.0, 1.0)
_hls_l_mapper = _range_mapper(0.0, 1.0, lambda v, min_, max_: Warning(
    'Lightness value should be no less than %.3d and no more than %.3d, but %.3d found.' % (min_, max_, v)))
_hls_s_mapper = _range_mapper(0.0, 1.0, lambda v, min_, max_: Warning(
    'Saturation value should be no less than %.3d and no more than %.3d, but %.3d found.' % (min_, max_, v)))


class HLSColorProxy:
    def __init__(self, this: 'Color', h: GetSetProxy, l: GetSetProxy, s: GetSetProxy):
        this.__this = this
        self.__hp = h
        self.__lp = l
        self.__sp = s

    @property
    def hue(self) -> float:
        return self.__hp.get()

    @hue.setter
    def hue(self, new: float):
        self.__hp.set(new)

    @property
    def lightness(self) -> float:
        return self.__lp.get()

    @lightness.setter
    def lightness(self, new: float):
        self.__lp.set(new)

    @property
    def saturation(self) -> float:
        return self.__sp.get()

    @saturation.setter
    def saturation(self, new: float):
        self.__sp.set(new)

    def __iter__(self):
        yield self.hue
        yield self.lightness
        yield self.saturation

    def __repr__(self):
        return '<{cls} hue: {hue}, lightness: {lightness}, saturation: {saturation}>'.format(
            cls=self.__class__.__name__,
            hue='%.3f' % (self.hue,),
            lightness='%.3f' % (self.lightness,),
            saturation='%.3f' % (self.saturation,),
        )


_ratio_to_255 = lambda x: int(round(x * 255))
_ratio_to_hex = post_process(lambda x: '%02x' % (x,))(_ratio_to_255)
_hex_to_255 = lambda x: int(x, base=16) if x is not None else None
_hex_to_ratio = post_process(lambda x: x / 255.0 if x is not None else None)(_hex_to_255)

_RGB_COLOR_PATTERN = re.compile(r'^#?([a-zA-Z\d]{2})([a-zA-Z\d]{2})([a-zA-Z\d]{2})([a-zA-Z\d]{2}|)$')


@freduce(init=None)
def _ratio_or(a, b):
    return b if a is None else a


class Color:
    """
    Overview:
        Color utility object.
    """

    def __init__(self, c: Union[str, Tuple[float, float, float]], alpha: Optional[float] = None):
        """
        Overview:
            Constructor of ``Color``.

        Arguments:
            - c (:obj:`Union[str, Tuple[float, float, float]]`): Color value, can be hex string value \
                or tuple rgb value.
            - alpha: (:obj:`Optional[float]`): Alpha value of color, \
                default is `None` which means no alpha value.
        """
        if isinstance(c, tuple):
            self.__r, self.__g, self.__b = _r_mapper(c[0]), _g_mapper(c[1]), _b_mapper(c[2])
            self.__alpha = _a_mapper(alpha) if alpha is not None else None
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

    @property
    def alpha(self) -> Optional[float]:
        """
        Overview:
            Get value of alpha.

        Returns:
            - alpha (:obj:`Optional[float]`): Alpha value.
        """
        return self.__alpha

    @alpha.setter
    def alpha(self, new: Optional[float]):
        """
        Overview:
            Set value of alpha.

        Arguments:
            - new (:obj:`Optional[float]`): New value of alpha.
        """
        if new is not None:
            new = _a_mapper(new)
        self.__alpha = new

    def __get_rgb(self):
        return self.__r, self.__g, self.__b

    def __set_rgb(self, r=None, g=None, b=None):
        self.__r, self.__g, self.__b = map(lambda args: _ratio_or(*args), zip((r, g, b), self.__get_rgb()))

    @property
    def rgb(self) -> RGBColorProxy:
        """
        Overview:
            Get rgb color system based color proxy.

        Returns:
            - proxy (:obj:`RGBColorProxy`): Rgb color proxy.
        """
        return RGBColorProxy(
            self,
            GetSetProxy(
                lambda: self.__r,
                lambda x: self.__set_rgb(r=_r_mapper(x)),
            ),
            GetSetProxy(
                lambda: self.__g,
                lambda x: self.__set_rgb(g=_g_mapper(x)),
            ),
            GetSetProxy(
                lambda: self.__b,
                lambda x: self.__set_rgb(b=_b_mapper(x)),
            ),
        )

    def __get_hsv(self):
        return colorsys.rgb_to_hsv(self.__r, self.__g, self.__b)

    def __set_hsv(self, h=None, s=None, v=None):
        h, s, v = map(lambda args: _ratio_or(*args), zip((h, s, v), self.__get_hsv()))
        self.__r, self.__g, self.__b = colorsys.hsv_to_rgb(h, s, v)

    @property
    def hsv(self) -> HSVColorProxy:
        """
        Overview:
            Get hsv color system based color proxy.

        Returns:
            - proxy (:obj:`HSVColorProxy`): Hsv color proxy.
        """
        return HSVColorProxy(
            self,
            GetSetProxy(
                lambda: self.__get_hsv()[0],
                lambda x: self.__set_hsv(h=_hsv_h_mapper(x)),
            ),
            GetSetProxy(
                lambda: self.__get_hsv()[1],
                lambda x: self.__set_hsv(s=_hsv_s_mapper(x)),
            ),
            GetSetProxy(
                lambda: self.__get_hsv()[2],
                lambda x: self.__set_hsv(v=_hsv_v_mapper(x)),
            ),
        )

    def __get_hls(self):
        return colorsys.rgb_to_hls(self.__r, self.__g, self.__b)

    def __set_hls(self, h=None, l_=None, s=None):
        h, l, s = map(lambda args: _ratio_or(*args), zip((h, l_, s), self.__get_hls()))
        self.__r, self.__g, self.__b = colorsys.hls_to_rgb(h, l, s)

    @property
    def hls(self) -> HLSColorProxy:
        """
        Overview:
            Get hls color system based color proxy.

        Returns:
            - proxy (:obj:`HLSColorProxy`): Hls color proxy.
        """
        return HLSColorProxy(
            self,
            GetSetProxy(
                lambda: self.__get_hls()[0],
                lambda x: self.__set_hls(h=_hls_h_mapper(x)),
            ),
            GetSetProxy(
                lambda: self.__get_hls()[1],
                lambda x: self.__set_hls(l_=_hls_l_mapper(x)),
            ),
            GetSetProxy(
                lambda: self.__get_hls()[2],
                lambda x: self.__set_hls(s=_hls_s_mapper(x)),
            ),
        )

    def __get_hex(self, include_alpha: bool):
        rs, gs, bs = _ratio_to_hex(self.__r), _ratio_to_hex(self.__g), _ratio_to_hex(self.__b)
        as_ = _ratio_to_hex(self.__alpha) if self.__alpha is not None and include_alpha else ''

        return '#' + rs + gs + bs + as_

    def __repr__(self):
        if self.__alpha is not None:
            return '<{cls} {hex}, alpha: {alpha}>'.format(
                cls=self.__class__.__name__,
                hex=self.__get_hex(False),
                alpha='%.3f' % (self.__alpha,),
            )
        else:
            return '<{cls} {hex}>'.format(
                cls=self.__class__.__name__,
                hex=self.__get_hex(False),
            )

    def __str__(self):
        return self.__get_hex(True)

    def __getstate__(self) -> Tuple[float, float, float, Optional[float]]:
        """
        Overview:
            Dump color as pickle object.

        Returns:
            - info (:obj:`Tuple[float, float, float, Optional[float]]`): Dumped data object.
        """
        return self.__r, self.__g, self.__b, self.__alpha

    def __setstate__(self, v: Tuple[float, float, float, Optional[float]]):
        """
        Overview:
            Load color from pickle object.
        Args:
            - v (:obj:`Tuple[float, float, float, Optional[float]]`): Dumped data object.
        """
        self.__r, self.__g, self.__b, self.__alpha = v

    def __hash__(self):
        """
        Overview:
            Get hash value of current object.

        Returns:
            - hash (:obj:`int`): Hash value of current color.
        """
        return hash(self.__getstate__())

    def __eq__(self, other):
        """
        Overview:
            Get equality between colors.

        Arguments:
            - other: Another object.

        Returns:
            - equal (:obj:`bool`): Equal or not.
        """
        if other is self:
            return True
        elif type(other) == type(self):
            return other.__getstate__() == self.__getstate__()
        else:
            return False

    @classmethod
    def from_hsv(cls, h, s, v, alpha=None) -> 'Color':
        """
        Overview:
            Load color from hsv system.

        Arguments:
            - h (:obj:`float`): Hue value, should be a float value in :math:`\\left[0, 1\\right)`.
            - s (:obj:`float`): Saturation value, should be a float value in :math:`\\left[0, 1\\right]`.
            - v (:obj:`float`): Brightness (value) value, should be a float value \
                in :math:`\\left[0, 1\\right]`.
            - alpha (:obj:`Optional[float]`): Alpha value, should be a float value \
                in :math:`\\left[0, 1\\right]`, default is None which means no alpha value is used.

        Returns:
            - color (:obj:`Color`): Color object.
        """
        return cls(colorsys.hsv_to_rgb(h, s, v), alpha)

    @classmethod
    def from_hls(cls, h: float, l: float, s: float, alpha: Optional[float] = None) -> 'Color':
        """
        Overview:
            Load color from hls system.

        Arguments:
            - h (:obj:`float`): Hue value, should be a float value in :math:`\\left[0, 1\\right)`.
            - l (:obj:`float`): Lightness value, should be a float value in :math:`\\left[0, 1\\right]`.
            - s (:obj:`float`): Saturation value, should be a float value in :math:`\\left[0, 1\\right]`.
            - alpha (:obj:`Optional[float]`): Alpha value, should be a float value \
                in :math:`\\left[0, 1\\right]`, default is None which means no alpha value is used.

        Returns:
            - color (:obj:`Color`): Color object.
        """
        return cls(colorsys.hls_to_rgb(h, l, s), alpha)
