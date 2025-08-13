# ruff: noqa: PLR2004
import re


def clean_document_number(value: str) -> str:
    return re.sub(r"[^0-9]", "", value)

def is_valid_cpf(cpf: str) -> bool:
    cpf = clean_document_number(cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for i in range(9, 11):
        s = sum(int(cpf[j]) * ((i+1) - j) for j in range(i))
        d = ((s * 10) % 11) % 10
        if int(cpf[i]) != d:
            return False
    return True

def is_valid_cnpj(cnpj: str) -> bool:
    cnpj = clean_document_number(cnpj)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False
    weight1 = [5,4,3,2,9,8,7,6,5,4,3,2]
    weight2 = [6] + weight1
    for i, weights in enumerate([weight1, weight2]):
        s = sum(int(cnpj[j]) * weights[j] for j in range(len(weights)))
        d = 11 - s % 11
        d = d if d < 10 else 0
        if int(cnpj[12 + i]) != d:
            return False
    return True
