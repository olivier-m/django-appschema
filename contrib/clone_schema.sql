-- Create plpgsql language if not exists
-- See http://wiki.postgresql.org/wiki/CREATE_OR_REPLACE_LANGUAGE
CREATE OR REPLACE FUNCTION make_plpgsql() RETURNS VOID AS $body$
	CREATE LANGUAGE plpgsql;
$body$ LANGUAGE SQL;

SELECT
    CASE
    WHEN EXISTS(
        SELECT 1
        FROM pg_catalog.pg_language
        WHERE lanname='plpgsql'
    )
    THEN NULL
    ELSE make_plpgsql()
END;
 
DROP FUNCTION make_plpgsql();

--
-- Function to copy a schema to another
--
CREATE OR REPLACE FUNCTION public.clone_schema(text, text) RETURNS integer AS $body$
DECLARE
	i_src ALIAS FOR $1;
	i_dst ALIAS FOR $2;
	v_table information_schema.tables.table_type%TYPE;
	v_fk record;
	v_seq record;
	v_seq_field record;
	v_func text;
	v_view record;
	
	v_sql text;
BEGIN
	-- Creatin schema
	EXECUTE('CREATE SCHEMA "' || i_dst || '";');
	
	-- Copying tables (with data)
	FOR v_table IN SELECT table_name 
		FROM information_schema.tables 
		WHERE table_type = 'BASE TABLE'
		AND table_schema = i_src
		ORDER BY table_name
	LOOP
		EXECUTE(
			'CREATE TABLE ' || i_dst || '.' || v_table
			|| '( LIKE ' || i_src || '.' || v_table
			|| ' INCLUDING DEFAULTS '
			|| ' INCLUDING CONSTRAINTS'
			|| ' INCLUDING INDEXES'
			|| ')'
		);
		EXECUTE(
			'INSERT INTO ' || i_dst || '.' || v_table
			|| ' (SELECT * FROM '|| i_src || '.' || v_table || ')'
		);
	END LOOP;
	
	-- Copying sequences
	FOR v_seq IN SELECT c.oid, c.relname
		FROM pg_catalog.pg_class c
		LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
		WHERE n.nspname = 'local'
		AND c.relkind = 'S'
	LOOP
		-- There is not way to obtain sequence definition then we simply
		-- create a new one. That's a bit lame.
		EXECUTE('CREATE SEQUENCE ' || i_dst || '.' || v_seq.relname);
		
		-- We need to alter every field that uses source schema sequences
		-- to use newly created ones
		FOR v_seq_field IN SELECT DISTINCT cl.relname, att.attname
			FROM pg_depend dep
			LEFT JOIN pg_class cl ON dep.refobjid=cl.oid
			LEFT JOIN pg_attribute att ON dep.refobjid=att.attrelid AND dep.refobjsubid=att.attnum
			WHERE dep.objid=v_seq.oid
			AND cl.relkind = 'r'
		LOOP
			EXECUTE('ALTER TABLE ' || i_dst || '.' || v_seq_field.relname
					|| ' ALTER COLUMN ' || v_seq_field.attname
					|| ' SET DEFAULT nextval(''' || i_dst || '.' || v_seq.relname || ''')');
			EXECUTE('ALTER SEQUENCE ' || i_dst || '.' || v_seq.relname
					|| ' OWNED BY ' || i_dst || '.' || v_seq_field.relname || '.' || v_seq_field.attname);
		END LOOP;
		
	END LOOP;
	
	-- Copying foreign keys
	FOR v_fk IN SELECT c.relname as tablename, conname,
		pg_catalog.pg_get_constraintdef(r.oid, true) as condef
		FROM pg_catalog.pg_constraint r
		INNER JOIN pg_catalog.pg_namespace n ON n.oid = r.connamespace
		INNER JOIN pg_catalog.pg_class c ON c.oid = r.conrelid
		WHERE r.contype = 'f'
		AND n.nspname = i_src
	LOOP
		v_fk.condef := replace(v_fk.condef, i_src || '.', i_dst || '.');
		EXECUTE(
			'ALTER TABLE ' || i_dst || '.' || v_fk.tablename
			|| ' ADD CONSTRAINT ' || v_fk.conname || ' ' || v_fk.condef
		);
	END LOOP;
	
	-- Copying functions
	FOR v_func IN SELECT pg_catalog.pg_get_functiondef(p.oid)
		FROM pg_catalog.pg_proc p
		LEFT JOIN pg_catalog.pg_namespace n ON n.oid = p.pronamespace
		WHERE n.nspname = i_src
	LOOP
		v_func := replace(v_func, i_src || '.', i_dst || '.');
		EXECUTE(v_func);
	END LOOP;
	
	-- Copying views
	-- TODO: handle custom column names in views
	FOR v_view IN SELECT c.relname, pg_catalog.pg_get_viewdef(c.oid) as viewdef
		FROM pg_catalog.pg_class c
		LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
		WHERE n.nspname = 'local'
		AND c.relkind IN ('v', 's')
	LOOP
		v_view.viewdef := replace(v_view.viewdef, i_src || '.', i_dst || '.');
		EXECUTE('CREATE VIEW ' || i_dst || '.' || v_view.relname || ' AS ' || v_view.viewdef);
	END LOOP;
	
	RETURN 1;
END;
$body$ LANGUAGE 'plpgsql';
