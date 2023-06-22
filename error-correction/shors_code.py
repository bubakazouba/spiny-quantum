import math
import random

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import Aer, assemble, transpile

# An implementation of Shor's 9-qubit error correction code.
def shors_code(input_bit=0, print_circuit=False):
    redundant_qubits = QuantumRegister(9, "redundant")
    syndrome = QuantumRegister(8, "syndrome")
    measurements = ClassicalRegister(8, "syndrome_measurement")
    outputs = ClassicalRegister(9, "output_measurement")

    qc = QuantumCircuit(redundant_qubits, syndrome, measurements, outputs)

    if input_bit == 1:
        qc.x(redundant_qubits[0])

    # Encoding.

    input_qubit = redundant_qubits[0]
    qc.cx(input_qubit, redundant_qubits[3])
    qc.cx(input_qubit, redundant_qubits[6])

    qc.barrier()

    qc.h(input_qubit)
    qc.h(redundant_qubits[3])
    qc.h(redundant_qubits[6])

    qc.barrier()

    qc.cx(input_qubit, redundant_qubits[1])
    qc.cx(input_qubit, redundant_qubits[2])

    qc.cx(redundant_qubits[3], redundant_qubits[4])
    qc.cx(redundant_qubits[3], redundant_qubits[5])

    qc.cx(redundant_qubits[6], redundant_qubits[7])
    qc.cx(redundant_qubits[6], redundant_qubits[8])

    qc.barrier()

    # Applying a random error.

    theta = random.uniform(0, 2 * math.pi)
    phi = random.uniform(0, 2 * math.pi)
    l = random.uniform(0, 2 * math.pi)
    noise_qubit = int(random.uniform(0, len(redundant_qubits)))
    qc.u(theta, phi, l, redundant_qubits[noise_qubit])

    # Syndrome computation.

    qc.h(syndrome)

    # Applying CZ operations to detect bit flip errors.
    qc.cz(syndrome[0], redundant_qubits[:2])
    qc.barrier()
    qc.cz(syndrome[1], redundant_qubits[1:3])
    qc.barrier()
    qc.cz(syndrome[2], redundant_qubits[3:5])
    qc.barrier()
    qc.cz(syndrome[3], redundant_qubits[4:6])
    qc.barrier()
    qc.cz(syndrome[4], redundant_qubits[6:8])
    qc.barrier()
    qc.cz(syndrome[5], redundant_qubits[7:9])
    qc.barrier()

    # Applying CX operations to detect phase flip errors.
    qc.cx(syndrome[6], redundant_qubits[0:6])
    qc.barrier()
    qc.cx(syndrome[7], redundant_qubits[3:9])
    qc.barrier()

    qc.h(syndrome)

    # Fixing bit flip errors.
    qc.cx(syndrome[0], redundant_qubits[0])
    qc.cx(syndrome[1], redundant_qubits[2])
    qc.mcx(syndrome[:2], redundant_qubits[0])
    qc.mcx(syndrome[:2], redundant_qubits[1])
    qc.mcx(syndrome[:2], redundant_qubits[2])

    qc.cx(syndrome[2], redundant_qubits[3])
    qc.cx(syndrome[3], redundant_qubits[5])
    qc.mcx(syndrome[2:4], redundant_qubits[3])
    qc.mcx(syndrome[2:4], redundant_qubits[4])
    qc.mcx(syndrome[2:4], redundant_qubits[5])

    qc.cx(syndrome[4], redundant_qubits[6])
    qc.cx(syndrome[5], redundant_qubits[8])
    qc.mcx(syndrome[4:6], redundant_qubits[6])
    qc.mcx(syndrome[4:6], redundant_qubits[7])
    qc.mcx(syndrome[4:6], redundant_qubits[8])

    # Fixing phase flip errors.
    qc.cz(syndrome[6], redundant_qubits[0])
    qc.cz(syndrome[7], redundant_qubits[6])
    qc.h(redundant_qubits)
    qc.mcx(syndrome[6:8], redundant_qubits[0])
    qc.mcx(syndrome[6:8], redundant_qubits[3])
    qc.mcx(syndrome[6:8], redundant_qubits[6])
    qc.h(redundant_qubits)

    # Decoding.

    qc.barrier()

    qc.cx(input_qubit, redundant_qubits[1])
    qc.cx(input_qubit, redundant_qubits[2])

    qc.cx(redundant_qubits[3], redundant_qubits[4])
    qc.cx(redundant_qubits[3], redundant_qubits[5])

    qc.cx(redundant_qubits[6], redundant_qubits[7])
    qc.cx(redundant_qubits[6], redundant_qubits[8])

    qc.barrier()

    qc.h(input_qubit)
    qc.h(redundant_qubits[3])
    qc.h(redundant_qubits[6])

    qc.barrier()

    input_qubit = redundant_qubits[0]
    qc.cx(input_qubit, redundant_qubits[3])
    qc.cx(input_qubit, redundant_qubits[6])

    qc.measure(syndrome, measurements)
    qc.measure(redundant_qubits, outputs)

    if print_circuit:
        print(qc)

    # Executing the quantum circuit on a simulator.
    aer_sim = Aer.get_backend("aer_simulator")
    transpiled = transpile(qc, aer_sim)
    result = aer_sim.run(transpiled).result()
    counts = result.get_counts()
    counts = dict(sorted(counts.items(), key=lambda state: state[1], reverse=True))
    counts = list(counts.items())

    # Displaying results.
    print(counts)

# Executing Shor's code multiple times to prove that it works with randomized errors.
num_executions = 10
for i in range(num_executions):
    shors_code(input_bit=1)
