import pandas as pd
import numpy as np

from .model.record import Record

from . import clean_format  # custom clean format depending on the source


class Read_Excel_Input:  
    def __init__(self, input_excel_file):
        # Initialize attributes for reading from Excel
        self.data_dfs = dict()
        self.metadata_df = pd.DataFrame()
        self.comp_like_df = pd.DataFrame(columns=['source', 'raw_item'])
        self.item_manual_mappings_df = pd.DataFrame(columns=['raw_item_from', 'raw_item_to', 'item_from', 'item_to'])
        
        # read excel input
        self.read_excel_input(input_excel_file)
        
        # Initilize attributes for processing raw data
        self._raw_data = list()  # a list of Records
        self.items = pd.DataFrame(columns=['raw_name', 'source', 'name',]) \
            .astype({'raw_name': str, 'source': str, 'name': str})
        self.data = pd.DataFrame()      
        
        # process raw data and initialize self.data
        self.process_raw_data()
        self.initialize_data()
        
    def read_excel_input(self, input_excel_file):
        """
        reads excel file into "raw" data (i.e. self.data_dfs)
        """
        print(f"Reading Excel File: {input_excel_file}...")
        
        with pd.ExcelFile(input_excel_file) as xls:
            # read metadata
            if 'metadata' in xls.sheet_names:
                self.metadata_df = pd.read_excel(xls, sheet_name='metadata').astype({'tab': str})
                missing_column = {'tab','name'} - set(self.metadata_df.columns)
                if missing_column:
                    raise ValueError(f"metadata is missing columns {missing_column}.")
            else:
                raise ValueError("The input Excel file must contain metadata sheet.")
                
                
            # read comp_like
            if 'comp_like' in xls.sheet_names:
                self.comp_like_df = pd.read_excel(xls, sheet_name='comp_like')
                self.comp_like_df['source'] = self.comp_like_df['source'].astype(str)
                missing_column = {'source', 'raw_item'} - set(self.comp_like_df.columns)
                if missing_column:
                    raise ValueError(f"rules is missing columns {missing_column}.")
                            
            # read item_manual_mappings
            if 'item_manual_mappings' in xls.sheet_names:
                self.item_manual_mappings_df = pd.read_excel(xls, sheet_name='item_manual_mappings')
                self.item_manual_mappings_df['item_from'] = self.item_manual_mappings_df['raw_item_from'].str.strip().str.lower()
                self.item_manual_mappings_df['item_to'] = self.item_manual_mappings_df['raw_item_to'].str.strip().str.lower()
                missing_column = {'raw_item_from', 'raw_item_to'} - set(self.item_manual_mappings_df.columns)
                if missing_column:
                    raise ValueError(f"item_manual_mappings is missing columns {missing_column}.") 
                
            # read sheets specified in metadata
            print("Reading sheets:", end=" ")
            for sheet_name in self.metadata_df['tab']:
                print(f"{sheet_name}", end=" ")
                self.data_dfs[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
            print()
                
    def _clean_raw_value(self, raw_value):
        """
        Helper function for insert_record(): cleans raw_value to return value
        """
        
        # NA is considered zero
        if isinstance(raw_value, (np.float64, float)) and np.isnan(raw_value):
            value = 0
        else:
            value = raw_value
        return value  
    
    def _register_item(self, raw_item, raw_source):
        """
        Helper function for insert_record(): registers raw_item into self.items
        """
        name = raw_item.strip().lower()
        
        # Check if there is at least one row where 'name' equals the name
        # and 'source' equals the raw_source --> for each source's item, there can be multiple periods
        if ((self.items['name'] == name) & (self.items['source'] == raw_source)).sum():
            return name           
       
        new_item = {
            'raw_name': raw_item,
            'source': raw_source,
            'name': name,
            }
        
        self.items = pd.concat([self.items, pd.DataFrame([new_item])], ignore_index=True)
        return name
        
    def _insert_record(self, row_num, raw_item, raw_period, raw_value, raw_source):
        """
        Helper function for process_raw_data(): inserts a new record into self._raw_data
        """
        
        value = self._clean_raw_value(raw_value)
        item = self._register_item(raw_item, raw_source)
        row_num = int(row_num)
            
        # register/udpate self.data
        record = Record(
            source=raw_source,
            record_type='original',
            period=raw_period,
            row_num=row_num,
            item=item,
            raw_item=raw_item,
            value=value,
            raw_value=raw_value,            
        )        
        self._raw_data.append(record)
             
    def process_raw_data(self):
        """
        processes raw data (i.e. self.data_dfs) into self._raw_data
        """
        print("Processing sheets:", end=" ")
        for raw_source in self.metadata_df['tab'].values:    
            print(f'{raw_source}', end=" ")
            
            # clean format (may be different for each filing)
            df = clean_format.clean_column_headings(self.data_dfs[raw_source])
            
            # check no duplicated items from the same source
            if df.duplicated(subset=['item'], keep=False).sum() > 0:
                raise ValueError(f"Cannot have duplicated item name in the same source:\n {df[df.duplicated(subset=['item'], keep=False)]}")
                
            # insert record
            for row_num, x in enumerate(df.to_dict('records')):
                raw_item = x['item']
                # assume the first column is item and the rest are periods
                for raw_period in df.columns[1:]:    
                    raw_value = x[raw_period]
                    self._insert_record(row_num, raw_item, raw_period, raw_value, raw_source)  
        print()
            
    def initialize_data(self):
        """
        creates self.data (a Dataframe) from self._raw_data (a list of Records)
        """
        print('initializing self.data...')
        self.data = pd.DataFrame(self._raw_data)
        self.data['record_type'] = pd.Categorical(self.data['record_type'], ["original", "base", "comp"]) 
        
        # Given a same source, verify you only have one item (i.e. no duplicated items)
        # already checked before, but does not hurt to check again
        if self.data.groupby(['source', 'period', 'item']).size().max() != 1:
            raise ValueError('Same source has duplicate items...')