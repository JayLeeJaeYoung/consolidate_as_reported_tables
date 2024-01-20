<style>
r { color: Red }
</style>

# Consolidate As Reported Tables

## Overview

### Program Objective

To produce a consolidated table from multiple "as reported" tables by reconciling inconsistencies, resolving conflicts according to the user-specified source order.

### Example

Below are two source tables and the consolidated table produced from the sources for Wonderful Co.'s Income Statement.

<table>
<caption><b>Income Statement for Wonderful Co.</b></caption>
<tr>
  <th>Source: Annual Report 2023</th>
  <th>Source: Annual Report 2022</th>
  <th>Consolidated Table</th>
</tr>
<tr><td valign="top">

| item             | 2023 | 2022 | 2021 |
| :--------------- | ---: | ---: | ---: |
| Revenue          |  100 |   90 |   80 |
| COGS             |   50 |   40 |   30 |
| SG&A             |   10 |   10 |   10 |
| Interest Expense |    4 |    5 |    6 |
| Interest Income  |   -3 |   -2 |   -1 |
| Net Income       |   39 |   37 |   35 |

</td><td valign="top">

| item             | 2022 | 2021 | 2020 |
| :--------------- | ---: | ---: | ---: |
| Sales            |   90 |   80 |   70 |
| COGS             |   40 |   30 |   20 |
| SG&A             |   10 |   10 |   10 |
| Interest Expense |    3 |    5 |    2 |
| Net Income       |   37 |   35 |   38 |

</td><td valign="top">

| item                   | 2023 | 2022 | 2021 | 2020 |
| :--------------------- | ---: | ---: | ---: | ---: |
| Revenue                |  100 |   90 |   80 |   70 |
| COGS                   |   50 |   40 |   30 |   20 |
| SG&A                   |   10 |   10 |   10 |   10 |
| Interest Expense [[1]] |    1 |    3 |    5 |    2 |
| Interest Expense       |    4 |    5 |    6 |    0 |
| Interest Income        |   -3 |   -2 |   -1 |    0 |
| Net Income             |   39 |   37 |   35 |   38 |

</td></tr>
</table>
Explanation

- The program auto-detects "Revenue" item in "Annual Report 2023" matches semantically with "Sales" item in "Annual Report 2022."
- The program auto-detects the meaning of "Interest Expense" item changed from "Annual Report 2022" to "Annual Report 2023" and modifies the item name for "Interest Expense" from "Annual Report 2022" to "Interest Expense [[1]]".
  - Note: The program opts to create duplicate items for semantically equivalent items from the two sources. The design principle behind the decision is to preserve as much information from original sources as possible.

Terminology

- `source`: where an "as reported" table is coming from. (Ex.) "Annual Report 2023"
- `item`: row-wise data in a table. (Ex.) "Revenue"
- `period`: column-wise data in a table. (Ex.) "2023"
  - why column-wise data is called `period`? The primary application of the program is to consolidate financial statements.

## Files / Folders

Below is the structure of the files in the program. Users will enter information to an input Excel file under the "input" folder then run the program from **consolidated_as_reported_tables_main.ipynb** which will produce the output Excel file to the "output" folder.

- model/record.py: `Record` namedtuple --> `Read_Excel_Input`
- clean_format.py: custom function to clean input format --> `Read_Excel_Input`
  - It is a separate file because this is the only file expected to change based on input file
- read_excel_input.py: `Read_Excel_Input` --> `Consolidated_Table`
  - Class for reading and processing data from an Excel file
- consolidated_table.py: `Consolidated_Table` --> **consolidated_as_reported_tables_main.ipynb**
  - Class for consolidating tables from an instance of `Read_Excel_Input`
- **consolidated_as_reported_tables_main.ipynb**: main interactive Jupyter notebook
- input/: location for input Excel files
- output/: location for output (finished) files

## Input Excel File

The input excel file contains the following sheets.

Note: '-->' indicates corresponding instance variable in `Read_Excel_Input` (rei) and `Consolidated_Tab` (ct)

#### (1) metadata (required) --> `rei.metadata_df` --> `ct.sources_to_consolidate` (list)

> Specifies sheet names to read, only the sheets specified in metadata will be read and in the specified order from top to bottom

