#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import copy

def readNetlist(file):
	nets = int(file.readline())
	inputs  = file.readline().split()
	inputs.sort()
	outputs = file.readline().split() 
	outputs.sort()

	# read mapping
	mapping = {} # numbers to letters 
	mapping_letter = {} #letters to numbers  
	while True:
		line = file.readline().strip()
		if not line:
			break

		net, name = line.split()
		mapping[int(net)] = name 
		mapping_letter[name] = int(net) 
	
	#inputs as numb
	inputs_numb = []
	for inp in inputs:
		inputs_numb.append(mapping_letter[inp])
	
	#outputs as numb
	outputs_numb = []
	for out in outputs:
		outputs_numb.append(mapping_letter[out])
	
	# read gates
	gates = []
	for line in file.readlines():
		bits = line.split()
		gate = bits.pop(0)
		ports = list( map(int,bits) )
		gates.append((gate,ports))
	return inputs, inputs_numb, outputs, outputs_numb, mapping, gates, nets, mapping_letter

def miter(nets1, nets2, gates1,gates2, mapping_let_numb1, mapping_let_numb2, mapping1, mapping2,
	inputs_numb1, inputs_numb2, outputs_numb1):

	#constructing gate
	#step1: joining 2 circuits
	"""
	The idea behind joining two circuits is, to join the first circuit 
	without any changes but for the second circuit all 
	net numbers except for input nets should be modified.
	"""
	gates = [] #container for all gates in the miter.
	gates = copy.deepcopy(gates1)
	# checking gates in the 2-nd circuit and assigning new net numbers 
	for gate in gates2:
		new_port = []
		for net in gate[1]:
			if (net not in inputs_numb2): #if the net is not an input to the second ckt
				new_port.append(net + nets1)
			else:
				new_port.append(mapping_let_numb1[mapping2[net]]) #determining the id of the input net
		gates.append((gate[0], new_port))
	
	#step2: combining outputs by XOR
	
	"""
	Construction of the XOR gate.
	Since the first circuit placed without any changes to the miter
	its outputs become inputs for the XOR gate.
	We only need to know the second inputs for the XOR gate which are nothing but outputs of second circuit.
	To find it out, we need to find out the new values of the second circuits'
	outputs.
	The output of the XOR gate is the number greater than the 
	sum of nets in both the circuits. 
	"""
	count_new_XOR = 1;
	xor_outputs = [] #XORs' outputs. Needed for ORing
	for output in outputs_numb1: 
		new_port = []
		new_port.append(output) #the first XOR's input
		new_port.append(mapping_let_numb2[mapping1[output]] + nets1) #the second XOR's input
		new_port.append(nets1 + nets2 + count_new_XOR) #XOR's output
		gates.append(('xor', new_port))
		xor_outputs.append(new_port[2])
		count_new_XOR += 1
		
	
	#step3: ORing all XORs
	"""
	In this step we need to OR all XORs. ORing is not needed 
	if there is only one XOR.
	The more the XORs, more the ORs.
	In this case we continue ORing all the ORs until we get 
	only one OR gate which gives the solution.
	"""
	if (len(xor_outputs) == 1): #only one XOR gate
		return gates
	new_net_numb = nets1 + nets2 + count_new_XOR #new output value for OR gate
	while (len(xor_outputs) != 1):
		input1 = xor_outputs.pop(0) #1-st OR's input
		input2 = xor_outputs.pop(0) #2-nd OR's input
		new_port = [input1, input2, new_net_numb] #OR's output
		gates.append(('or', new_port))
		xor_outputs.append(new_net_numb)
		new_net_numb += 1
		
	
	return gates

