"""Invented analytic/independent convex references, no observation reader."""
import unittest
import numpy as np
from scipy.optimize import lsq_linear
from gaussian_mean_profile_v1 import profile_mean

class ProfileControls(unittest.TestCase):
    def test_known_box_corner_and_cost(self):
        r = profile_mean(np.eye(2), np.array([-2., 3.]), {0: (0., 4.), 1: (-1., 1.)})
        np.testing.assert_array_equal(r['coefficients'], [0., 1.])
        self.assertEqual(r['quadratic'], 8.)
        self.assertTrue(r['linear_parameters_identified'])

    def test_independent_bounded_convex_solver(self):
        rng = np.random.default_rng(7182)
        for k in range(8):
            a = rng.normal(size=(19, 5)); y = rng.normal(size=19)
            bounds = {0: (0., .2), 3: (-.1, .1)}
            r = profile_mean(a, y, bounds)
            lower = np.full(5, -np.inf); upper = np.full(5, np.inf)
            lower[[0, 3]] = [0., -.1]; upper[[0, 3]] = [.2, .1]
            q = lsq_linear(a, y, bounds=(lower, upper), tol=1e-13)
            with self.subTest(case=k):
                self.assertAlmostEqual(r['quadratic'], float(np.sum((a @ q.x - y) ** 2)), places=9)
                np.testing.assert_allclose(a @ r['coefficients'], a @ q.x, rtol=1e-7, atol=1e-7)

    def test_fixed_coefficient_reprofiles_other_terms(self):
        a = np.array([[1., 1.], [2., -1.], [3., 2.]])
        y = np.array([.3, 2., 1.])
        r = profile_mean(a, y, {0: (0., 4.)}, fixed={0: .7})
        expected = (a[:, 1] @ (y - .7 * a[:, 0])) / (a[:, 1] @ a[:, 1])
        np.testing.assert_allclose(r['coefficients'], [.7, expected], atol=1e-14)

    def test_units_and_row_permutation(self):
        rng = np.random.default_rng(312)
        a = rng.normal(size=(17, 4)); y = rng.normal(size=17)
        r = profile_mean(a, y, {0: (0., 2.), 3: (-1., 1.)})
        factors = np.array([1e-6, 1e5, 1e-3, 1e3])
        permutation = rng.permutation(len(y))
        b = profile_mean((a * factors)[permutation], y[permutation], {0: (0., 2. / factors[0]), 3: (-1. / factors[3], 1. / factors[3])})
        np.testing.assert_allclose(b['coefficients'] * factors, r['coefficients'], rtol=1e-8, atol=1e-8)
        self.assertAlmostEqual(r['quadratic'], b['quadratic'], places=11)

    def test_rank_loss_and_zero_column_not_confidence(self):
        a = np.column_stack([np.ones(5), np.ones(5), np.zeros(5)])
        r = profile_mean(a, np.arange(5.), {})
        self.assertFalse(r['linear_parameters_identified'])
        self.assertEqual(r['full_column_rank'], 1)
        self.assertNotIn('covariance', r)
        self.assertAlmostEqual(r['quadratic'], 10.)

    def test_exact_zero_face(self):
        r = profile_mean(np.ones((4, 1)), -np.ones(4), {0: (0., 40.)})
        self.assertEqual(r['coefficients'][0], 0.)
        self.assertEqual(r['active_bounds'], [{'column': 0, 'side': 'LOWER'}])

    def test_fixed_outside_domain(self):
        with self.assertRaises(ValueError):
            profile_mean(np.eye(2), [1., 2.], {0: (0., 1.)}, fixed={0: 2.})

    def test_booleans_nonfinite_and_strings_rejected(self):
        for y in ([True, 1.], [np.nan, 1.], ['1', '2']):
            with self.subTest(target=y), self.assertRaises(ValueError):
                profile_mean(np.eye(2), y, {})
        with self.assertRaises(ValueError):
            profile_mean(np.eye(2), [1., 2.], {0: (False, 1.)})

if __name__ == '__main__':
    unittest.main(verbosity=2)