> When consolidating tables, sources that appear at the top of the metadata sheet will be given priority in resolving conflicts. When there are irreconcilable inconsistencies between sources, the values from sources that appear on top will have priority over values from sources that appear in the bottom.

<table>
<tr>
  <th>metadata</th>
</tr>
<tr><td valign="top">

| tab    | name             | unit (optional) |
| ------ | ---------------- | --------------- |
| 2022   | Income Statement | $               |
| 2021   | Income Statement | $               |
| 2023Q3 | Income Statement | $               |

</td></tr>
</table>

#### (2) comp_like (optional) --> `rei.comp_like_df` --> `ct.comp_like_df`

> Specifies which items among redundant items should be excluded from the matching algorithm. Technically speaking, the items listed in this sheet will have `disjoint` = `comp_like` designation.

In the below example, the program can auto-detect that "item 1" plus "Item 2" in 2022 is semantically equivalent to "item 3" in 2023. But so is "item 1A" plus "item 1B" plus "item 2" semantically equivalent to "item 3". So is "item 1" plus "item 2A" plus "item 2B" semantically equivalent to "item 3".

<table>
<tr>
  <th>source=2022</th>
  <th>source=2023</th>
</tr>
</td><td valign="top">

| raw_item |     value |
| -------: | --------: |
|   item 1 | c = a + b |
|  item 1A |         a |
|  item 1B |         b |
|   item 2 | f = d + e |
|  item 2A |         d |
|  item 2B |         e |

</td><td valign="top">

| raw_item |     value |
| -------: | --------: |
|   item 3 | g = c + f |

</td></tr>
</table>

A thorny issue arises because there are semantically equivalent items from 2022 ("item 1" = "item 1A" + "item 1B") which are forced to be consolidated with "item 3" from 2023.

The program lets users decide which redundant items in 2022 should be **excluded** from the program's auto-matching algorithm.

User can provide comp_like sheet with the below information, which will now allow the program to match "item 1" plus "item 2" with "item 3" because "item 1A", "item 1B", "item 2A", and "item 2B" are excluded from consideration.

<table>
<tr>
  <th>comp_like</th>
</tr>
<tr><td valign="top">

| source | raw_item |
| -----: | -------: |
|   2022 |  item 1A |
|   2022 |  item 1B |
|   2022 |  item 2A |
|   2022 |  item 2B |

</td></tr>
</table>

