from unittest import TestCase, main

import numpy as np

from newlang import State


class TestNumbers(TestCase):

    def test_assign(self):
        state = State()
        res, err = state.parse('a=1')
        self.assertFalse(err)
        self.assertEqual(res, 1)
        res, err = state.parse('a')
        self.assertFalse(err)
        self.assertEqual(res, 1)

    def test_math_e(self):
        res, err = State().parse('1e-6')
        self.assertFalse(err)
        self.assertEqual(res, 1e-6)

    def test_cond_equals(self):
        res, err = State().parse('1==1')
        self.assertFalse(err)
        self.assertEqual(res, True)

    def test_add(self):
        res, err = State().parse('1-1+1')
        self.assertFalse(err)
        self.assertEqual(res, 1)

    def test_mul(self):
        res, err = State().parse('2*2*2')
        self.assertFalse(err)
        self.assertEqual(res, 8)

        res, err = State().parse('8/2/2')
        self.assertFalse(err)
        self.assertEqual(res, 2)

        res, err = State().parse('3 % 2')
        self.assertFalse(err)
        self.assertEqual(res, 1)

    def test_pow(self):
        res, err = State().parse('2^2^2')
        self.assertFalse(err)
        self.assertEqual(res, 16)

    def test_abs(self):
        res, err = State().parse('|-2|')
        self.assertFalse(err)
        self.assertEqual(res, 2)


class TestMatrices(TestCase):

    def test_assign(self):
        res, err = State().parse('a=[1,0;0,-1]')
        self.assertFalse(err)
        a = np.eye(2)
        a[1, 1] = -1
        self.assertTrue(np.all(np.equal(a, res)))

    def test_add(self):
        state = State()
        _, _ = state.parse('a=[1,0;0,-1]')
        _, _ = state.parse('b=[-1,0;0,1]')
        res, err = state.parse('a+b')
        self.assertFalse(err)
        self.assertTrue(np.all(np.equal(res, np.zeros(2))))

    def test_mul(self):
        state = State()
        _, _ = state.parse('a=eye(2)')
        _, _ = state.parse('b=[2,2;2,2]')
        res, err = state.parse('a*b')
        self.assertFalse(err)
        self.assertTrue(np.all(np.equal(res, np.full(2, 2))))

        res, err = state.parse('a.*b')
        self.assertFalse(err)
        self.assertTrue(np.all(np.equal(res, np.eye(2) * 2)))

    def test_index(self):
        state = State()
        _, _ = state.parse('a=[1,0;0,-1]')
        res, err = state.parse('a(1,1)')
        self.assertFalse(err)
        self.assertEqual(res, -1)

    def test_transpose(self):
        state = State()
        _, _ = state.parse('a=[1,2;3,4]')
        res, err = state.parse('a\'')
        self.assertFalse(err)

        a = np.array([[1, 2], [3, 4]])
        a = np.transpose(a)
        self.assertTrue(np.all(np.equal(a, res)))

    def test_scalar_product(self):
        state = State()
        _, _ = state.parse('a=[2,2,2]')
        res, err = state.parse('a*a')
        self.assertFalse(err)
        self.assertEqual(res, 12)


class TestBuiltins(TestCase):

    def test_numpy(self):
        res, err = State().parse('sin(pi/2)')

        self.assertFalse(err)
        self.assertEqual(res, 1)

    def test_numpy_linalg(self):
        res, err = State().parse('rank([1,0;0,1])')

        self.assertFalse(err)
        self.assertEqual(res, 2)


class TestFunctions(TestCase):

    def test_fn_closure(self):
        state = State()
        _, _ = state.parse('a=3')
        _, _ = state.parse('f = x => x + a')
        res, err = state.parse('f(20)')
        self.assertFalse(err)
        self.assertEqual(res, 23)

        _, _ = state.parse('a=5')
        res, err = state.parse('f(20)')
        self.assertFalse(err)
        self.assertEqual(res, 25)

    def test_map(self):
        state = State()
        _, _ = state.parse('a=[1,2,3]')
        _, _ = state.parse('f = x => x^2')
        res, err = state.parse('map(f, a)')
        self.assertFalse(err)
        a = np.array([1, 4, 9])
        self.assertTrue(np.all(np.equal(res, a)))


if __name__ == '__main__':
    main()
