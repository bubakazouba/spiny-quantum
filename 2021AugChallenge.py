from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit import Aer, execute
from qiskit.circuit import Parameter
from scipy.optimize import minimize
from qiskit import IBMQ, BasicAer
import numpy as np
import math
from qiskit.quantum_info.operators import Operator, Pauli
from qiskit.extensions import HamiltonianGate
import time


def get_H(nqubits):
  H = []
  # make a 2^n x 2^n matrix of 0's
  for i in range(2**nqubits):
    H.append([0] * (2**nqubits))
  for i in range(len(H)):
    # special case since log(0) is -inf
    if i == 0:
      H[i][i] = 1000000
      continue
    # 0001, 0010, 0100, 1000
    # Only acceptable measurements of a W state should receive a negative energy
    l = np.log(i) / np.log(2)
    if int(l) == l:
      H[i][i] = -1000000
    else:
      H[i][i] = 1000000
  return H


def compute_expectation(counts, shots, is_smooth, want_equal_distribution):
  error = 0.0
  for bitstring, count in counts.items():
    count_of_1s = len([x for x in bitstring if x == "1"])
    # penalize if it's not an expected measurement of the W state
    if is_smooth:
      error += count * abs(count_of_1s - 1)
    else:
      error += count if count_of_1s != 1 else 0
    if want_equal_distribution and count_of_1s == 1:
      expected_count = shots / len(bitstring)
      error += abs(expected_count -
                   count) * 0.1  # smaller error for unequal distribution
  return error / shots


# We will also bring the different circuit components that
# build the qaoa circuit under a single function
def create_qaoa_circ(nqubits, theta):
  p = len(theta) // 2  # number of alternating unitaries
  qc = QuantumCircuit(nqubits)

  beta = theta[:p]
  gamma = theta[p:]

  # initial_state
  for i in range(0, nqubits):
    qc.h(i)

  for irep in range(0, p):
    # problem unitary
    problem_unitary_gate = HamiltonianGate(get_H(nqubits), 2 * gamma[irep])
    qc.append(problem_unitary_gate, range(nqubits))

    # mixer unitary
    for i in range(nqubits):
      qc.rx(2 * beta[irep], i)

  qc.measure_all()

  return qc


# Finally we write a function that executes the circuit on the chosen backend
def get_expectation(nqubits, shots, is_smooth, want_equal_distribution):
  """
    Runs parametrized circuit

    Args:
        p: int, Number of repetitions of unitaries
  """

  backend = Aer.get_backend("qasm_simulator")
  backend.shots = shots

  def execute_circ(theta):
    qc = create_qaoa_circ(nqubits, theta)
    results = execute(qc, backend=backend, shots=shots).result()
    counts = results.get_counts()
    return compute_expectation(counts, shots, is_smooth,
                               want_equal_distribution)

  return execute_circ

##########################
###### Benchmarking
def get_theta(p, psdistribution):
  if psdistribution == "ONES_AND_ZEROS":
    return [1] * p + [0] * p
  elif psdistribution == "DEC_AND_INC":
    theta = []
    for i in range(p):
      theta.append(1 - i / p)
    for i in range(p):
      theta.append(i / p)
    return theta


nqubitss = [3, 4, 5]
shotss = [2**10, 2**16, 2**20]
ps = [2, 4, 6, 8]
methods = ["L-BFGS-B", "BFGS", "COBYLA"]
psdistributions = ["ONES_AND_ZEROS", "DEC_AND_INC"]
is_smooths = [False, True]
want_equal_distributions = [True, False]

for want_equal_distribution in want_equal_distributions:
  for is_smooth in is_smooths:
    for nqubits in nqubitss:
      for shots in shotss:
        for p in ps:
          for method in methods:
            for psdistribution in psdistributions:
              print(
                  "START: want_equal_distribution={}, is_smooth={}, nqubits={}, shots={}, p={}, method={}, psdistribution={}"
                  .format(want_equal_distribution, is_smooth, nqubits, shots, p,
                          method, psdistribution))
              expectation = get_expectation(nqubits, shots, is_smooth,
                                            want_equal_distribution)
              sum_error = 0
              n_runs = 25
              for i in range(n_runs):
                start = time.time()
                print("run={}".format(i))
                error = minimize(
                    expectation, get_theta(p, psdistribution),
                    method=method).fun
                sum_error += error
                end = time.time()
                print("error={}, avg={}, time taken={}".format(
                    error, sum_error / (i + 1), end - start))
              print("score={}".format(sum_error / n_runs))
