#!/usr/bin/python3.5 -u
#################################################################################################
# PROGRAM DETAILS:
#################################################################################################
# Program name: XML_Proc.py
# Author: Ciro Emmanuel
# Description: this program decodes a mobile network configuration XML, converting the data into tables and exporting those tables to an Excel file.
# 
# Current version: 2.0 [*** RELEASED ***]
#   - Changes:
#       - New HTML front-end allows for file selection on dialog box. This new version deals with that change.
#	- Improvement: checking the Excel file availability before processing. Added a backup option for saving the file. 
# Current version: 1.0 [*** OLD VERSION ***]
# Dependencies:
# - Version: Python 3.6.4 (Anaconda distribution recommended)
# - Modules: see modules import block, below.

#################################################################################################
# MODULES IMPORT:
#################################################################################################
import os
import sys
import pandas as pd
import numpy as np
import inspect
# Importing the 'cgi' module
import cgi
# For debugging purposes:
import cgitb
cgitb.enable()


#################################################################################################
# CONFIGURATION PARAMETERS AND SETUP:
#################################################################################################
DEBUG = False
NON_DEBUG = False
# OUTPUT FOLDERS:
DEFAULT_OUT_FOLDER = "/home/refarmingnokia/www/DATA/_scripts_output/"
BACKUP_OUT_FOLDER = "../output/"
# CONFIGURABLE PARAMETERS - READ FROM THE HTML USER INTERFACE LAUNCH FILE, AS SPECIFIED BY THE USER:
# Start the HTML content printing:
print("Content-type: text/html\r\n\r\n")
print("<html>") 
print("<title>XML_Proc - Processing...</title>")
print("<body>")
print("<h1>XML FILE PROCESSING</h1>")
print("<br>")
print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
# Read the parameters from the html submission:
try:
    form = cgi.FieldStorage()

    # 1.- XML FILE
    file_item = form['xmlfile']
    fichero_form = file_item.file
    nombre_fichero = file_item.filename

    # 2.- TABLES TO DECODE / EXPORT
    try:
        list_text = form.getvalue("listoftables")
        if list_text == None or list_text == "":
            # No list of tables indicated, default to "decode all tables"
            export_specification = {}
        else:
            # There is a list of tables specified, try to decode that list:
            list_text_no_spaces = list_text.replace(" ","")
            list_tables = list_text_no_spaces.split(',')
            export_specification = {table : [] for table in list_tables}
    except Exception as exception_error:
        # Some error happened when decoding the list of tables to decode, default to "all tables"
        print("** WARNING !! COULD NOT DECODE THE SPECIFICATON OF TABLES !! DEFAULTING TO DECODE AND EXTRACT ALL EXISTING TABLES...<br>")
        print("** System error code is: ",exception_error,"<br><br>")
        print("** This is the user's input the program tried to understand: %s<br>" %list_text)
        print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
        export_specification = {}
except Exception as exception_error:
    print("*** ERROR !!! SOME ERROR HAPPENED WHEN RECEIVING THE PARAMETERS FROM THE HTML FORM !!!<br>")
    print("*** System error code is: ",exception_error,"<br><br>")
    print("Exiting program... REASON: could not parse parameters from HTML form.<br>")
    print("--- END OF PROGRAM --- FAILED<br><br>")
    print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
    print("<script>")
    print("document.title='XML_Proc - FINISHED - FAILED'")
    print("</script>")
    sys.exit(1)


# PREPARE THE OUTPUT FILENAME (AND A BACKUP):
output_file = os.path.abspath(DEFAULT_OUT_FOLDER + nombre_fichero + "_" + 
                              "-".join(sorted(export_specification.keys())) +
                              "_EXCEL.xlsx")

backup_output_file = os.path.abspath(BACKUP_OUT_FOLDER + nombre_fichero + "_" + 
                                      "-".join(sorted(export_specification.keys())) +
                                      "_EXCEL.xlsx")

