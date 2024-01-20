def clean_column_headings(data_df):
    """
    THIS FUNCTION'S IMPLEMENTATION MAY VARY DEPENDING ON SOURCE
    
    MAKES FIRST COLUMN'S NAME TO BE 'item'
    
    for Samchully
    change 'Unnamed: 0' to 'item' in the heading
    """
    df = data_df.copy()
    column_headings = df.columns.tolist()
    if column_headings[0] == 'Unnamed: 0':
        column_headings[0] = 'item'
        df.columns = column_headings
    return df
