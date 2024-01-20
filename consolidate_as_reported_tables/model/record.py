from collections import namedtuple
      
Record = namedtuple('Record', 
            [
                'source',   # source worksheet name 
                'record_type',  # pd.Categorical 'original' or 'base' or 'comp'
                'period',   # column name from source worksheet name
                'row_num',  # row number in the source
                'item',     # item name used as primary key (cleaned from raw_item)
                'raw_item',   # raw item name as is reported from source
                'value',   # cleaned value from raw_value
                'raw_value', # raw value as is reported from source
            ]
        )