# SHOW CHOSEN PARAMETERS:
print("PARAMETERS CHOSEN:<br>")
print("XML filename = %s<br>" %nombre_fichero)
print("List of tables to decode and extract = ",sorted(export_specification.keys()),"<br>")
if export_specification == {}:
    print("&nbsp&nbsp--- NOTE: the list of tables is empty, so all the existing tables will be decoded.<br>")
print("Output filename = %s<br><br>" %output_file)
print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")


# MODIFY THE FILENAMES IF NEEDED (as this program starts inside the 'src' subfolder, but filenames are probably referred to the parent folder)
#if (os.path.isabs(filename)):
#    # This is an absolute path, nothing needs to be done.
#    pass
#else:
#    # This is a relative path, we need to go up one level in the filename:
#    filename = "../"+filename
#if (os.path.isabs(output_file)):
#    # This is an absolute path, nothing needs to be done.
#    pass
#else:
#    # This is a relative path, we need to go up one level in the filename:
#    output_file = "../"+output_file

#################################################################################################
# FUNCTION DEFINITIONS
#################################################################################################
# FUNCTION TO DECODE A LINE:
def decode_line(binary_string, line_number):
    # Returns the decoded line, and a flag telling if decoding was successful or not.
    # In the unsuccessful case, the original, unchanged string is returned.
    try:
        dl_decoded_line = binary_string.decode('utf-8')
        return dl_decoded_line, True
    except UnicodeDecodeError:
        print("*** ERROR - 'UnicodeDecodeError' IN UTF-8 !!!<br>")
        print("*** IN LINE NUMBER: %s<br>" %line_number)
        print("Trying 'ascii' instead, just in case...<br>")
        try:
            dl_decoded_line = binary_string.decode('ascii')
            return dl_decoded_line, True
            print("ASCII SUCCEEDED !<br>")
        except:
            print("*** ERROR - ASCII DID NOT WORK, EITHER !!!<br>")
            print("*** IN LINE NUMBER: %s<br>" %line_number)
            return binary_string, False


#################################################################################################
# PREPARING EXCELWRITER INSTANCE FOR WRITING
#################################################################################################
print("<br>")
print("<br>")
print("CHECKING AND PREPARING EXCEL FILE HANDLER...<br>")
print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")

# Create a Pandas Excel writer using XlsxWriter as the engine.
selected_out_file = None
print("Trying main output file path '%s'...<br>" %output_file)
path_exists = os.path.isdir(os.path.dirname(os.path.abspath(output_file)))
if path_exists:
    try:
        writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
        print("...success.<br><br>")
        selected_out_file = "main"
    except:
        print("--- SYSTEM ERROR CODE: %s !! ***<br>" %sys.exc_info()[0])
        print("Main output file path is fine, but some error happened with %s...<br><br>"
              %output_file)
        selected_out_file = None
else:
        print("Main output file path does not exist '%s'.<br><br>" %backup_output_file)
        selected_out_file = None

if not path_exists or selected_out_file == None:
    print("Main output file path has failed: %s<br>" %output_file)
    print("Trying backup path (current folder) '%s'...<br>" %backup_output_file)
    path_exists = os.path.isdir(os.path.dirname(os.path.abspath(backup_output_file)))
    if path_exists:
        try:
            writer = pd.ExcelWriter(backup_output_file, engine='xlsxwriter')
            print("...success.<br><br>")
            selected_out_file = "backup"
        except:
            print("--- SYSTEM ERROR CODE: %s !! ***<br>" %sys.exc_info()[0])
            print("Backup output file path is fine, but some error happened with %s...<br>"
                  %backup_output_file)
            selected_out_file = None
            print("Unable to write results! Exiting the program...<br><br>")
            print("--- END OF PROGRAM --- FAILED<br><br>")
            sys.exit(1)
    else:
        print("Backup output file path does not exist '%s'.<br>" %backup_output_file)
        selected_out_file = None
        print("Unable to write results! Exiting the program...<br><br>")
        print("--- END OF PROGRAM --- FAILED<br><br>")
        sys.exit(1)