def cnf_initial(miter):
	"""
	Since we have only 4 types of gates we know
	how the cnf looks like for each gate. To build the cnf for
	the whole miter we need to build cnfs for each 
	gate in the miter and combine them.
	"""
	cnf_init  = [ ]
	final_net = 0 #the last unit clause net.
	for gate in miter:
		if (gate[0] != 'inv'): 
			inp1 = gate[1][0]
			inp2 = gate[1][1]
			out  = gate[1][2]
			
			if (gate[0] == 'and'):
				cnf_init.append( [inp1, -out] )
				cnf_init.append( [inp2, -out] )
				cnf_init.append( [-inp1,-inp2, out] )
			
			elif (gate[0] == 'or'):
				cnf_init.append( [-inp1, out] )
				cnf_init.append( [-inp2, out] )
				cnf_init.append( [inp1, inp2, -out] )
				final_net = out 
				
			elif (gate[0] == 'xor'):
				cnf_init.append( [inp1, inp2, -out] )
				cnf_init.append( [-inp1, -inp2, -out] )
				cnf_init.append( [-inp1, inp2, out] )
				cnf_init.append( [inp1, -inp2, out] )
				final_net = out
		elif (gate[0] == 'inv'):
			inp = gate[1][0]
			out = gate[1][1]
			cnf_init.append( [inp, out] )
			cnf_init.append( [-inp, -out] )
		else:
			print("No such gate")
			sys.exit(0)
	
	cnf_init.append([final_net])
	return cnf_init


def Putnam(cnf):
	"""
	Davis Putnam algorithm based is on recursion.
	This implementation has not considered the pure literal rule,
	because of the following observations made: 
	1. Pure literal rule is very rarely applicable (as there is very little chance 
	of the literal being present only in pure form )
	2. As the purpose of pure literal is to just speed up runtime of the davis putnam algorithm, it does not affect the final result.
	"""
	#unit clause rule
	for clause in reversed(cnf):
		if len(clause) == 1:
			reduce_cnf(cnf, clause[0])
			return Putnam(cnf)
	
	#terminal conditions
	if len(cnf) == 0: 	#empty cnf case
		solution(1)   	#solution found
		sys.exit(0) 	#terminate the algorithm
	if [] in cnf: 		#empty clause case
		return 0
	
	cnf1 = copy.deepcopy(cnf)
	cnf0 = copy.deepcopy(cnf)
	variable = cnf[-1][-1] #last literal in the last clause of the cnf
	return (Putnam(reduce_cnf(cnf0, variable)) or Putnam(reduce_cnf(cnf1,-variable)))
	

def reduce_cnf(cnf, net_numb):
	"""
	This function sets 1 or 0 to a given literal of the cnf
	and simplifies the given cnf.
	Also, we add the literal and it's value to the counter_example
	dictionary for the counter example.
	"""

	if (net_numb < 0):                  #perform to check in which form(positive or negative) the literal is present.
		counter_example[-net_numb] = 0  #setting the positive variation of the literal to zero
	else:
		counter_example[net_numb] = 1

	for net in reversed(cnf):
		if ( net.count(net_numb) ): #when a literal is set to one, entire clause is removed.
			cnf.remove(net)
		elif (net.count(-net_numb)): #when a literal is set to zero only the literal is removed.
			net.remove(-net_numb)
	return cnf		
	
	
def solution(putnam_result):
	"""
	This function provides the final result based on 
	the output of Putnam algorithm.
	"""
	if putnam_result == 1:
		print('Not eqiuvalent! Counter example:')
		print('Inputs:')
		for input in inputs_numb1:
			print(mapping1[input] , ':', counter_example[input])
		print('Outputs netlist 1:')
		for output in outputs_numb1:
			print(mapping1[output], ':', counter_example[output])	
		print('Outputs netlist 2:')
		for output in outputs_numb2:
			print(mapping2[output]aw, ':', counter_example[output + nets1])
	else:
		print('Equivalent!')
  
# read netlists
inputs1, inputs_numb1, outputs1, outputs_numb1, mapping1, gates1, nets1, mapping_let_numb1 = readNetlist(open(sys.argv[1],"r"))
inputs2, inputs_numb2, outputs2, outputs_numb2, mapping2, gates2, nets2, mapping_let_numb2 = readNetlist(open(sys.argv[2],"r"))
counter_example = {}  #dictionary containing the counter example
miter_gates = miter(nets1, nets2, gates1,gates2, mapping_let_numb1, mapping_let_numb2, mapping1, mapping2,
	inputs_numb1, inputs_numb2, outputs_numb1) #miter
cnf = cnf_initial(miter_gates) #initial cnf
solution(Putnam(cnf))
