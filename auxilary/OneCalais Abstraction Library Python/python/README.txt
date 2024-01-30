OneCalais Abstraction Layer , Python Sample Code


Setup your environment.
1. unzip the package and install it by writing: python setup.py install
2. install third party library: rdflib

The purpose of this code is to give an easy way to parse and XML/RDF and to populate it in a simple and intuitive objects structure.
The calaisModel class has some static methods for creating a Model class from RDF files, It is intended use is as a base class from which CalaisModel can be derived.

A simple code for creating a Model instance from RDF file.


from calaisModel import CalaisModel
from collections import defaultdict
from pprint import pprint
import pdb


#fname = r'C:\_projects\calaisModel\sample\20100119-nVMN2D0Mdn_xml.xml'
#cm = CalaisModel(fname)

SNIPPET_HALF_SIZE = 200
WINDOW_SIZE = 50


class CalaisModel:

	def __init__(self, filepath):
		self.calaisModel = CalaisModel(filepath)

	def getDocText(self):
		docinfo = self.calaisModel.getCalaisObjectByType(u'http://s.opencalais.com/1/type/sys/DocInfo')[0]
		return docinfo.getLiterals()[u'http://s.opencalais.com/1/pred/document'][0]

	def getCompanies(self):
		ret = list()
		comps = self.calaisModel.getCalaisObjectByType(u'http://s.opencalais.com/1/type/em/e/Company')
		for comp in comps:
			dcomp = dict()
			ret.append(dcomp)
			literals = comp.getLiterals()
			dcomp['name'] = literals['http://s.opencalais.com/1/pred/name'][0]
			try:
				dcomp['confidence'] = literals['http://s.opencalais.com/1/pred/confidencelevel'][0]
			except:
				pass
			brs = comp.getBackReferences()
			if 'http://s.opencalais.com/1/pred/subject' in brs:
				subjs = brs['http://s.opencalais.com/1/pred/subject']
				resolved_company = None
				if 'http://s.opencalais.com/1/type/er/Company' in subjs:
					resolved_company = subjs['http://s.opencalais.com/1/type/er/Company'][0]
					literals = resolved_company.getLiterals()
					dcomp['resolution'] = dict()
					dcomp['resolution']['name'] = literals['http://s.opencalais.com/1/pred/name'][0]
					dcomp['resolution']['commonname'] = literals['http://s.opencalais.com/1/pred/commonname'][0]
					dcomp['resolution']['permid'] = literals['http://s.opencalais.com/1/pred/permid'][0]
					dcomp['resolution']['score'] = literals['http://s.opencalais.com/1/pred/score'][0]
				insts = subjs['http://s.opencalais.com/1/type/sys/InstanceInfo']
				dcomp['instances'] = list()
				for inst in insts:
					literals = inst.getLiterals()
					exact = literals['http://s.opencalais.com/1/pred/exact'][0]
					length = literals['http://s.opencalais.com/1/pred/length'][0]
					offset = literals['http://s.opencalais.com/1/pred/offset'][0]
					dcomp['instances'].append({'exact':exact, 'length':length, 'offset':offset})
				if 'http://s.opencalais.com/1/type/sys/RelevanceInfo' in subjs:
					relInfo = subjs['http://s.opencalais.com/1/type/sys/RelevanceInfo'][0]
					if 'http://s.opencalais.com/1/pred/relevance' in relInfo.getLiterals():
						dcomp['relevance'] = relInfo.getLiterals()['http://s.opencalais.com/1/pred/relevance'][0]
		return ret

	# company: 'http://s.opencalais.com/1/type/em/e/Company'
	# person: 'http://s.opencalais.com/1/type/em/e/Person'
	def getEntities(self, ent_id):
		ret = list()
		ents = self.calaisModel.getCalaisObjectByType(ent_id)
		for ent in ents:
			dent = dict()
			ret.append(dent)
			literals = ent.getLiterals()
			dent['name'] = literals['http://s.opencalais.com/1/pred/name'][0]
			try:
				dent['confidence'] = literals['http://s.opencalais.com/1/pred/confidencelevel'][0]
			except:
				pass
			brs = ent.getBackReferences()
			if 'http://s.opencalais.com/1/pred/subject' in brs:
				subjs = brs['http://s.opencalais.com/1/pred/subject']
				insts = subjs['http://s.opencalais.com/1/type/sys/InstanceInfo']
				dent['instances'] = list()
				for inst in insts:
					literals = inst.getLiterals()
					exact = literals['http://s.opencalais.com/1/pred/exact'][0]
					length = literals['http://s.opencalais.com/1/pred/length'][0]
					offset = literals['http://s.opencalais.com/1/pred/offset'][0]
					dent['instances'].append({'exact':exact, 'length':length, 'offset':offset})
		return ret

	@staticmethod
	def createOffsetToEntityMap(ents):
		ret = dict()
		for ent in ents:
			insts = ent['instances']
			for inst in insts:
				ret[int(inst['offset'])] = ent
		return ret

	@staticmethod
	def getIntersectingEntities(start, end, o2e, offset, doctext):
		ients = set()
		ents_offsets = set(o2e.keys())
		valid_range = set(range(start, end))
		isect = ents_offsets.intersection(valid_range)
		for idx in isect:
			if '\n\n' in doctext[offset:idx]: continue
			if '\n\n' in doctext[idx:offset]: continue
			ent = o2e[idx]
			if 'resolution' in ent:
				ients.add((ent['name'], ent['resolution']['permid']))
			else:
				ients.add((ent['name'], ''))
		return ients

	@staticmethod
	def getEntitiesInVicinity(offset, length, o2e, doctext, window_size=WINDOW_SIZE):
		ret = list()
		ients = set()
		start = offset - window_size if offset - window_size > 0 else 0
		ients.update(getIntersectingEntities(start, offset, o2e, offset, doctext))
		end = offset + length + window_size
		ients.update(getIntersectingEntities(offset+length, end, o2e, offset, doctext))
		if ients:
			start = offset - SNIPPET_HALF_SIZE if offset - SNIPPET_HALF_SIZE > 0 else 0
			end = offset + length + SNIPPET_HALF_SIZE
			snippet = doctext[start:end]
			for ient in ients:
				ret.append((ient[0], ient[1], snippet))
		return ret

	@staticmethod
	def getTermsInVicinity(offset, length, reg_pats, doctext, window_size=WINDOW_SIZE):
		ret = list()
		start = offset - window_size if offset - window_size > 0 else 0
		end = offset + length + window_size
		for pat in reg_pats:
			m = pat.search(doctext[start:end])
			if m:
				match = m.group()
				match_offset = m.start() + start
				if '\n\n' in doctext[offset:match_offset]: continue
				if '\n\n' in doctext[match_offset:offset]: continue
				start_snippet = offset - SNIPPET_HALF_SIZE if offset - SNIPPET_HALF_SIZE > 0 else 0
				end_snippet = offset + length + SNIPPET_HALF_SIZE
				snippet = doctext[start_snippet:end_snippet]
				ret.append((match, snippet))
		return ret

	@staticmethod
	def ppd(x):
		pprint(dict(x))