#################################################################################################
# DATA PROCESSING
#################################################################################################
# PROCESSING
#### NOTAS... INTENTAR USAR COMO SPLIT EL TABULADOR, PERO ANTES, HAY QUE SUSTITUIR LOS "<" Y ">" POR EL TABULADOR,
#### YA QUE ESTOS PARECEN MARCAR DE ALGÚN MODO LAS "FRONTERAS" DE LOS CAMPOS... LOS ESPACIOS METIDOS EN LAS CADENAS
#### ENCERRADAS EN "" SON LOS QUE DAN PROBLEMAS CON LOS SPLITS...
DEBUG_num_ops = {'DECODE':0,'DECODE_FIELDS':0,'list.append()':0,'pd.DataFrame()':0,'pd.concat()':0}
MAX_LINES_TO_SHOW = 200 # BE CAREFUL WITH THIS... SETTING IT TOO HIGH WILL CAUSE JUPYTER NOTEBOOK SIZE TO GROW TOO MUCH !!!
# List the objects in which the user has shown interest:
print("SELECTED MOs:<br>")
if export_specification == {}:
    all_mo_selected = True
    selected_mo_list = list([])
    print("&ltNo MOs specified: all MOs will be retrieved&gt<br>")
    print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
else:
    all_mo_selected = False
    selected_mo_list = list(export_specification.keys())
    print(selected_mo_list)
