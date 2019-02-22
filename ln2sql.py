#!/usr/bin/python3

import os, sys, getopt
import unicodedata
import mysql.connector
import matplotlib.pyplot  as plt
import numpy as np
import pandas as pd

from Database import Database
from LangConfig import LangConfig
from Parser import Parser
from Thesaurus import Thesaurus
from StopwordFilter import StopwordFilter

class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class ln2sql:
    def __init__(self, database_path, input_sentence, language_path, thesaurus_path, json_output_path):
        database = Database()
        database.load(database_path)
        #database.print_me()

        config = LangConfig()
        config.load(language_path)

        parser = Parser(database, config)
        #print(str(parser))

        if thesaurus_path is not None:
            thesaurus = Thesaurus()
            thesaurus.load(thesaurus_path)
            parser.set_thesaurus(thesaurus)

        queries = parser.parse_sentence(input_sentence)
        #print(str(queries)) 

        if json_output_path is not None:
            self.remove_json(json_output_path)
            for query in queries:
                query.print_json(json_output_path)

        full_query = ''
        for query in queries:
                full_query += str(query)
                string = (full_query.replace("\n"," "),)
                mydb = mysql.connector.connect(host='localhost',database='mysql',user='root',password='root')
                mycursor = mydb.cursor()
                sql = """%s"""
                #query = "SELECT * FROM city";
                mycursor.execute(sql, string)
                myresult = mycursor.fetchall()
                for row in myresult:
                     print(row)

    def remove_json(self, filename="output.json"):
        if os.path.exists(filename):
            os.remove(filename)

def print_help_message():
    print('\n')
    print ('Usage:')
    print ('\tpython ln2sql.py -d <path> -l <path> -i <input-sentence> [-t <path>] [-j <path>]')
    print ('Parameters:')
    print ('\t-h\t\t\tprint this help message')
    print ('\t-d <path>\t\tpath to SQL dump file')
    print ('\t-l <path>\t\tpath to language configuration file')
    print ('\t-i <input-sentence>\tinput sentence to parse')
    print ('\t-j <path>\t\tpath to JSON output file')
    print ('\t-t <path>\t\tpath to thesaurus file')
    print ('\n')

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"d:l:i:t:j:")
        database_path = None
        input_sentence = None
        language_path = None
        thesaurus_path = None
        json_output_path = None

        for i in range(0, len(opts)):
            if opts[i][0] == "-d":
                database_path = opts[i][1]
            elif opts[i][0] == "-l":
                language_path = opts[i][1]
            elif opts[i][0] == "-i":
                input_sentence = opts[i][1]
            elif opts[i][0] == "-j":
                json_output_path = opts[i][1]
            elif opts[i][0] == "-t":
                thesaurus_path = opts[i][1]
            else:
                print_help_message()
                sys.exit()

        if (database_path is None) or (input_sentence is None) or (language_path is None):
            print_help_message()
            sys.exit()
        else:
            if thesaurus_path is not None:
                thesaurus_path = str(thesaurus_path)
            if json_output_path is not None:
                json_output_path = str(json_output_path)

        #try:
        ln2sql(str(database_path), str(input_sentence), str(language_path), thesaurus_path, json_output_path)
        #except Exception, e:
        #    print color.BOLD + color.RED + str(e) + color.END

    except getopt.GetoptError:
        print_help_message()
        sys.exit()

if __name__ == '__main__':
    main(sys.argv[1:])
