CREATE FUNCTION delete_old_rows() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  DELETE FROM token WHERE timestamp < NOW() - INTERVAL '65 seconds';
  RETURN NULL;
END;
$$;
CREATE TRIGGER trigger_delete_old_rows
    AFTER INSERT ON token
    EXECUTE PROCEDURE delete_old_rows();