num_line = 0
not_decoded_lines = 0
not_decoded_types = {}
not_processed_lines = 0
not_processed_types = {}
df_parsing_errors = 0
df_parsing_affected_items = {}
# BEGIN --- VERSION 3.0:
tables_dict = {}
# END --- VERSION 3.0:
# The key of this dictionary is the table name (i.e. the class of the object)
# Each element contains itself a dictionary, composed of all possible possible headers found in that object.
# Each of those items contains: the number of rows; the number of columns; and all the data conforming to each of the headers groups
# Example:
# tables_dict = {'BSC' : {{'<col_struct_1>':[234,12,[[3,1,...],[2,2,...],...]]},
#                         {'<col_struct_2>':[125,11,[[6,2,...],[1,3,...],...]]}},
#                 'BTS' :  {{'<col_struct_3>':[1245,34,[[3,3,...],[9,1,...],...]]},
#                         {'<col_struct_4>':[1252,32,[[5,27,...],[7,1,...],...]]}},
#                 ...
#               }
# Stores elements in the form '[a,b]', where 'a' is the number of elements of the table, and 'b' is the DataFrame containing
# the records of the table.
in_mo = False
in_list = False
in_item = False
with fichero_form:
#with open(nombre_fichero, 'rb') as fichero:
    for file_line in fichero_form:
        if DEBUG == True:
            if num_line <= MAX_LINES_TO_SHOW:
                print("DEBUG --- PROCESSING LINE %d ...<br>" %num_line)
                print("DEBUG --- file_line =", file_line,"<br>")
                print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
        decoded = False
        num_line += 1
        # FULLY NEW APPROACH TO THE LOOP, IN ORDER TO REDUCE THE EXECUTION TIME - VERSION 2:
        strip_line = file_line.strip()
        if strip_line[:14] == b"<managedObject":
            # This is a new managed object, check if it is in the user's list of interest.
            # Decode the line:
            DEBUG_num_ops['DECODE'] += 1
            decoded_line, decoded = decode_line(strip_line, num_line)
            if decoded == True:
                # The line was correctly decoded, try to decode the fields:
                # Decode the fields:
                try:
                    #decoded_fields = decoded_line.replace('="','\t').replace('">','\t').replace('" ','\t').replace('>','').replace('<','').replace('"','').strip().split('\t')
                    DEBUG_num_ops['DECODE_FIELDS'] += 1
                    decoded_fields = decoded_line[1:-1].replace('"','\t').strip().split('\t')
                    decoded = True
                    try:
                        indice = selected_mo_list.index(decoded_fields[1])
                        mo_in_interest_list = True
                    except:
                        mo_in_interest_list = False
                        pass
                    if all_mo_selected or mo_in_interest_list:
                        # This kind of object is of interest:
                        in_mo = True
                        # Record the current table and the current object, and start generating the record:
                        table_name = decoded_fields[1]
                        field_names = ["_ID."+x for x in decoded_fields[2::2]]
                        values = decoded_fields[3::2]
                        # Initialize the parameter names and values:
                        mo_parameter_names = []
                        mo_parameter_values = []
                        if DEBUG == True:
                            if num_line <= MAX_LINES_TO_SHOW:
                                print("DEBUG --- ENTERING MO...<br>")
                                print("DEBUG --- object of table = %s<br>" %table_name)
                                print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
                    else:
                        # This object is of no interest for the user, we will ignore any line behind this one, until a new
                        # object is found:
                        pass
                except:
                    print("DEBUG --- *** ERROR *** FIELD DECODING FAILED !!!<br>")
                    print("DEBUG --- num_line = %s<br>" %num_line)
                    print("DEBUG --- decoded_line = %s<br>" %decoded_line)
                    print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
                    not_decoded_lines += 1
                    try:
                        not_decoded_types[decoded_line[:13]] += 1
                    except KeyError:
                        try:
                            not_decoded_types[decoded_line[:13]] = 1
                        except IndexError:
                            # Could not record the type of not processed type for this line:
                            pass
            else:
                # The line was not decoded properly:
                print("*** ERROR - NEITHER UTF-8 NOR ASCII DECODED THE LINE !!!<br>")
                print("*** ERROR - Number of line = %d" %num_line)
                print("*** ERROR - file_line =", file_line,"<br>")
                print("*** ERROR - strip_line =", strip_line,"<br>")
                print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
        else:
            # This is not an object beginning.
            if in_mo == True:
                # If we are inside an object of interest, process the line:
                if strip_line[:10] == b"<list name":
                    # This is the start of a list of parameters: 
                    # Decode the line:
                    DEBUG_num_ops['DECODE'] += 1
                    decoded_line, decoded = decode_line(strip_line, num_line)
                    if decoded == True:
                        # The line was correctly decoded, try to decode the fields:
                        # Decode the fields:
                        try:
                            #decoded_fields = decoded_line.replace('="','\t').replace('">','\t').replace('" ','\t').replace('>','').replace('<','').replace('"','').strip().split('\t')
                            DEBUG_num_ops['DECODE_FIELDS'] += 1
                            decoded_fields = decoded_line[1:-1].replace('"','\t').strip().split('\t')
                            in_list = True
                            # Initialize list of elements, and its name:
                            list_of_elements = []
                            list_name = decoded_fields[1]
                            if DEBUG == True:
                                if num_line <= MAX_LINES_TO_SHOW:
                                    print("DEBUG --- ENTERING list...<br>")
                                    print("DEBUG --- list name = %s<br>" %list_name)
                        except:
                            print("DEBUG --- *** ERROR *** FIELD DECODING FAILED !!!<br>")
                            print("DEBUG --- decoded_line = %s<br>" %decoded_line)
                            print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
                            not_decoded_lines += 1
                            try:
                                not_decoded_types[decoded_line[:9]] += 1
                            except KeyError:
                                try:
                                    not_decoded_types[decoded_line[:9]] = 1
                                except IndexError:
                                    # Could not record the type of not processed type for this line:
                                    pass
                    else:
                        # The line was not decoded properly:
                        print("*** ERROR - NEITHER UTF-8 NOR ASCII DECODED THE LINE !!!<br>")
                        print("*** ERROR - Number of line = %d" %num_line,"<br>")
                        print("*** ERROR - file_line =", file_line,"<br>")
                        print("*** ERROR - strip_line =", strip_line,"<br>")
                        print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
                elif strip_line == b"<item>":
                    # This is the start of a composite item (inside a list, probably):
                    # NO NEED TO DECODE.
                    in_item = True
                    # Initialize the list of items:
                    list_of_items = []
                    if DEBUG == True:
                        if num_line <= MAX_LINES_TO_SHOW:
                            print("DEBUG --- ENTERING item...<br>")
                            print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
                elif strip_line[:7] == b"<p name":
                    # This is a parameter, it could be part of a managed object, a list, or an item.
                    # Decode the line:
                    DEBUG_num_ops['DECODE'] += 1
                    decoded_line, decoded = decode_line(strip_line, num_line)
                    if decoded == True:
                        # The line was correctly decoded, try to decode the fields:
                        # Decode the fields:
                        try:
                            DEBUG_num_ops['DECODE_FIELDS'] += 1
                            decoded_fields = decoded_line[1:-1].replace('"','\t').strip().split('\t')
                            # Depending on that, processing might vary:
                            if DEBUG == True:
                                if num_line <= MAX_LINES_TO_SHOW:
                                    print("DEBUG --- ENTERING p name...<br>")
                                    print("DEBUG --- parameter name = %s<br>" %decoded_fields[1])
                                    print("DEBUG --- parameter value = %s<br>" %decoded_fields[2][1:-3])
                                    print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
                            if in_item == True:
                                # This is a parameter of an item, we must add the parameter to the list of items:
                                list_of_items.append([decoded_fields[1],decoded_fields[2][1:-3]])
                            elif in_list == True:
                                # This is a parameter of a list, we must add the parameter to the list:
                                list_of_elements.append([decoded_fields[1],decoded_fields[2][1:-3]])
                            else:
                                # We are not currently inside an item or element, so this is a "base" parameter of the menaged object,
                                # so we add it to the list of parameters:
                                mo_parameter_names.append(decoded_fields[1])
                                mo_parameter_values.append(decoded_fields[2][1:-3])
                        except:
                            print("DEBUG --- *** ERROR *** FIELD DECODING FAILED !!!<br>")
                            print("DEBUG --- decoded_line = %s<br>" %decoded_line)
                            print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
                            not_decoded_lines += 1
                            try:
                                not_decoded_types[decoded_line[:6]] += 1
                            except KeyError:
                                try:
                                    not_decoded_types[decoded_line[:6]] = 1
                                except IndexError:
                                    # Could not record the type of not processed type for this line:
                                    pass
                    else:
                        # The line was not decoded properly:
                        print("*** ERROR - NEITHER UTF-8 NOR ASCII DECODED THE LINE !!!<br>")
                        print("*** ERROR - Number of line = %d<br>" %num_line)
                        print("*** ERROR - file_line =", file_line,"<br>")
                        print("*** ERROR - strip_line =", strip_line,"<br>")
                        print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
                elif strip_line[:3] == b"<p>":
                    # This is a parameter, which will probably be part of a list:
                    # NO NEED TO DECODE, SLICING SHOULD BE ENOUGH
                    # CORRECTION: DECODED IS NEEDED, SO AS TO NOT GET A BINARY VALUE ("b'0" OR SIMILAR FOR EXAMPLE)
                    decoded_line, decoded = decode_line(strip_line, num_line)
                    if DEBUG == True:
                        if num_line <= MAX_LINES_TO_SHOW:
                            print("DEBUG --- ENTERING <p>...<br>")
                            print("DEBUG --- parameter value = %s<br>" %decoded_line[3:-4])
                            print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
                    if in_item == True:
                        # We are inside an item, add the parameter to the item (not ure if this should be the case...):
                        list_of_items.append(decoded_line[3:-4])
                    elif in_list == True:
                        list_of_elements.append(decoded_line[3:-4])
                    else:
                        # Not inside a list or inside an item, should not be the case:
                        print("* WARNING --- FOUND A 'p' LINE OUTSIDE A LIST OR ITEM ! *<br>")
                        print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
                elif strip_line[:6] == b"</item":
                    # This is the closing of the current composite item (inside a list, or maybe inside an object):
                    # NO NEED TO DECODE.
                    # Close the item:
                    in_item = False
                    if DEBUG == True:
                        if num_line <= MAX_LINES_TO_SHOW:
                            print("DEBUG --- CLOSING item...<br>")
                            print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
                    if in_list == True:
                        # We are currently inside a list, the item is part of the list:
                        # Add the item to the list:
                        list_of_elements.append(list_of_items)
                    else:
                        # We are not currently inside a list, the item is part of a parameter (probably, this will never be the case):
                        # Add it to the parameter list (with empty name???)
                        if DEBUG == True:
                            print("DEBUG --- *WARNING - item found directly below a managed object *<br>")
                            print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
                        mo_parameter_names.append('')
                        mo_parameter_values.append(list_of_items)
                elif strip_line[:6] == b"</list":
                    # This is the closing of a list of parameters:
                    # NO NEED TO DECODE.
                    # Close the list, and store it as a parameter of the current MO object:
                    in_list = False
                    if DEBUG == True:
                        if num_line <= MAX_LINES_TO_SHOW:
                            print("DEBUG --- CLOSING list...<br>")
                            print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
                    mo_parameter_names.append(list_name)
                    mo_parameter_values.append(list_of_elements)
                elif strip_line[:15] == b"</managedObject":
                    # This is the end of an object:
                    # This is the closing of a managedObject, store the managedObject record in its proper dataframe:
                    # NO NEED TO DECODE.
                    # Close the managedObject, and store it in the table:
                    in_mo = False
                    # BEGIN - MODIFICATION - VERSION 3.0:
                    new_record_names = field_names+mo_parameter_names
                    new_record_values = values+mo_parameter_values
                    #new_record = np.reshape(np.array(new_record_values, dtype=object), (1,len(new_record_values)))
                    if DEBUG == True:
                        if num_line <= MAX_LINES_TO_SHOW:
                            print("DEBUG --- Closing MO...<br>")
                            print("DEBUG --- object of table = %s<br>" %table_name)
                            print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
                    if NON_DEBUG == True:
                        if num_line <= MAX_LINES_TO_SHOW:
                            print("DEBUG --- new_record_names = ", new_record_names,"<br>")
                            print("DEBUG --- new_record_values = ", new_record_values,"<br>")
                    try:
                        #DEBUG_num_ops['pd.DataFrame()'] += 1
                        #DEBUG_num_ops['pd.concat()'] += 1
                        columns_structure_key = "/".join(new_record_names)
                        try:
                            # Check if the table is already in the dictionary (first key):
                            if (tables_dict[table_name] == {}):
                                # The table has not been included yet in the dictionary:
                                # This part of the code should never be reached !!
                                print("*** WARNING --- THIS PART OF THE CODE SHOULD HAVE NEVER BEEN REACHED !!! --- Line:",inspect.currentframe().f_back.f_lineno,"<br>")
                                print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
                                # COMMANDS TO FAIL AND STOP
                                #a = {'1':1,'2':2}
                                #b = a['3']
                            else:
                                # The table is already in the dictionary, and have some items in it, let's see if the 
                                # current column structure for the table is already there too:
                                try:
                                    tables_dict[table_name][columns_structure_key][0] += 1
                                    DEBUG_num_ops['list.append()'] += 1
                                    tables_dict[table_name][columns_structure_key][2].append(new_record_values)
                                except KeyError:
                                    # This columns structure is not yet recorded for this table, initialize it:
                                    tables_dict[table_name][columns_structure_key] = [1,len(new_record_names),[new_record_values]]
                        except KeyError:
                            # The table is not in the dictionary yet, initialize the table entry with this struct and data:
                            tables_dict[table_name] = {columns_structure_key : [1,len(new_record_names),[new_record_values]]}
                    except:
                        # Any other, unexpected error:
                        # DEBUG
                        print("*** ERROR --- UNEXPECTED ERROR WHEN CLOSING MANAGED OBJECT !!! --- Code line:",inspect.currentframe().f_back.f_lineno,"<br>")
                        print("*** SYSTEM INFO ON ERROR: %s<br>" %sys.exc_info()[0])
                        print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
                        # COMMANDS TO FAIL AND STOP
                        #a = {'1':1,'2':2}
                        #b = a['3']
                else:
                    # Any other line has not been contemplated yet, record it:
                    not_processed_lines += 1
                    try:
                        not_processed_types[strip_line[:4]] += 1
                    except KeyError:
                        try:
                            not_processed_types[strip_line[:4]] = 1
                        except IndexError as error_index:
                            # Could not record the type of not processed type for this line:
                            print("*** ERROR --- COULD NOT RECORD THE TYPE OF NOT-PROCESSED LINE !!! --- Code line:",inspect.currentframe().f_back.f_lineno,"<br>")
                            print("*** CURRENT FILE LINE: %d<br>" %num_line)
                            print("*** SYSTEM INFO ON ERROR: %s<br>" %error_index)
                            print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
            else:
                # If we are not inside an object of interest, just ignore the line, do not process it.
                # Do nothing, go to the next line.
                pass
