from pprint import pprint as p

import numpy as np
from scipy import linalg, sparse, stats
import project.esn.transformer as tr
from project.esn import matrix as m
from project.esn import trainer as t
from project.esn import updater as up
from project.esn import utils as ut
from project.music_gen.data_types import Tempo
import project.esn.transformer as tr
from project.esn import teacher as te


@ut.mydataclass(init=True, repr=True)
class Runner:
    _runner: callable
    updator: up.Updator
    run_length: int
    inputs: np.ndarray = np.zeros((0, 0))
    outputs: np.ndarray = np.zeros((0, 0))

    def __call__(self):
        return self._runner(self.updator, self.inputs, self.outputs)

    def __lshift__(self, other):
        (inps, outs) = other
        self.inputs = inps
        self.outputs = outs
        return self


d_runner = lambda fun: lambda updator, inputs, outputs=None: Runner(
    fun, updator, inputs, outputs)


@d_runner
def runner(updator: up.Updator, inputs, outputs=None):
    outputs = np.zeros(len(inputs)) if outputs is None else outputs
    gen = zip(inputs, outputs)
    (u, o) = next(gen)
    try:
        while True:
            new_uo = yield updator << (u, o)
            (u, o) = next(gen) if new_uo == None else new_uo
    except StopIteration as e:
        return


def run_extended(r: Runner, init_len=0):
    states = np.zeros((len(r.inputs) + 1, r.updator.weights.W_res.shape[0]))
    states[0, :] = r.updator.state[:, 0]
    for (i, s) in zip(range(len(r.inputs)), r()):
        states[i + 1, :] = s[:, 0]

    states = states[1:, :]
    return m.build_extended_states(r.inputs, states, init_len)


def run_gen_mode(r: Runner, ta: callable, input):
    outputs = np.zeros((r.run_length, r.updator.weights.W_out.shape[0]))
    gen_state = (r << (np.array([input]), None))()
    for i in range(r.run_length):
        state = gen_state.send((input, None) if i != 0 else None)
        input = ta(r.updator >> input)
        outputs[i, :] = input

    return outputs


@ut.mydataclass(init=True, repr=True, check=False)
class ESN:
    _runner: Runner
    trainer: t.Trainer
    transformer: callable
    init_len: int = 100

    def __lshift__(self, other):
        (input, desired) = other
        ex_state = run_extended(self._runner << (input, None), self.init_len)
        self._runner.updator.weights.W_out = self.trainer << (ex_state,
                                                              desired)
        return ex_state

    def __rshift__(self, other):
        return run_gen_mode(self._runner, self.transformer, other)


@ut.mydataclass(init=True, repr=True, check=False)
class Data:
    data: np.ndarray
    tempo: Tempo
    init_len: int
    train_len: int
    test_len: int

    def desired(self):
        return self.data[self.init_len + 1:self.train_len + 1]

    def training_data(self):
        return self.data[:self.train_len]

    def test_data(self):
        return self.data[self.train_len + 1:]

    def start_input(self):
        return self.data[self.train_len]


@ut.mydataclass(init=True, repr=True, check=False)
class Run:
    data: Data
    in_out: int = 1
    reservoir: int = 100
    error_len: int = 500
    leaking_rate: float = 0.3
    spectral_radius: float = 0.9
    density: float = 0.5
    reg: float = 1e-8
    transformer: callable = lambda x: x
    evaluation: callable = te._mse_nd

    def __call__(self, input=None, desired=None):
        input = self.data.start_input() if input is None else input
        desired = self.data.test_data() if desired is None else desired
        output = self.esn >> input
        return (output,
                self.evaluation(output, ut.force_2dim(desired),
                                self.error_len), self.data.tempo)

    def __enter__(self):
        self.init_len = self.data.init_len
        matrixs = m.esn_matrixs(
            m.generate_rmatrix(
                self.reservoir,
                self.in_out,
                spectral_radius=self.spectral_radius,
                density=self.density,
            ))

        updator = up.vanilla_updator(matrixs,
                                     np.zeros((self.reservoir, 1)),
                                     leaking_rate=self.leaking_rate)

        trainer = t.ridge_reg(param=self.reg)

        self.esn = ESN(runner(updator, self.data.test_len), trainer,
                       self.transformer, self.init_len)
        self.activations = self.esn << (self.data.training_data(),
                                        self.data.desired())
        return self

    def __exit__(self, err_t, err_v, traceback):
        pass
