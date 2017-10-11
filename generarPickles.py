# =========== TIME ===========
import time
start = time.time()
# ========= END_TIME =========
INPUT = '../../dataset/noticias2013_reducido'
INPUT_TERMINOS_ECONOMICOS = '../../dataset/terminos_economicos_the_economist.txt'

#OUT
pickle_lista_noticias_term_econ = 'noticia_term_econ.p'
noticias_pickle = 'lista_noticias.p'
term_econ_pickle = 'lista_terminos_economicos.p'
pickle_union = 'diccionario_union.p'
pickle_cardinalidad = 'diccionario_cardinalidad.p'
# ================ FILTER ================
import pickle

def list_in_list(l1,l2):
	if len(l1)>len(l2):
		print('[WARNING] l1 es más larga que l2 (list_in_list method).')
	for i in range(0,len(l2)-len(l1)+1):
		if (l2[i:i+len(l1)] == l1  ):
			return True
	return False

from bs4 import BeautifulSoup
import re
from nltk import word_tokenize
print('[INFO] Definimos método para filtrar html a través de la librería bs4 (BeautifulSoup).')
def clean_html(texto):
	texto = re.sub('&apos;',"'",texto)
	texto = re.sub('&quot;','"',texto)
	return BeautifulSoup(texto,'html.parser').get_text()

stopwords_list = []
from nltk.corpus import stopwords
stop_words_file = '../../dataset/stopwords.txt'
print('[INFO] Leemos corpus de stopwords de nltk y del archivo {}'.format(stop_words_file))
stopwords_list = stopwords.words('english')
stopwords_list += open(stop_words_file,'r',encoding='utf-8').read().splitlines()
stopwords_list = list(set(stopwords_list))

def filter_stopwords(lista_palabras):
	return [palabra for palabra in lista_palabras if not palabra in stopwords_list]

print('[OK] Definimos un filtro de noticias que: transforma enteros en enteros, elimina html de titulo y cuerpo, tokeniza tanto titulo como cuerpo y le elimina las stopwords')
def filter_new(noticia):
	id     = int(noticia[0])
	fecha  = noticia[1]
	titulo = clean_html(noticia[2])
	texto  = clean_html(noticia[3])
	lista_palabras = word_tokenize(titulo) + word_tokenize(texto)
	lista_palabras = [palabra.lower() for palabra in lista_palabras]
	lista_palabras = filter_stopwords(lista_palabras)
	return (id,fecha,titulo,texto,lista_palabras)
# ========= END_FILTER_FUNCTIONS =========
print('========================== PASO 1 ==========================')
print('[OK] Primero leemos las noticias del año 2013 de The Guardian.')
try:
	print('[OK] Intentamos leer pickle de noticias: {}.'.format(noticias_pickle))
	noticias = pickle.load(open(noticias_pickle, 'rb'))
	print('[OK] Pickle leído correctamente.')
except:
	print('[WARNING] Pickle no encontrado, procedemos a leer archivo: {}.'.format(INPUT))
	lines = open(INPUT,'r',encoding='utf-8').read().splitlines()
	def get_feature(lines,feature):
		return [line[len(feature):] for line in lines if line.startswith(feature)]
	titulos      = get_feature(lines, 'webTitle: ')
	textos       = get_feature(lines, 'bodytext: ')
	fechas       = get_feature(lines, 'webPublicationDate: ')
	instance_nro = get_feature(lines, 'instanceNro: ')
	print('[OK] Archivo leído.')
	noticias = list(zip(instance_nro,fechas,titulos,textos))
	#FILTER
	print('[OK] Comenzamos filtrado y construcción de un única lista de palabras por noticia (word_tokenize,clean_html, filtrado de stopwords).')
	noticias = [filter_new(noticia) for noticia in noticias]
	pickle.dump(noticias,open(noticias_pickle,'wb'))
	print('[OK] Pickle de noticias generado (id,fecha,titulo,texto,lista_palabras) (archivo: {}).'.format(noticias_pickle))

print('[INFO] cantidad de noticias: {}'.format(len(noticias)))

print('========================== PASO 2 ==========================')
print('[OK] Leemos terminos economicos.')

try:
	print('[OK] Leemos pickle con terminos economicos presentes en el corpus de noticias (archivo: {}).'.format(term_econ_pickle))
	terminos_economicos = pickle.load(open(term_econ_pickle, 'rb'))
	print('[OK] Picke leído correctamente.')
except:
	print('[WARNING] Pickle no encontrado, leemos terminos economicos del archivo: {}.'.format(INPUT_TERMINOS_ECONOMICOS))
	terminos_economicos = open(INPUT_TERMINOS_ECONOMICOS,'r',encoding='utf-8').read().splitlines()
	terminos_economicos = [termino.lower().split(' ') for termino in terminos_economicos]

	def exist_in_corpus(termino):
		return any(list_in_list(termino,noticia[4]) for noticia in noticias)
	print('[OK] Filtramos términos economicos que no aparecen en el corpus de noticias.')
	terminos_economicos = [termino for termino in terminos_economicos if exist_in_corpus(termino)]
	print('[OK] Generamos el picke de términos económicos.')
	pickle.dump(terminos_economicos, open(term_econ_pickle,'wb'))
	print('[OK] Pickle generado correctamente.')