# At the end of the process, we have everything we need in the dict{dict{list[rows,columns,list[data]]}},
# we then convert it into the relevant DataFrames:
#DEBUG_num_ops['pd.concat()'] += 1
tables_df_dict = {}
for clave_tabla in sorted(tables_dict.keys()):
    element = 0
    # POSSIBLE IMPROVEMENT: GENERATE EACH DATAFRAME USING THE MOST REPEATED COLUMNS STRUCTURE.    
    for clave_col_struct in tables_dict[clave_tabla].keys():
        element += 1
        if (element == 1):
            # This is the first element, it generates the initial DataFrame structure.
            DEBUG_num_ops['pd.DataFrame()'] += 1
            try:
                tables_df_dict[clave_tabla] = pd.DataFrame(data=np.array(tables_dict[clave_tabla][clave_col_struct][2], dtype=object).reshape((tables_dict[clave_tabla][clave_col_struct][0],tables_dict[clave_tabla][clave_col_struct][1])),
                                                           columns=clave_col_struct.split('/'))
            except:
                # Could not add a given DataFrame into a given table:
                print("*** ERROR --- COULD NOT PARSE '%s' COLUMN STRUCT INTO DATAFRAME FOR TABLE %s<br>" %(clave_col_struct,clave_tabla))
                print("*** SYSTEM INFO ON ERROR: %s<br>" %sys.exc_info()[0])
                print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
                df_parsing_errors += 1
                try:
                    # Record the struct column unable to be parsed in this table:
                    try:
                        df_parsing_affected_items[clave_tabla].append(clave_col_struct)
                    except:
                        print("*** ERROR --- COULD NOT RECORD THE DATAFRAME PARSING ERROR FOR TUPLE (table,col_struct) = (%s,%s)<br>" %(clave_tabla,clave_col_struct))
                        print("*** SYSTEM INFO ON ERROR: %s<br>" %sys.exc_info()[0])
                        print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
                except KeyError:
                    # This table has not an entry yet, initialize it:
                    try:
                        df_parsing_affected_items[clave_tabla] = list(clave_col_struct)
                    except:
                        print("*** ERROR --- COULD NOT RECORD THE DATAFRAME PARSING ERROR FOR TUPLE (table,col_struct) = (%s,%s)<br>" %(clave_tabla,clave_col_struct))
                        print("*** SYSTEM INFO ON ERROR: %s<br>" %sys.exc_info()[0])
                        print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
        else:
            # Add the next structure to the DataFrame:
            DEBUG_num_ops['pd.concat()'] += 1
            try:
                tables_df_dict[clave_tabla] = pd.concat([tables_df_dict[clave_tabla],pd.DataFrame(data=np.array(tables_dict[clave_tabla][clave_col_struct][2], dtype=object).reshape((tables_dict[clave_tabla][clave_col_struct][0],tables_dict[clave_tabla][clave_col_struct][1])),
                                                      columns=clave_col_struct.split('/'))], ignore_index=True)
            except:
                # Could not add a given DataFrame into a given table:
                print("*** ERROR --- COULD NOT PARSE '%s' COLUMN STRUCT INTO DATAFRAME FOR TABLE %s<br>" %(clave_col_struct,clave_tabla))
                print("*** SYSTEM INFO ON ERROR: %s<br>" %sys.exc_info()[0])
                print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
                df_parsing_errors += 1
                try:
                    # Record the struct column unable to be parsed in this table:
                    try:
                        df_parsing_affected_items[clave_tabla].append(clave_col_struct)
                    except:
                        print("*** ERROR --- COULD NOT RECORD THE DATAFRAME PARSING ERROR FOR TUPLE (table,col_struct) = (%s,%s)<br>" %(clave_tabla,clave_col_struct))
                        print("*** SYSTEM INFO ON ERROR: %s<br>" %sys.exc_info()[0])
                        print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
                except KeyError:
                    # This table has not an entry yet, initialize it:
                    try:
                        df_parsing_affected_items[clave_tabla] = list(clave_col_struct)
                    except:
                        print("*** ERROR --- COULD NOT RECORD THE DATAFRAME PARSING ERROR FOR TUPLE (table,col_struct) = (%s,%s)<br>" %(clave_tabla,clave_col_struct))
                        print("*** SYSTEM INFO ON ERROR: %s<br>" %sys.exc_info()[0])
                        print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")

