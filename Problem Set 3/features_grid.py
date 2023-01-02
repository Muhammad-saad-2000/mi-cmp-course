from typing import List
from grid import GridEnv
from mathutils import Direction, Point
from base_rl import FeatureExtractor, Features

# A class that convert a GridEnv state to a set of features
# The features are the x and y position of the player in addition to a constant (1)
class GridFeatureExtractor(FeatureExtractor[Point, Direction]):

    # Returns a list of feature names.
    # This will be used by the Approximate Q-Learning agent to initialize its weights dictionary.
    @property
    def feature_names(self) -> List[str]:
        features = ["X", "Y", "1"]
        return features
    
    # Given an enviroment and an observation (a state), return a set of features that represent the given state
    def extract_features(self, env: GridEnv, obs: Point) -> Features:
        x, y = obs
        w, h = env.mdp.size
        # We normalize the position to be in the range 0-1 to improve the training process
        # (so that the updates don't overshoot due to large gradients)
        x /= w
        y /= h
        features = {
            "X": x,
            "Y": y,
            "1": 1
        }
        return features