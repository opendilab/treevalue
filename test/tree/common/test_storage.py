import pickle
from functools import partial

import pytest

from treevalue.tree.common import create_storage, TreeStorage, delayed_partial
from treevalue.tree.common import raw as _native_raw

try:
    _ = reversed({}.keys())
except TypeError:
    _reversible = False
else:
    _reversible = True

iter_raws = pytest.mark.parametrize(['raw'], [
    (partial(_native_raw, safe=None),),
    (partial(_native_raw, safe=True),),
    (partial(_native_raw, safe=False),),
])


# noinspection PyArgumentList,DuplicatedCode,PyTypeChecker
@pytest.mark.unittest
class TestTreeStorage:
    @iter_raws
    def test_init(self, raw):
        _ = create_storage({'a': 1, 'b': 2, 'c': raw({'x': 3, 'y': 4}), 'd': {'x': 3, 'y': 4}})

    @iter_raws
    def test_get(self, raw):
        t = create_storage({'a': 1, 'b': 2, 'c': raw({'x': 3, 'y': 4}), 'd': {'x': 3, 'y': 4}})
        assert t.get('a') == 1
        assert t.get('b') == 2
        assert t.get('c') == {'x': 3, 'y': 4}
        assert isinstance(t.get('d'), TreeStorage)
        assert t.get('d').get('x') == 3
        assert t.get('d').get('y') == 4

        with pytest.raises(KeyError):
            _ = t.get('fff')

        cnt1, cnt2, cnt3 = 0, 0, 0

        def f1():
            nonlocal cnt1
            cnt1 += 1
            return 2

        def f2(x, y):
            nonlocal cnt2
            cnt2 += 1
            return {'x': x, 'y': y}

        def f3(x, y):
            nonlocal cnt3
            cnt3 += 1
            return create_storage({'x': x, 'y': raw(y)})

        t2 = create_storage({
            'a': 1,
            'b': delayed_partial(f1),
            'c': delayed_partial(f2, delayed_partial(f1), 3),
            'd': delayed_partial(f3, 3, delayed_partial(f2, 3, 4))
        })

        assert t2.get('a') == 1

        assert cnt1 == 0
        assert t2.get('b') == 2
        assert cnt1 == 1
        assert t2.get('b') == 2
        assert cnt1 == 1

        assert (cnt1, cnt2) == (1, 0)
        assert t2.get('c') == {'x': 2, 'y': 3}
        assert (cnt1, cnt2) == (2, 1)
        assert t2.get('c') == {'x': 2, 'y': 3}
        assert (cnt1, cnt2) == (2, 1)

        assert (cnt1, cnt2, cnt3) == (2, 1, 0)
        assert t2.get('d').get('x') == 3
        assert t2.get('d').get('y') == {'x': 3, 'y': 4}
        assert (cnt1, cnt2, cnt3) == (2, 2, 1)
        assert t2.get('d').get('x') == 3
        assert t2.get('d').get('y') == {'x': 3, 'y': 4}
        assert (cnt1, cnt2, cnt3) == (2, 2, 1)

    @iter_raws
    def test_get_or_default(self, raw):
        t = create_storage({'a': 1, 'b': 2, 'c': raw({'x': 3, 'y': 4}), 'd': {'x': 3, 'y': 4}})
        assert t.get_or_default('a', 233) == 1
        assert t.get_or_default('b', 233) == 2
        assert t.get_or_default('c', 233) == {'x': 3, 'y': 4}
        assert isinstance(t.get_or_default('d', 233), TreeStorage)
        assert t.get_or_default('d', 233).get_or_default('x', 233) == 3
        assert t.get_or_default('d', 233).get_or_default('y', 233) == 4

        assert t.get_or_default('fff', 233) == 233

        t1 = create_storage({
            'a': delayed_partial(lambda: t.get('a')),
            'b': delayed_partial(lambda: t.get('b')),
            'c': delayed_partial(lambda: t.get('c')),
            'd': delayed_partial(lambda: t.get('d')),
        })
        assert t1.get_or_default('a', 233) == 1
        assert t1.get_or_default('b', 233) == 2
        assert t1.get_or_default('c', 233) == {'x': 3, 'y': 4}
        assert isinstance(t1.get_or_default('d', 233), TreeStorage)
        assert t1.get_or_default('d', 233).get_or_default('x', 233) == 3
        assert t1.get_or_default('d', 233).get_or_default('y', 233) == 4

        assert t1.get_or_default('fff', 233) == 233
        assert t1.get_or_default('fff', delayed_partial(lambda: 2345)) == 2345
        assert not t1.contains('fff')

    @iter_raws
    def test_pop(self, raw):
        t = create_storage({'a': 1, 'b': 2, 'c': raw({'x': 3, 'y': 4}), 'd': {'x': 3, 'y': 4}})
        assert t.pop('a') == 1
        with pytest.raises(KeyError):
            t.pop('a')

        assert t.pop('b') == 2
        assert t.pop('c') == {'x': 3, 'y': 4}

        td = t.pop('d')
        assert isinstance(td, TreeStorage)
        assert td.get('x') == 3
        assert td.get('y') == 4

        with pytest.raises(KeyError):
            t.pop('aksjdlasdkjf')

        cnt1, cnt2, cnt3 = 0, 0, 0

        def f1():
            nonlocal cnt1
            cnt1 += 1
            return 2

        def f2(x, y):
            nonlocal cnt2
            cnt2 += 1
            return {'x': x, 'y': y}

        def f3(x, y):
            nonlocal cnt3
            cnt3 += 1
            return create_storage({'x': x, 'y': raw(y)})

        t2 = create_storage({
            'a': 1,
            'b': delayed_partial(f1),
            'c': delayed_partial(f2, delayed_partial(f1), 3),
            'd': delayed_partial(f3, 3, delayed_partial(f2, 3, 4))
        })

        assert t2.pop('a') == 1

        assert cnt1 == 0
        assert t2.pop('b') == 2
        assert cnt1 == 1
        with pytest.raises(KeyError):
            t2.pop('b')
        assert cnt1 == 1

        assert (cnt1, cnt2) == (1, 0)
        assert t2.pop('c') == {'x': 2, 'y': 3}
        assert (cnt1, cnt2) == (2, 1)
        with pytest.raises(KeyError):
            t2.pop('c')
        assert (cnt1, cnt2) == (2, 1)

        assert (cnt1, cnt2, cnt3) == (2, 1, 0)
        assert t2.get('d').pop('x') == 3
        assert t2.get('d').pop('y') == {'x': 3, 'y': 4}
        assert (cnt1, cnt2, cnt3) == (2, 2, 1)
        with pytest.raises(KeyError):
            t2.get('d').pop('x')
        with pytest.raises(KeyError):
            t2.get('d').pop('y')
        assert (cnt1, cnt2, cnt3) == (2, 2, 1)

    @iter_raws
    def test_pop_or_default(self, raw):
        t = create_storage({'a': 1, 'b': 2, 'c': raw({'x': 3, 'y': 4}), 'd': {'x': 3, 'y': 4}})
        assert t.pop_or_default('a', 233) == 1
        with pytest.raises(KeyError):
            t.pop('a')
        assert t.pop_or_default('a', 233) == 233

        assert t.pop_or_default('b', 233) == 2
        assert t.pop_or_default('c', 233) == {'x': 3, 'y': 4}

        td = t.pop_or_default('d', 233)
        assert isinstance(td, TreeStorage)
        assert td.pop_or_default('x', 233) == 3
        assert td.pop_or_default('y', 233) == 4

        assert t.pop_or_default('fff', 233) == 233

        t = create_storage({'a': 1, 'b': 2, 'c': raw({'x': 3, 'y': 4}), 'd': {'x': 3, 'y': 4}})
        t1 = create_storage({
            'a': delayed_partial(lambda: t.get('a')),
            'b': delayed_partial(lambda: t.get('b')),
            'c': delayed_partial(lambda: t.get('c')),
            'd': delayed_partial(lambda: t.get('d')),
        })
        assert t1.pop_or_default('a', 233) == 1
        assert t1.pop_or_default('b', 233) == 2
        assert t1.pop_or_default('c', 233) == {'x': 3, 'y': 4}

        t1d = t1.pop_or_default('d', 233)
        assert isinstance(t1d, TreeStorage)
        assert t1d.pop_or_default('x', 233) == 3
        assert t1d.pop_or_default('y', 233) == 4

        assert t1.pop_or_default('fff', 233) == 233
        assert t1.pop_or_default('fff', delayed_partial(lambda: 2345)) == 2345
        assert not t1.contains('fff')

    def test_popitem(self):
        t = create_storage({})
        with pytest.raises(KeyError):
            t.popitem()

        t1 = create_storage({'a': 1, 'b': 2, 'c': {'x': 2}})
        assert sorted([t1.popitem() for _ in range(t1.size())]) == [
            ('a', 1), ('b', 2), ('c', create_storage({'x': 2}))
        ]

        t2 = create_storage({
            'a': delayed_partial(lambda: 1),
            'b': delayed_partial(lambda: 2),
        })
        assert sorted([t2.popitem() for _ in range(t2.size())]) == [
            ('a', 1), ('b', 2)
        ]

        d1 = delayed_partial(lambda: 1)
        d2 = delayed_partial(lambda x: x + 1, d1)
        t3 = create_storage({
            'a': d1, 'b': d2, 'c': d1,
        })
        assert sorted([t3.popitem() for _ in range(t3.size())]) == [
            ('a', 1), ('b', 2), ('c', 1)
        ]

    @iter_raws
    def test_set(self, raw):
        t = create_storage({})
        t.set('a', 1)
        t.set('b', 2)
        t.set('c', {'x': 3, 'y': 4})
        t.set('d', create_storage({'x': 3, 'y': 4}))
        t.set('_0a', None)

        assert t.get('a') == 1
        assert t.get('b') == 2
        assert t.get('c') == {'x': 3, 'y': 4}
        assert isinstance(t.get('d'), TreeStorage)
        assert t.get('_0a') is None

        t.set('', 233)
        assert t.get('') == 233

        t.set('a' * 1000, 234)
        assert t.get('a' * 1000) == 234

        t.set('0' * 1000, 235)
        assert t.get('0' * 1000) == 235

        t.set('ff', raw(1))
        assert t.get('ff') == 1

        t.set('fff', raw({'x': 1, 'y': 2}))
        assert t.get('fff') == {'x': 1, 'y': 2}

    @iter_raws
    def test_setdefault(self, raw):
        t = create_storage({})
        assert t.setdefault('a', 1) == 1
        assert t == create_storage({'a': 1})
        assert t.setdefault('b', 2) == 2
        assert t == create_storage({'a': 1, 'b': 2})
        assert t.setdefault('a', 100) == 1
        assert t == create_storage({'a': 1, 'b': 2})

        assert t.setdefault('c', create_storage({'a': 100, 'b': 200})) == create_storage({'a': 100, 'b': 200})
        assert t == create_storage({'a': 1, 'b': 2, 'c': {'a': 100, 'b': 200}})
        assert t.setdefault('c', create_storage({'a': 400, 'b': 300})) == create_storage({'a': 100, 'b': 200})
        assert t == create_storage({'a': 1, 'b': 2, 'c': {'a': 100, 'b': 200}})

        d1 = delayed_partial(lambda: 1)
        assert t.setdefault('g', delayed_partial(lambda x: x + 1, d1)) == 2
        assert t == create_storage({'a': 1, 'b': 2, 'c': {'a': 100, 'b': 200}, 'g': 2})
        assert t.setdefault('g', delayed_partial(lambda x: x * 100, d1)) == 2
        assert t == create_storage({'a': 1, 'b': 2, 'c': {'a': 100, 'b': 200}, 'g': 2})

    @iter_raws
    def test_del_(self, raw):
        t = create_storage({'a': 1, 'b': 2, 'c': raw({'x': 3, 'y': 4}), 'd': {'x': 3, 'y': 4}})
        t.del_('c')
        t.del_('b')

        assert t.get('a') == 1
        with pytest.raises(KeyError):
            _ = t.get('c')
        with pytest.raises(KeyError):
            _ = t.get('b')
        assert isinstance(t.get('d'), TreeStorage)

        with pytest.raises(KeyError):
            t.del_('fff')

    @iter_raws
    def test_clear(self, raw):
        t = create_storage({'a': 1, 'b': 2, 'c': raw({'x': 3, 'y': 4}), 'd': {'x': 3, 'y': 4}})
        t.clear()
        assert t == create_storage({})
        assert t.size() == 0

        d1 = delayed_partial(lambda: 1)
        d2 = delayed_partial(lambda x: x + 1, d1)
        t1 = create_storage({'a': d1, 'b': d2, 'c': d1, 'd': 100})
        t1.clear()
        assert t1 == create_storage({})
        assert t1.size() == 0

    @iter_raws
    def test_contains(self, raw):
        t = create_storage({'a': 1, 'b': 2, 'c': raw({'x': 3, 'y': 4}), 'd': {'x': 3, 'y': 4}})
        assert t.contains('a')
        assert t.contains('b')
        assert t.contains('c')
        assert t.contains('d')
        assert not t.contains('f')
        assert not t.contains('kdfsj')

    @iter_raws
    def test_size(self, raw):
        t = create_storage({'a': 1, 'b': 2, 'c': raw({'x': 3, 'y': 4}), 'd': {'x': 3, 'y': 4}})
        assert t.size() == 4
        assert t.get('d').size() == 2

        t.set('f', None)
        assert t.size() == 5

        t.del_('a')
        t.del_('c')
        t.del_('d')
        assert t.size() == 2

    @iter_raws
    def test_empty(self, raw):
        t = create_storage({'a': 1, 'b': 2, 'c': raw({'x': 3, 'y': 4}), 'd': {'x': 3, 'y': 4}})
        assert not t.empty()
        assert not t.get('d').empty()

        t.del_('a')
        t.del_('c')
        t.get('d').del_('x')
        assert not t.empty()
        assert not t.get('d').empty()

        t.get('d').del_('y')
        assert t.get('d').empty()

        t.del_('b')
        t.del_('d')
        assert t.empty()

    @iter_raws
    def test_dump(self, raw):
        h1 = {'x': 3, 'y': 4}
        h2 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'c': raw(h1), 'd': h2})

        _dumped = t.dump()
        assert _dumped['a'] == 1
        assert _dumped['b'] == 2
        assert _dumped['c'] == {'__treevalue/raw/wrapper': h1}
        assert _dumped['c']['__treevalue/raw/wrapper'] is h1
        assert _dumped['d']['x'] == 3
        assert _dumped['d']['y'] == 4

        t2 = create_storage({
            'a': 1,
            'b': delayed_partial(lambda x: x + 1, 1),
            'c': delayed_partial(lambda: h1),
            'd': delayed_partial(lambda: create_storage(h2)),
        })
        _dumped = t2.dump()
        assert _dumped['a'] == 1
        assert _dumped['b'] == 2
        assert _dumped['c'] == {'__treevalue/raw/wrapper': h1}
        assert _dumped['c']['__treevalue/raw/wrapper'] is h1
        assert _dumped['d']['x'] == 3
        assert _dumped['d']['y'] == 4

    @iter_raws
    def test_deepdump(self, raw):
        h1 = {'x': 3, 'y': 4}
        h2 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'c': raw(h1), 'd': h2})

        _dumped = t.deepdump()
        assert _dumped['a'] == 1
        assert _dumped['b'] == 2
        assert _dumped['c'] == {'__treevalue/raw/wrapper': h1}
        assert _dumped['c']['__treevalue/raw/wrapper'] == h1
        assert _dumped['c']['__treevalue/raw/wrapper'] is not h1
        assert _dumped['c'] is not h1
        assert _dumped['d']['x'] == 3
        assert _dumped['d']['y'] == 4

    @iter_raws
    def test_deepdumpx(self, raw):
        h1 = {'x': 3, 'y': 4}
        h2 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'c': raw(h1), 'd': h2})

        _dumped = t.deepdumpx(lambda x: -x if isinstance(x, int) else {'holy': 'shit'})
        assert _dumped['a'] == -1
        assert _dumped['b'] == -2
        assert _dumped['c'] == {'__treevalue/raw/wrapper': {'holy': 'shit'}}
        assert _dumped['c']['__treevalue/raw/wrapper'] == {'holy': 'shit'}
        assert _dumped['d']['x'] == -3
        assert _dumped['d']['y'] == -4

    @iter_raws
    def test_copy(self, raw):
        h1 = {'x': 3, 'y': 4}
        h2 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'c': raw(h1), 'd': h2})

        t1 = t.copy()
        assert t1.get('a') == 1
        assert t1.get('b') == 2
        assert t1.get('c') is h1
        assert t1.get('d').get('x') == 3
        assert t1.get('d').get('y') == 4

    @iter_raws
    def test_deepcopy(self, raw):
        h1 = {'x': 3, 'y': 4}
        h2 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'c': raw(h1), 'd': h2})

        t1 = t.deepcopy()
        assert t1.get('a') == 1
        assert t1.get('b') == 2
        assert t1.get('c') == h1
        assert t1.get('c') is not h1
        assert t1.get('d').get('x') == 3
        assert t1.get('d').get('y') == 4

    @iter_raws
    def test_deepcopyx(self, raw):
        h1 = {'x': 3, 'y': 4}
        h2 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'c': raw(h1), 'd': h2})

        t1 = t.deepcopyx(lambda x: -x if isinstance(x, int) else {'holy': 'shit'}, False)
        assert t1.get('a') == -1
        assert t1.get('b') == -2
        assert t1.get('c') == {'holy': 'shit'}
        assert t1.get('d').get('x') == -3
        assert t1.get('d').get('y') == -4

    @iter_raws
    def test_pickle(self, raw):
        h1 = {'x': 3, 'y': 4}
        h2 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'c': raw(h1), 'd': h2})

        t1 = pickle.loads(pickle.dumps(t))
        assert t1.get('a') == 1
        assert t1.get('b') == 2
        assert t1.get('c') == h1
        assert t1.get('c') is not h1
        assert t1.get('d').get('x') == 3
        assert t1.get('d').get('y') == 4

    @iter_raws
    def test_detach(self, raw):
        h1 = {'x': 3, 'y': 4}
        h2 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'c': raw(h1), 'd': h2})

        dt = t.detach()
        assert dt['a'] == 1
        assert dt['b'] == 2
        assert dt['c'] == h1
        assert isinstance(dt['d'], TreeStorage)
        assert dt['d'].get('x') == 3
        assert dt['d'].get('y') == 4

    @iter_raws
    def test_copy_from(self, raw):
        h1 = {'x': 3, 'y': 4}
        h2 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'c': raw(h1), 'd': h2, 'f': h2})

        h3 = {'x': 33, 'y': 44}
        h4 = {'x': 33, 'y': 44}
        t1 = create_storage({'a': 11, 'e': 2333, 'c': raw(h3), 'd': h4})
        did = id(t1.get('d'))
        t1.copy_from(t)
        assert t1 is not t
        assert t1.get('a') == 1
        assert t1.get('b') == 2
        assert t1.get('c') is h1
        assert t1.get('d').get('x') == 3
        assert t1.get('d').get('y') == 4
        assert id(t1.get('d')) == did
        assert not t1.contains('e')
        assert t1.get('f').get('x') == 3
        assert t1.get('f').get('y') == 4
        assert t1.get('f') is not t.get('f')

        t2 = create_storage({
            'a': delayed_partial(lambda: 11),
            'b': delayed_partial(lambda: 22),
            'c': delayed_partial(lambda: {'x': 3, 'y': 5}),
            'd': delayed_partial(lambda: create_storage({'x': 3, 'y': 7})),
        })
        t1.copy_from(t2)
        assert t1.get('a') == 11
        assert t1.get('b') == 22
        assert t1.get('c') == {'x': 3, 'y': 5}
        assert t1.get('d').get('x') == 3
        assert t1.get('d').get('y') == 7

    @iter_raws
    def test_deepcopy_from(self, raw):
        h1 = {'x': 3, 'y': 4}
        h2 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'c': raw(h1), 'd': h2, 'f': h2})

        h3 = {'x': 33, 'y': 44}
        h4 = {'x': 33, 'y': 44}
        t1 = create_storage({'a': 11, 'e': 2333, 'c': raw(h3), 'd': h4})
        t1.deepcopy_from(t)
        assert t1 is not t
        assert t1.get('a') == 1
        assert t1.get('b') == 2
        assert t1.get('c') == h1
        assert t1.get('c') is not h1
        assert t1.get('d').get('x') == 3
        assert t1.get('d').get('y') == 4
        assert not t1.contains('e')
        assert t1.get('f').get('x') == 3
        assert t1.get('f').get('y') == 4
        assert t1.get('f') is not t.get('f')

        t2 = create_storage({
            'a': delayed_partial(lambda: 11),
            'b': delayed_partial(lambda: 22),
            'c': delayed_partial(lambda: {'x': 3, 'y': 5}),
            'd': delayed_partial(lambda: create_storage({'x': 3, 'y': 7})),
        })
        t1.deepcopy_from(t2)
        assert t1.get('a') == 11
        assert t1.get('b') == 22
        assert t1.get('c') == {'x': 3, 'y': 5}
        assert t1.get('d').get('x') == 3
        assert t1.get('d').get('y') == 7

    @iter_raws
    def test_repr(self, raw):
        h1 = {'x': 3, 'y': 4}
        h2 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'c': raw(h1), 'd': h2, 'f': h2})

        assert repr(('a', 'b', 'c', 'd', 'f')) in repr(t)
        assert repr(('x', 'y')) in repr(t.get('d'))
        assert repr(('x', 'y')) in repr(t.get('f'))

    @iter_raws
    def test_eq(self, raw):
        h1 = {'x': 3, 'y': 4}
        h2 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'c': raw(h1), 'd': h2, 'f': h2})
        t1 = create_storage({'a': 1, 'b': 2, 'c': raw(h1), 'd': h2, 'f': h2})
        t2 = create_storage({'a': 1, 'b': 2, 'c': raw(h1), 'd': h2, 'f': {'x': 3, 'y': 3, 'z': 4}})

        assert t == t
        assert t == t1
        assert t != t2
        assert t != None

        t3 = create_storage({
            'a': delayed_partial(lambda: 11),
            'b': delayed_partial(lambda: 22),
            'c': delayed_partial(lambda: {'x': 3, 'y': 5}),
            'd': delayed_partial(lambda: create_storage({'x': 3, 'y': 7})),
        })
        t4 = create_storage({
            'a': delayed_partial(lambda: t3.get('a')),
            'b': delayed_partial(lambda: t3.get('b')),
            'c': delayed_partial(lambda: t3.get('c')),
            'd': delayed_partial(lambda: t3.get('d')),
        })
        assert t3 == t4

    @iter_raws
    def test_keys(self, raw):
        h1 = {'x': 3, 'y': 4}
        h2 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'c': raw(h1), 'd': h2, 'f': h2})

        assert set(t.iter_keys()) == {'a', 'b', 'c', 'd', 'f'}
        assert set(t.get('f').iter_keys()) == {'x', 'y'}

        if _reversible:
            assert list(t.iter_rev_keys()) == list(t.iter_keys())[::-1]
        else:
            with pytest.raises(TypeError):
                t.iter_rev_keys()

    def test_values(self):
        h1 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'd': h1})

        assert set(t.get('d').iter_values()) == {3, 4}
        assert len(list(t.iter_values())) == 3
        assert 1 in t.iter_values()
        assert 2 in t.iter_values()
        if _reversible:
            assert list(t.iter_rev_values()) == list(t.iter_values())[::-1]
        else:
            with pytest.raises(TypeError):
                _ = list(t.iter_rev_values())

        t1 = create_storage({
            'a': delayed_partial(lambda: t.get('a')),
            'b': delayed_partial(lambda: t.get('b')),
            'd': delayed_partial(lambda: t.get('d')),
        })
        assert set(t1.get('d').iter_values()) == {3, 4}
        assert len(list(t1.iter_values())) == 3
        assert 1 in t1.iter_values()
        assert 2 in t1.iter_values()
        if _reversible:
            assert list(t1.iter_rev_values()) == list(t1.iter_values())[::-1]
        else:
            with pytest.raises(TypeError):
                _ = list(t1.iter_rev_values())

    @iter_raws
    def test_items(self, raw):
        h1 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'd': raw(h1)})

        for k, v in t.iter_items():
            if k == 'a':
                assert v == 1
            elif k == 'b':
                assert v == 2
            elif k == 'd':
                assert v == h1
            else:
                pytest.fail('Should not reach here.')

        if _reversible:
            assert list(t.iter_rev_items()) == list(t.iter_items())[::-1]
        else:
            with pytest.raises(TypeError):
                _ = list(t.iter_rev_items())

        t1 = create_storage({
            'a': delayed_partial(lambda: t.get('a')),
            'b': delayed_partial(lambda: t.get('b')),
            'd': delayed_partial(lambda: t.get('d')),
        })
        for k, v in t1.iter_items():
            if k == 'a':
                assert v == 1
            elif k == 'b':
                assert v == 2
            elif k == 'd':
                assert v == h1
            else:
                pytest.fail('Should not reach here.')

        if _reversible:
            assert list(t1.iter_rev_values()) == list(t1.iter_values())[::-1]
        else:
            with pytest.raises(TypeError):
                _ = list(t1.iter_rev_values())

    def test_hash(self):
        h = {}

        h1 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'd': h1})
        t1 = create_storage({
            'a': delayed_partial(lambda: t.get('a')),
            'b': delayed_partial(lambda: t.get('b')),
            'd': delayed_partial(lambda: t.get('d')),
        })
        t2 = create_storage({
            'a': delayed_partial(lambda: t.get('a')),
            'b': delayed_partial(lambda: 3),
            'd': delayed_partial(lambda: t.get('d')),
        })

        h[t] = 1
        assert t1 in h
        assert h[t1] == 1
        assert t2 not in h
