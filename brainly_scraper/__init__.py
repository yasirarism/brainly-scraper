from io import BytesIO
from typing import Union
import requests, html_text
header={'host': 'brainly.co.id', 'content-type': 'application/json; charset=utf-8', 'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0'}
class attachment:
    def __init__(self, url) -> None:
        self.url = url["url"]
        self.content =requests.get(self.url,  stream=True)
        self.size = int(self.content.headers["Content-Length"])
    def download(self, out: bool=False)->Union[BytesIO, None]:
        '''
        :param out: filename -> save as file | boolean -> bytesio/buffer object

        `Example 1``
        ```
        >>> <attachment Object>.download('attachment.png')
        ```
        `Example 2`
        ```
        >>> open('images.jpg','wb').write(<attachment Object>.download().getvalue())
        ```
        '''
        if isinstance(out, str):
            open(out, "wb").write(self.content.content)
        else:
            return BytesIO(self.content.content)
    def __str__(self) -> str:
        return "<[ type: attachment ]>"
    def __repr__(self) -> str:
        return self.__str__()
class answers:
    def __init__(self, json) -> None:
        self.content = json["content"]
        self.attachments = [attachment(x) for x in json["attachments"]]
    def __str__(self) -> str:
        return f"<[ type Text {'& ATTACHMENT' if self.attachments else ''}]>"
    def __repr__(self) -> str:
        return self.__str__()
class question:
    def __init__(self, node) -> None:
        self.content = node["node"]["content"]
        self.attachments:list[attachment] = [attachment(x) for x in node["node"]["attachments"]]
    def __repr__(self) -> str:
        return f"<( QUESTION:1 ATTACHMENT: {self.attachments.__len__()})>"
    def __str__(self) -> str:
        return self.__repr__().__str__()
class content:
    def __init__(self, json: dict) -> None:
        self.question = question(json)
        self.answers = [answers(x) for x in json["node"]["answers"]["nodes"]]
    def __repr__(self) -> str:
        return f"<( QUESTION: 1 ANSWER:{self.answers.__len__()} )>"
    def __str__(self) -> str:
        return self.__repr__().__str__()
def brainly(query:str, first:int,after=None)->list[content]:
    '''
    :param query: keyword
    :param first: length result
    :param after:

    `Example`
    ```python
    >>> from brainly_scraper import brainly
    >>> brain=brainly('1+1')
    #get question && answer
    >>> for i in brain:
    ...     print(f'question: {i.question.content}')
    ...     print(f'attachments: {i.question.attachments}')
    ...     for answ in i.answers:
    ...         print(f'question: {answ.content}')
    ...         print(f'attachments: {answ.attachments}')
    ```
    '''
    body={'operationName': 'SearchQuery', 'variables': {'query': query, 'after': after, 'first': first}, 'query': 'query SearchQuery($query: String!, $first: Int!, $after: ID) {\n\tquestionSearch(query: $query, first: $first, after: $after) {\n\tedges {\n\t  node {\ncontent\n\t\tattachments{\nurl\n}\n\t\tanswers {\n\t\t\tnodes {\ncontent\n\t\t\t\tattachments{\nurl\n}\n}\n}\n}\n}\n}\n}\n'}
    req=requests.post("https://brainly.co.id/graphql/id", headers=header, json=body).json()
    for i in req["data"]["questionSearch"]["edges"]:
        i["node"]["content"] = html_text.parse_html(i["node"]["content"]).text_content()
        for iX in i["node"]["answers"]["nodes"]:
            iX["content"] = html_text.parse_html(iX["content"]).text_content()
    return [content(js) for js in req["data"]["questionSearch"]["edges"]]