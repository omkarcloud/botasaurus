import random
import math
import numpy as np
import pytweening


class HumanizeMouseTrajectory:
    def __init__(self, from_point, to_point, **kwargs):
        self.from_point = from_point
        self.to_point = to_point
        self.points = self.generate_curve(**kwargs)

    def generate_curve(self, **kwargs):
        """Generates the curve based on arguments below, default values below are automatically modified to cause randomness"""
        offset_boundary_x = kwargs.get("offset_boundary_x", 80)
        offset_boundary_y = kwargs.get("offset_boundary_y", 80)
        left_boundary = (
            kwargs.get("left_boundary", min(self.from_point[0], self.to_point[0]))
            - offset_boundary_x
        )
        right_boundary = (
            kwargs.get("right_boundary", max(self.from_point[0], self.to_point[0]))
            + offset_boundary_x
        )
        down_boundary = (
            kwargs.get("down_boundary", min(self.from_point[1], self.to_point[1]))
            - offset_boundary_y
        )
        up_boundary = (
            kwargs.get("up_boundary", max(self.from_point[1], self.to_point[1]))
            + offset_boundary_y
        )
        knots_count = kwargs.get("knots_count", 2)
        distortion_mean = kwargs.get("distortion_mean", 1)
        distortion_st_dev = kwargs.get("distortion_st_dev", 1)
        distortion_frequency = kwargs.get("distortion_frequency", 0.5)
        tween = kwargs.get("tweening", pytweening.easeOutQuad)
        target_points = kwargs.get("target_points", 100)

        internalKnots = self.generate_internal_knots(
            left_boundary, right_boundary, down_boundary, up_boundary, knots_count
        )
        points = self.generate_points(internalKnots)
        points = self.distort_points(
            points, distortion_mean, distortion_st_dev, distortion_frequency
        )
        points = self.tween_points(points, tween, target_points)
        return points

    def generate_internal_knots(
        self, l_boundary, r_boundary, d_boundary, u_boundary, knots_count
    ):
        """Generates the internal knots of the curve randomly"""
        if not (
            self.check_if_numeric(l_boundary)
            and self.check_if_numeric(r_boundary)
            and self.check_if_numeric(d_boundary)
            and self.check_if_numeric(u_boundary)
        ):
            raise ValueError("Boundaries must be numeric values")
        if not isinstance(knots_count, int) or knots_count < 0:
            knots_count = 0
        if l_boundary > r_boundary:
            raise ValueError(
                "left_boundary must be less than or equal to right_boundary"
            )
        if d_boundary > u_boundary:
            raise ValueError(
                "down_boundary must be less than or equal to upper_boundary"
            )
        try:
            knotsX = np.random.choice(range(l_boundary, r_boundary) or l_boundary, size=knots_count)
            knotsY = np.random.choice(range(d_boundary, u_boundary) or d_boundary, size=knots_count)
        except TypeError:
            knotsX = np.random.choice(
                range(int(l_boundary), int(r_boundary)), size=knots_count
            )
            knotsY = np.random.choice(
                range(int(d_boundary), int(u_boundary)), size=knots_count
            )
        knots = list(zip(knotsX, knotsY))
        return knots

    def generate_points(self, knots):
        """Generates the points from BezierCalculator"""
        if not self.check_if_list_of_points(knots):
            raise ValueError("knots must be valid list of points")

        midPtsCnt = max(
            abs(self.from_point[0] - self.to_point[0]),
            abs(self.from_point[1] - self.to_point[1]),
            2,
        )
        knots = [self.from_point] + knots + [self.to_point]
        return BezierCalculator.calculate_points_in_curve(int(midPtsCnt), knots)

    def distort_points(
        self, points, distortion_mean, distortion_st_dev, distortion_frequency
    ):
        """Distorts points by parameters of mean, standard deviation and frequency"""
        if not (
            self.check_if_numeric(distortion_mean)
            and self.check_if_numeric(distortion_st_dev)
            and self.check_if_numeric(distortion_frequency)
        ):
            raise ValueError("Distortions must be numeric")
        if not self.check_if_list_of_points(points):
            raise ValueError("points must be valid list of points")
        if not (0 <= distortion_frequency <= 1):
            raise ValueError("distortion_frequency must be in range [0,1]")

        distorted = []
        for i in range(1, len(points) - 1):
            x, y = points[i]
            delta = (
                np.random.normal(distortion_mean, distortion_st_dev)
                if random.random() < distortion_frequency
                else 0
            )
            # distorted += ((x, y + delta),)
            distorted.append((x, y + delta))
        distorted = [points[0]] + distorted + [points[-1]]
        return distorted

    def tween_points(self, points, tween, target_points):
        """Modifies points by tween"""
        if not self.check_if_list_of_points(points):
            raise ValueError("List of points not valid")
        if not isinstance(target_points, int) or target_points < 2:
            raise ValueError("target_points must be an integer greater or equal to 2")

        res = []
        for i in range(target_points):
            index = int(tween(float(i) / (target_points - 1)) * (len(points) - 1))
            res.append(points[index])
        return res

    @staticmethod
    def check_if_numeric(val):
        """Checks if value is proper numeric value"""
        return isinstance(val, (float, int, np.int32, np.int64, np.float32, np.float64))

    def check_if_list_of_points(self, list_of_points):
        """Checks if list of points is valid"""
        if not isinstance(list_of_points, list):
            return False
        try:
            point = lambda p: (
                (len(p) == 2)
                and self.check_if_numeric(p[0])
                and self.check_if_numeric(p[1])
            )
            return all(map(point, list_of_points))
        except (KeyError, TypeError):
            return False


class BezierCalculator:
    @staticmethod
    def binomial(n, k):
        """Returns the binomial coefficient "n choose k" """
        return math.factorial(n) / float(math.factorial(k) * math.factorial(n - k))

    @staticmethod
    def bernstein_polynomial_point(x, i, n):
        """Calculate the i-th component of a bernstein polynomial of degree n"""
        return BezierCalculator.binomial(n, i) * (x**i) * ((1 - x) ** (n - i))

    @staticmethod
    def bernstein_polynomial(points):
        """
        Given list of control points, returns a function, which given a point [0,1] returns
        a point in the Bézier curve described by these points
        """

        def bernstein(t):
            n = len(points) - 1
            x = y = 0
            for i, point in enumerate(points):
                bern = BezierCalculator.bernstein_polynomial_point(t, i, n)
                x += point[0] * bern
                y += point[1] * bern
            return x, y

        return bernstein

    @staticmethod
    def calculate_points_in_curve(n, points):
        """
        Given list of control points, returns n points in the Bézier curve,
        described by these points
        """
        curvePoints = []
        bernstein_polynomial = BezierCalculator.bernstein_polynomial(points)
        for i in range(n):
            t = i / (n - 1)
            curvePoints.append((bernstein_polynomial(t)))
        return curvePoints