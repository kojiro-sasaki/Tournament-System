GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA public
TO service_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE
ON TABLES
TO service_role;

-- Allow anon users to read all public tables
GRANT SELECT
ON ALL TABLES IN SCHEMA public
TO anon;

-- Allow anon users to register new users only
GRANT INSERT
ON public.users
TO anon;