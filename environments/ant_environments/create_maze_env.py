

# NOTE THIS CODE IS TAKEN FROM https://github.com/tensorflow/models/tree/master/research/efficient-hrl/environments
# and is not my code.


import tensorflow as tf

import gin.tf
from ant_environments.ant_maze_env import AntMazeEnv
from ant_environments.point_maze_env import PointMazeEnv
from tf_agents.environments import gym_wrapper, tf_py_environment


@gin.configurable
def create_maze_env(env_name=None, top_down_view=False):
    n_bins = 0
    manual_collision = False
    if env_name.startswith('Ego'):
        n_bins = 8
        env_name = env_name[3:]
    if env_name.startswith('Ant'):
        cls = AntMazeEnv
        env_name = env_name[3:]
        maze_size_scaling = 8
    elif env_name.startswith('Point'):
        cls = PointMazeEnv
        manual_collision = True
        env_name = env_name[5:]
        maze_size_scaling = 4
    else:
        assert False, 'unknown env %s' % env_name

    maze_id = None
    observe_blocks = False
    put_spin_near_agent = False
    if env_name == 'Maze':
        maze_id = 'Maze'
    elif env_name == 'Push':
        maze_id = 'Push'
    elif env_name == 'Fall':
        maze_id = 'Fall'
    elif env_name == 'Block':
        maze_id = 'Block'
        put_spin_near_agent = True
        observe_blocks = True
    elif env_name == 'BlockMaze':
        maze_id = 'BlockMaze'
        put_spin_near_agent = True
        observe_blocks = True
    else:
        raise ValueError('Unknown maze environment %s' % env_name)

    gym_mujoco_kwargs = {
        'maze_id': maze_id,
        'n_bins': n_bins,
        'observe_blocks': observe_blocks,
        'put_spin_near_agent': put_spin_near_agent,
        'top_down_view': top_down_view,
        'manual_collision': manual_collision,
        'maze_size_scaling': maze_size_scaling
    }
    gym_env = cls(**gym_mujoco_kwargs)
    gym_env.reset()
    wrapped_env = gym_wrapper.GymWrapper(gym_env)
    return wrapped_env


class TFPyEnvironment(tf_py_environment.TFPyEnvironment):

    def __init__(self, *args, **kwargs):
        super(TFPyEnvironment, self).__init__(*args, **kwargs)

    def start_collect(self):
        pass

    def current_obs(self):
        time_step = self.current_time_step()
        # For some reason, there is an extra dim.
        return time_step.observation[0]

    def step(self, actions):
        actions = tf.expand_dims(actions, 0)
        next_step = super(TFPyEnvironment, self).step(actions)
        return next_step.is_last()[0], next_step.reward[0], next_step.discount[0]

    def reset(self):
        return super(TFPyEnvironment, self).reset()