print("<br>")
print("PROCESS COMPLETED.<br>")
print("<br>")
print("- Number of lines read = %d<br>" %num_line)
print("<br>")
print(" - Tables generated =", tables_df_dict.keys(),"<br>")
print("<br>")
print(" - Not processed lines = %d<br>" %not_processed_lines)
print(" - Count by type of not processed lines:<br>")
print(not_processed_types,"<br>")
print("<br>")
print(" - Not decoded lines = %d<br>" %not_decoded_lines)
print(" - Count by type of not decoded lines:<br>")
print(not_decoded_types,"<br>")
print("<br>")
print(" Summary of operations:<br>")
print(DEBUG_num_ops,"<br>")
print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")

# SUMMARY OF CREATED TABLES:
print("<br>")
print("SUMMARY OF DECODED TABLES:<br>")
print("==========================<br>")
print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
for clave in tables_df_dict.keys():
    print("Table %s - %d elements<br>" %(clave,tables_df_dict[clave].shape[0]))
    print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")


#################################################################################################
# WRITE TABLES TO EXCEL OUTPUT FILE
#################################################################################################
print("<br>")
print("<br>")
print("Writing the tables to Excel file...<br>")
print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
### Export selected tables:
# Source for multiple Excel saving: https://xlsxwriter.readthedocs.io/example_pandas_multiple.html