print('[INFO] cantidad de términos ecónomicos en el corpus: {}'.format(len(terminos_economicos)))

economic_first_word = set([term_econ[0] for term_econ in terminos_economicos])

def longest_list(lista_de_listas):
	if len(lista_de_listas) == 0:
		return []
	mayor = 0
	for index in range(0,len(lista_de_listas)):
		elem     = lista_de_listas[index]
		anterior = lista_de_listas[mayor]
		if len(elem)>len(anterior):
			mayor = index
	return lista_de_listas[mayor]

def filter_non_economic(lista_palabras):
	to_return_list = []
	index = 0
	for palabra in lista_palabras:
		if palabra in economic_first_word:
			candidatos = []
			for econ_term in terminos_economicos:
				if index + len(econ_term) <= len(lista_palabras) and econ_term == lista_palabras[index: (index + len(econ_term))]:
					candidatos.append(econ_term)
			lista_mas_larga = longest_list(candidatos)
			if len(lista_mas_larga)>0:
				to_return_list.append(lista_mas_larga)
		index += 1
	return to_return_list


print('========================== PASO 3 ==========================')
print('[OK] Leemos noticias con la lista de palabras filtradas para que solo haya palabras economicas (id,fecha,titulo,texto,lista_palabras_economicas).')
print('[INFO] La lista de palabras económicas es una lista de términos, donde cada término puede tener más de una palabra (lista de listas).')

try:
	print('[OK] Intentamos leer las noticias con filtro de palabras económicas directamente del pickle : {}.'.format(pickle_lista_noticias_term_econ))
	noticias = pickle.load(open(pickle_lista_noticias_term_econ,'rb'))
	print('[OK] Pickle leído correctamente.')
except:
	print('[WARNING] Pickle no encontrado, filtramos las noticias que ya teníamos para eliminar todas palabras no económicas de la lista de palabras.')
	noticias = [(id,fecha,titulo,texto,filter_non_economic(lista_palabras) ) for (id,fecha,titulo,texto,lista_palabras) in noticias]
	print('[OK] Generamos pickle de noticias con palabras no económicas fitlradas (archivo: {}).'.format(pickle_lista_noticias_term_econ))
	pickle.dump(noticias,open(pickle_lista_noticias_term_econ,'wb'))
	print('[OK] Pickle generado correctamente.')


indice_terminos = [tuple(term) for term in terminos_economicos]
inverse_index   = dict([(palabra,indice) for (indice,palabra) in enumerate(indice_terminos)] )

print('[INFO] La cantidad de noticias leídas es la misma que antes: {}'.format(len(noticias)))

print('========================== PASO 4 ==========================')
def cant_documentos(lista_palabras):
	lista_palabras = [list(elem) for elem in lista_palabras]
	count = 0
	for noticia in noticias:
		if all(palabra in noticia[4] for palabra in lista_palabras):
			count += 1
	return count


print('[OK] Intentamos crear el diccionario de la union.')

try:
	print('[OK] Intentamos leer el pickle de la union (archivo: {}).'.format(pickle_union))
	union = pickle.load(open(pickle_union,'rb'))
except:
	print('[WARNING] Pickle no encontrado.')
	union = {}
	print('[OK] creando diccionario con la union.')
	for row in range(0,(len(indice_terminos)-1)):
		print('row {}/{}'.format(row,len(indice_terminos) -1))
		for column in range(row+1,len(indice_terminos)):
			valor_union = cant_documentos([indice_terminos[row],indice_terminos[column]])
			union[(row,column)] = valor_union
			union[(column,row)] = valor_union
	pickle.dump(union,open(pickle_union,'wb'))

print('========================== PASO 5 ==========================')
print('[OK] Intentamos obtener la frecuencia de cada termino economico.')
from collections import defaultdict
try:
	print('[OK] Intentamos leer pickle: {}'.format(pickle_cardinalidad))
	cardinalidad = pickle.load(open(pickle_cardinalidad,'rb'))
except:
	print('[WARNING] Pickle no encontrado, se procede a calcular la cardinalidad para cada termino.')
	cardinalidad = defaultdict(int)
	for termino in indice_terminos:
		frec = cant_documentos([termino])
		cardinalidad[inverse_index[termino]] = frec
	pickle.dump(cardinalidad,open(pickle_cardinalidad,'wb'))


# =========== TIME ===========
end = time.time()
print('tiempo transcurrido: '+str(end-start)+' secs.')
# ========= END_TIME =========
