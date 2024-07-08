##### LIBRARY #####
import re
import pandas as pd


##### FUNCTIONS #####
def remove_comments(view_definition):
    # split text into lines
    lines = view_definition.split('\n')
    # remove comment
    cleaned_lines = [line.split('--')[0] for line in lines]
    cleaned_lines = [line.split('#')[0] for line in cleaned_lines]
    # return cleaned view definition
    return '\n'.join(cleaned_lines)

def extract_sources(text):
    # define pattern to search
    pattern = re.compile(r'\b(from|join)\b', re.IGNORECASE)
    # find matches
    matches = pattern.finditer(text)
    # iterate through matches to find sources
    sources = []
    for match in matches:
        # extract text
        start_index = match.end()
        source = text[start_index:].strip().split()[0]
        # clean #1: remove symbols
        if '`' in source:
            parts = source.split('`')
            if len(parts) > 2:
                source = parts[1]
        source = re.sub(r'[^a-zA-Z0-9._]', '', source)
        # clean #2: remove project name 
        parts = source.split('.')
        if len(parts) > 2:
            source = '.'.join(parts[-2:])
        # clean #3: append only if it's not cte
        parts = source.split('.')
        if len(parts) == 2:
            sources.append(source)
    # return sources
    return sources

def get_edges(df_raw):
    df_raw_ = df_raw.copy()
    # remove comments and extract sources
    df_raw_['view_definition_wo_comments'] = df_raw_['view_definition'].apply(remove_comments)
    df_raw_['sources'] = df_raw_['view_definition_wo_comments'].apply(extract_sources)
    df_raw_ = df_raw_.explode('sources')[['table_name', 'sources']].rename(columns={'table_name': 'table', 'sources': 'source'})
    # add scheme in front of table
    df_raw_['table'] = df_raw_['table'].apply(lambda x: 'defi_bi.' + x)
    # remove _v and _t
    df_raw_['table'] = df_raw_['table'].apply(lambda x: x[:-2] if x.endswith('_v') or x.endswith('_t') else x)
    df_raw_['source'] = df_raw_['source'].apply(lambda x: x[:-2] if x.endswith('_v') or x.endswith('_t') else x)
    df_raw_.drop_duplicates(inplace=True)
    # return processed data
    return df_raw_

def get_nodes(df_edges):
    df_edges_ = df_edges.copy()
    all_tables = set(df_edges_['table'])
    all_sources = set(df_edges_['source'])
    all_tables_sources = all_tables.union(all_sources)
    # classify table type
    results = []
    for ts in all_tables_sources:
        if ts in all_tables and ts in all_sources:
            results.append({'table': ts, 'type': 'default'})
        elif ts in all_sources:
            results.append({'table': ts, 'type': 'input'})
        else:
            results.append({'table': ts, 'type': 'output'})
    df_result = pd.DataFrame(results)
    # return node
    return df_result

def get_lineage(df_edges, selected_table):
    # initiate process
    prev_left = df_edges.copy()
    prev_right = df_edges.copy()
    left = df_edges[(df_edges.table==selected_table)].copy()
    right = df_edges[(df_edges.source==selected_table)].copy()
    # iterate to find left lineage
    while prev_left.shape != left.shape:
        prev_left = left.copy()
        left = pd.concat([left, df_edges[(df_edges.table.isin(prev_left.source))].copy()]).drop_duplicates()
    # iterate to find right lineage
    while prev_right.shape != right.shape:
        prev_right = right.copy()
        right = pd.concat([right, df_edges[(df_edges.source.isin(prev_right.table))].copy()]).drop_duplicates()
    # combine left and right
    df_lineage = pd.concat([left,right]).drop_duplicates()
    return df_lineage.sort_values(['table', 'source'])