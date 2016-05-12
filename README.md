# mbclean
Beautifies MapBasic code by standardising formatting and whitespace.

_MapBasic is ugly enough as it is - at least your formatting doesn't have to be!_

## Features

* Standardises spacing, such as whitespace around brackets and function names
* Automatically indents code blocks
* Standardises capitalization of commands and MapBasic functions
* Warns on non standard variable naming (ie not using basic `sSomeString` or `iIntValue` conventions)

## Usage

To clean up a MapBasic script, use the `clean_mb.py` script. There's two ways to use this script:

1. By passing a specific filename to the script - eg `clean_mb.py d:\myproject\switch_to_qgis.mb`, or
2. By passing a folder name containing MapBasic files to the script - eg `clean_mb.py d:\my_1990s_toolkit_project\mb`. All `.mb` files in the folder will be cleaned.




