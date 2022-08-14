from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import Aer, assemble, transpile

redundant_qubits = QuantumRegister(9, "redundant")
syndrome = QuantumRegister(8, "syndrome")
measurements = ClassicalRegister(8, "syndrome_measurement")

qc = QuantumCircuit(redundant_qubits, syndrome, measurements)

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

# Apply an error.

qc.x(input_qubit)

# Syndrome.

qc.h(syndrome)

# TODO - Apply CZ and CNOT operations to detect errors.

qc.h(syndrome)
qc.measure(syndrome, measurements)

print(qc)

aer_sim = Aer.get_backend("aer_simulator")
transpiled = transpile(qc, aer_sim)
result = aer_sim.run(transpiled).result()
counts = result.get_counts()
counts = dict(sorted(counts.items(), key=lambda state: state[1], reverse=True))
counts = list(counts.items())

print(counts[0][0])
