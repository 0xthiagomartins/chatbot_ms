from langchain import LLMChain, SequentialChain, SimpleSequentialChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from typing import Any, List, Optional
import os


class LangChainFactory:
    """
    Factory class to create different types of LangChain chains.
    """

    def __init__(self, llm: Optional[Any] = None):
        """
        Initialize the factory with a language model instance.

        :param llm: An instance of a language model, e.g., OpenAI().
                    If None, a default OpenAI instance will be created.
        """
        if llm is None:
            self.llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            self.llm = llm

    def create_llm_chain(
        self,
        prompt_template: str,
        input_variables: Optional[List[str]] = None,
        output_key: Optional[str] = None,
        **kwargs
    ) -> LLMChain:
        """
        Create an LLMChain with the given prompt template.

        :param prompt_template: The prompt template string.
        :param input_variables: List of input variable names for the prompt.
        :param output_key: Key name for the output in the chain's result.
        :param kwargs: Additional keyword arguments for LLMChain.
        :return: An instance of LLMChain.
        """
        if input_variables is None:
            input_variables = ["input"]
        prompt = PromptTemplate(
            template=prompt_template, input_variables=input_variables
        )
        chain = LLMChain(llm=self.llm, prompt=prompt, output_key=output_key, **kwargs)
        return chain

    def create_sequential_chain(
        self,
        chains: List[LLMChain],
        input_variables: Optional[List[str]] = None,
        output_variables: Optional[List[str]] = None,
        verbose: bool = False,
        **kwargs
    ) -> SequentialChain:
        """
        Create a SequentialChain from a list of chains.

        :param chains: A list of chain instances to be executed in sequence.
        :param input_variables: List of input variable names for the sequential chain.
        :param output_variables: List of output variable names for the sequential chain.
        :param verbose: If True, the chain will print debug information.
        :param kwargs: Additional keyword arguments for SequentialChain.
        :return: An instance of SequentialChain.
        """
        sequential_chain = SequentialChain(
            chains=chains,
            input_variables=input_variables,
            output_variables=output_variables,
            verbose=verbose,
            **kwargs
        )
        return sequential_chain

    def create_simple_sequential_chain(
        self, chains: List[LLMChain], **kwargs
    ) -> SimpleSequentialChain:
        """
        Create a SimpleSequentialChain from a list of chains.

        :param chains: A list of chain instances to be executed in sequence.
        :param kwargs: Additional keyword arguments for SimpleSequentialChain.
        :return: An instance of SimpleSequentialChain.
        """
        simple_sequential_chain = SimpleSequentialChain(chains=chains, **kwargs)
        return simple_sequential_chain
