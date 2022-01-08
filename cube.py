#!/usr/bin/env python3

from typing import Dict, Tuple, NamedTuple, Optional
from collections import deque

import numpy as np
from matplotlib import pyplot as plt
from scipy.spatial.transform import Rotation as R
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

tau = np.pi*2

# For each axis, the color at -1 and at 1.
COLOR_LETTERS = [{-1: 'O', 1: 'R'}, {-1: 'G', 1: 'B'}, {-1: 'Y', 1: 'W'}]
# Matplotlib colors from letters
LETTER_COLOR = {
    'B': 'b',
    'G': 'g',
    'Y': 'yellow',
    'W': 'w',
    'R': 'r',
    'O': 'orange',
}

State = Dict[Tuple[int, int, int], str]


class Move(NamedTuple):
    # 0, 1, 2 - x, y or z
    axis: int
    # 1: positive direction of axis. -1: negative direction of axis. 0: rotate entire cube
    side: int
    # 1 - 90 deg CW, 2 - 180 deg, -1 - 90 deg CCW
    n: int


def _insert(t: Tuple, where: int, val: int) -> Tuple:
    r = list(t)
    r.insert(where, val)
    return tuple(r)


def _remove(t, where):
    r = list(t)
    del r[where]
    return tuple(r)


def get_arranged_state() -> State:
    r = {}
    for axis in range(3):
        for sgn in [-1, 1]:
            color = COLOR_LETTERS[axis][sgn]
            for x in range(-1, 2):
                for y in range(-1, 2):
                    r[_insert((x, y), axis, sgn * 2)] = color
    return r


def get_rot(move: Move, portion: float = 1):
    angle = -tau / 4 * move.n * (-1 if move.side == -1 else 1) * portion
    return R.from_rotvec([angle if i == move.axis else 0 for i in range(3)])


def transform(state: State, move: Move) -> State:
    rot = get_rot(move)
    r = {}
    for k, color in state.items():
        if move.side == 0 or k[move.axis] * move.side >= 1:
            k = tuple(rot.apply(k).round().astype(int))
        r[k] = color
    return r


class CubeFigure:
    def __init__(self, state=None, frame_duration_ms=50, n_frames=10):
        if state is None:
            state = get_arranged_state()

        self.state = state
        self.frame_duration_ms = frame_duration_ms
        self.n_frames = n_frames
        self.fig = fig = plt.figure()
        self.ax = ax = fig.add_subplot(111, projection='3d')

        verts, facecolors = self._get_verts_facecolors(state)
        self.poly3dcol = Poly3DCollection(verts, facecolors=facecolors, edgecolor='k')
        ax.add_collection3d(self.poly3dcol)
        ax.set_box_aspect([ub - lb for lb, ub in (getattr(ax, f'get_{a}lim')() for a in 'xyz')])
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        ax.set_xlim3d(-2, 2)
        ax.set_ylim3d(-2, 2)
        ax.set_zlim3d(-2, 2)

        self._move_keys = {
            'r': Move(0, 1, 1),
            'l': Move(0, -1, 1),
            'b': Move(1, 1, 1),
            'f': Move(1, -1, 1),
            'u': Move(2, 1, 1),
            'd': Move(2, -1, 1),
            'x': Move(0, 0, 1),
            'y': Move(2, 0, 1),
            'z': Move(1, 0, -1),
        }
        for k, move in list(self._move_keys.items()):
            # noinspection PyProtectedMember
            self._move_keys[k.upper()] = move._replace(n=-move.n)

        self._frame_queue = deque()
        self._timer = self.fig.canvas.new_timer(interval=frame_duration_ms)
        self._timer.add_callback(self._on_timer)

        self.fig.canvas.mpl_disconnect(self.fig.canvas.manager.key_press_handler_id)
        self.fig.canvas.mpl_connect('key_press_event', self._on_press)

    @staticmethod
    def _get_face_verts(xyz):
        """Get the 4 vertices corresponding to a given face"""
        axis, = [i for i, x in enumerate(xyz) if abs(x) == 2]
        x0, y0 = _remove(xyz, axis)
        face = xyz[axis] * 0.75  # 2 -> 1.5
        return [_insert((x0 + x, y0 + y), axis, face)
                for x, y in [(-0.5, -0.5), (-0.5, 0.5), (0.5, 0.5), (0.5, -0.5)]]

    @classmethod
    def _get_verts_facecolors(cls, state: State, move: Optional[Move] = None, portion: float = 1):
        rot = get_rot(move, portion) if move is not None else None
        verts = []
        facecolors = []
        for k, col in state.items():
            face = cls._get_face_verts(k)
            if move is not None and (move.side == 0 or k[move.axis] * move.side >= 1):
                face = rot.apply(face)
            verts.append(face)
            facecolors.append(LETTER_COLOR[col])
        return verts, facecolors

    def _on_press(self, event):
        try:
            move = self._move_keys[event.key]
        except KeyError:
            return
        self.move(move)

    def move(self, move: Move):
        for i in range(self.n_frames):
            self._frame_queue.append((self.state, move, (i + 1) / self.n_frames))
        self._timer.start()
        self.state = transform(self.state, move)

    def _on_timer(self):
        if not self._frame_queue:
            self._timer.stop()
            return
        state, move, portion = self._frame_queue.popleft()
        verts, facecolors = self._get_verts_facecolors(state, move, portion)
        self.poly3dcol.set_verts(verts)
        self.poly3dcol.set_facecolor(facecolors)
        self.fig.canvas.draw()


def main():
    _cube = CubeFigure()
    plt.show()


if __name__ == '__main__':
    main()
