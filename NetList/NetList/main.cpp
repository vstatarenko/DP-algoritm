/*
* Equivalence Checker for netlists
*
*
* Name 1: ...
* Matriculation Number 1: ...
*
* Name 2: ...
* Matriculation Number 2: ...
*
*/

#include <stdio.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <map>
#include <string>
#include <cstdlib>

using namespace std;

typedef enum
{
	AND,
	OR,
	INV,
	XOR,
	ZERO,
	ONE,
	UNDEFINED
} GateType;

typedef struct
{
	GateType type;
	vector<int> nets;
} Gate;

typedef vector<Gate> GateList;

int netCount1, netCount2;
vector<string> inputs1, outputs1, inputs2, outputs2;
map<string, int> map1, map2;
GateList gates1, gates2;

int readFile(string filename, int & netCount, vector<string> & inputs, vector<string> & outputs, map<string, int> & map, GateList & gates)
{
	ifstream file(filename.c_str());
	if (!file.is_open())
	{
		cout << " hi" << endl;
		return -1;
	}
	string curLine;
	// net count
	getline(file, curLine);
	netCount = atoi(curLine.c_str());
	// inputs
	getline(file, curLine);
	stringstream inputsStream(curLine);
	string buf;
	while (inputsStream >> buf)
	{
		inputs.push_back(buf);
	}
	// outputs
	getline(file, curLine);
	stringstream outputsStream(curLine);
	while (outputsStream >> buf)
	{
		outputs.push_back(buf);
	}
	// mapping
	for (size_t i = 0; i<inputs1.size() + outputs1.size(); i++)
	{
		getline(file, curLine);
		stringstream mappingStream(curLine);
		mappingStream >> buf;
		int curNet = atoi(buf.c_str());
		mappingStream >> buf;
		map[buf] = curNet;
	}
	// empty line
	getline(file, curLine);
	if (curLine.length() > 1)
	{
		return -1;
	}
	// gates
	while (getline(file, curLine))
	{
		stringstream gateStream(curLine);
		gateStream >> buf;
		Gate curGate;
		curGate.type = (buf == "and" ? AND : buf == "or" ? OR : buf == "inv" ? INV : buf == "xor" ? XOR : buf == "zero" ? ZERO : buf == "one" ? ONE : UNDEFINED);
		if (curGate.type == UNDEFINED)
		{
			return -1;
		}
		while (gateStream >> buf)
		{
			int curNet = atoi(buf.c_str());
			curGate.nets.push_back(curNet);
		}
		gates.push_back(curGate);
	}
	return 0;
}

int readFiles(string filename1, string filename2)
{
	if (readFile(filename1, netCount1, inputs1, outputs1, map1, gates1) != 0)
	{
		return -1;
	}
	if (readFile(filename2, netCount2, inputs2, outputs2, map2, gates2) != 0)
	{
		return -1;
	}
	return 0;
}

// Prints internal data structure
void printData(int & netCount, vector<string> & inputs, vector<string> & outputs, map<string, int> & map, GateList & gates)
{
	cout << "Net count: " << netCount << "\n\n";
	cout << "Inputs:\n";
	for (size_t i = 0; i<inputs.size(); i++)
	{
		cout << inputs[i] << "\n";
	}
	cout << "\n";
	cout << "Outputs:\n";
	for (size_t i = 0; i<outputs.size(); i++)
	{
		cout << outputs[i] << "\n";
	}
	cout << "\n";
	cout << "Mapping (input/output port to net number):\n";
	for (size_t i = 0; i<inputs.size(); i++)
	{
		cout << inputs[i] << " -> " << map[inputs[i]] << "\n";
	}
	for (size_t i = 0; i<outputs.size(); i++)
	{
		cout << outputs[i] << " -> " << map[outputs[i]] << "\n";
	}
	cout << "\n";
	cout << "Gates:\n";
	for (size_t i = 0; i<gates.size(); i++)
	{
		Gate & curGate = gates[i];
		cout << (curGate.type == AND ? "AND" : curGate.type == OR ? "OR" : curGate.type == INV ? "INV" : curGate.type == XOR ? "XOR" : curGate.type == ZERO ? "ZERO" : curGate.type == ONE ? "ONE" : "ERROR");
		cout << ": ";
		for (size_t j = 0; j<curGate.nets.size(); j++)
		{
			cout << curGate.nets[j] << " ";
		}
		cout << "\n";
	}
	cout << "\n";
}

// Prints the internal data structure for netlist 1 or 2
void printDataForNetlist(int netlistNumber)
{
	if (netlistNumber == 1)
	{
		printData(netCount1, inputs1, outputs1, map1, gates1);
	}
	else if (netlistNumber == 2)
	{
		printData(netCount2, inputs2, outputs2, map2, gates2);
	}
	else
	{
		cout << "Invalid netlist number " << netlistNumber << " (must be 1 or 2)\n";
	}
}


//
// Add auxiliary functions here (if necessary)
//


void DP(vector< vector<int> > cnf)
{
	//
	// Add code for Davis Putnam algorithm here
	//
}

int main(int argc, char ** argv)
{
	if (argc != 3)
	{
		cerr << "Wrong argument count!\n";
		system("PAUSE");
		return -1;
	}
	if (readFiles(argv[1], argv[2]) != 0)
	{
		cerr << "Error while reading files!\n";
		cout << netCount1 << endl;
		system("PAUSE");
		return -1;
	}

	// The following global variables are now defined (examples are for file xor2.net):
	//
	// int netCount1, netCount2
	// - total number of nets in netlist 1 / 2
	// - e.g. netCount1 is 3
	//
	// vector<string> inputs1, outputs1, inputs2, outputs2
	// - names of inputs / outputs in netlist 1 / 2
	// - e.g. inputs1[0] contains "a_0"
	//
	// map<string, int> map1, map2
	// - mapping from input / output names to net numbers in netlist 1 / 2
	// - e.g. map1["a_0"] is 1, map1["b_0"] is 2, ...
	//
	// GateList gates1, gates2
	// - list (std::vector<Gate>) of all gates in netlist 1 / 2
	// - e.g.:
	//   - gates1[0].type is XOR
	//   - gates1[0].nets is std::vector<int> and contains three ints (one for each XOR port)
	//   - gates1[0].nets[0] is 1 (first XOR input port)
	//   - gates1[0].nets[1] is 2 (second XOR input port)
	//   - gates1[0].nets[2] is 3 (XOR output port)

	// Print out data structure - (for debugging)
	cout << "Netlist 1:\n==========\n";
	printDataForNetlist(1);
	cout << "\nNetlist 2:\n==========\n";
	printDataForNetlist(2);


	//
	// Add your code to build the CNF.
	// The CNF should be a vector of vectors of ints. Each "inner" vector represents one clause. The "outer" vector represents the whole CNF.
	//
	vector< vector<int> > cnf;

	//
	// Check CNF for satisfiability using the Davis Putnam algorithm
	//
	DP(cnf);

	//
	// Print result
	//
	// ...

	system("PAUSE");
	return 0;
}
