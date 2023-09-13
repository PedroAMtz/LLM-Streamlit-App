from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader

def langchain_pdf_reader(pdf_file: str) -> list:

    """_Function that utilizes langchain text splitter
        to extract text from a pdf file_

    Returns
    -------
    _list_
        _The text as string stored in a list_
    """
    try:
        pdf_reader = PdfReader(pdf_file)

        text = ""
        context = []

        for page in pdf_reader.pages:
            text += page.extract_text()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=200, length_function=len)
            chunks = text_splitter.split_text(text=text)
            context.append(chunks)
        return context[-1]
    except NameError:
        pass       

if __name__ == "__main__":

    pdf_file = "GPC_DM.pdf"
    text_extracted = langchain_pdf_reader(pdf_file=pdf_file)
    print(text_extracted)

    #loader = PyPDFLoader("GPC_DM.pdf")
    #pages = loader.load_and_split()
    #print(pages[0])

