import pickle

import pytest

from treevalue.tree.common import create_storage, raw, TreeStorage, delayed_partial


# noinspection PyArgumentList,DuplicatedCode,PyTypeChecker
@pytest.mark.unittest
class TestTreeStorage:
    def test_init(self):
        _ = create_storage({'a': 1, 'b': 2, 'c': raw({'x': 3, 'y': 4}), 'd': {'x': 3, 'y': 4}})

    def test_get(self):
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

    def test_get_or_default(self):
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

    def test_set(self):
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

        with pytest.raises(KeyError):
            t.set('', 233)
        with pytest.raises(KeyError):
            t.set('a' * 1000, 233)
        with pytest.raises(KeyError):
            t.set('0' + 'a' * 10, 233)

    def test_del_(self):
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

    def test_contains(self):
        t = create_storage({'a': 1, 'b': 2, 'c': raw({'x': 3, 'y': 4}), 'd': {'x': 3, 'y': 4}})
        assert t.contains('a')
        assert t.contains('b')
        assert t.contains('c')
        assert t.contains('d')
        assert not t.contains('f')
        assert not t.contains('kdfsj')

    def test_size(self):
        t = create_storage({'a': 1, 'b': 2, 'c': raw({'x': 3, 'y': 4}), 'd': {'x': 3, 'y': 4}})
        assert t.size() == 4
        assert t.get('d').size() == 2

        t.set('f', None)
        assert t.size() == 5

        t.del_('a')
        t.del_('c')
        t.del_('d')
        assert t.size() == 2

    def test_empty(self):
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

    def test_dump(self):
        h1 = {'x': 3, 'y': 4}
        h2 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'c': raw(h1), 'd': h2})

        _dumped = t.dump()
        assert _dumped['a'] == 1
        assert _dumped['b'] == 2
        assert _dumped['c'].value() is h1
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
        assert _dumped['c'].value() is h1
        assert _dumped['d']['x'] == 3
        assert _dumped['d']['y'] == 4

    def test_deepdump(self):
        h1 = {'x': 3, 'y': 4}
        h2 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'c': raw(h1), 'd': h2})

        _dumped = t.deepdump()
        assert _dumped['a'] == 1
        assert _dumped['b'] == 2
        assert _dumped['c'].value() == h1
        assert _dumped['c'] is not h1
        assert _dumped['d']['x'] == 3
        assert _dumped['d']['y'] == 4

    def test_deepdumpx(self):
        h1 = {'x': 3, 'y': 4}
        h2 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'c': raw(h1), 'd': h2})

        _dumped = t.deepdumpx(lambda x: -x if isinstance(x, int) else {'holy': 'shit'})
        assert _dumped['a'] == -1
        assert _dumped['b'] == -2
        assert _dumped['c'].value() == {'holy': 'shit'}
        assert _dumped['d']['x'] == -3
        assert _dumped['d']['y'] == -4

    def test_copy(self):
        h1 = {'x': 3, 'y': 4}
        h2 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'c': raw(h1), 'd': h2})

        t1 = t.copy()
        assert t1.get('a') == 1
        assert t1.get('b') == 2
        assert t1.get('c') is h1
        assert t1.get('d').get('x') == 3
        assert t1.get('d').get('y') == 4

    def test_deepcopy(self):
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

    def test_deepcopyx(self):
        h1 = {'x': 3, 'y': 4}
        h2 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'c': raw(h1), 'd': h2})

        t1 = t.deepcopyx(lambda x: -x if isinstance(x, int) else {'holy': 'shit'}, False)
        assert t1.get('a') == -1
        assert t1.get('b') == -2
        assert t1.get('c') == {'holy': 'shit'}
        assert t1.get('d').get('x') == -3
        assert t1.get('d').get('y') == -4

    def test_pickle(self):
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

    def test_detach(self):
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

    def test_copy_from(self):
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

    def test_deepcopy_from(self):
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

    def test_repr(self):
        h1 = {'x': 3, 'y': 4}
        h2 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'c': raw(h1), 'd': h2, 'f': h2})

        assert repr(('a', 'b', 'c', 'd', 'f')) in repr(t)
        assert repr(('x', 'y')) in repr(t.get('d'))
        assert repr(('x', 'y')) in repr(t.get('f'))

    def test_eq(self):
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

    def test_keys(self):
        h1 = {'x': 3, 'y': 4}
        h2 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'c': raw(h1), 'd': h2, 'f': h2})

        assert set(t.keys()) == {'a', 'b', 'c', 'd', 'f'}
        assert set(t.get('f').keys()) == {'x', 'y'}

    def test_values(self):
        h1 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'd': h1})

        assert set(t.get('d').values()) == {3, 4}
        assert len(list(t.values())) == 3
        assert 1 in t.values()
        assert 2 in t.values()

        t1 = create_storage({
            'a': delayed_partial(lambda: t.get('a')),
            'b': delayed_partial(lambda: t.get('b')),
            'd': delayed_partial(lambda: t.get('d')),
        })
        assert set(t1.get('d').values()) == {3, 4}
        assert len(list(t1.values())) == 3
        assert 1 in t1.values()
        assert 2 in t1.values()

    def test_items(self):
        h1 = {'x': 3, 'y': 4}
        t = create_storage({'a': 1, 'b': 2, 'd': raw(h1)})

        for k, v in t.items():
            if k == 'a':
                assert v == 1
            elif k == 'b':
                assert v == 2
            elif k == 'd':
                assert v == h1
            else:
                pytest.fail('Should not reach here.')

        t1 = create_storage({
            'a': delayed_partial(lambda: t.get('a')),
            'b': delayed_partial(lambda: t.get('b')),
            'd': delayed_partial(lambda: t.get('d')),
        })
        for k, v in t1.items():
            if k == 'a':
                assert v == 1
            elif k == 'b':
                assert v == 2
            elif k == 'd':
                assert v == h1
            else:
                pytest.fail('Should not reach here.')

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
