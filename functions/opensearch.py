import pandas as pd
import numpy as np
from langchain_core.documents import Document
from langchain_community.vectorstores import OpenSearchVectorSearch
from opensearchpy import RequestsHttpConnection, AWSV4SignerAuth
import time  
from langchain_core.documents import Document


class OpenSearch:

	CHUNK_SIZE = 500

	def __init__(self, url, username, password, index, env="tec"):
		if "tec" in env:
			from functions.langchain_utils import get_embeddings

		elif "pt" in env:

			from functions.chatgpt_utils import get_embeddings
		else:
			raise Exception("Env not defined or not found")

		self.get_embeddings = get_embeddings

		self.client = self.get_client(url, username, password, index)
		self.index = index

	# def __init__(self, client, index):
	# 	self.client = client
	# 	self.index = index


	def get_client(self, url, username, password, index):
		return OpenSearchVectorSearch(
			index_name=index,
			embedding_function=None,
			opensearch_url=url,
			http_auth=(username, password),
			use_ssl=True,
			verify_certs=False       
		)
	
	def search(self, embedding, number_of_samples=8):
		return self.client.similarity_search_by_vector(embedding, k=number_of_samples, vector_field="vector")


	def search(self, text:str, number_of_samples=8):
		embedding = self.get_embeddings(text)
		return self.client.similarity_search_by_vector(embedding, k=number_of_samples, vector_field="vector")

	def get_similar_examples(self, text="", embedding=None, n=5, as_text=True, threshold=None, filter={}):
		if text!="" and embedding==None:
			result = self.search(text, n)
		elif embedding!=None:
			result = self.search(embedding, n)

		if as_text:
			examples = ""
			for r in result:
				examples += f"Question: {r.page_content}\n"
				# examples += f"Entity: {r.metadata['entity_0']}\n"
				examples += f"{r.metadata['sql']}\n\n"
		else:
			examples = []
			for r in result:
				data = {"question": r.page_content, 'sql': r.metadata['sql'], 'entity': r.metadata['entity_0']}
				examples.append(data)

		return examples

	def get_similar_keywords_question_examples(self, text="", embedding=None, n=5, as_text=True, threshold=None, filter={}):
		if text!="" and embedding==None:
			result = self.search(text, n)
		elif embedding!=None:
			result = self.search(embedding, n)

		if as_text:
			examples = ""
			for r in result:
				examples += f"Question: {r.page_content}\n"
				examples += f"Entity: {self.__process_entity(r.metadata)}\n\n"

		else:
			examples = []
			for r in result:
				data = {"question": r.page_content, 'sql': r.metadata['sql'], 'entity': self.__process_entity(r.metadata)}
				examples.append(data)

		return examples

	def add_documents(self, documents):

		docs_embeddings = []
		metadatas = []
		for d in documents:
			docs_embeddings.append([d['page_content'], self.get_embeddings(d['page_content'])])
			metadatas.append(d['metadata'])
	
		self.add(docs_embeddings, metadatas)
	
	def add(self, docs_embeddings, metadatas):

		for chunk in self.__chunk_list(docs_embeddings, metadatas):
			self.client.add_embeddings(text_embeddings=chunk[0], metadatas=chunk[1], vector_field="vector")
		print("Inserted")

	def __chunk_list(self, data, metadata):
		TOTAL = len(data)
		for i in range(0, TOTAL, OpenSearch.CHUNK_SIZE):
			yield data[i:i + OpenSearch.CHUNK_SIZE], metadata[i:i + OpenSearch.CHUNK_SIZE]


	def __process_entity(self, document):

		entity_key = 'entity_'
		t_attr = len(document.keys())-2
		i = 0
		keywords = ""
		while i < t_attr:
			key = f"{entity_key}{str(i)}"
			value = document.get(key, None)
			if value != None:
				keywords += f"{value} "
			else:
				break
			i+=1
		return keywords


if __name__ == "__main__": 
	## Test OpenSearch
	# user = "mondial_all"
	# password = ""
	# url = "https://beatriz.tecgraf.puc-rio.br:9200"
	# index = "mondial-scheduler"


	# op =  OpenSearch(url, user, password, index, "tec")


	# print(len(op.get_embeddings("cuba")))

	# result = op.search("cuba", number_of_samples=5)
	# print(result[0])
 print("Done")