import json
# import openai
import os
import time
from tqdm import tqdm
import numpy as np
import pandas as pd
from dotenv import load_dotenv

class QuestionRetriever():
    """
    Manages dataset question retrieval via vector similarity search.

    Attributes:
        dataset (dict[]): List of dictionaries representing the dataset
        dataset_path (str): Path to .json file containing the dataset.
        include_sql (bool, optional): Whether to include both the question and SQL query in the dataset vectorization or only the question.
                                    Default: True (includes question and SQL)
        vectors_path (str): Path to .npy file containing the dataset vectors.
        vectorize (bool): Whether to vectorize the dataset if vectors are not found at the specified path.
        embedding_model (EmbeddingModel): Embedding model to use for vectorization.
    """
    def __init__(self, dataset_path="", dataset=None, include_sql=True, vectors_path="", vectorize=False, embedding_model=None):
        self.dataset_path = dataset_path
        self.include_sql = include_sql
        # self.environment = environment

        if embedding_model == None:

            from functions.langchain_utils import get_embeddings
            # self.embedding_model_name = "text-embedding-ada-002"

            self.get_embedding = get_embeddings
        else:
           self.get_embedding = embedding_model

        if dataset is None:
            self.dataset = self.load_dataset(self.dataset_path)
        else:
            self.dataset = dataset

        if vectors_path != "" and os.path.isfile(vectors_path):
            try:
                self.dataset_embeddings = self.load_dataset_vectors(vectors_path)
            except:
                if vectorize:
                    print("Could not load dataset vectors. Vectorizing dataset...")
                    self.dataset_embeddings = self.vectorize_dataset()
                else:
                    print("Could not load dataset vectors and \"vectorize\" is set to False.")
        else:
            if vectorize:
                self.dataset_embeddings = self.vectorize_dataset()
            else:
                print("No vectors found and \"vectorize\" is set to False.")

        print(len(self.dataset))
        print(len(self.dataset_embeddings))

    def load_dataset(self, dataset_path):
        """
        Loads dataset from specified path.
        """
        with open(dataset_path, 'r') as f:
            df = pd.read_csv(dataset_path)
            for column in df.columns:
                if "Unnamed: 0" in column:
                    df = df.drop(columns=[column])
            return df

    def vectorize_dataset(self):
        """
        Gets OpenAI embeddings for the entire dataset using the specified model.

        Args:
            dataset_path (str): Path to .json file containing the dataset.
        
        Returns:
            np.array: numpy array containing the dataset vectors
        """

        dataset_embeddings = []

        for dataset_entry in tqdm(list(self.dataset.iterrows())):
            if self.include_sql:
                text_to_encode = f"Question: {dataset_entry[1]['question']}\nSQL: {dataset_entry[1]['sql']}"
            else:
                text_to_encode = dataset_entry[1]["question"]
            dataset_embeddings.append(self.get_embedding(text_to_encode))

        return dataset_embeddings
    
    def load_dataset_vectors(self, file_path):
        """
        Loads the vectorized dataset from the specified path.

        Args:
            file_path (str)
        
        Returns:
            np.array: The dataset vectors
        """
        return np.load(file_path)

    def save_vectors(self, file_path):
        """
        Saves the vectorized dataset to the specified path.

        Args:
            file_path (str)
        """
        np.save(file_path, self.dataset_embeddings)

    def calculate_similarities(self, text_embedding, all_embeddings=[]):
        """
        Calculates the similarity between the input embedding and the embedding of each dataset instance.

        Args:
            text_embedding (float[]): Input vector

        Returns:
            np.array: numpy array containing the similarity of each vector to the input embedding
        """
        
        embeddings = self.dataset_embeddings
        if len(all_embeddings) > 0:
            embeddings = all_embeddings
        similarities = np.dot(embeddings, text_embedding)
        print(similarities.shape)
        return similarities

    def get_similar_examples(self, text="", embedding=None, n=5, as_text=True, threshold=None, filter={}):
        """
        Finds the dataset entries with the highest similarity to the
        input text or embedding.
        Uses embedding if one is specified, otherwise uses text.

        Args:
            text (str): Input text
            embedding (float[]): Input embedding vector
            n (int, optional): Number of entries to return. May return fewer entries depending on threshold. Default: 5
            as_text (bool, optional): Whether to return the results as plain text, ready to be included in prompt.
                If false, returns array of dicts containing question, SQL and similarity. Default: True
            threshold (float): Minimum desired similarity values. If specified, will only return entries with
                similarity >= threshold. Default: None
            filter_param (dict): a dict mapping filter parameters to values to filter by (key, value) . Ex.: {'entity': ['value_1', 'value_2']}. Default {}
        
        Returns:
            One of:
            str: String containg question and SQL query from each query
            or
            dict[]: List of dataset entries, as formatted in the dataset
        """
        
        embeddings = self.dataset_embeddings 
        dataset = self.dataset
      
        if embedding is None:
            embedding = self.get_embedding(text)
 
        if filter != {}:
            dataset, embeddings = self.filter_dataset(filter)

        question_similarities = self.calculate_similarities(embedding, embeddings)

        similar_vector_indices = np.flip(np.argsort(question_similarities)[-n:])

        if threshold is not None:
            amount_above_threshold = (question_similarities > threshold).sum()
            similar_vector_indices = similar_vector_indices[:amount_above_threshold]

        similar_questions = dataset.loc[similar_vector_indices]


        if as_text:
            examples_string = ""

            for question in similar_questions.iterrows():
                instance_index = question[0]
                examples_string += f"Question: {dataset.iloc[instance_index]['question']}\n"
                # examples_string += f"Entity: {dataset.iloc[instance_index]['entity']}\n"
                examples_string += f"{dataset.iloc[instance_index]['sql']}\n\n"

            return examples_string
        else:
            examples = []

            for i,question in enumerate(similar_questions.iterrows()):
                instance_index = question[0]
                instance = dataset.loc[instance_index].to_dict()
                instance["similarity"] = question_similarities[similar_vector_indices[i]]

                examples.append(instance)

            return examples
        
        
    def get_similar_entries_by_index(self, index, n=5, as_text=True, threshold=None, filter={}):
        """
        Finds the dataset entries with the highest similarity to
        the entry at the specified index.

        Args:
            index (nit): Index of input entry
            n (int, optional): Number of entries to return. Default: 5
            as_text (bool, optional): Whether to return the results as plain text, ready to be included in prompt. Default: True
            filter_param (dict): a dict mapping filter parameters to values to filter by (key, value) . Ex.: {'entity': ['value_1', 'value_2']}. Default {}
        """
        text = self.dataset.iloc[index]["question"]
        embedding = self.dataset_embeddings[index]
        print("Question: " + text)
        return self.get_similar_examples(embedding=embedding, n=n, as_text=as_text, threshold=threshold, filter=filter)
    

    def remove_duplicates(self):
        """
        Removes duplicate dataset entries.
        """
        indices_to_keep = self.dataset.duplicated(keep='first').apply(lambda x: not x).to_numpy()
        self.dataset = self.dataset.drop_duplicates(ignore_index=True)
        self.dataset_embeddings = np.array(self.dataset_embeddings).reshape((len(self.dataset_embeddings), -1))[indices_to_keep]
        # np.save(EMBEDDINGS_FILE_RESULT, embeddings)
        # dataset_df.to_csv(DATASET_FILE_RESULT)
        
    def filter_dataset(self, filter_param={}):
        """
        Filters dataset based on specified criteria.
        
        Args:
            filter_param (dict): a dict mapping filter parameters to values to filter by (key, value) . Ex.: {'entity': ['value_1', 'value_2']}
            
        Returns:
            np.array (tuple): the filtered dataset and numpy array filtered containing the dataset vectors
        """
        try:
            key, values = list(filter_param.items())[0]
            filtered_df = self.dataset[self.dataset[key].str.lower().isin([v.lower() for v in values])].reset_index(drop=True)
            filtered_embeddings = self.dataset_embeddings[filtered_df.index]
            return filtered_df, filtered_embeddings
        except:
           raise Exception("Invalid filter parameter or key error")
           
        