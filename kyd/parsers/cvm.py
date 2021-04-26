
from . import GenericParser, float_or_none

def handle_row(row, names, parser=lambda x: x):
    fields = [parser(val.strip()) for val in row.split(';')]
    fields = [None if val == '' else val for val in fields]
    row = dict(zip(names, fields))
    cnpj_fundo_str_num = row['cnpj_fundo'].replace('.', '')\
        .replace('/', '').replace('-', '')
    return (cnpj_fundo_str_num, row)


def handle_informes_diarios(row):
    _names = 'CNPJ_FUNDO;DT_COMPTC;VL_TOTAL;VL_QUOTA;VL_PATRIM_LIQ;CAPTC_DIA;RESG_DIA;NR_COTST'
    names = _names.lower().split(';')
    parser = GenericParser()
    return handle_row(row, names, parser.parse)


def handle_info_cadastral(row):
    _names = 'CNPJ_FUNDO;DENOM_SOCIAL;DT_REG;DT_CONST;DT_CANCEL;SIT;DT_INI_SIT;DT_INI_ATIV;DT_INI_EXERC;DT_FIM_EXERC;CLASSE;DT_INI_CLASSE;RENTAB_FUNDO;CONDOM;FUNDO_COTAS;FUNDO_EXCLUSIVO;TRIB_LPRAZO;INVEST_QUALIF;TAXA_PERFM;INF_TAXA_PERFM;TAXA_ADM;INF_TAXA_ADM;VL_PATRIM_LIQ;DT_PATRIM_LIQ;DIRETOR;CNPJ_ADMIN;ADMIN;PF_PJ_GESTOR;CPF_CNPJ_GESTOR;GESTOR;CNPJ_AUDITOR;AUDITOR;CNPJ_CUSTODIANTE;CUSTODIANTE;CNPJ_CONTROLADOR;CONTROLADOR'
    names = _names.lower().split(';')
    vals = handle_row(row, names)
    vals[1]['taxa_perfm'] = float_or_none(vals[1]['taxa_perfm'])
    vals[1]['taxa_adm'] = float_or_none(vals[1]['taxa_adm'])
    vals[1]['vl_patrim_liq'] = float_or_none(vals[1]['vl_patrim_liq'])
    return vals
