#!/usr/bin/python3
import networkx as nx
MiGrafo = nx.DiGraph()


cardinalidad_pickle        = 'diccionario_cardinalidad.p'
union_pickle               = 'diccionario_union.p'
terminos_economicos_pickle = 'lista_terminos_economicos.p'


umbral = 0.95
con_prob1 = True

import pickle
def load(file):
	return pickle.load(open(file,'rb'))
def dump(obj, file):
	pickle.dump(obj,open(file,'wb'))

cardinalidad        = load(cardinalidad_pickle)
union               = load(union_pickle)
terminos_economicos = load(terminos_economicos_pickle)
vertices_agregados = set()


def add_vertex(index):
	if not index in vertices_agregados:
		etiqueta = " ".join(terminos_economicos[index])
		MiGrafo.add_node(index,label=str(etiqueta))
		vertices_agregados.add(index)

# Construimos arcos
for row in range(0,len(terminos_economicos)-1):
	for column in range(row+1,len(terminos_economicos)):
		index1 = row
		index2 = column

		term1  = tuple(terminos_economicos[index1])
		term2  = tuple(terminos_economicos[index2])

		val1   = union[(index1,index2)]/cardinalidad[index1] # T1 -> T2
		val2   = union[(index1,index2)]/cardinalidad[index2] # T2 -> T1

		if max(val1,val2)>0.8  and ((max(val1,val2)!=1.0) or con_prob1)  and cardinalidad[index1]>1 and cardinalidad[index2]>1:
			add_vertex(index1)
			add_vertex(index2)
			if val1>val2:
				print('{} --> {}: {}  ({}/{})'.format(term1,term2,val1,union[(index1,index2)],cardinalidad[index1]))
				MiGrafo.add_edge(index1,index2,weight=val1)
			else:
				print('{} --> {}: {}  ({}/{})'.format(term2,term1,val2,union[(index1,index2)],cardinalidad[index2]))
				MiGrafo.add_edge(index2,index1,weight=val2)

dump(MiGrafo,'MiGrafo.p')
