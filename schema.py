#!/usr/bin/python

'''
Copyright (c) 2013, Evan Cordeiro
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following condition is met:
    
    * Neither the name of the author nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import os, sys, json

try:
	import MySQLdb as mdb
	import MySQLdb.cursors
except:
	print "Must have the python module MySQLdb installed."
	print "Try sudo apt-get install python-mysqldb or apt-cache search mysql python"
	exit()

class SchemaParser:	

	req_args = [
			{ 'key' : "host", 'prompt' : "host: ", 'type' : unicode},
			{ 'key' : "user", 'prompt' : "mysql user: ", 'type' : unicode },
			{ 'key': "pass", 'prompt' : "mysql password: ", 'type' : unicode },
			{ 'key' : "schema", 'prompt' : "database name: ", 'type' : unicode },
			]
	
	opt_args = [
			{ 'key' : "port", 'prompt' : "port: ", 'type' : int, 'default' : 3306 },
			{ 'key' : "table_columns", 'prompt' : "table column list: ", 'type' : list, 'default' : ["TABLE_NAME"] },
			{ 'key' : "column_columns", 'prompt' : "column column list: ", 'type' : list, 'default' : ["COLUMN_NAME","COLUMN_TYPE", "COLUMN_DEFAULT","IS_NULLABLE",] },
			{ 'key' : "show_views", 'prompt' : "show views? : ", 'type' : bool, 'default' : False },
			{ 'key' : "verbose", 'prompt' : "verbose: ", 'type' : bool, 'default' : False },
			{ 'key' : "encoding", 'prompt' : "encoding (input and db): ", 'type' : unicode, 'default' : "utf8" }
			]

	schema_obj = {}
			
	def __init__(self, args = None):
		if args is None:
			if len( sys.argv ) > 1:
				try:
					args = json.loads( sys.argv[1] )
					self.validateParameters(args)
				except ValueError as e:
					print "Command-line arguments supplied in non JSON format - switching to interactive mode"
					self.getParameters()
			else:
				self.getParameters()
		else:
			self.validateParameters(args)
		
	def getParameters(self, args = None):
		
		inputs = {}
		req_args = self.req_args
		opt_args = self.opt_args
		
		for arg in req_args:
			if arg['type'] == bool:
				inputs[arg['key']] = self.raw_bool(arg['prompt']) 
			elif arg['type'] == int:
				inputs[arg['key']] = self.raw_int(arg['prompt']) 
			elif arg['type'] == str:
				inputs[arg['key']] = self.raw_string(arg['prompt']) 
			elif arg['type'] == list:
				inputs[arg['key']] = self.raw_list(arg['prompt'])
			elif arg['type'] == unicode:
				inputs[arg['key']] = unicode( self.raw_string(arg['prompt']))
			else:
				exit("unexpected error in self.req_args")
	
		for arg in opt_args:
			inputs[arg['key']] = arg['default']
	
		self.params = inputs
				
	
	def validateParameters(self, inputs):
		req_args = self.req_args
		opt_args = self.opt_args
		
		for arg in req_args:
			try:
				if not type( inputs[arg['key']] ) == arg['type']:
					print "parameter " + arg['key'] + " : " + inputs[arg['key']] + " expected " + str(arg['type']) + " but found " + str( type( inputs[arg['key']] ) )
					exit()
			except KeyError:
				print "parameter " + arg['key'] + " not supplied"
				exit()
		
		for arg in opt_args:
			try:
				if not type( inputs[arg['key']] ) == arg['type']:
					print "parameter " + arg['key'] + " expected " + str(arg['type']) + " using default"
					inputs[arg['key']] == arg['default']
			except KeyError:
				inputs[arg['key']] = arg['default']
		
		self.params = inputs
	
	def raw_bool(self, prompt, loop = True):
		while True:
			input = raw_input(prompt)
			if input.lower() in [ 'true', 't', 'y', 'yes' ]:
				return True
			elif input.lower() in [ 'false', 'f', 'n', 'no' ]:
				return False
			else:
				print "expecting 'true/false/t/f/y/n/yes/no'"
				if not loop:
					return None
			
	def raw_int(self, prompt, loop = True):
		while True:
			try:
				input = int( raw_input(prompt) )
				return input
			except ValueError:
				print "expecting int value"
				if not loop:
					return None
			
		
	def raw_string(self, prompt, loop = True):
		return raw_input(prompt)

	def raw_list(self, prompt, loop = True):
		while True:
			input = raw_input(prompt)
			try:
				input = json.loads(input)
				return input
			except:
				print "expecting list in format [\"str1\", \"str2\", ...] "
				if not loop:
					return None
		
		return input

	
	def getSchema(self):
		self.schema_obj['column_attribute_names'] = self.params['column_columns']
		self.getTables()
		self.getColumns()
		self.getForeignKeys()
		
	def getTables(self):
		table_cols = ""
		for col_name in self.params['table_columns']:
			table_cols += col_name + ","
		table_cols = table_cols[:-1]
		tables_sql = "SELECT "+table_cols+" FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '" + self.params['schema'] + "'"
		
		if not self.params['show_views']:
			tables_sql += " AND TABLE_TYPE <> 'VIEW'"
		
		tables_sql += ";"
		tables = self.db_select(tables_sql)
		
		self.schema_obj['tables'] = {}
		for t in tables:
			table = {}
			table['attributes'] = {}
			for t_attr, t_val in t.iteritems():
				table['attributes'][t_attr] = t_val
			self.schema_obj['tables'][t['TABLE_NAME']] = table
			
	def getColumns(self):
		column_cols = ""
		for col_name in self.params['column_columns']:
			column_cols += col_name + ","
		column_cols = column_cols[:-1]
		for table in self.schema_obj['tables'].itervalues():
			
			col_sql = "SELECT "+column_cols+"  FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '" + self.params['schema'] + "' AND TABLE_NAME = '"+ table['attributes']['TABLE_NAME'] +"' ORDER BY ORDINAL_POSITION"
			
			col_sql += ";"
			cols = self.db_select(col_sql)
		
			table['columns'] = {}
			table['column_names'] = []
			for c in cols:
				col = {}
				col['attributes'] = {}
				table['column_names'].append(c['COLUMN_NAME'])
				
				for c_attr, c_val in c.iteritems():
					col['attributes'][c_attr] = c_val
				table['columns'][c['COLUMN_NAME']] = col 
	
	def getForeignKeys(self):
		fk_sql = "SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE CONSTRAINT_SCHEMA = '"+self.params['schema']+"' AND REFERENCED_TABLE_SCHEMA = '"+self.params['schema']+"' AND POSITION_IN_UNIQUE_CONSTRAINT IS NOT NULL;";
		fkeys = self.db_select(fk_sql)
		for fkey in fkeys:
			self.schema_obj['tables'][fkey['TABLE_NAME']]['columns'][fkey['COLUMN_NAME']]['fk'] = { 'table' : fkey['REFERENCED_TABLE_NAME'], 'column' : fkey['REFERENCED_COLUMN_NAME'] }
			
		
	def db_select(self, sql, vars = () ):
		dbh = mdb.connect(host=self.params['host'], user=self.params['user'], passwd=self.params['pass'], db=self.params['schema'], cursorclass=mdb.cursors.DictCursor)
		cursor = dbh.cursor()
		cursor.execute(sql.encode(self.params['encoding']), vars)
		ret = cursor.fetchall()
		cursor.close()
		return ret
	
	def json(self):
		out = json.dumps(self.schema_obj)
		return out.encode(self.params['encoding'])
		
	def verbose(self, set = None):
		if set is None:
			return self.params['verbose']
		else:
			self.params['verbose'] = bool( set )
			return self.params['verbose']
		
try:

	parser = SchemaParser()
	
	
	if parser.verbose():
		print "Welcome to " + sys.argv[0] + "!" 
		print "Rated the top MySQL schema to JSON util in " + os.path.dirname(os.path.realpath(__file__))
	
	parser.getSchema()

	if parser.verbose():
		file_loc = raw_input("output file name: ")
		try:
			ofile = open(file_loc)
		except:
			print "Could not open " + file_loc + " for writing"
			exit()
		ofile.write( parser.json() )
		ofile.close()	
		print "done"
	else:	
		print parser.json()

	exit()

except Exception as e:
	print "unexpected error " + str( e )
