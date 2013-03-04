/*
Copyright (c) 2013, Evan Cordeiro
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions is met:
    
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
*/
var SchemaBuilder = { 
	
	defaultOptions : {
		prefix : "db_" ,
		table_class : "schema_table"
	},
	
	SchemaBuilder : function(json, options){

		this.schema = json;
		this.tables = this.schema.tables;
		this.DOMTables = {};
		this.options = options || SchemaBuilder.defaultOptions;	
		this._column_descriptions = {};
			
		this.buildTables = function(){
				
			for( table_name in this.tables ){
				this.buildTable( this.tables[table_name] )
			}
		}

		this.buildTable = function(table){
		
			var html_table, thead, tr, th, td, text;
			
			html_table = document.createElement("table");
			html_table.setAttribute("id", this.options.prefix + table.attributes.TABLE_NAME);
			html_table.setAttribute("class", this.options.table_class);
			
			thead = html_table.appendChild( document.createElement("thead") );
			tr = thead.appendChild( document.createElement("tr") );
			
			for( col_name in table.columns ){
				for( col_attr in table.columns[col_name].attributes ){	
					var th = tr.appendChild( document.createElement("th" ) );
					th.setAttribute("class", col_attr );
					th.appendChild( document.createTextNode(col_attr) );
				}
				break;
			}
			
			th = tr.appendChild( document.createElement("th" ) );
			th.setAttribute("class", "description" );
			th.appendChild( document.createTextNode("DESCRIPTION") );
			
			tbody = html_table.appendChild( document.createElement("tbody") );
			
			for(var i = 0; i < table.column_names.length; i++ ){
				col_name = table.column_names[i];
				var col = table.columns[col_name];
				var tr = tbody.appendChild( document.createElement("tr") );
				tr.setAttribute("id", this.options.prefix + table.attributes.TABLE_NAME +"-"+ col.attributes.COLUMN_NAME );
								
				for( var j = 0; j < this.schema.column_attribute_names.length; j++ ){
					attr_name = this.schema.column_attribute_names[j];
					var td = tr.appendChild( document.createElement("td") ); 
					td.setAttribute("class", attr_name );
					td.appendChild( document.createTextNode( table.columns[col_name].attributes[attr_name] ) );					
				}
				
				if( hasOwnProperty( col, "fk" ) ){
						
					tr.setAttribute( "class", "has-foreign-key");		
					tr.setAttribute( "data-fk_table_id", this.options.prefix + table.attributes.TABLE_NAME);		
					tr.setAttribute( "data-fk_column_id", this.options.prefix + table.attributes.TABLE_NAME +"-"+ col.attributes.COLUMN_NAME);		
					console.log(tr);
				}
				
				var td = tr.appendChild( document.createElement("td") ); 
				td.setAttribute("class", "description" );
				td.appendChild( document.createTextNode( this.getColumnDescription(table.attributes.TABLE_NAME, col_name) ) );
				
				
				
			}
			
			this.DOMTables[table.attributes.TABLE_NAME] = html_table;
		}
		
		
		this.getTable = function(table_name){
			return this.DOMTables[table_name];
		}
		
		this.getAllTables = function(){
			
			tables = [];
			
			for( table in this.tables ){
				tables.push( this.getTable(table) ) 
			}
			
			return tables;
			
		}
		
		this.setColumnDescriptions = function(desc){
			this._column_descriptions = desc;
		}
		
		this.getColumnDescription = function(t_name, c_name){
			if( hasOwnProperty( this._column_descriptions, t_name ) ){ 
				if( hasOwnProperty(this._column_descriptions[t_name], c_name )){
					return this._column_descriptions[t_name][c_name];
				}
			}
			return "";
		}
		
		function hasOwnProperty(obj, prop){
			var proto = obj.__proto__ || obj.constructor.prototype;
			return (prop in obj) &&
				(!(prop in proto) || proto[prop] !== obj[prop]);
		}

		if ( Object.prototype.hasOwnProperty ) {
			function hasOwnProperty(obj, prop){
				return obj.hasOwnProperty(prop);
			}
		}
		
	}


}