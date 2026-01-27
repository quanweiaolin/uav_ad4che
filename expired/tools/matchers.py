import cv2 as cv

class BaseMatcher:
    def match(self, des1, des2):
        raise NotImplementedError

class BFMatcher(BaseMatcher):
    def __init__(self, norm_type=cv.NORM_HAMMING, crossCheck=False):
        self.matcher = cv.BFMatcher(norm_type, crossCheck=crossCheck)

    def match(self, des1, des2):
        if des1 is None or des2 is None:
            return []
        matches = self.matcher.knnMatch(des1, des2, k=2)
        # ratio test
        good = [m for m, n in matches if m.distance < 0.8 * n.distance]
        return good

class FLANNMatcher(BaseMatcher):
    def __init__(self):
        index_params = dict(algorithm=1, trees=5)
        search_params = dict(checks=50)
        self.matcher = cv.FlannBasedMatcher(index_params, search_params)

    def match(self, des1, des2):
        if des1 is None or des2 is None:
            return []
        matches = self.matcher.knnMatch(des1, des2, k=2)
        good = [m for m, n in matches if m.distance < 0.8 * n.distance]
        return good