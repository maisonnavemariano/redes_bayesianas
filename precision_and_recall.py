import pickle
def load(file):
	return pickle.load(open(file,'rb'))
noticias = load('noticias_y_relevancia.p')

def precision_and_recall_and_total(umbral):
	business   = 0
	umbral_pos = 0
	union      = 0
	for noticia in noticias:
		if noticia[4] == 'Business':
			business += 1
		if noticia[6]>umbral:
			umbral_pos += 1
		if noticia[6]>umbral and noticia[4]=='Business':
			union += 1
	if umbral_pos == 0:
		return 0, union/business
	return union/umbral_pos, union/business, umbral_pos
print('recall,precision')
maximo = max([noticia[6] for noticia in noticias])
for i in range(0,maximo):
	p,r,t = precision_and_recall_and_total(i)
	print('{},{}'.format(r,p))
	#print('umbral: {}, precision: {}, recall: {} cantidad de noticias: {}/{}'.format(i,p,r,t,len(noticias)))