# Architecture

The demo is a self-contained offline desktop application.

- `core.py`: local database schema, password hashing and sales transaction logic.
- `clientes.py`: customer registration and updates.
- `inventario.py`: study catalog and direct costs.
- `ventas.py`: multi-line sales with local folios.
- `pedidos.py`: laboratory Excel receipts and financial reporting exports.
- `pedidos_ui.py`: date and branch filters for exports.
- `proveedor.py`: validated Excel catalog import and export.
- `informacion.py`: local demo configuration.
- `scripts/init_demo.py`: entirely synthetic example data.

The app intentionally does not synchronize databases between computers. Each installation stores its own local SQLite database. The demo does not implement robust conflict resolution across branches or real-world patient privacy controls.