# Write each dataframe to a different worksheet.
try:
    if export_specification == {}:
        lista_claves = sorted(tables_df_dict.keys())
    else:
        lista_claves =sorted(export_specification.keys())
except:
    lista_claves = sorted(tables_df_dict.keys())
for clave in lista_claves:
    print("WRITING TABLE %s TO EXCEL WRITER OBJECT...<br>" %clave)
    print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
    try:
        #tables_df_dict[clave].to_excel(writer, sheet_name=clave, index=False, freeze_panes=(1,0))
        tables_df_dict[clave].apply(pd.to_numeric, errors = 'ignore').\
            to_excel(writer, sheet_name=clave, index=False, freeze_panes=(1,0))
    except KeyError:
        print("*** ERROR - TABLA %s NO GENERADA !! ***<br>" %clave)
        print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
    except:
        print("*** ERROR NO ESPECIFICADO AL GENERAR LA TABLA %s !! ***<br>" %clave)
        print("--- SYSTEM ERROR CODE: %s !! ***<br>" %sys.exc_info()[0])
        print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")

# Close the Pandas Excel writer and output the Excel file.
print("SAVING EXCEL WRITER OBJECT TO FILE...")
print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
writer.save()
print("...done.<br><br>")
print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")

#################################################################################################
# END OF PROGRAM
#################################################################################################
if selected_out_file == "main":
    print("Output file generated: %s<br>" %output_file)
else:
    print("Output file generated: %s<br>" %backup_output_file)
print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
print("<br>")
print("<br>")
print("--- END OF PROGRAM --- SUCCESS<br><br>")
print("<br>")
print("<script>window.scrollTo(0,document.body.scrollHeight);</script>")
# End the HTML content printing:
print("</body>")
print("<script>")
print("document.title='XML FILE PROCESSING - FINISHED - SUCCESS'")
print("</script>")
print("</html>") 