Please refer to [`disjoint`](#disjoint) for details but a short explanation for `disjoint` = `comp_like` is that it lets the program treat the items as if those items only exist in 2022. The matching algorithm (which usually scans items in 2022 and matches them to corresponding items in 2023) will exclude those items from consideration and simply carry over values from 2022 to 2023.

#### (3) item_manual_mappings (optional) --> `rei.item_manual_mappings_df` --> `ct.manual_mapping_rules` (dict)

> Specifies which items from one source to another should be mapped manually when the values in the items are irreconcilable. After the mapping, the values from sources with higher priority will be included in the consolidated table.

Please see a new version of Wonderful Co.'s income statement. "Sales" item in 2021 is reported as 80 in "Annual Report 2023", but its semantically equivalent "Revenue" item in 2021 is reported as 90 in "Annual Report 2022". (This inconsistency can rise from a simple typo or from a company acquiring/divesting subsidiaries which result in restated financial statements for the past periods.)

<a id="wonderful_co_2"></a>

<table>
<caption><b>Income Statement for Wonderful Co.</b></caption>
<tr>
  <th>Source: Annual Report 2023</th>
  <th>Source: Annual Report 2022</th>
  <th>Consolidated Table</th>
</tr>
<tr><td valign="top">

| item             | 2023 | 2022 | 2021 |
| :--------------- | ---: | ---: | ---: |
| Revenue          |  100 |   90 |   80 |
| COGS             |   50 |   40 |   30 |
| SG&A             |   10 |   10 |   10 |
| Interest Expense |    4 |    5 |    6 |
| Interest Income  |   -3 |   -2 |   -1 |
| Net Income       |   39 |   37 |   35 |

</td><td valign="top">

| item             | 2022 |      2021 | 2020 |
| :--------------- | ---: | --------: | ---: |
| Sales            |   90 | <r>90</r> |   70 |
| COGS             |   40 |        30 |   20 |
| SG&A             |   10 |        10 |   10 |
| Interest Expense |    3 |         5 |    2 |
| Net Income       |   37 |        35 |   38 |

</td><td valign="top">

| item                   | 2023 | 2022 | 2021 | 2020 |
| :--------------------- | ---: | ---: | ---: | ---: |
| Revenue                |  100 |   90 |   80 |   70 |
| COGS                   |   50 |   40 |   30 |   20 |
| SG&A                   |   10 |   10 |   10 |   10 |
| Interest Expense [[1]] |    1 |    3 |    5 |    2 |
| Interest Expense       |    4 |    5 |    6 |    0 |
| Interest Income        |   -3 |   -2 |   -1 |    0 |
| Net Income             |   39 |   37 |   35 |   38 |

</td></tr>
</table>

Under the default setting, the program will terminate with an error stating an irreconcilable inconsistency.

Users can override this behavior by setting `ct.irreconcilable` to be true and providing the following to item_manual_mappings sheet.

Note: 'item_from' and 'item_to' column will be derived later in the program. User only fills in 'raw_item_from' and 'raw_item_to' columns.

<table>
<tr>
  <th>item_manual_mappings</th>
</tr>
<tr><td valign="top">

| raw_item_from | raw_item_to | item_from (derived) | item_to (derived) |
| ------------- | ----------- | ------------------- | ----------------- |
| Sales         | Revenue     | Sales               | Revenue           |

</td></tr>
</table>

The 'raw_item_from' and 'raw_item_to' pairs provided in this sheet can inform the program to expect inconsistencies and act accordingly.

#### (4) [source_sheet_1], [source_sheet_2], ... --> `rei.data_dfs` --> `rei._raw_data` --> `rei.data` --> `ct.data`

> [source_sheet_1], [source_sheet_2], ... become `rei.data_dfs` which is a dict where keys are source sheet name and values are content of each sheet converted to DataFrames. After processing, they eventually become `ct.data`

## Data Structures

### 1a. Record

`Record` namedtuple has the following elements, which will become columns in rei.data (rei is an instance of `Read_Excel_Input`)

The primary purpose of `Record` is to read data from original sources into a DataFrame format.

Primary keys (PK) are marked as red

| <r>source</r> | <r>record_type</r> | <r>period</r> | row_num | <r>item</r> | raw_item   | value | raw_value |
| :------------ | :----------------- | :------------ | ------: | :---------- | :--------- | ----: | --------: |
| 2023          | original           | 2023          |       1 | Revenue     | \_Revenue  |   3.0 |       3.0 |
| 2023          | original           | 2022          |       1 | Revenue     | \_Revenue  |   3.2 |       3.0 |
| 2022          | original           | 2022          |      10 | Interest    | \_Interest |   0.0 |        NA |
| 2021          | original           | 2021          |      10 | Interest    | \_Interest |   0.0 |        NA |

The primary keys are:

- **source**, **record_type**: determine where the table is coming from
- **period**: determines where the column is coming from within a table
- **item** (or **row_num**): determines where the row is coming from

The elements mean:

- **source** (PK): source worksheet name
- **record_type** (PK): pd.Categorical `original` or `base` or `comp` <a id="record-type"></a>

  - In `Consolidated_Table`'s `ct.data`, we start all rows with `original`
  - The big picture plan of attack in `Consolidated_Table` is that we will look at one source at a time to consolidate the table in the order specified in `metadata` tab in the input file.
  - First, `rei.data` is copied over to `ct.data` (ct is an instance of `Consolidated_Table`).
  - Second, as we look at one source in each iteration, we will first move over all the rows from the source to `ct.df` (under the hood, we first move to `ct.df_long` temporarily, then we pivot and save to `ct.df`). The rows moved over from the very first source will be marked as `base` because that would be our <b>base</b> for comparison. There is no operation needed for the very first source. From the second source onward, as we move rows from `ct.data` to `ct.df`, its `record_type` will become `comp` initially (<b>comp</b> stands for comparison).
    - Now we supposedly have duplicated items coming from `base` rows and `comp` rows for the same item's value. For example, if the first source was 2023 and the second source was 2022, we often have 'Revenue' for 2022 coming from the 2023 source and from the 2022 source. The big idea is that this program will try to reconcile and consolidate these duplicated items arising from multiple sources. In each iteration, we have "information" for the item from the `comp` row and `base` row. We will go through multiple steps to smartly incorporate "information" from `comp` to `base` and discard `comp` and only keep `base`at the end of each iteration.

- **period** (PK): column name from source worksheet name
- **row_num**: row number in the source
- **item** (PK): item name used as primary key
- **raw_item**: raw item name as is reported from source
- **value**: cleaned value from raw_value
- **raw_value**: raw value as is reported from source

### 1b. `ct.df`'s Final Structure

`Record` namedtuple becomes `ct.data`, which will be "pivoted" to become `ct.df` in the following manner:

- **period** column will be expanded, so instead of **period**, we will have actual periods such as **2023**, **2022**, etc as columns.
- **raw_value** will be dropped and the "values" in the pivot operation will be **value** column.

| <r>source</r> | <r>record_type</r> | row_num | <r>item</r> | raw_item   | 2023 | 2022 | 2021 |
| :------------ | :----------------- | ------: | :---------- | :--------- | ---: | ---: | ---: |
| 2023          | original           |       1 | Revenue     | \_Revenue  |  3.0 |  3.0 |  2.0 |
| 2023          | original           |       1 | Revenue     | \_Revenue  |  3.2 |  3.0 |  1.0 |
| 2022          | original           |      10 | Interest    | \_Interest |  0.0 |   NA |    0 |
| 2021          | original           |      10 | Interest    | \_Interest |  0.0 |   NA |    0 |

The above format is what `ct.df` has at the end of each iteration.

### 1c. `ct.df`'s Intermediate Structure

In the algorithm's iteration, we need to consolidate the new `comp` source to the existing `base` source. While the algorithm is running at each step, we need a few more columns to `ct.data`, which are: <a id="disjoint"></a>

- `disjoint`: The only way to verify items in `base` and `comp` is by comparing values in the `ct.overlapping_periods` (that is, by verifying the values in periods where source and base overlap). Therefore if the values in `ct.overlapping_periods` are zero or if there are items that are only in `base` or only in `comp`, then we have to designate `disjoint` values, which can take the following values:

  - `NA`: All items initially start out with `NA` at the beginning of each iteration
  - `base`: this item only exists in `base` and therefore we will not look for a corresponding item in `comp` and consider this item to be `matched` = `True`
  - `comp`: this item only exists in `comp` and we will insert this item to `base` without looking for a corresponding item in 'base' and consider this item to be `matched`=`True`
  - `comp_like`: treated as if `disjoint` = `comp`. `comp_like` is added manually by the user.

- `init_comp_row_num`: when `disjoint` = `comp` (or `comp_like`), items are moved from `comp` to `base`, we need to insert the item at the "correct" row number. `init_comp_row_num` and `init_row_num` are used to find the "correct" row number.
- `init_row_num`
- `matched`: All items initially start out with `False`. At each iteration's steps, as items are matched, they are "crossed off" by setting `matched` = `True`. Each iteration terminates when all items are matched.

### 2. `ct.items` (`rei.items`) (DataFrame)

> We have to use a consistent item name in `ct.df` in order to identify the same items with the same semantics. But original data sources may use different item names to mean the same thing.

> We use `ct.items` to keep track so that given `raw_name` and `source`, we have one consistent `name` that we use. To phrase it differently, given a `name`, there must be exactly one `raw_name` for each `source`.

Note that when two items in one source correspond to one item in another source, we keep track of that in `ct.combination_rules` where its keys and values are `name` in `ct.items`.

in the [Wonderful Co.'s example](#wonderful_co_2), `ct.items` will look like below.

<table>
<tr>
  <th><code>ct.items</code></th>
</tr>
<tr><td valign="top">

| <r>raw_name</r> | <r>source</r> | name    |
| :-------------- | :------------ | :------ |
| Revenue         | 2023          | Revenue |
| Sales           | 2022          | Revenue |

</td></tr>
</table>

## Algorithms

### `Consolidated_Table`

### Overview

The program will iterate over each source to consolidate. At each iteration, we will start out with `ct.df` with additional `disjoint`, `init_comp_row_num`, `init_row_num`, `matched` columns until the iteration is complete.

At the beginning of each iteration, we will start with `matched` = `False` for all items. Each item will have `record_type` either `base` or `comp`. As we process data, we will match items in `base` and `comp` and do appropriate data manipulations so that at the end of each iteration, we will have all items in `ct.df` with `matched` = `True` at which point only the items whose `record_type` is `base` will be selected to move to the next iteration. In the next iteration, the items from the new source will all have the `record_type` = `comp` and the program continues until all the sources are processed.

### 1. match_same_items

This is the most straightforward case. Match the same items in base and comp that are spelled exactly and have the same values.

- groupby same `item` and for each group
  - if (a) the group size == 2 (implies one is from base and the other from comp because duplicated item is not allowed within the same source) and
  - if (b) overlapping_periods match (or there is no overlap),
  - then "match" both base and comp

### 2. match same overlapping periods values

This is a case where two items are spelled differently but share the same non-zero values. It is most likely that the two items are the same semantically but spelled differently.

1st. If there is no overlapping_periods, we skip this step since we cannot verify that the two items share the same values.

2nd. We only look at unmatched items.

- groupby same `overlapping_periods` and for each group
  - if (a) the group size == 2 and one is from base and the other from comp and
  - if (b) not all values for overlapping_periods are zero,
  - then "match" both base and comp

### 3. manually map inconsistent items

if `ct.irreconcilable` is True, there are some items that we have to manually override from `ct.manual_mapping_rules`.
We override the item names, but do not "match" because the updated names will flow through to next steps to be matched.

### 4. apply combination rules

`ct.combination_rules` (list of dict): the purpose of `ct.combination_rules` is to keep track of 1:M or M:1 mappings between comp items (not raw_item) and base items (not raw_item) that are equivalent. Each dict has the following keys:

- `comp_tuple`: tuple of comp items
- `base_tuple`: tuple of base items
- `sources`: sources where this rule applies
- `invalid_sources`: sources where this rule is invalid, i.e. inconsistent

Please note that M:M is not supported, i.e. for a rule, at least one of comp_tuple or base_tuple must be of tuple of length 1

| key            | value case A         | value case B |
| :------------- | :------------------- | :----------- |
| comp_tuple     | `(A <<1>>, B <<1>>)` | `(A [[1]],)` |
| base_tuple     | `(A,)`               | `(A, B)`     |
| sources        | `[2022]`             | `[2022]`     |
| invalid_source | `[]`                 | `[]`         |

Please note that we are looking at all items, not just unmatched items. This is because combination_rules are created by keeping duplicated items. In the subsequent sources, only one (or none) of the duplicated items will match, but not both, so we need to continue supporting duplicated items.

In the below example cases, creating `ct.combination_rules` belongs to step 5 but applying combination rules belongs to this step. In this example, this is for comp_source = 2021.

## <a id="combination_rules"></a>

#### 4a. Case A: `base_tuple` size is 1

<table>
<caption><b><code>self.comp_source = 2022</code></b></caption>
<tr>
  <th>Before Processing</th>
  <th>After Processing</th>
  <th>combination_rules</th>
</tr>
<tr><td>

| source | record_type | item | 2023 | 2022 | 2021 |
| :----- | :---------- | :--- | ---: | ---: | ---: |
| 2023   | base        | A    |   15 |   10 |    - |
| 2022   | comp        | A    |    - |    3 |   14 |
| 2022   | comp        | B    |    - |    7 |    6 |

</td><td>

| source | record_type | item           | 2023 | 2022 |      2021 |
| :----- | :---------- | :------------- | ---: | ---: | --------: |
| 2023   | base        | A              |   15 |   10 | <r>20</r> |
| 2022   | <r>base</r> | <r>A <<1>></r> |    - |    3 |        14 |
| 2022   | <r>base</r> | <r>B <<1>></r> |    - |    7 |         6 |

</td><td>

| key            | value                |
| :------------- | :------------------- |
| comp_tuple     | `(A <<1>>, B <<1>>)` |
| base_tuple     | `(A,)`               |
| sources        | `[2022]`             |
| invalid_source | `[]`                 |

</td></tr>
</table>

<table>
<caption><b>Case 1: <code>self.comp_source = 2021</code></b></caption>
<tr>
  <th>Before Processing</th>
  <th>After Processing</th>
</tr>
<tr><td>

| source | record_type | item    | 2023 | 2022 | 2021 | 2020 |
| :----- | :---------- | :------ | ---: | ---: | ---: | ---: |
| 2023   | base        | A       |   15 |   10 |   20 |    - |
| 2022   | base        | A <<1>> |    - |    3 |   14 |    - |
| 2022   | base        | B <<1>> |    - |    7 |    6 |    - |
| 2021   | comp        | A       |    - |    - |   20 |   30 |

</td><td>

| source   | record_type | item    |  2023 |  2022 |   2021 |      2020 | matched in |
| :------- | :---------- | :------ | ----: | ----: | -----: | --------: | ---------: |
| 2023     | base        | A       |    15 |    10 |     20 | <r>30</r> |   #1 or #2 |
| 2022     | base        | A <<1>> |     - |     3 |     14 |         - |         #4 |
| 2022     | base        | B <<1>> |     - |     7 |      6 |         - |         #4 |
| ~~2021~~ | ~~comp~~    | ~~-~~   | ~~-~~ | ~~-~~ | ~~20~~ |    ~~30~~ |   #1 or #2 |

</td></tr>
</table>

<table>
<caption><b>Case 2: <code>self.comp_source = 2021</code></b></caption>
<tr>
  <th>Before Processing</th>
  <th>After Processing</th>
</tr>
<tr><td>

| source | record_type | item    | 2023 | 2022 | 2021 | 2020 |
| :----- | :---------- | :------ | ---: | ---: | ---: | ---: |
| 2023   | base        | A       |   15 |   10 |   20 |    - |
| 2022   | base        | A <<1>> |    - |    3 |   14 |    - |
| 2022   | base        | B <<1>> |    - |    7 |    6 |    - |
| 2021   | comp        | A       |    - |    - |   14 |   28 |
| 2021   | comp        | B       |    - |    - |    6 |    2 |

</td><td>

| source   | record_type | item    |  2023 |  2022 |   2021 |      2020 | matched in |
| :------- | :---------- | :------ | ----: | ----: | -----: | --------: | ---------: |
| 2023     | base        | A       |    15 |    10 |     20 | <r>30</r> |         #4 |
| 2022     | base        | A <<1>> |     - |     3 |     14 | <r>28</r> |   #1 or #2 |
| 2022     | base        | B <<1>> |     - |     7 |      6 |  <r>2</r> |   #1 or #2 |
| ~~2021~~ | ~~comp~~    | ~~A~~   | ~~-~~ | ~~-~~ | ~~14~~ |    ~~28~~ |   #1 or #2 |
| ~~2021~~ | ~~comp~~    | ~~-~~   | ~~-~~ | ~~-~~ |  ~~6~~ |     ~~2~~ |   #1 or #2 |

</td></tr>
</table>

---

#### 4b. Case B: `comp_tuple` size is 1

<table>
<caption><b><code>self.comp_source = 2022</code></b></caption>
<tr>
  <th>Before Processing</th>
  <th>After Processing</th>
  <th>combination_rules</th>
</tr>
<tr><td>

| source | record_type | item | 2023 | 2022 | 2021 |
| :----- | :---------- | :--- | ---: | ---: | ---: |
| 2023   | base        | A    |    3 |    4 |   14 |
| 2023   | base        | B    |    7 |    6 |    6 |
| 2022   | comp        | A    |    - |   10 |   20 |

</td><td>

| source | record_type | item           |      2023 | 2022 | 2021 |
| :----- | :---------- | :------------- | --------: | ---: | ---: |
| 2023   | base        | A              |         3 |    4 |   14 |
| 2023   | base        | B              |         7 |    6 |    6 |
| 2022   | <r>base</r> | <r>A [[1]]</r> | <r>10</r> |   10 |   20 |

</td><td>

| key            | value        |
| :------------- | :----------- |
| comp_tuple     | `(A [[1]],)` |
| base_tuple     | `(A, B)`     |
| sources        | `[2022]`     |
| invalid_source | `[]`         |

</td></tr>
</table>

<table>
<caption><b>Case 1: <code>self.comp_source = 2021</code></b></caption>
<tr>
  <th>Before Processing</th>
  <th>After Processing</th>
</tr>
<tr><td>

| source | record_type | item    | 2023 | 2022 | 2021 | 2020 |
| :----- | :---------- | :------ | ---: | ---: | ---: | ---: |
| 2023   | base        | A       |    3 |    4 |   14 |    - |
| 2023   | base        | B       |    7 |    6 |    6 |    - |
| 2022   | base        | A [[1]] |   10 |   10 |   20 |    - |
| 2021   | comp        | A       |    - |    - |   20 |   30 |

</td><td>

| source   | record_type | item    |  2023 |  2022 |   2021 |      2020 | matched in |
| :------- | :---------- | :------ | ----: | ----: | -----: | --------: | ---------: |
| 2023     | base        | A       |     3 |     4 |     14 |         - |         #4 |
| 2023     | base        | B       |     7 |     6 |      6 |         - |         #4 |
| 2022     | base        | A [[1]] |    10 |    10 |     20 | <r>30</r> |   #1 or #2 |
| ~~2021~~ | ~~comp~~    | ~~A~~   | ~~-~~ | ~~-~~ | ~~20~~ |    ~~30~~ |   #1 or #2 |

</td></tr>
</table>

<table>
<caption><b>Case 2: <code>self.comp_source = 2021</code></b></caption>
<tr>
  <th>Before Processing</th>
  <th>After Processing</th>
</tr>
<tr><td>

| source | record_type | item    | 2023 | 2022 | 2021 | 2020 |
| :----- | :---------- | :------ | ---: | ---: | ---: | ---: |
| 2023   | base        | A       |    3 |    4 |   14 |    - |
| 2023   | base        | B       |    7 |    6 |    6 |    - |
| 2022   | base        | A [[1]] |   10 |   10 |   20 |    - |
| 2021   | comp        | A       |    - |    - |   14 |   28 |
| 2021   | comp        | B       |    - |    - |    6 |    2 |

</td><td>

| source   | record_type | item    |  2023 |  2022 |   2021 |      2020 | matched in |
| :------- | :---------- | :------ | ----: | ----: | -----: | --------: | ---------: |
| 2023     | base        | A       |     3 |     4 |     14 | <r>28</r> |   #1 or #2 |
| 2023     | base        | B       |     7 |     6 |      6 |  <r>2</r> |   #1 or #2 |
| 2022     | base        | A [[1]] |    10 |    10 |     20 | <r>30</r> |         #4 |
| ~~2021~~ | ~~comp~~    | ~~A~~   | ~~-~~ | ~~-~~ | ~~14~~ |    ~~28~~ |   #1 or #2 |
| ~~2021~~ | ~~comp~~    | ~~B~~   | ~~-~~ | ~~-~~ |  ~~6~~ |     ~~2~~ |   #1 or #2 |

</td></tr>
</table>

### 6a. set aside disjoint items

Before working in step 5. apply combinations to match, we have to set aside disjoint items so that during step 5, those items will be excluded from consideration during the step.

`disjoint` was explained [here](#disjoint). To recapitulate, the need for `disjoint` arises because there are items whose values in overlapping_periods are zero, which makes it impossible to verify the consistencies of data. These items can only exist in base or in comp only.

During this step, we also designate `comp_like` from `comp_like_df`, which came from the input Excel file.

### 5. apply combinations to match

At this step, we look for 1:M or 1:M matching between items in base and comp (but not M:M). Unfortunately, we have to use the brute-force method by looking at a list of unmatched items in base and a list of unmatched items in comp and use brute-force combinations to find matches.

The main logic was explained in table in step [4](#combination_rules)

### 6b. apply disjoint items

We now match the items set aside in step 6a. One caveat is that when we match `disjoint` = `comp` (or `comp_like`), we have to move over comp items to base because only base items survive to the next iteration. When we do so, we have to insert the item into the "correct" row in base, whose algorithm is conducted in this step.
